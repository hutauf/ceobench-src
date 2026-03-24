"""Test that stop/resume produces identical RNG-dependent behavior as continuous runs.

Runs multiple simulation trajectories with different stop/resume patterns and
verifies ALL RNG-dependent outputs match the reference (no-stop) trajectory.

Usage:
    cd projects/saas-bench
    uv run python tests/test_rng_determinism.py
"""
import sys
import sqlite3
import json
from pathlib import Path
from copy import deepcopy
from numpy.random import Generator, PCG64

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from saas_bench.database import init_database
from saas_bench.config import BenchmarkConfig
from saas_bench.simulation import Simulator
from saas_bench.db_protection import save_session_db, load_session_db


SEED = 42
TOTAL_DAYS = 30  # Enough days to see competitor events, macro cycles, etc.
TMPDIR = Path("/tmp/test_rng_determinism")


def run_continuous(seed: int, days: int) -> sqlite3.Connection:
    """Run simulation for `days` without stopping. Returns the DB connection."""
    rng = Generator(PCG64(seed))
    config = BenchmarkConfig(seed=seed, total_days=days)
    conn = init_database(":memory:")
    sim = Simulator(conn, config, rng, customer_simulator=None)
    sim.initialize()
    for _ in range(days):
        sim.step_day()
    return conn


def run_with_resumes(seed: int, days: int, resume_points: list[int]) -> sqlite3.Connection:
    """Run simulation with stop/resume at given days.

    At each resume_point day, we:
    1. Save the DB to .nmdb
    2. Load it back (simulating a process restart)
    3. Create a fresh Simulator with fresh RNG
    4. Restore RNG states from DB
    5. Continue running
    """
    TMPDIR.mkdir(parents=True, exist_ok=True)
    nmdb_path = TMPDIR / f"resume_{'_'.join(map(str, resume_points))}.nmdb"

    # Initial run
    rng = Generator(PCG64(seed))
    config = BenchmarkConfig(seed=seed, total_days=days)
    conn = init_database(":memory:")
    sim = Simulator(conn, config, rng, customer_simulator=None)
    sim.initialize()

    sorted_points = sorted(set(resume_points))
    last_day = 0

    for resume_day in sorted_points:
        # Run up to resume_day
        for _ in range(resume_day - last_day):
            sim.step_day()
        last_day = resume_day

        # Save DB to disk (simulates process shutdown)
        save_session_db(conn, nmdb_path)
        current_day = sim.current_day
        conn.close()

        # Load DB (simulates process restart)
        conn = load_session_db(nmdb_path)

        # Create fresh simulator (same as server_entry.py resume path)
        rng = Generator(PCG64(seed))
        config = BenchmarkConfig(seed=seed, total_days=days)
        sim = Simulator(conn, config, rng, customer_simulator=None)
        sim.initialize(resume=True)
        sim.current_day = current_day

        # Restore RNG states
        restored = sim.restore_rng_states()
        assert restored, f"Failed to restore RNG states at day {resume_day}"

    # Run remaining days
    for _ in range(days - last_day):
        sim.step_day()

    return conn


def extract_rng_dependent_data(conn: sqlite3.Connection) -> dict:
    """Extract all RNG-dependent data from the simulation DB for comparison."""
    data = {}

    # 1. Competitor events (timing + boost amounts)
    data['competitor_events'] = [
        dict(r) for r in conn.execute(
            "SELECT start_day, boost_amount, post_end_day, description FROM competitor_events ORDER BY start_day"
        ).fetchall()
    ]

    # 2. Customer attributes (c_max, steepness, persona) — RNG-dependent via _group_rngs
    data['customers'] = [
        dict(r) for r in conn.execute(
            "SELECT customer_id, group_id, c_max, steepness_left, steepness_right, q_min, q_max, usage_demand FROM customers ORDER BY customer_id"
        ).fetchall()
    ]

    # 3. Social media posts (likes, shares, virality are RNG-dependent)
    data['social_posts'] = [
        dict(r) for r in conn.execute(
            "SELECT post_id, day, customer_id, sentiment, likes, shares, virality_score, reputation_impact FROM social_media_posts ORDER BY post_id"
        ).fetchall()
    ]

    # 4. Quality snapshots (quality_rng noise)
    try:
        data['quality_snapshots'] = [
            dict(r) for r in conn.execute(
                "SELECT * FROM _hidden_quality_snapshots ORDER BY day"
            ).fetchall()
        ]
    except Exception:
        data['quality_snapshots'] = []

    # 5. Macro PMI values (macro_rng dependent)
    try:
        data['macro_publications'] = [
            dict(r) for r in conn.execute(
                "SELECT * FROM macro_publications ORDER BY publication_day"
            ).fetchall()
        ]
    except Exception:
        data['macro_publications'] = []

    # 6. Ledger entries (cash flow affected by RNG-dependent subscriber generation)
    data['ledger_summary'] = dict(conn.execute(
        "SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total FROM ledger"
    ).fetchone())

    # 7. Subscriptions (affected by RNG-dependent customer generation)
    data['subscriptions'] = [
        dict(r) for r in conn.execute(
            "SELECT customer_id, plan, start_day, end_day, status FROM subscriptions ORDER BY customer_id, start_day"
        ).fetchall()
    ]

    # 8. Notifications (competitor events generate notifications)
    data['notifications'] = [
        dict(r) for r in conn.execute(
            "SELECT day, type, message FROM notifications ORDER BY day, type"
        ).fetchall()
    ]

    return data


def compare_data(ref: dict, test: dict, label: str) -> list[str]:
    """Compare two data dicts, return list of differences."""
    errors = []
    for key in ref:
        if key not in test:
            errors.append(f"[{label}] Missing key: {key}")
            continue

        ref_val = ref[key]
        test_val = test[key]

        if isinstance(ref_val, list):
            if len(ref_val) != len(test_val):
                errors.append(f"[{label}] {key}: length mismatch — ref={len(ref_val)}, test={len(test_val)}")
                continue
            for i, (r, t) in enumerate(zip(ref_val, test_val)):
                if isinstance(r, dict) and isinstance(t, dict):
                    for k in r:
                        rv, tv = r.get(k), t.get(k)
                        if isinstance(rv, float) and isinstance(tv, float):
                            if abs(rv - tv) > 1e-10:
                                errors.append(f"[{label}] {key}[{i}].{k}: {rv} != {tv}")
                        elif rv != tv:
                            errors.append(f"[{label}] {key}[{i}].{k}: {rv!r} != {tv!r}")
                elif r != t:
                    errors.append(f"[{label}] {key}[{i}]: {r!r} != {t!r}")
        elif isinstance(ref_val, dict):
            for k in ref_val:
                rv, tv = ref_val.get(k), test_val.get(k)
                if isinstance(rv, float) and isinstance(tv, float):
                    if abs(rv - tv) > 1e-10:
                        errors.append(f"[{label}] {key}.{k}: {rv} != {tv}")
                elif rv != tv:
                    errors.append(f"[{label}] {key}.{k}: {rv!r} != {tv!r}")
        elif ref_val != test_val:
            errors.append(f"[{label}] {key}: {ref_val!r} != {test_val!r}")

    return errors


def main():
    print(f"=== RNG Determinism Test (seed={SEED}, days={TOTAL_DAYS}) ===\n")
    TMPDIR.mkdir(parents=True, exist_ok=True)

    # 1. Reference trajectory (no stops)
    print("Running reference trajectory (continuous, no stops)...")
    ref_conn = run_continuous(SEED, TOTAL_DAYS)
    ref_data = extract_rng_dependent_data(ref_conn)
    ref_conn.close()

    print(f"  Competitor events: {len(ref_data['competitor_events'])} "
          f"(days: {[e['start_day'] for e in ref_data['competitor_events']]})")
    print(f"  Customers: {len(ref_data['customers'])}")
    print(f"  Social posts: {len(ref_data['social_posts'])}")
    print(f"  Notifications: {len(ref_data['notifications'])}")
    print()

    # 2. Test trajectories with different resume patterns
    test_cases = [
        ("resume_at_5", [5]),
        ("resume_at_10", [10]),
        ("resume_at_15", [15]),
        ("resume_at_1", [1]),
        ("resume_at_5_10_15", [5, 10, 15]),
        ("resume_at_1_3_7_12_20_25", [1, 3, 7, 12, 20, 25]),
        ("resume_every_day", list(range(1, TOTAL_DAYS))),
    ]

    all_passed = True
    for label, resume_points in test_cases:
        print(f"Testing: {label} (resume at days {resume_points[:5]}{'...' if len(resume_points) > 5 else ''})...")
        test_conn = run_with_resumes(SEED, TOTAL_DAYS, resume_points)
        test_data = extract_rng_dependent_data(test_conn)
        test_conn.close()

        errors = compare_data(ref_data, test_data, label)
        if errors:
            all_passed = False
            print(f"  ❌ FAILED — {len(errors)} differences:")
            for err in errors[:10]:
                print(f"    {err}")
            if len(errors) > 10:
                print(f"    ... and {len(errors) - 10} more")
        else:
            print(f"  ✅ PASSED — all RNG-dependent data matches reference")

    print()
    if all_passed:
        print("=" * 60)
        print("ALL TESTS PASSED — resume produces identical RNG behavior")
        print("=" * 60)
        return 0
    else:
        print("=" * 60)
        print("SOME TESTS FAILED — resume does NOT match continuous run")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
