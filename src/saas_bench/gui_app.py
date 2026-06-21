"""Browser GUI for playing CEOBench without simulator LLM calls.

Run locally:
    uv run uvicorn saas_bench.gui_app:app --host 0.0.0.0 --port 8787
"""

from __future__ import annotations

import json
import shutil
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from numpy.random import Generator, PCG64
from pydantic import BaseModel, Field

from .config import BenchmarkConfig, CAPACITY_TIERS, MODEL_TIERS
from .database import (
    get_active_subscriber_count,
    get_cash,
    get_config,
    get_discovered_groups,
    get_mrr,
    init_database,
    save_predictions,
)
from .environment import build_weekly_dashboard, get_thread_inbox_items
from .simulation import Simulator
from .tools import AgentTools, ToolResult


APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "gui_static"
DEFAULT_WORKSPACE = Path("gui_runs/current")


def build_ceo_briefing(total_days: int) -> Dict[str, Any]:
    weeks = (total_days + 6) // 7
    years = total_days / 365.0
    return {
        "title": "You are the CEO of NovaMind AI",
        "summary": (
            f"You run a B2B/B2C AI SaaS company for {total_days} simulated days "
            f"({weeks} weeks, about {years:.1f} years). Your objective is to maximize "
            "ending cash. Cash is your score."
        ),
        "responsibilities": [
            "Set subscription prices, model tiers, usage quotas, promotions, and capacity.",
            "Allocate daily operations, development, targeted development, and paid acquisition spend.",
            "Research customer segments and invest in R&D to keep quality ahead of rising expectations.",
            "Handle enterprise leads and renewal/churn-prevention negotiations before they time out.",
            "Advance time one week at a time and submit a short rationale plus cash forecasts.",
        ],
        "no_llm_note": (
            "This GUI runs the no-LLM variant: social media content, social replies, "
            "and social judging are disabled."
        ),
        "weekly_workflow": [
            "Read the dashboard and current alerts.",
            "Adjust business controls.",
            "Check market/R&D and enterprise opportunities.",
            "Enter a rationale and cash forecasts.",
            "Simulate the next week.",
        ],
    }


class ResetRequest(BaseModel):
    seed: int = 42
    days: int = 500
    initial_cash: float = 1_000_000.0


class AdvanceRequest(BaseModel):
    rationale: str = "GUI player advanced the simulation."
    predictions: Optional[Dict[str, Dict[str, float]]] = None


class ToolRequest(BaseModel):
    args: Dict[str, Any] = Field(default_factory=dict)


class GameService:
    def __init__(self, workspace: Path = DEFAULT_WORKSPACE):
        self.workspace = workspace.resolve()
        self.db_path = self.workspace / "world.db"
        self.meta_path = self.workspace / "meta.json"
        self.agent_workspace = self.workspace / "agent_workspace"
        self.lock = threading.RLock()
        self.conn = None
        self.config: BenchmarkConfig | None = None
        self.rng: Generator | None = None
        self.simulator: Simulator | None = None
        self.tools: AgentTools | None = None
        self.last_dashboard = ""
        self.last_week_result = None
        self.load_or_create()

    def load_or_create(self) -> None:
        with self.lock:
            if self.db_path.exists() and self.meta_path.exists():
                meta = json.loads(self.meta_path.read_text())
                self._open_existing(meta)
            else:
                self.reset(ResetRequest())

    def reset(self, req: ResetRequest) -> Dict[str, Any]:
        with self.lock:
            if self.conn is not None:
                self.conn.close()
                self.conn = None
            if self.workspace.exists():
                shutil.rmtree(self.workspace)
            self.workspace.mkdir(parents=True, exist_ok=True)
            self.agent_workspace.mkdir(parents=True, exist_ok=True)

            self.config = BenchmarkConfig(
                seed=req.seed,
                total_days=req.days,
                initial_cash=req.initial_cash,
            )
            self.rng = Generator(PCG64(req.seed))
            self.conn = init_database(self.db_path, check_same_thread=False)
            self.simulator = Simulator(self.conn, self.config, self.rng)
            self._disable_social_media()
            self.simulator.initialize()
            self.tools = AgentTools(
                self.conn,
                0,
                self.agent_workspace,
                rng=self.rng,
                config=self.config,
                seed=req.seed,
            )
            self.last_week_result = None
            self.last_dashboard = build_weekly_dashboard(self.conn, 0)
            self._save_meta(status="created")
            return self.state()

    def _open_existing(self, meta: Dict[str, Any]) -> None:
        self.config = BenchmarkConfig(
            seed=int(meta.get("seed", 42)),
            total_days=int(meta.get("total_days", 500)),
            initial_cash=float(meta.get("initial_cash", 1_000_000.0)),
        )
        self.rng = Generator(PCG64(self.config.seed))
        self.conn = init_database(self.db_path, check_same_thread=False)
        self.simulator = Simulator(self.conn, self.config, self.rng)
        self._disable_social_media()
        self.simulator.initialize(resume=True)
        self._restore_advanced_config()
        self.simulator.current_day = int(meta.get("current_day", 0))
        if self.simulator.current_day > 0:
            self.simulator.restore_rng_states()
        self.tools = AgentTools(
            self.conn,
            self.simulator.current_day,
            self.agent_workspace,
            rng=self.rng,
            config=self.config,
            seed=self.config.seed,
        )
        self.last_dashboard = build_weekly_dashboard(self.conn, self.simulator.current_day)

    def _disable_social_media(self) -> None:
        assert self.simulator is not None
        self.simulator._generate_sampled_social_posts = lambda *args, **kwargs: ([], {})
        self.simulator._collect_macro_social_post_work = lambda *args, **kwargs: []
        self.simulator._generate_competitor_event_posts = lambda *args, **kwargs: None
        self.simulator._submit_social_posts_async = lambda *args, **kwargs: []
        self.simulator._collect_social_posts_async = lambda *args, **kwargs: None
        self.simulator._process_agent_social_posts = lambda *args, **kwargs: None

    def _save_meta(self, status: str = "running") -> None:
        assert self.simulator is not None and self.config is not None
        meta = {
            "seed": self.config.seed,
            "total_days": self.config.total_days,
            "initial_cash": self.config.initial_cash,
            "current_day": self.simulator.current_day,
            "status": status,
            "updated_at": time.time(),
            "llm_disabled": True,
            "social_media_disabled": True,
        }
        self.meta_path.write_text(json.dumps(meta, indent=2))

    def _tool_result(self, result: ToolResult) -> Dict[str, Any]:
        return {
            "success": result.success,
            "message": result.message,
            "data": result.data,
        }

    def call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            if self.tools is None:
                raise HTTPException(500, "Game is not initialized")
            self.tools.set_current_day(self.simulator.current_day)
            dispatch = {
                "set_prices": lambda: self.tools.set_prices({k: v for k, v in args.items() if v is not None}),
                "set_model_tiers": lambda: self.tools.set_model_tiers({k: v for k, v in args.items() if v is not None}),
                "set_usage_quotas": lambda: self.tools.set_usage_quotas(args),
                "set_daily_spend": lambda: self.tools.set_daily_spend({k: v for k, v in args.items() if v is not None}),
                "set_targeted_ad_spend": lambda: self.tools.set_targeted_ad_spend(args.get("targeted_spend", args)),
                "set_targeted_ops_spend": lambda: self.tools.set_targeted_ops_spend(
                    targeted_spend=args.get("targeted_spend"),
                    by_group=args.get("by_group"),
                    by_plan=args.get("by_plan"),
                    by_group_plan=args.get("by_group_plan"),
                    by_customer=args.get("by_customer"),
                ),
                "set_targeted_dev_spend": lambda: self.tools.set_targeted_dev_spend(args.get("targeted_spend", args)),
                "set_capacity_tier": lambda: self.tools.set_capacity_tier(args.get("tier", args.get("capacity_tier", 0))),
                "set_ads_strength": lambda: self.tools.set_ads_strength(
                    global_strength=args.get("global_strength"),
                    by_group=args.get("by_group"),
                    by_customer=args.get("by_customer"),
                ),
                "set_lead_promotion": lambda: self.tools.set_lead_promotion(
                    global_promotion=args.get("global_promotion"),
                    by_group=args.get("by_group"),
                    by_channel=args.get("by_channel"),
                    by_channel_group=args.get("by_channel_group"),
                ),
                "set_promotion": lambda: self.tools.set_promotion(
                    global_promotion=args.get("global_promotion"),
                    by_group=args.get("by_group"),
                    by_customer=args.get("by_customer"),
                    by_group_plan=args.get("by_group_plan"),
                ),
                "research_market": lambda: self.tools.research_market(),
                "research_group": lambda: self.tools.research_group(args.get("group_id", ""), args.get("target_level")),
                "start_research_project": lambda: self.tools.start_research_project(args.get("tier", 0)),
                "send_enterprise_deal": lambda: self.tools.send_enterprise_deal(deals=args.get("deals", [])),
                "reject_enterprise_deal": lambda: self.tools.reject_enterprise_deal(deals=args.get("deals", [])),
            }
            if name not in dispatch:
                raise HTTPException(404, f"Unknown or disabled tool: {name}")
            result = dispatch[name]()
            self.conn.commit()
            self._restore_advanced_config()
            self._save_meta()
            return self._tool_result(result)

    def advance_week(self, req: AdvanceRequest) -> Dict[str, Any]:
        with self.lock:
            if self.simulator is None or self.tools is None:
                raise HTTPException(500, "Game is not initialized")
            if self.simulator.current_day >= self.config.total_days:
                raise HTTPException(400, "Simulation is already complete")

            old_day = self.simulator.current_day
            predictions = self._parse_predictions(req.predictions)
            save_predictions(self.conn, old_day, predictions, time.time())
            self.conn.commit()

            week_result = self.simulator.step_week()
            self.last_week_result = week_result
            self.tools.set_current_day(self.simulator.current_day)
            inbox = get_thread_inbox_items(self.conn, self.simulator.current_day, old_day + 1)
            self.last_dashboard = build_weekly_dashboard(
                self.conn,
                self.simulator.current_day,
                week_result,
                inbox_items=inbox,
            )
            self._save_meta(status="complete" if self.simulator.current_day >= self.config.total_days else "running")
            return {"success": True, "dashboard": self.last_dashboard, "state": self.state()}

    def _parse_predictions(self, raw: Optional[Dict[str, Dict[str, float]]]) -> Dict[int, Dict[str, Dict[str, float]]]:
        cash = get_cash(self.conn)
        if raw is None:
            raw = {
                "cash_1wk": {"point": cash, "lower": cash * 0.9, "upper": cash * 1.1},
                "cash_4wk": {"point": cash, "lower": cash * 0.75, "upper": cash * 1.25},
                "cash_12wk": {"point": cash, "lower": cash * 0.5, "upper": cash * 1.5},
                "cash_26wk": {"point": cash, "lower": cash * 0.25, "upper": cash * 2.0},
            }
        mapping = {"cash_1wk": 7, "cash_4wk": 28, "cash_12wk": 84, "cash_26wk": 182}
        parsed = {}
        for key, horizon in mapping.items():
            entry = raw.get(key)
            if not entry:
                raise HTTPException(400, f"Missing prediction {key}")
            point = float(entry["point"])
            lower = float(entry["lower"])
            upper = float(entry["upper"])
            if lower > point or point > upper:
                raise HTTPException(400, f"{key} must satisfy lower <= point <= upper")
            parsed[horizon] = {"cash": {"point": point, "lower": lower, "upper": upper}}
        return parsed

    def state(self) -> Dict[str, Any]:
        with self.lock:
            conn = self.conn
            day = self.simulator.current_day if self.simulator else 0
            config = dict(get_config(conn, day) or {})
            service = self._latest_service()
            return {
                "meta": {
                    "day": day,
                    "week": (day + 6) // 7,
                    "total_days": self.config.total_days,
                    "seed": self.config.seed,
                    "llm_disabled": True,
                    "social_media_disabled": True,
                    "complete": day >= self.config.total_days,
                },
                "kpis": {
                    "cash": get_cash(conn),
                    "mrr": get_mrr(conn),
                    "active_subscribers": get_active_subscriber_count(conn),
                    "individual_subscribers": self._scalar("""
                        SELECT COUNT(*) FROM subscriptions s
                        JOIN customers c ON s.customer_id = c.customer_id
                        WHERE s.status = 'subscribed' AND s.end_day IS NULL AND c.customer_type = 'small'
                    """),
                    "enterprise_seats": self._scalar("""
                        SELECT COALESCE(SUM(CAST(c.seat_count AS INTEGER)), 0)
                        FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
                        WHERE s.status = 'subscribed' AND s.end_day IS NULL AND c.customer_type = 'large'
                    """),
                    "open_issues": self._scalar("""
                        SELECT COUNT(*) FROM customer_state cs
                        JOIN subscriptions s ON cs.customer_id = s.customer_id
                        WHERE s.status = 'subscribed' AND s.end_day IS NULL AND cs.open_issue_days > 0
                    """),
                },
                "config": config,
                "service": service,
                "quality": self._quality_rows(config),
                "segments": self._segments(),
                "ad_spend": getattr(self.config, "targeted_ad_spend", {}),
                "targeted_dev": getattr(self.config, "targeted_dev_spend", {}),
                "targeted_ops": self._targeted_ops_state(),
                "promotion": self._promotion_state(),
                "lead_promotion": self._lead_promotion_state(),
                "ads_strength": self._ads_strength_state(),
                "capacity_tiers": self._capacity_tiers(),
                "model_tiers": self._model_tiers(),
                "research_projects": self._research_projects(),
                "enterprise_threads": self._enterprise_threads(),
                "ledger": self._ledger_summary(),
                "dashboard": self.last_dashboard or build_weekly_dashboard(conn, day),
                "briefing": build_ceo_briefing(self.config.total_days),
            }

    def _scalar(self, sql: str, params: tuple = ()) -> Any:
        row = self.conn.execute(sql, params).fetchone()
        return row[0] if row else 0

    def _latest_service(self) -> Dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT * FROM service_day ORDER BY day DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None

    def _json_config(self, config: Dict[str, Any], key: str) -> Dict[str, Any]:
        raw = config.get(key)
        if isinstance(raw, str) and raw:
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {}
        return raw if isinstance(raw, dict) else {}

    def _latest_override(self, setting_type: str) -> Dict[str, Any]:
        row = self.conn.execute(
            """
            SELECT settings_json FROM config_overrides
            WHERE setting_type = ?
            ORDER BY day DESC, id DESC
            LIMIT 1
            """,
            (setting_type,),
        ).fetchone()
        if not row:
            return {}
        try:
            return json.loads(row["settings_json"])
        except (TypeError, json.JSONDecodeError):
            return {}

    def _restore_advanced_config(self) -> None:
        if self.config is None:
            return
        ad = self._latest_override("targeted_ad_spend").get("targeted_spend")
        if ad is not None:
            self.config.targeted_ad_spend = ad
        ops = self._latest_override("targeted_ops_spend")
        if ops:
            if "by_group" in ops or "by_plan" in ops or "by_group_plan" in ops or "by_customer" in ops:
                self.config.targeted_ops_spend = ops.get("by_group", {})
                self.config.targeted_ops_spend_by_plan = ops.get("by_plan", {})
                self.config.targeted_ops_spend_by_group_plan = ops.get("by_group_plan", {})
                self.config.targeted_ops_spend_by_customer = {
                    int(k): v for k, v in ops.get("by_customer", {}).items()
                }
            else:
                self.config.targeted_ops_spend = ops
        dev = self._latest_override("targeted_dev_spend").get("targeted_spend")
        if dev is not None:
            self.config.targeted_dev_spend = dev

        ads = self._latest_override("ads_strength")
        if ads:
            self.config.ads_strength_global = float(ads.get("global", 0.0))
            self.config.ads_strength_by_group = ads.get("by_group", {})
            self.config.ads_strength_by_customer = ads.get("by_customer", {})

        lead = self._latest_override("lead_promotion")
        if lead:
            self.config.lead_promotion_global = float(lead.get("global", 0.0))
            self.config.lead_promotion_by_group = lead.get("by_group", {})
            self.config.lead_promotion_by_channel = lead.get("by_channel", {})
            self.config.lead_promotion_by_channel_group = lead.get("by_channel_group", {})

        promo = self._latest_override("promotion")
        if promo:
            self.config.promotion_global = float(promo.get("global", 0.0))
            self.config.promotion_by_group = promo.get("by_group", {})
            self.config.promotion_by_customer = promo.get("by_customer", {})
            self.config.promotion_by_group_plan = promo.get("by_group_plan", {})

    def _promotion_state(self) -> Dict[str, Any]:
        return {
            "global": getattr(self.config, "promotion_global", 0.0),
            "by_group": getattr(self.config, "promotion_by_group", {}),
            "by_customer": getattr(self.config, "promotion_by_customer", {}),
            "by_group_plan": getattr(self.config, "promotion_by_group_plan", {}),
        }

    def _lead_promotion_state(self) -> Dict[str, Any]:
        return {
            "global": getattr(self.config, "lead_promotion_global", 0.0),
            "by_group": getattr(self.config, "lead_promotion_by_group", {}),
            "by_channel": getattr(self.config, "lead_promotion_by_channel", {}),
            "by_channel_group": getattr(self.config, "lead_promotion_by_channel_group", {}),
        }

    def _ads_strength_state(self) -> Dict[str, Any]:
        return {
            "global": getattr(self.config, "ads_strength_global", 0.0),
            "by_group": getattr(self.config, "ads_strength_by_group", {}),
            "by_customer": getattr(self.config, "ads_strength_by_customer", {}),
        }

    def _targeted_ops_state(self) -> Dict[str, Any]:
        return {
            "by_group": getattr(self.config, "targeted_ops_spend", {}),
            "by_plan": getattr(self.config, "targeted_ops_spend_by_plan", {}),
            "by_group_plan": getattr(self.config, "targeted_ops_spend_by_group_plan", {}),
            "by_customer": {
                str(k): v
                for k, v in getattr(self.config, "targeted_ops_spend_by_customer", {}).items()
            },
        }

    def _quality_rows(self, config: Dict[str, Any]) -> list[Dict[str, Any]]:
        q_shared = float(self._scalar("SELECT COALESCE(value, 0) FROM global_state WHERE key = 'q_shared_bonus'") or 0.0)
        bonuses = {}
        for row in self.conn.execute("SELECT key, value FROM global_state WHERE key LIKE 'q_group_bonus_%'").fetchall():
            bonuses[row["key"][len("q_group_bonus_"):]] = float(row["value"])
        base = BenchmarkConfig.base_product_quality
        tiers = {
            "A": int(config.get("tier_A", 1)),
            "B": int(config.get("tier_B", 2)),
            "C": int(config.get("tier_C", 3)),
        }
        rows = []
        for gid in sorted(get_discovered_groups(self.conn)):
            gb = bonuses.get(gid, 0.0)
            rows.append({
                "group_id": gid,
                "group_bonus": gb,
                "A": (base + q_shared + gb) * MODEL_TIERS[tiers["A"]].quality_multiplier,
                "B": (base + q_shared + gb) * MODEL_TIERS[tiers["B"]].quality_multiplier,
                "C": (base + q_shared + gb) * MODEL_TIERS[tiers["C"]].quality_multiplier,
            })
        return rows

    def _segments(self) -> list[Dict[str, Any]]:
        rows = self.conn.execute("""
            SELECT gil.group_id, gil.info_level, gil.is_discoverable, gil.discovered_day,
                   COUNT(s.subscription_id) AS active_subscribers
            FROM group_info_levels gil
            LEFT JOIN customers c ON c.group_id = gil.group_id
            LEFT JOIN subscriptions s ON s.customer_id = c.customer_id
                AND s.status = 'subscribed' AND s.end_day IS NULL
            WHERE gil.info_level > 0
            GROUP BY gil.group_id, gil.info_level, gil.is_discoverable, gil.discovered_day
            ORDER BY gil.group_id
        """).fetchall()
        return [dict(row) for row in rows]

    def _capacity_tiers(self) -> Dict[str, Any]:
        return {str(k): dict(v) for k, v in CAPACITY_TIERS.items()}

    def _model_tiers(self) -> Dict[str, Any]:
        return {
            str(k): {
                "cost_per_usage_unit": v.unit_cost,
                "quality_multiplier": v.quality_multiplier,
                "class_name": f"Tier {k}",
            }
            for k, v in MODEL_TIERS.items()
        }

    def _research_projects(self) -> list[Dict[str, Any]]:
        rows = self.conn.execute("""
            SELECT tier, status, started_day, expected_completion_day,
                   actual_completion_day, expected_quality_boost, quality_boost_applied
            FROM research_projects
            ORDER BY tier, started_day DESC
            LIMIT 100
        """).fetchall()
        return [dict(row) for row in rows]

    def _enterprise_threads(self) -> list[Dict[str, Any]]:
        rows = self.conn.execute("""
            SELECT et.thread_id, et.customer_id, et.thread_type, et.day,
                   et.sender, et.message_text, et.closed, CAST(c.seat_count AS INTEGER) AS seats,
                   c.group_id, c.email
            FROM enterprise_turns et
            JOIN customers c ON c.customer_id = et.customer_id
            WHERE et.message_id = (
                SELECT MAX(et2.message_id) FROM enterprise_turns et2
                WHERE et2.thread_id = et.thread_id
            )
            AND et.closed = 0
            ORDER BY et.day DESC
            LIMIT 50
        """).fetchall()
        return [dict(row) for row in rows]

    def _ledger_summary(self) -> list[Dict[str, Any]]:
        rows = self.conn.execute("""
            SELECT category, SUM(amount) AS amount
            FROM ledger
            WHERE day >= ?
            GROUP BY category
            ORDER BY amount ASC
        """, (max(0, self.simulator.current_day - 30),)).fetchall()
        return [dict(row) for row in rows]


service = GameService()
app = FastAPI(title="CEOBench GUI", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/state")
def get_state():
    return service.state()


@app.post("/api/reset")
def reset(req: ResetRequest):
    return service.reset(req)


@app.post("/api/tool/{name}")
def call_tool(name: str, req: ToolRequest):
    return service.call_tool(name, req.args)


@app.post("/api/advance-week")
def advance_week(req: AdvanceRequest):
    return service.advance_week(req)
