"""
Headless competitor event simulation — pure RNG, no LLM, no DB.

Replicates the exact competitor event logic from simulation.py:
  - _competitor_rng seeded deterministically from seed 42
  - Same lognormal boost sampling, magnitude scaling, grace period
  - Two configs: baseline (v3.2x) and doubled frequency (halved intervals)
"""
import numpy as np
from numpy.random import Generator, PCG64

SEED = 42
TOTAL_DAYS = 500
GRACE_PERIOD = 100  # drift_grace_period_days (v3.2v+)

# v3.2x baseline config
BASELINE = {
    "mean_interval": 20,
    "min_interval": 10,
    "boost_mu": -3.85,
    "boost_sigma": 1.2,
    "boost_min": 0.004,
    "boost_max": 0.35,
    "scale_min": 1.0,
    "scale_max": 4.0,
}


def make_competitor_rng(seed):
    """Replicate how simulation.py creates _competitor_rng from main rng."""
    main_rng = Generator(PCG64(seed))
    # simulation.py draws in __init__: macro_seed, competitor_seed
    _ = int(main_rng.integers(0, 2**63))  # macro_seed draw
    competitor_seed = int(main_rng.integers(0, 2**63))
    return Generator(PCG64(competitor_seed ^ 0x434F4D50))


def simulate_events(cfg, total_days=TOTAL_DAYS):
    """Run competitor event simulation, return list of events."""
    rng = make_competitor_rng(SEED)
    events = []
    last_event_day = -cfg["mean_interval"]  # same as simulation.py default
    cumulative_boost = 0.0

    for day in range(total_days):
        # Grace period
        if day < GRACE_PERIOD:
            continue

        days_since_last = day - last_event_day

        # First-half frequency reduction (1.5x intervals)
        mean_interval = cfg["mean_interval"]
        min_interval = cfg["min_interval"]
        half_sim = max(total_days // 2, 1)
        if day < half_sim:
            mean_interval *= 1.5
            min_interval *= 1.5

        # Min interval check
        if days_since_last < min_interval:
            continue

        # Daily probability (Poisson process)
        daily_prob = 1.0 / mean_interval
        if rng.random() >= daily_prob:
            continue

        # --- Event triggered ---
        raw_boost = float(rng.lognormal(cfg["boost_mu"], cfg["boost_sigma"]))
        base_boost = max(cfg["boost_min"], min(raw_boost, cfg["boost_max"]))

        day_frac = min(day / max(total_days, 1), 1.0)
        magnitude_scale = cfg["scale_min"] + (cfg["scale_max"] - cfg["scale_min"]) * day_frac
        boost = base_boost * magnitude_scale

        cumulative_boost += boost
        events.append({
            "day": day,
            "raw_boost": raw_boost,
            "base_boost": base_boost,
            "magnitude_scale": magnitude_scale,
            "boost": boost,
            "cumulative": cumulative_boost,
        })
        last_event_day = day

    return events


def print_events(events, label):
    print(f"\n{'='*80}")
    print(f"  {label}")
    print(f"{'='*80}")
    print(f"{'#':>3}  {'Day':>5}  {'Raw':>8}  {'Base':>8}  {'Scale':>6}  {'Boost':>8}  {'Cumul':>8}")
    print(f"{'-'*3}  {'-'*5}  {'-'*8}  {'-'*8}  {'-'*6}  {'-'*8}  {'-'*8}")
    for i, e in enumerate(events):
        print(f"{i+1:3d}  {e['day']:5d}  {e['raw_boost']:8.5f}  {e['base_boost']:8.5f}  "
              f"{e['magnitude_scale']:6.2f}  {e['boost']:8.5f}  {e['cumulative']:8.5f}")
    if events:
        boosts = [e['boost'] for e in events]
        print(f"\nTotal events: {len(events)}")
        print(f"Total cumulative boost: {events[-1]['cumulative']:.5f}")
        print(f"Mean boost per event: {np.mean(boosts):.5f}")
        print(f"Min/Max boost: {min(boosts):.5f} / {max(boosts):.5f}")
    else:
        print("\nNo events triggered.")


if __name__ == "__main__":
    # Baseline (v3.2x)
    baseline_events = simulate_events(BASELINE)
    print_events(baseline_events, "BASELINE (v3.2x) — seed 42, 500 days")

    # Doubled frequency: halve intervals
    doubled = {**BASELINE, "mean_interval": 10, "min_interval": 5}
    doubled_events = simulate_events(doubled)
    print_events(doubled_events, "2× FREQUENCY — seed 42, 500 days")

    # Summary comparison
    print(f"\n{'='*80}")
    print(f"  COMPARISON")
    print(f"{'='*80}")
    b_total = baseline_events[-1]['cumulative'] if baseline_events else 0
    d_total = doubled_events[-1]['cumulative'] if doubled_events else 0
    print(f"Baseline:  {len(baseline_events):3d} events, cumulative boost = {b_total:.5f}")
    print(f"2× Freq:   {len(doubled_events):3d} events, cumulative boost = {d_total:.5f}")
    if b_total > 0:
        print(f"Ratio:     {d_total/b_total:.2f}× more total boost")
