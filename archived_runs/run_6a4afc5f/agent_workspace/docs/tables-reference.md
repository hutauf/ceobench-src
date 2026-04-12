# NovaMind Database Tables Reference

Reference for all queryable database tables. Query via:
- `novamind-operation query "SELECT * FROM table_name LIMIT 10"`
- Python: `novamind_api.query("SELECT * FROM table_name LIMIT 10")`

**Note:** Schema introspection queries (PRAGMA, sqlite_master) are blocked.
Use this reference or `docs/tables/*.json` for schema information.

---

## `ad_channel_leads`

Advertising channel effectiveness history

| Column | Description |
|--------|-------------|
| `id` | INTEGER PRIMARY KEY — Unique record ID |
| `day` | INTEGER — Simulation day |
| `channel_id` | TEXT — Ad channel identifier |
| `group_id` | TEXT — Customer group targeted |
| `leads_generated` | INTEGER — Number of leads generated |
| `spend` | REAL — Amount spent |

---

## `ads_revenue`

Per-customer daily ad revenue breakdown. Only rows where revenue > 0 are recorded.

| Column | Description |
|--------|-------------|
| `day` | INTEGER — Simulation day |
| `customer_id` | INTEGER — Foreign key to customers |
| `group_id` | TEXT — Customer group at time of recording |
| `ads_strength` | REAL — Effective ads strength applied (0.0-1.0) |
| `revenue` | REAL — Ad revenue generated for this customer on this day |

---

## `agent_social_media_posts`

Social media posts and replies authored by the agent (CEO). Use post_social_media tool to create.

| Column | Description |
|--------|-------------|
| `agent_post_id` | INTEGER PRIMARY KEY — Unique post ID |
| `day` | INTEGER — Day posted |
| `content` | TEXT — Post content (max 280 characters) |
| `reply_to_post_id` | INTEGER — If replying to a customer post, the post_id (NULL for original posts) |
| `views` | INTEGER — View count (updated next day) |
| `comment_post_ids` | TEXT — JSON list of post_ids from social_media_posts that are customer comments on this agent post (e.g. [101, 105, 108]) |

---

## `config_history`

Daily snapshot of all agent-configurable settings

| Column | Description |
|--------|-------------|
| `day` | INTEGER PRIMARY KEY — Simulation day |
| `price_A` | REAL — Plan A monthly price |
| `price_B` | REAL — Plan B monthly price |
| `price_C` | REAL — Plan C monthly price |
| `tier_A` | INTEGER — Plan A model tier (1-5) |
| `tier_B` | INTEGER — Plan B model tier (1-5) |
| `tier_C` | INTEGER — Plan C model tier (1-5) |
| `spend_advertising` | REAL — Total advertising spend per day |
| `spend_operations` | REAL — Operations spend per day |
| `spend_development` | REAL — Development spend per day |
| `capacity_tier` | INTEGER — Capacity tier (0-7) |
| `ad_spend_social_media` | REAL — Social media ad spend |
| `ad_spend_search_ads` | REAL — Search ads spend |
| `ad_spend_linkedin` | REAL — LinkedIn ads spend |
| `ad_spend_content_marketing` | REAL — Content marketing spend |
| `ad_spend_referral_program` | REAL — Referral program spend |
| `quota_A` | INTEGER — Plan A usage quota (units/day/customer) |
| `quota_B` | INTEGER — Plan B usage quota (units/day/customer) |
| `quota_C` | INTEGER — Plan C usage quota (units/day/customer) |

---

## `config_overrides`

History of all advanced config changes (ads, promotions, targeted spend). Each row records a tool call that changed a setting. Query this to see current and historical promotion/ads/spend settings.

| Column | Description |
|--------|-------------|
| `id` | INTEGER PRIMARY KEY — Unique entry ID |
| `day` | INTEGER — Simulation day when the change was made |
| `tool_name` | TEXT — Tool that made the change (e.g., 'set_promotion', 'set_ads_strength', 'set_lead_promotion', 'set_targeted_ad_spend', 'set_targeted_ops_spend', 'set_targeted_dev_spend') |
| `setting_type` | TEXT — Category: 'promotion', 'lead_promotion', 'ads_strength', 'targeted_ad_spend', 'targeted_ops_spend', 'targeted_dev_spend' |
| `settings_json` | TEXT — Full JSON snapshot of all current settings for this tool after the change |

---

## `customers`

All customers (small and enterprise)

| Column | Description |
|--------|-------------|
| `customer_id` | INTEGER PRIMARY KEY — Unique customer identifier |
| `customer_type` | TEXT — 'small' or 'large' (enterprise) |
| `created_day` | INTEGER — Simulation day customer was created |
| `persona_industry` | TEXT — Industry/domain (e.g., creative, legal, manufacturing) |
| `persona_role` | TEXT — Role/position (e.g., freelancer, managing-partner) |
| `persona_experience` | TEXT — Experience level (e.g., early-career, veteran) |
| `persona_work_style` | TEXT — Work style (e.g., scrappy, methodical, strategic) |
| `persona_tech_savvy` | TEXT — Tech savviness (e.g., basic, expert) |
| `company_size_descriptor` | TEXT — Company size descriptor (enterprise only) |
| `company_culture` | TEXT — Company culture (enterprise only) |
| `company_decision_style` | TEXT — Decision style (enterprise only) |
| `company_primary_concern` | TEXT — Primary concern (enterprise only) |
| `persona_description` | TEXT — Human-readable brief description |
| `email` | TEXT — Email address (enterprise only) |
| `contract_start_day` | INTEGER — Day enterprise contract started (enterprise only, updated on renewal) |
| `acquisition_source` | TEXT — How acquired: 'word_of_mouth' or ad channel ID |
| `group_id` | TEXT — Customer segment group identifier (e.g., 'S1', 'S2', 'E1') |

---

## `daily_usage`

Per-customer daily usage records

| Column | Description |
|--------|-------------|
| `day` | INTEGER — Simulation day |
| `customer_id` | INTEGER — Foreign key to customers |
| `usage_units` | INTEGER — Usage units consumed that day |

---

## `enterprise_turns`

Enterprise negotiation turns — each row is one message in a conversation. message_id is the unique identifier for each message.

| Column | Description |
|--------|-------------|
| `message_id` | INTEGER PRIMARY KEY — Unique message identifier (use this to reference messages in send_enterprise_deal/reject_enterprise_deal) |
| `customer_id` | INTEGER — Foreign key to customers |
| `thread_type` | TEXT — 'new_lead', 'plan_change', 'churn_prevention', 'renegotiation', 'renewal', 'general' |
| `turn_number` | INTEGER — 0-indexed turn within thread |
| `sender` | TEXT — 'customer', 'agent', or 'system' |
| `message_text` | TEXT — Message text (empty string for agent structural-only turns) |
| `offer_json` | TEXT — JSON structured offer data (empty object {} if none) |
| `day` | INTEGER — Simulation day of this turn |
| `email` | TEXT — Email of sender (enterprise customers, empty string if none) |
| `seat_count` | INTEGER — Number of seats for this customer at time of this turn |
| `closed` | INTEGER — 0=open, 1=closed. Only set for accepted/agent_rejected. |
| `close_reason` | TEXT — empty string while open; 'accepted' or 'agent_rejected' when closed |

---

## `group_info_levels`

Customer group discovery and research levels

| Column | Description |
|--------|-------------|
| `group_id` | TEXT PRIMARY KEY — Customer group identifier |
| `info_level` | INTEGER — Current info level (0=undiscovered, 1-5=researched) |
| `is_discoverable` | INTEGER — 1 if discoverable (not initial), 0 if initial |
| `discovered_day` | INTEGER — Day first discovered (NULL if Level 0) |
| `last_research_day` | INTEGER — Day of last research upgrade |

---

## `issues`

Individual customer support issues with full lifecycle tracking

| Column | Description |
|--------|-------------|
| `issue_id` | INTEGER PRIMARY KEY — Unique issue ID (auto-incrementing) |
| `customer_id` | INTEGER — Foreign key to customers |
| `group_id` | TEXT — Customer segment group identifier (e.g., S1, E1) |
| `open_day` | INTEGER — Simulation day when the issue was created |
| `days_open` | INTEGER — How many days the issue has been open (increments daily) |
| `status` | TEXT — 'open' or 'resolved' |
| `resolved_day` | INTEGER — Simulation day when resolved (NULL if still open) |
| `resolution_type` | TEXT — How resolved: 'ops_resolved' (via operations spend) |

---

## `ledger`

Financial ledger — all income and expenses

| Column | Description |
|--------|-------------|
| `id` | INTEGER PRIMARY KEY — Unique entry ID |
| `day` | INTEGER — Simulation day |
| `category` | TEXT — Category: 'subscription_payment', 'compute', 'capacity', 'advertising', 'operations', 'development', 'lead_acquisition_cost', 'initial_funding', 'market_research', 'group_research', 'research_project' |
| `amount` | REAL — Amount (positive=income, negative=expense) |
| `note` | TEXT — Description of the transaction |

---

## `macroeconomic_conditions`

Macroeconomic conditions (ISM PMI business cycle index). PMI > 50 = expansion, PMI < 50 = contraction. Published monthly with ~30 day delay (like real ISM reports). Each reading is the AVERAGE PMI over the prior measurement period, not a single-day snapshot. NOTE: Data is delayed — the most recent reading reflects conditions from ~30 days ago.

| Column | Description |
|--------|-------------|
| `day` | INTEGER PRIMARY KEY — Simulation day when PMI was MEASURED (not published). The reading appears in this table ~30 days after this day. |
| `pmi_value` | REAL — Average ISM PMI over the measurement period (30-70 scale). >50 = expansion, <50 = contraction. This is a period average, not a point-in-time value. |
| `pmi_trend` | TEXT — 'strong_expansion' (>58), 'expansion' (52-58), 'neutral' (48-52), 'contraction' (42-48), 'severe_contraction' (<42) |
| `pmi_change` | REAL — Change in average PMI from previous reading (positive = improving) |
| `cycle_phase` | TEXT — 'peak', 'declining', 'trough', 'recovering' — current position in business cycle |
| `description` | TEXT — Human-readable economic summary for the measurement period |

---

## `notifications`

Agent inbox — all notifications and alerts

| Column | Description |
|--------|-------------|
| `notification_id` | INTEGER PRIMARY KEY — Unique notification ID |
| `day` | INTEGER — Day of notification |
| `type` | TEXT — Notification type (e.g., large_customer_message, research_complete, ...) |
| `message` | TEXT — Notification message string |

---

## `research_projects`

R&D research tier invocations (in-progress, completed). 20 independent tiers, repeatable — same tier can be started multiple times. Tiers 1-10: standard R&D. Tiers 11-20: frontier moonshots (higher cost, longer timelines, more variance, better quality/$).

| Column | Description |
|--------|-------------|
| `project_id` | TEXT PRIMARY KEY — Unique invocation ID (e.g., "t1_1", "t1_2", "t3_1") |
| `tier` | INTEGER — Tier number (1-20) |
| `status` | TEXT — 'in_progress', 'completed' |
| `started_day` | INTEGER — Day this invocation was started |
| `expected_completion_day` | INTEGER — Expected completion day (sampled from Normal distribution) |
| `expected_quality_boost` | REAL — Sampled quality boost to be applied on completion |
| `quality_boost_applied` | REAL — Actual quality boost applied on completion |

---

## `segment_discovery`

History of all market research (segment discovery) attempts and outcomes

| Column | Description |
|--------|-------------|
| `id` | INTEGER PRIMARY KEY — Unique attempt ID (auto-incrementing) |
| `day` | INTEGER — Simulation day of the attempt |
| `cost` | REAL — Amount spent on this attempt |
| `success` | INTEGER — 1 if a new segment was discovered, 0 if not |
| `discovered_group_id` | TEXT — Group ID discovered (NULL if unsuccessful) |

---

## `service_day`

Daily service metrics (quality, uptime, capacity)

| Column | Description |
|--------|-------------|
| `day` | INTEGER PRIMARY KEY — Simulation day |
| `total_usage_units` | INTEGER — Total usage across all customers |
| `p95_ms` | REAL — P95 latency in milliseconds |
| `error_rate` | REAL — Error rate (0.0-1.0) |
| `downtime_minutes` | INTEGER — Minutes of downtime |
| `capacity_tier` | INTEGER — Current capacity tier (0-7) |
| `capacity_units` | INTEGER — Total capacity units available |

---

## `social_media_posts`

Public customer feedback posts on social media

| Column | Description |
|--------|-------------|
| `post_id` | INTEGER PRIMARY KEY — Unique post ID |
| `day` | INTEGER — Day posted |
| `content` | TEXT — Post content text |

---

## `subscriptions`

Customer subscriptions (current and historical)

| Column | Description |
|--------|-------------|
| `subscription_id` | INTEGER PRIMARY KEY — Unique subscription ID |
| `customer_id` | INTEGER — Foreign key to customers |
| `plan` | TEXT — Plan tier: 'A', 'B', or 'C' |
| `listed_price` | REAL — List price per seat in $ (before promotions; enterprise may have negotiated price) |
| `promotion` | REAL — Total promotion $ currently applied (updated at each billing cycle) |
| `effective_price` | REAL — Actual price per seat = listed_price - promotion (floored at 0). Use this for revenue/satisfaction calculations. |
| `start_day` | INTEGER — Day subscription started |
| `end_day` | INTEGER — Day subscription ended (NULL if active) |
| `status` | TEXT — 'lead', 'subscribed', 'cancelled', 'lost' |
| `billing_day_mod30` | INTEGER — Billing cycle day (0-29) |
| `seat_count` | INTEGER — Number of seats for this subscription |
| `pending_plan` | TEXT — Scheduled plan change (NULL if none) |
| `pending_price` | REAL — Negotiated price for pending plan change |
| `contract_months` | INTEGER — Commitment length in months (1=month-to-month) |
| `contract_end_day` | INTEGER — Day when contract expires (NULL for month-to-month) |

---
