# 🔓 Decrypting the CEO-Bench Database

Each finished CEO-Bench run leaves a single ledger file at:

```
<run_dir>/world.nmdb
```

`*.nmdb` files are **SQLCipher** databases — page-level AES-256 encrypted SQLite.
Without the key, the file looks like random bytes; vanilla `sqlite3` cannot open
it (different page layout). The key (`NMDB_KEY`) is held only by the host
harness and never exposed to the agent sandbox.

This page covers two things:

1. **Decrypt** an `.nmdb` ledger to a plain `world.db` SQLite file.
2. **Compute cash-on-hand** for every day of the run.

---

## 🔑 The `NMDB_KEY` environment variable

The SQLCipher key is read from `NMDB_KEY`. Whoever launched the run set it
(typically via `.env`); to decrypt a run you need the **same** value that was
active when the run was created. If the key is rotated, old `.nmdb` files become
permanently undecryptable, so keep a record of the key you ran with.

```bash
export NMDB_KEY="<the key that was active when the run was launched>"
```

---

## Option A — One-shot decrypt to plain SQLite

The fastest way to get a normal `.db` file you can open with any tool
(`sqlite3` CLI, DB Browser for SQLite, pandas, etc.):

```bash
uv run python scripts/decode_db.py bash_agent_runs/run_<id>/world.nmdb \
    -o /tmp/world.db
```

Then open it like any SQLite database:

```bash
sqlite3 /tmp/world.db
sqlite> .tables
```

`scripts/decode_db.py` also supports:

```bash
# Full JSON dump of every table
uv run python scripts/decode_db.py path/to/world.nmdb --dump

# Just specific tables
uv run python scripts/decode_db.py path/to/world.nmdb --dump \
    --tables ledger,subscriptions,customer_state

# Drop into an interactive sqlite3 shell
uv run python scripts/decode_db.py path/to/world.nmdb --shell

# Export every table as CSV
uv run python scripts/decode_db.py path/to/world.nmdb --csv-dir /tmp/csvs/

# Quick summary (row counts, day range, ending cash)
uv run python scripts/decode_db.py path/to/world.nmdb --summary
```

---

## Option B — Open the encrypted file directly in Python

If you want to query without writing a plaintext copy to disk, open the
SQLCipher file in-place:

```python
from pathlib import Path
from saas_bench.db_protection import open_encrypted

conn = open_encrypted(Path("bash_agent_runs/run_<id>/world.nmdb"))
rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print([r[0] for r in rows])
```

`open_encrypted` reads `NMDB_KEY` from the environment and returns a normal
`sqlcipher3.Connection` — a drop-in for `sqlite3.Connection`.

For bulk analysis (recommended), load the whole DB into memory once:

```python
from saas_bench.db_protection import load_session_db
conn = load_session_db(Path("path/to/world.nmdb"))   # in-memory sqlite3 conn
```

---

## 💰 Computing cash-on-hand per day

Every monetary event in the simulation is appended to the `ledger` table:

| column     | type    | meaning                                                                                |
|------------|---------|----------------------------------------------------------------------------------------|
| `day`      | INTEGER | Simulated day on which the entry occurred (day 0 = initial funding)                    |
| `category` | TEXT    | One of: `subscription_payment`, `compute`, `capacity`, `advertising`, `operations`, `development`, `lead_acquisition_cost`, `initial_funding`, `market_research`, `group_research`, `research_project`, `ad_revenue` |
| `amount`   | REAL    | Positive for income, negative for cost                                                 |
| `note`     | TEXT    | Free-form description                                                                  |

**Cash-on-hand on day _d_** is just the running sum of `amount` over all entries
with `day ≤ d`. The starting balance is the `initial_funding` row on day 0.

### Per-day cash trajectory (one-row-per-day)

```sql
WITH daily_net AS (
    SELECT day, SUM(amount) AS net_change
    FROM ledger
    GROUP BY day
)
SELECT
    day,
    net_change,
    SUM(net_change) OVER (ORDER BY day) AS cash_on_hand
FROM daily_net
ORDER BY day;
```

### Cash on a specific day

```sql
SELECT COALESCE(SUM(amount), 0) AS cash_on_hand
FROM ledger
WHERE day <= :target_day;
```

### Per-day cash trajectory in pandas

```python
import pandas as pd
from saas_bench.db_protection import load_session_db

conn = load_session_db("bash_agent_runs/run_<id>/world.nmdb")
ledger = pd.read_sql_query("SELECT day, category, amount FROM ledger", conn)

daily = (
    ledger.groupby("day", as_index=False)["amount"]
          .sum()
          .rename(columns={"amount": "net_change"})
          .sort_values("day")
)
daily["cash_on_hand"] = daily["net_change"].cumsum()
print(daily.tail())
```

### Per-day revenue, costs, and cash together

```sql
WITH daily AS (
    SELECT
        day,
        SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS revenue,
        SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) AS costs,
        SUM(amount) AS net_change
    FROM ledger
    GROUP BY day
)
SELECT
    day,
    revenue,
    costs,
    net_change,
    SUM(net_change) OVER (ORDER BY day) AS cash_on_hand
FROM daily
ORDER BY day;
```

### Final score (end-of-run cash)

The headline benchmark score is simply:

```sql
SELECT COALESCE(SUM(amount), 0) AS final_cash FROM ledger;
```

This is exactly what `database.get_cash(conn)` returns inside the engine.

---

## 🧭 Other tables you may want

After decrypting, these are the most useful tables for analysis:

| Table             | What it holds                                                          |
|-------------------|------------------------------------------------------------------------|
| `ledger`          | Every income/cost event (use this for cash-on-hand)                    |
| `subscriptions`   | All individual subscriptions (active + churned), with plan + group     |
| `customer_state`  | Per-(group, day) customer counts and conversion-funnel state           |
| `enterprise_deals`| All enterprise contracts (status, MRR, seats, expiry)                  |
| `config_history`  | One row per day: prices, daily spend per category, capacity tier       |
| `ad_channel_leads`| Per-(day, channel, group) leads generated and spend                    |
| `predictions`     | Forecasts the agent submitted at each `next-week` call (cash + 95% CI) |
| `social_posts`    | Customer + competitor social-media posts seen by the agent             |
| `events`          | Competitor events, macro shocks, R&D milestones                        |
| `actions`         | Every tool call the agent made, with arguments                         |

Run `.schema <table>` in `sqlite3` (or `PRAGMA table_info(<table>)`) to see
columns and types.

---

## 🧷 Anti-cheat properties (for reference)

The encryption is what stops the agent from peeking ahead at hidden state during
a run:

- The `.nmdb` file is a SQLCipher DB — vanilla `sqlite3` (the only sqlite3 the
  agent sandbox has) **cannot** open it.
- The key lives only in `NMDB_KEY` on the host. The bwrap sandbox strips
  `NMDB_KEY` before spawning the agent.
- The public `novamind-operation` zipapp does not contain the key — it talks to
  the engine over an internal port that's only reachable from the host.

So the workflow is: run → encrypted ledger written by the host → after the run
finishes, set `NMDB_KEY` on your machine and decrypt for analysis.
