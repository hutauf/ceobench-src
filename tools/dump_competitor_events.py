"""Enumerate all competitor events for seed=42 under a given config.

Faithfully reproduces the _competitor_rng draw sequence from simulation.py:
- _process_competitor_events: 1 random() draw per day past grace/cutoff & min_interval
- On trigger: 1 lognormal draw for raw_boost
- _generate_competitor_event_posts: 2 integers per post per day, for each active event
  (posts happen for days where post_end_day >= current_day)
"""

import argparse
from numpy.random import Generator, PCG64


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--total-days", type=int, default=500)
    p.add_argument("--grace", type=int, default=50)
    p.add_argument("--late-cutoff", type=int, default=30)
    p.add_argument("--mean-interval", type=int, default=6)
    p.add_argument("--min-interval", type=int, default=2)
    p.add_argument("--mu", type=float, default=-4.4505)  # current*1.3
    p.add_argument("--sigma", type=float, default=1.2)
    p.add_argument("--boost-min", type=float, default=0.00219375)
    p.add_argument("--boost-max", type=float, default=0.191953125)
    p.add_argument("--scale-min", type=float, default=1.0)
    p.add_argument("--scale-max", type=float, default=2.0)
    p.add_argument("--post-days", type=int, default=3)
    p.add_argument("--posts-per-day", type=int, default=2)
    args = p.parse_args()

    # Reproduce the RNG derivation from simulation.py:140-169
    main_rng = Generator(PCG64(args.seed))
    _macro_seed = int(main_rng.integers(0, 2**63))  # eaten by _macro_rng
    competitor_seed = int(main_rng.integers(0, 2**63))
    comp_rng = Generator(PCG64(competitor_seed ^ 0x434F4D50))

    ramp_end_day = max(args.total_days - args.late_cutoff, 2)
    half_sim = max(args.total_days // 2, 1)

    events = []
    active_events = []  # list of (start_day, post_end_day)
    last_event_day = -args.mean_interval

    for day in range(1, args.total_days + 1):
        # === _process_competitor_events draws ===
        in_grace = (args.grace > 0 and day < args.grace)
        in_late_cutoff = (args.late_cutoff > 0 and day > args.total_days - args.late_cutoff)

        if not in_grace and not in_late_cutoff:
            days_since_last = day - last_event_day

            # Apply first-half 1.5x interval multiplier
            mean_i = args.mean_interval
            min_i = args.min_interval
            if day < half_sim:
                mean_i *= 1.5
                min_i *= 1.5

            if days_since_last >= min_i:
                r = comp_rng.random()  # 1 draw
                daily_prob = 1.0 / mean_i
                if r < daily_prob:
                    # Trigger event
                    raw_boost = float(comp_rng.lognormal(args.mu, args.sigma))  # 1 draw
                    base_boost = max(args.boost_min, min(raw_boost, args.boost_max))
                    day_frac = max(0.0, min((day - 1) / max(ramp_end_day - 1, 1), 1.0))
                    magnitude_scale = args.scale_min + (args.scale_max - args.scale_min) * day_frac
                    boost = base_boost * magnitude_scale
                    post_end_day = day + args.post_days
                    events.append({
                        "day": day,
                        "raw_boost": raw_boost,
                        "base_boost": base_boost,
                        "magnitude_scale": magnitude_scale,
                        "boost": boost,
                        "post_end_day": post_end_day,
                    })
                    active_events.append((day, post_end_day))
                    last_event_day = day

        # === _generate_competitor_event_posts draws ===
        # Filter to events still active today (post_end_day >= current_day)
        still_active = [(s, e) for (s, e) in active_events if e >= day]
        if still_active:
            # Only first event is used in code, but each post consumes 2 integer draws
            for _ in range(args.posts_per_day):
                _ = comp_rng.integers(0, 5)   # competitor_name
                _ = comp_rng.integers(0, 7)   # perspective
        active_events = still_active

    print(f"Total events: {len(events)}")
    print(f"{'Day':>4} {'Raw':>10} {'Base':>10} {'Scale':>6} {'Final':>10} {'Severity':>14}")
    for e in events:
        b = e["boost"]
        if b < 0.03:
            sev = "minor"
        elif b < 0.10:
            sev = "moderate"
        elif b < 0.20:
            sev = "major"
        else:
            sev = "transformative"
        print(f"{e['day']:>4} {e['raw_boost']:>10.5f} {e['base_boost']:>10.5f} {e['magnitude_scale']:>6.3f} {b:>10.5f} {sev:>14}")


if __name__ == "__main__":
    main()
