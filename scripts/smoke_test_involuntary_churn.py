"""v3.4ab smoke test: verify involuntary churn helper + integration plumbing.

Without an agent driving prices/spend, the headless sim creates no subscribers, so we
can't observe churn end-to-end here. Instead this test verifies:
  1. ChurnReason.INVOLUNTARY exists and serializes to 'involuntary'
  2. All 26 groups (initial + discoverable) have involuntary_churn_mean/std populated
  3. _get_involuntary_churn_mu returns a draw inside [mean - 4σ, mean + 4σ] per group
  4. Same (group, month) → same μ_t (cache is stable)
  5. Different month → different μ_t (with high probability)
  6. enable_involuntary_churn=False kills the helper (returns 0.0)
  7. Cache is independent of customer visit order (re-derivation matches)
  8. Different seeds → different μ_t streams (with high probability)
"""
import sys
from pathlib import Path
from numpy.random import Generator, PCG64

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from saas_bench.database import init_database
from saas_bench.config import BenchmarkConfig, CUSTOMER_GROUPS, ChurnReason, generate_discoverable_groups
from saas_bench.simulation import Simulator


def _make_sim(seed: int, enable: bool = True):
    rng = Generator(PCG64(seed))
    config = BenchmarkConfig(seed=seed, total_days=120, enable_involuntary_churn=enable)
    conn = init_database(":memory:")
    sim = Simulator(conn, config, rng, customer_simulator=None)
    sim.initialize()
    return sim


def test_enum_value():
    assert ChurnReason.INVOLUNTARY.value == "involuntary"
    print("  [PASS] ChurnReason.INVOLUNTARY.value == 'involuntary'")


def test_all_26_groups_populated():
    rng = Generator(PCG64(42))
    disc = generate_discoverable_groups(rng)
    all_groups = {**CUSTOMER_GROUPS, **disc}
    assert len(all_groups) == 26, f"expected 26 groups, got {len(all_groups)}"
    missing = [k for k, g in all_groups.items()
               if not hasattr(g, 'involuntary_churn_mean') or g.involuntary_churn_mean is None]
    assert not missing, f"groups missing involuntary_churn_mean: {missing}"
    # Sanity: at least 5 distinct mean values across the 26 groups
    distinct_means = {round(g.involuntary_churn_mean, 4) for g in all_groups.values()}
    assert len(distinct_means) >= 5, f"only {len(distinct_means)} distinct means — likely all defaults"
    print(f"  [PASS] all 26 groups populated; {len(distinct_means)} distinct mean values")


def test_helper_in_range():
    """For each group, μ_t must be within ±4σ of mean (probability of failure ~6e-5 per group)."""
    sim = _make_sim(42)
    for gid, g in CUSTOMER_GROUPS.items():
        sim.current_day = 0
        sim._involuntary_churn_mu_cache.clear()
        mu = sim._get_involuntary_churn_mu(gid)
        lo = max(0.0, g.involuntary_churn_mean - 4 * g.involuntary_churn_std)
        hi = min(1.0, g.involuntary_churn_mean + 4 * g.involuntary_churn_std)
        assert lo <= mu <= hi, f"{gid}: μ_t={mu:.4f} outside [{lo:.4f}, {hi:.4f}]"
    print("  [PASS] all initial groups draw μ_t within ±4σ of mean")


def test_cache_stability_within_month():
    sim = _make_sim(42)
    sim.current_day = 5
    a = sim._get_involuntary_churn_mu("S1")
    sim.current_day = 12  # same month (5 // 30 == 12 // 30 == 0)
    b = sim._get_involuntary_churn_mu("S1")
    assert a == b, f"same-month draw differed: {a} vs {b}"
    print(f"  [PASS] same-month draws identical: S1 μ_t = {a:.5f}")


def test_cache_changes_across_month():
    sim = _make_sim(42)
    sim.current_day = 0
    a = sim._get_involuntary_churn_mu("S1")
    sim.current_day = 35  # next month (35 // 30 == 1)
    b = sim._get_involuntary_churn_mu("S1")
    # Could theoretically be equal but extremely rare
    assert a != b, f"month-0 and month-1 draws were identical: {a}"
    print(f"  [PASS] cross-month draws differ: month0={a:.5f}, month1={b:.5f}")


def test_kill_switch():
    sim = _make_sim(42, enable=False)
    sim.current_day = 0
    for gid in ("S1", "E1", "D_S05", "D_E03"):
        mu = sim._get_involuntary_churn_mu(gid)
        assert mu == 0.0, f"kill-switch failed: {gid} → {mu}"
    print("  [PASS] enable_involuntary_churn=False → all groups return 0.0")


def test_cache_independent_of_visit_order():
    """μ_t for (group, month) must be independent of which customer visits first."""
    sim_a = _make_sim(42)
    sim_b = _make_sim(42)
    # Pretend sim_a visits S1 first, then E1; sim_b visits E1 first, then S1.
    sim_a.current_day = 7
    a_s1 = sim_a._get_involuntary_churn_mu("S1")
    a_e1 = sim_a._get_involuntary_churn_mu("E1")
    sim_b.current_day = 7
    b_e1 = sim_b._get_involuntary_churn_mu("E1")
    b_s1 = sim_b._get_involuntary_churn_mu("S1")
    assert a_s1 == b_s1, f"S1 differs by visit order: {a_s1} vs {b_s1}"
    assert a_e1 == b_e1, f"E1 differs by visit order: {a_e1} vs {b_e1}"
    print(f"  [PASS] cache stable across visit order: S1={a_s1:.5f}, E1={a_e1:.5f}")


def test_different_seeds_differ():
    sim_a = _make_sim(42)
    sim_b = _make_sim(123)
    sim_a.current_day = 0
    sim_b.current_day = 0
    diffs = 0
    for gid in CUSTOMER_GROUPS:
        a = sim_a._get_involuntary_churn_mu(gid)
        b = sim_b._get_involuntary_churn_mu(gid)
        if a != b:
            diffs += 1
    assert diffs >= 4, f"only {diffs}/{len(CUSTOMER_GROUPS)} groups differ across seeds"
    print(f"  [PASS] {diffs}/{len(CUSTOMER_GROUPS)} initial groups differ between seed=42 and seed=123")


def test_aggregate_distribution():
    """Across 100 months, group-level μ_t empirical mean should be close to configured mean."""
    sim = _make_sim(42)
    samples = []
    for month in range(100):
        sim.current_day = month * 30
        sim._involuntary_churn_mu_cache.clear()
        samples.append(sim._get_involuntary_churn_mu("S1"))
    emp_mean = sum(samples) / len(samples)
    cfg_mean = CUSTOMER_GROUPS["S1"].involuntary_churn_mean
    # Standard error of mean ≈ σ/√n = 0.015/10 = 0.0015. Allow 5× SE.
    tol = 5 * CUSTOMER_GROUPS["S1"].involuntary_churn_std / (len(samples) ** 0.5)
    assert abs(emp_mean - cfg_mean) < tol, f"empirical mean {emp_mean:.5f} ≠ config {cfg_mean} (tol {tol:.5f})"
    print(f"  [PASS] S1 empirical mean over 100 months: {emp_mean:.5f} (target {cfg_mean})")


if __name__ == "__main__":
    print("Running v3.4ab involuntary-churn smoke tests...\n")
    test_enum_value()
    test_all_26_groups_populated()
    test_helper_in_range()
    test_cache_stability_within_month()
    test_cache_changes_across_month()
    test_kill_switch()
    test_cache_independent_of_visit_order()
    test_different_seeds_differ()
    test_aggregate_distribution()
    print("\n✅ All v3.4ab smoke tests passed.")
