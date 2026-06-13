"""Regression tests for core CEOBench mechanisms.

These tests pin the current single-company benchmark behavior so future arena
work can extend it without silently changing initial conditions or core rules.
"""

import math

import pytest
from numpy.random import default_rng

from saas_bench.config import (
    BenchmarkConfig,
    CUSTOMER_GROUPS,
    INITIAL_CUSTOMER_GROUPS,
    RESEARCH_TIERS_BY_ID,
)
from saas_bench.database import (
    get_cash,
    get_global_state,
    get_group_info_level,
    get_undiscovered_groups,
    init_database,
)
from saas_bench.simulation import Simulator
from saas_bench.tools import AgentTools


def _initialized_sim(tmp_path, *, config=None, seed=123):
    config = config or BenchmarkConfig(seed=seed)
    conn = init_database(tmp_path / "ceobench.db")
    sim = Simulator(conn, config, default_rng(seed))
    sim.initialize()
    return conn, sim, config


def _agent_tools(conn, tmp_path, config, *, day=0, seed=123):
    return AgentTools(
        conn,
        current_day=day,
        workspace_path=tmp_path / "workspace",
        rng=default_rng(seed),
        config=config,
        seed=seed,
    )


def test_initial_state_matches_benchmark_defaults(tmp_path):
    conn, _sim, config = _initialized_sim(tmp_path)

    assert get_cash(conn) == pytest.approx(config.initial_cash)
    assert get_global_state(conn, "q_shared_bonus") == pytest.approx(0.0)

    ledger = conn.execute("SELECT day, category, amount FROM ledger").fetchall()
    assert [(row["day"], row["category"], row["amount"]) for row in ledger] == [
        (0, "initial_funding", config.initial_cash)
    ]

    initial_config = conn.execute(
        "SELECT * FROM config_history WHERE day = 0"
    ).fetchone()
    assert initial_config["price_A"] == pytest.approx(config.default_price_A)
    assert initial_config["price_B"] == pytest.approx(config.default_price_B)
    assert initial_config["price_C"] == pytest.approx(config.default_price_C)
    assert initial_config["tier_A"] == config.default_tier_A
    assert initial_config["tier_B"] == config.default_tier_B
    assert initial_config["tier_C"] == config.default_tier_C
    assert initial_config["spend_advertising"] == pytest.approx(
        config.default_spend_advertising
    )
    assert initial_config["spend_operations"] == pytest.approx(
        config.default_spend_operations
    )
    assert initial_config["spend_development"] == pytest.approx(
        config.default_spend_development
    )
    assert initial_config["capacity_tier"] == config.default_capacity_tier
    assert initial_config["quota_A"] == config.default_quota_A
    assert initial_config["quota_B"] == config.default_quota_B
    assert initial_config["quota_C"] == config.default_quota_C

    for group_id, group_cfg in INITIAL_CUSTOMER_GROUPS.items():
        assert get_group_info_level(conn, group_id) == 1

        snapshot = conn.execute(
            """
            SELECT snapshot_day, snapshot_c_max, snapshot_q_min, snapshot_market_cap
            FROM group_insight_snapshots
            WHERE group_id = ?
            """,
            (group_id,),
        ).fetchone()
        assert snapshot["snapshot_day"] == 0
        assert snapshot["snapshot_c_max"] == pytest.approx(group_cfg.c_max_mean)
        assert snapshot["snapshot_q_min"] == pytest.approx(group_cfg.q_min_mean)
        assert snapshot["snapshot_market_cap"] == pytest.approx(
            group_cfg.base_market_cap
        )

    assert len(get_undiscovered_groups(conn)) == (
        config.discoverable_individual_count + config.discoverable_enterprise_count
    )


def test_quality_price_curve_and_acceptance_rule(tmp_path):
    _conn, sim, _config = _initialized_sim(tmp_path)

    curve_kwargs = {
        "steepness_left": 0.8,
        "steepness_right": 1.6,
        "c_max": 100.0,
        "q_max": 0.8,
        "q_min": 0.2,
    }
    required_at_free = sim._compute_required_quality(cost=0.0, **curve_kwargs)
    required_at_mid = sim._compute_required_quality(cost=50.0, **curve_kwargs)
    required_at_budget = sim._compute_required_quality(cost=100.0, **curve_kwargs)
    required_above_budget = sim._compute_required_quality(cost=101.0, **curve_kwargs)

    assert 0.2 <= required_at_free < required_at_mid < required_at_budget <= 0.8
    assert required_above_budget == pytest.approx(0.8)

    affordable_required_quality = sim._compute_required_quality(
        cost=75.0, **curve_kwargs
    )
    assert sim._plan_acceptable(
        quality=affordable_required_quality, cost=75.0, **curve_kwargs
    )
    assert not sim._plan_acceptable(
        quality=math.nextafter(affordable_required_quality, 0.0),
        cost=75.0,
        **curve_kwargs,
    )
    assert not sim._plan_acceptable(quality=1.0, cost=101.0, **curve_kwargs)

    assert sim._compute_satisfaction(
        quality=affordable_required_quality + 0.05,
        cost=75.0,
        **curve_kwargs,
    ) == pytest.approx(0.05)


def test_new_customer_selects_best_plan_or_no_plan(tmp_path):
    config = BenchmarkConfig(seed=123, base_product_quality=0.5)
    _conn, sim, _config = _initialized_sim(tmp_path, config=config, seed=123)

    plan_config = {
        "price_A": 10.0,
        "price_B": 25.0,
        "price_C": 40.0,
        "tier_A": 1,
        "tier_B": 3,
        "tier_C": 5,
    }

    assert (
        sim._select_best_plan(
            steepness_left=0.8,
            steepness_right=1.6,
            c_max=100.0,
            config=plan_config,
            overload=0.0,
            outage=False,
            q_max=0.8,
            q_min=0.2,
        )
        == "C"
    )

    unaffordable_config = {
        "price_A": 101.0,
        "price_B": 125.0,
        "price_C": 140.0,
        "tier_A": 1,
        "tier_B": 3,
        "tier_C": 5,
    }

    assert (
        sim._select_best_plan(
            steepness_left=0.8,
            steepness_right=1.6,
            c_max=100.0,
            config=unaffordable_config,
            overload=0.0,
            outage=False,
            q_max=0.8,
            q_min=0.2,
        )
        is None
    )


def test_market_research_discovers_one_group_and_charges_cash(tmp_path):
    config = BenchmarkConfig(seed=123, market_research_discover_prob=1.0)
    conn, _sim, config = _initialized_sim(tmp_path, config=config, seed=123)
    tools = _agent_tools(conn, tmp_path, config, seed=123)

    undiscovered_before = set(get_undiscovered_groups(conn))
    cash_before = get_cash(conn)

    result = tools.research_market()

    assert result.success
    assert get_cash(conn) == pytest.approx(cash_before - config.discovery_cost_level_1)

    discovered_group_id = result.data["discovered_group_id"]
    assert discovered_group_id in undiscovered_before
    assert get_group_info_level(conn, discovered_group_id) == 1
    assert len(get_undiscovered_groups(conn)) == len(undiscovered_before) - 1

    discovery = conn.execute(
        """
        SELECT day, cost, success, discovered_group_id, remaining_undiscovered
        FROM segment_discovery
        """
    ).fetchone()
    assert discovery["day"] == 0
    assert discovery["cost"] == pytest.approx(config.discovery_cost_level_1)
    assert discovery["success"] == 1
    assert discovery["discovered_group_id"] == discovered_group_id
    assert discovery["remaining_undiscovered"] == len(undiscovered_before) - 1

    snapshot = conn.execute(
        "SELECT snapshot_day FROM group_insight_snapshots WHERE group_id = ?",
        (discovered_group_id,),
    ).fetchone()
    assert snapshot["snapshot_day"] == 0


def test_group_research_is_delayed_and_updates_visibility_on_completion(tmp_path):
    conn, sim, config = _initialized_sim(tmp_path)
    tools = _agent_tools(conn, tmp_path, config)

    cash_before = get_cash(conn)
    result = tools.research_group("S1", target_level=2)

    assert result.success
    assert get_cash(conn) == pytest.approx(cash_before - config.research_cost_level_2)
    assert get_group_info_level(conn, "S1") == 1

    pending = conn.execute(
        """
        SELECT group_id, from_level, to_level, cost, started_day,
               expected_completion_day, status
        FROM pending_group_research
        WHERE group_id = 'S1'
        """
    ).fetchone()
    assert pending["from_level"] == 1
    assert pending["to_level"] == 2
    assert pending["cost"] == pytest.approx(config.research_cost_level_2)
    assert pending["started_day"] == 0
    assert pending["expected_completion_day"] == config.group_research_delay_level_2
    assert pending["status"] == "in_progress"

    sim.current_day = config.group_research_delay_level_2 - 1
    sim._process_group_research({})
    assert get_group_info_level(conn, "S1") == 1

    sim.current_day = config.group_research_delay_level_2
    sim._process_group_research({})

    assert get_group_info_level(conn, "S1") == 2
    completed = conn.execute(
        "SELECT status FROM pending_group_research WHERE group_id = 'S1'"
    ).fetchone()
    assert completed["status"] == "completed"

    group_cfg = CUSTOMER_GROUPS["S1"]
    snapshot = conn.execute(
        """
        SELECT snapshot_day, snapshot_c_max, snapshot_q_min, snapshot_market_cap
        FROM group_insight_snapshots
        WHERE group_id = 'S1'
        """
    ).fetchone()
    assert snapshot["snapshot_day"] == config.group_research_delay_level_2
    assert snapshot["snapshot_c_max"] == pytest.approx(group_cfg.c_max_mean)
    assert snapshot["snapshot_q_min"] == pytest.approx(group_cfg.q_min_mean)
    assert snapshot["snapshot_market_cap"] == pytest.approx(
        group_cfg.base_market_cap
        * (
            1
            + group_cfg.annual_cap_growth_rate
            * config.group_research_delay_level_2
            / 365.0
        )
    )


def test_group_insights_are_deterministic_and_hide_true_internal_parameters(tmp_path):
    conn, _sim, config = _initialized_sim(tmp_path)
    tools = _agent_tools(conn, tmp_path, config)

    first = tools.get_group_insights("S1")
    second = tools.get_group_insights("S1")

    assert first.success
    assert first.data == second.data
    assert first.data["group_id"] == "S1"
    assert first.data["info_level"] == 1
    assert first.data["noise"] == "±65%"

    estimates = first.data["estimates"]
    assert {
        "willingness_to_pay",
        "usage_volume",
        "quality_floor_q_min",
        "contract_lockin_aversion",
        "market_cap",
        "annual_market_cap_growth_rate",
    }.issubset(estimates)
    assert "c_max_mean" not in estimates
    assert "q_min_mean" not in estimates
    assert "network_influence" in first.data
    assert "reputation_influence" in first.data


def test_research_project_completion_applies_sampled_quality_boost(tmp_path):
    conn, sim, config = _initialized_sim(tmp_path)
    tools = _agent_tools(conn, tmp_path, config)
    research_tier = RESEARCH_TIERS_BY_ID[1]

    cash_before = get_cash(conn)
    result = tools.start_research_project(1)

    assert result.success
    assert get_cash(conn) == pytest.approx(cash_before - research_tier.cost)

    project = conn.execute(
        """
        SELECT project_id, tier, status, started_day, expected_completion_day,
               expected_quality_boost, actual_completion_day, quality_boost_applied
        FROM research_projects
        WHERE tier = 1
        """
    ).fetchone()
    assert project["project_id"] == "t1_1"
    assert project["status"] == "in_progress"
    assert project["started_day"] == 0
    assert project["expected_completion_day"] >= 30
    assert project["expected_quality_boost"] >= 0.001
    assert project["actual_completion_day"] is None
    assert project["quality_boost_applied"] == pytest.approx(0.0)

    sim.current_day = project["expected_completion_day"] - 1
    sim._process_research_projects({})
    assert get_global_state(conn, "q_shared_bonus") == pytest.approx(0.0)

    sim.current_day = project["expected_completion_day"]
    sim._process_research_projects({})

    completed = conn.execute(
        """
        SELECT status, actual_completion_day, quality_boost_applied
        FROM research_projects
        WHERE project_id = 't1_1'
        """
    ).fetchone()
    expected_boost = project["expected_quality_boost"]
    assert completed["status"] == "completed"
    assert completed["actual_completion_day"] == project["expected_completion_day"]
    assert completed["quality_boost_applied"] == pytest.approx(expected_boost)
    assert get_global_state(conn, "q_shared_bonus") == pytest.approx(expected_boost)
    assert get_global_state(
        conn, "unreleased_base_quality_improvement"
    ) == pytest.approx(expected_boost)
