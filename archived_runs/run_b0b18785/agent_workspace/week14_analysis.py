import novamind_api as nm
import json

day = nm.vars.current_day
print(f"=== Week 14 Analysis (Day {day}) ===")

# Cash
cash = nm.query("SELECT SUM(amount) as cash FROM ledger")
print(f"Cash: ${cash['rows'][0]['cash']:,.0f}")

# Issues by group
issues = nm.query("SELECT group_id, COUNT(*) as n, AVG(days_open) as avg_days FROM issues WHERE status='open' GROUP BY group_id ORDER BY n DESC")
print("\n--- Issues by Group ---")
total_issues = 0
for r in issues['rows']:
    print(f"  {r['group_id']}: {r['n']} issues, avg {r['avg_days']:.1f} days")
    total_issues += r['n']
print(f"  TOTAL: {total_issues}")

# Subs by group
subs = nm.query("SELECT c.group_id, COUNT(*) as n, SUM(s.seat_count) as seats, SUM(s.seat_count*s.effective_price) as mrr FROM subscriptions s JOIN customers c ON s.customer_id=c.customer_id WHERE s.status='subscribed' GROUP BY c.group_id ORDER BY mrr DESC")
print("\n--- Subs by Group ---")
total_mrr = 0
for r in subs['rows']:
    seats = r['seats'] or 1
    n = r['n']
    mrr = r['mrr'] or 0
    total_mrr += mrr
    print(f"  {r['group_id']}: {n} subs, {seats} seats, MRR=${mrr:,.0f}")
print(f"  TOTAL MRR: ${total_mrr:,.0f}")

# Large enterprise subs
large = nm.query("SELECT s.customer_id, c.group_id, s.plan, s.seat_count, s.effective_price, s.seat_count*s.effective_price as mrr FROM subscriptions s JOIN customers c ON s.customer_id=c.customer_id WHERE s.status='subscribed' AND s.seat_count >= 100 ORDER BY mrr DESC LIMIT 20")
print("\n--- Large Enterprise Subs ---")
for r in large['rows']:
    print(f"  CID={r['customer_id']} {r['group_id']} Plan {r['plan']} {r['seat_count']}seats @${r['effective_price']:.2f} = ${r['mrr']:,.0f}/mo")

# Ledger costs last 7 days
costs = nm.query(f"SELECT category, SUM(amount)/7.0 as daily_avg FROM ledger WHERE day >= {day-7} AND amount < 0 GROUP BY category ORDER BY daily_avg ASC")
print("\n--- Daily Costs (Last 7 days) ---")
total_cost = 0
for r in costs['rows']:
    print(f"  {r['category']}: ${-r['daily_avg']:,.0f}/day")
    total_cost += -r['daily_avg']
print(f"  TOTAL COSTS: ${total_cost:,.0f}/day")

# Revenue last 7 days
rev = nm.query(f"SELECT SUM(amount)/7.0 as daily_avg FROM ledger WHERE day >= {day-7} AND amount > 0")
print(f"\n--- Daily Revenue (Last 7 days) ---")
print(f"  Revenue: ${rev['rows'][0]['daily_avg']:,.0f}/day")
print(f"  Net: ${rev['rows'][0]['daily_avg'] - total_cost:,.0f}/day")

