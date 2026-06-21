#!/usr/bin/env python3
"""Run the Appendix B rule-based CEOBench baseline without LLM calls."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from numpy.random import default_rng

from saas_bench.config import AD_CHANNELS, CAPACITY_TIERS, BenchmarkConfig
from saas_bench.database import get_active_subscriber_count, get_cash, init_database
from saas_bench.simulation import Simulator
from saas_bench.tools import AgentTools


PRICE_BOOKS = {
    "cheap": {
        "prices": {"A": 8, "B": 18, "C": 40},
        "tiers": {"A": 1, "B": 2, "C": 3},
        "quotas": {"A": 50_000, "B": 200_000, "C": 1_000_000},
    },
    "mid": {
        "prices": {"A": 12, "B": 25, "C": 55},
        "tiers": {"A": 1, "B": 2, "C": 4},
        "quotas": {"A": 60_000, "B": 250_000, "C": 1_200_000},
    },
}

SPEND_PACKAGES = {
    "light": {
        "S1": {"dev": 2_000, "ad": 250},
        "S3": {"dev": 1_500, "ad": 600},
    },
    "medium": {
        "S1": {"dev": 4_000, "ad": 500},
        "S3": {"dev": 3_000, "ad": 1_200},
    },
    "heavy": {
        "S1": {"dev": 6_000, "ad": 750},
        "S3": {"dev": 4_500, "ad": 1_800},
    },
}


def best_ad_channel(group_id: str) -> str:
    return max(
        AD_CHANNELS,
        key=lambda channel: AD_CHANNELS[channel].leads_per_1000_dollars.get(group_id, 0.0),
    )


def selected_groups(rule: str, day: int) -> list[str]:
    if rule == "s1_only":
        return ["S1"]
    if rule == "s1_then_s3":
        return ["S1", "S3"] if day >= 30 else ["S1"]
    raise ValueError(f"unknown target rule: {rule}")


def recent_average_usage(conn, current_day: int, lookback_days: int = 7) -> float:
    start_day = max(1, current_day - lookback_days + 1)
    row = conn.execute(
        """
        SELECT AVG(total_usage) FROM (
            SELECT day, SUM(usage_units) AS total_usage
            FROM daily_usage
            WHERE day BETWEEN ? AND ?
            GROUP BY day
        )
        """,
        (start_day, current_day),
    ).fetchone()
    return float(row[0] or 0.0)


def target_capacity_tier(avg_usage: float, utilization: float = 0.8) -> int:
    required_capacity = avg_usage / utilization if utilization > 0 else avg_usage
    for tier, info in sorted(CAPACITY_TIERS.items()):
        if info["capacity_units"] >= required_capacity:
            return tier
    return max(CAPACITY_TIERS)


def current_capacity_tier(conn) -> int:
    row = conn.execute(
        "SELECT capacity_tier FROM config_history ORDER BY day DESC LIMIT 1"
    ).fetchone()
    return int(row["capacity_tier"] if row else 0)


def move_one_tier_toward(current: int, target: int) -> int:
    if target > current:
        return current + 1
    if target < current:
        return current - 1
    return current


def completed_day(conn) -> int:
    """Return the last fully simulated day recorded in the database."""
    row = conn.execute("SELECT MAX(day) FROM service_day").fetchone()
    return int(row[0] or 0)


def apply_policy(
    conn,
    tools: AgentTools,
    *,
    day: int,
    price_book: str,
    target_rule: str,
    spend_package: str,
    cash_floor: float,
) -> dict:
    tools.set_current_day(day)

    book = PRICE_BOOKS[price_book]
    package = SPEND_PACKAGES[spend_package]
    groups = selected_groups(target_rule, day)
    cash = get_cash(conn)
    optional_spend_enabled = cash > cash_floor

    results = {}
    results["set_prices"] = tools.set_prices(book["prices"]).success
    results["set_model_tiers"] = tools.set_model_tiers(book["tiers"]).success
    results["set_usage_quotas"] = tools.set_usage_quotas(book["quotas"]).success

    active_subscribers = get_active_subscriber_count(conn)
    operations_spend = max(100.0, 0.05 * active_subscribers)
    global_dev = 200 if optional_spend_enabled else 0
    results["set_daily_spend"] = tools.set_daily_spend(
        {"operations": operations_spend, "development": global_dev}
    ).success

    if optional_spend_enabled:
        targeted_dev = {gid: package[gid]["dev"] for gid in groups}
        targeted_ads = {}
        if day >= 20:
            for gid in groups:
                channel = best_ad_channel(gid)
                targeted_ads.setdefault(channel, {})[gid] = package[gid]["ad"]
    else:
        targeted_dev = {}
        targeted_ads = {}

    results["set_targeted_dev_spend"] = tools.set_targeted_dev_spend(targeted_dev).success
    results["set_targeted_ad_spend"] = tools.set_targeted_ad_spend(targeted_ads).success

    avg_usage = recent_average_usage(conn, day) if day > 0 else 0.0
    target_tier = target_capacity_tier(avg_usage)
    capacity_tier = move_one_tier_toward(current_capacity_tier(conn), target_tier)
    results["set_capacity_tier"] = tools.set_capacity_tier(capacity_tier).success

    return {
        "day": day,
        "cash": cash,
        "active_subscribers": active_subscribers,
        "operations_spend": operations_spend,
        "groups": groups,
        "optional_spend_enabled": optional_spend_enabled,
        "targeted_dev": targeted_dev,
        "targeted_ads": targeted_ads,
        "avg_usage": avg_usage,
        "target_capacity_tier": target_tier,
        "capacity_tier": capacity_tier,
        "results": results,
    }


def run(args: argparse.Namespace) -> dict:
    workspace = args.workspace.resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    db_path = workspace / "rule_based_world.db"
    db_existed = db_path.exists()
    if db_existed and not (args.keep_existing or args.resume):
        for suffix in ("", "-wal", "-shm"):
            path = Path(f"{db_path}{suffix}")
            if path.exists():
                path.unlink()
        db_existed = False

    config = BenchmarkConfig(seed=args.seed, total_days=args.days)
    conn = init_database(db_path)
    rng = default_rng(args.seed)

    # No CustomerSimulator is passed here. That disables all live LLM calls.
    simulator = Simulator(conn, config, rng)
    # The Appendix B baseline does not use social media. Avoid the agent-post
    # judge path entirely so the run stays LLM-free and does no debug-log churn.
    simulator._process_agent_social_posts = lambda config: None
    resume_requested = args.resume or args.keep_existing
    resume_from_day = completed_day(conn) if db_existed and resume_requested else 0
    if resume_from_day > 0:
        simulator.initialize(resume=True)
        simulator.current_day = resume_from_day
        if not simulator.restore_rng_states():
            raise RuntimeError(
                f"Cannot resume {db_path}: no saved RNG state found. "
                "Run again without --resume/--keep-existing to start fresh."
            )
    else:
        simulator.initialize()

    tools = AgentTools(
        conn,
        simulator.current_day,
        workspace / "agent_workspace",
        rng=rng,
        config=config,
        seed=args.seed,
    )

    history_path = workspace / "rule_based_history.json"
    if resume_from_day > 0 and history_path.exists():
        history = json.loads(history_path.read_text())
    else:
        history = []
    last_result = None
    while simulator.current_day < args.days and not simulator.shutdown_mode:
        day = simulator.current_day
        policy = apply_policy(
            conn,
            tools,
            day=day,
            price_book=args.price_book,
            target_rule=args.target_rule,
            spend_package=args.spend_package,
            cash_floor=args.cash_floor,
        )

        remaining = args.days - simulator.current_day
        if remaining >= 7:
            last_result = simulator.step_week()
        else:
            last_result = None
            for _ in range(remaining):
                last_result = simulator.step_day()
                if simulator.shutdown_mode:
                    break

        history.append(
            {
                **policy,
                "end_day": simulator.current_day,
                "end_cash": get_cash(conn),
                "active_subscribers_end": get_active_subscriber_count(conn),
                "shutdown": simulator.shutdown_mode,
            }
        )

        if args.verbose:
            latest = history[-1]
            print(
                f"day {latest['end_day']:3d}: cash=${latest['end_cash']:,.2f}, "
                f"subs={latest['active_subscribers_end']:,}, "
                f"capacity={latest['capacity_tier']}, "
                f"ads={latest['targeted_ads']}"
            )

    api_tokens = conn.execute(
        "SELECT COALESCE(SUM(input_tokens), 0), COALESCE(SUM(output_tokens), 0), COALESCE(SUM(cost_usd), 0) FROM api_costs"
    ).fetchone()

    summary = {
        "seed": args.seed,
        "days_requested": args.days,
        "days_run": simulator.current_day,
        "resumed_from_day": resume_from_day,
        "price_book": args.price_book,
        "target_rule": args.target_rule,
        "spend_package": args.spend_package,
        "cash_floor": args.cash_floor,
        "final_cash": get_cash(conn),
        "active_subscribers": get_active_subscriber_count(conn),
        "shutdown": simulator.shutdown_mode,
        "api_input_tokens": int(api_tokens[0]),
        "api_output_tokens": int(api_tokens[1]),
        "api_cost_usd": float(api_tokens[2]),
        "db_path": str(db_path),
    }

    (workspace / "rule_based_summary.json").write_text(json.dumps(summary, indent=2))
    (workspace / "rule_based_history.json").write_text(json.dumps(history, indent=2))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--days", type=int, default=500)
    parser.add_argument("--workspace", type=Path, default=Path("rule_based_runs/default"))
    parser.add_argument("--price-book", choices=sorted(PRICE_BOOKS), default="mid")
    parser.add_argument("--target-rule", choices=["s1_only", "s1_then_s3"], default="s1_only")
    parser.add_argument("--spend-package", choices=sorted(SPEND_PACKAGES), default="heavy")
    parser.add_argument("--cash-floor", type=float, default=100_000)
    parser.add_argument("--keep-existing", action="store_true", help="Reuse an existing workspace DB if present.")
    parser.add_argument("--resume", action="store_true", help="Resume an existing run from its saved DB/RNG state.")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    summary = run(args)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
