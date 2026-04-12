# NovaMind AI - CEO Memory File
*Updated each week before next_week. Context resets each week — this is my only persistent memory.*

## Simulation Status
- **Current Week**: 16 (Day 112) → advancing to Week 17
- **Cash**: -$33,970 (NEGATIVE! But $232K billing due -> +$95K by Day 119)
- **Goal**: Maximize cash over 500 days (71 weeks)
- **MRR**: $847,294/mo ($28,243/day)

## ROOT CAUSE IDENTIFIED: Compute Costs Destroying Profitability
- **PROBLEM**: Model tiers T4(B) and T5(C) cost $0.012 and $0.030/unit
- **RESULT**: Compute was $34,919/day = $244K/WEEK
- **Enterprise revenue** was only $677K/month but compute ALONE was $976K/month
- **FIXED Week 16**: Downgraded B: T4→T3, C: T5→T4
  - B: saves ~$9,221/day (T4→T3 = 50% reduction)
  - C: saves ~$7,658/day (T5→T4 = 60% reduction)
  - **Total savings: $16,879/day = $118K/week!**

## Week 16 Changes Made
1. **Model tiers**: A=2, B=3 (was 4), C=4 (was 5)
   - B quality: -10% (T4 1.00x → T3 0.90x)
   - C quality: -9% (T5 1.10x → T4 1.00x)
   - E1 B plan quality: 0.4475 → 0.4028 (still >> E1 floor 0.155-0.361)
   - E2 C plan quality: 0.4852 → 0.4411 (E2 was subscribing at 0.4852 despite floor est 0.625 ±65%)
2. **Capacity**: Tier 3 → Tier 4 ($1330 → $4000/day)
   - Fixed: Usage was 2.38M/day vs Tier 3 cap 2.5M = 95% overload!
   - E2/E3 complaints about rate-limiting resolved
3. **Ops**: base=$2000 (was $3000), targeted E1=$500, E2=$500, E3=$300, S=0
4. **Dev**: base=$800, targeted E1=$100, E2=$150, E3=$100, S=0
5. **Enterprise deals**: 37+ sent (all urgent + churn prevention)
6. **Social**: Post #13 - replied to E2 rate-limiting complaint

## Current Configuration (Week 16 END)
- **Prices**: A=$22, B=$79, C=$149
- **Model Tiers**: A=2 (0.75x), B=3 (0.90x), C=4 (1.00x) ← CHANGED
- **Quotas**: A=20000, B=150000, C=500000 (per customer per day)
- **Capacity**: Tier 4 (8M/day = $4000/day) ← UPGRADED
- **Daily Spend**: Ads=$400, Ops=$2000 base, Dev=$800
- **Targeted Ops**: E1=$500, E2=$500, E3=$300 = $1300 total
- **Targeted Dev**: E1=$100, E2=$150, E3=$100 = $350 total
- **Grand total ops: $3300/day** (was $5900)
- **Grand total dev: $1150/day** (was $1800)
- **Ad channels**: LinkedIn=50%, content=20%, search=15%, social=5%, referral=10%

## Financial Metrics (Day 112)
- **Weekly revenue**: $219,398 (from billing cycle)
- **Weekly costs (OLD)**: $302,660 → NET: -$83K/week
- **Weekly costs (NEW est)**: ~$103K/week → NET: +$116K/week
- **Enterprise MRR**: 
  - E1: ~$318K/mo (62 subs, ~22K B-plan seats)
  - E2: ~$281K/mo (16 subs, ~8K seats; C plan)
  - E3: ~$78K/mo (2 subs)
- **Individual MRR**: S1=$78K, S2=$28K, S3=$47K = $153K/month

## Cash Projections
- **Day 119**: -$34K + $233K billing - $103K costs = **+$96K**
- **Day 126**: +$96K + ~$200K billing - $103K = **+$193K**
- **R&D T1 ($167K)**: Start at Day 119 IF cash > $167K confirmed ← NEXT WEEK
- NOTE: Model tier downgrade may cause some E2 churn → reduce E2 revenue

## Quality Status (Day 112 - AFTER tier changes)
- **base=0.20, global_bonus=0.1933**
- NEW delivered quality (A=T2, B=T3, C=T4):
  - E1: Plan A=0.3356, Plan B=0.4028, Plan C=0.4476, grp_bonus=+0.0543
  - E2: Plan B=0.3970, Plan C=0.4411, grp_bonus=+0.0478
  - E3: Plan B=0.3651, Plan C=0.4057, grp_bonus=+0.0124
- **RISK**: E2 C plan quality 0.4411 - they were subscribing at 0.4852 before
  - Their floor estimate: 0.625 ±65% → range 0.219-1.031
  - TRUE floor likely around 0.44-0.48 based on observed behavior
  - Some E2 churn possible next few weeks

## Competitor Quality Events (MAJOR THREAT)
From social posts (Day 100-102):
- RivalTech: +0.2904 quality boost
- CloudPeak: +0.2904 quality boost
- QuantumEdge: +0.2657 quality boost
- RivalTech (2nd): +0.2171 quality boost
- CloudPeak (2nd): +0.2657 quality boost
**Total competitor pressure: ~1.3+ quality boost to customer expectations!**
This is PERMANENT - must use R&D to offset

## Issues Status (Day 112) - STRUCTURAL PROBLEM
- S1: 8,879 (was 7,900 - GROWING!) avg 30 days open
- S2: 1,637 (was 1,521 - GROWING!) avg 23 days
- S3: 2,252 (was 2,147 - GROWING!) avg 28 days
- E1: 19, E2: 7, E3: 1 (manageable)
- **Decision**: Accept individual attrition. Ops spend not helping.
  Cut all individual ops to $0 (they're not resolving anyway)

## Enterprise Subscribers (Key)
| CID | Plan | Seats | $/seat | MRR |
|-----|------|-------|--------|-----|
| 68260 | B | 2,000 | $20 | $40,000 |
| 29324 | B | 1,875 | $20 | $37,500 |
| 66815 | C | 809 | $40 | $32,360 |
| 67504 | C | 771 | $40 | $30,840 |
| 46588 | C | 871 | $28.86 | $25,141 |
| 71494 | C | 586 | $40 | $23,440 |
| 72456 | B | 842 | $25 | $21,050 |
| 62816 | C | 507 | $40 | $20,280 |

## R&D Status - NONE STARTED
| Tier | Name | Cost | Mean Quality |
|------|------|------|------|
| T1 | Prompt Engineering | $167K | +0.040 |
| T2 | Eval & Testing | $333K | +0.070 |
| T3 | Caching & Latency | $500K | +0.110 |
| T4 | Fine-Tuning | $667K | +0.160 |
| T5 | RAG & Knowledge | $833K | +0.220 |

**PLAN**: Start T1 Week 17 (Day 119) if cash > $167K (projected ~$96K-$193K depending on churn)
Actually: Start T1 at Day 119 only if cash confirmed > $200K
If cash $96K-$167K: Wait another week (Day 126)

## Macroeconomic Context (Day 112)
- PMI: 46.1 (contraction, down 2.9 from last week)
- S1 customers freezing budgets - explains very low S1 conversion (2 new subs/week!)
- Enterprise deals still happening but slower evaluation

## Strategy

### IMMEDIATE (Week 17):
1. **Monitor E2 churn** from quality tier downgrade (crucial!)
   - If >3 E2 customers churn, may need to revert C tier or raise dev spend
2. **Check cash at Day 119** - if >$200K, start R&D T1
3. **Enterprise**: Keep responding to new leads. ~20-40 fresh leads/week.
4. **Watch individual subscriber count**: S1 declining (macroeconomic + issues)

### Cash Path
- Day 119: ~+$96K (billing inbound)
- Day 126: ~+$193K 
- Day 133: ~+$290K → Start T1 R&D ($167K) → cash $123K
- Continue building cash for T2 R&D ($333K)

### Key Risks
1. **E2 churn from model tier downgrade**: Quality 0.4852→0.4411 may trigger churn
2. **Competitor quality pressure**: ~1.3+ boost to expectations, growing each event
3. **PMI contraction**: S1/S2/S3 new customer flow declining
4. **Individual issues structural**: Not resolvable with ops spend

### Phase 2 (When cash > $500K):
1. R&D T1 ($167K) → T2 ($333K)
2. Consider raising enterprise prices to improve margins
3. May need to raise B plan prices if E2 C plan customers churn (shift focus to B plan)

## Enterprise Deal Strategy
- E1: First offer B=$20/A=$12; Counter: their_offer*1.15, floor B=$8/A=$5
- E2/E3: First offer C=$40/B=$25; Counter: their_offer*1.15, floor C=$15/B=$10
- At turn >=4: multiply by 1.05, use floor directly
- Churn prevention: offer same price or -12% max discount

## Known Good API Patterns
```python
# MRR
nm.query("SELECT SUM(seat_count * effective_price) as mrr FROM subscriptions WHERE status='subscribed'")

# Enterprise threads (AGENT must respond - sender != 'agent')
threads = nm.query("""SELECT et.customer_id, c.group_id, et.thread_type, 
    et.turn_number, et.sender, et.day, et.offer_json
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0 AND et.sender != 'agent'
ORDER BY et.customer_id ASC, et.turn_number DESC""")

# Key: A sender='system' turn=0 means new lead arrived (WE haven't replied yet)
# sender='agent' means WE replied last - WAITING for customer

# Issues by group
nm.query("SELECT group_id, COUNT(*) as n, AVG(days_open) as avg_days FROM issues WHERE status='open' GROUP BY group_id")

# Billing pipeline (next 7 days)
nm.query(f"SELECT SUM(seat_count*effective_price) as rev_due, COUNT(*) as n FROM subscriptions WHERE status='subscribed' AND ((billing_day_mod30 - {day % 30} + 30) % 30) <= 7")

# Cash
nm.query("SELECT SUM(amount) as cash FROM ledger")

# Cost breakdown
nm.query(f"SELECT category, SUM(amount)/7.0 as daily_avg FROM ledger WHERE day >= {day-7} AND amount < 0 GROUP BY category ORDER BY daily_avg ASC")

# Social posts
posts = nm.analytics.get_social_posts(days=7, limit=30)
posts['posts']  # NOT posts['rows']!

# Social media post
nm.marketing.post_social_media(content="...", reply_to_post_id=NNN)  # max 280 chars, 1/day
```

## Errors to Avoid
- Subscriptions JOIN with customers loses seat_count - query subscriptions DIRECTLY
- Enterprise turns: use `closed=0` NOT `status='pending'`
- Subscriptions: use `status='subscribed'` NOT `status='active'`
- customers table: customer_type is 'small'/'large' not 'enterprise'
- R&D result key is `tiers` (LIST) - tiers 1-20
- nm.vars only has `current_day` (no cash attribute)
- DO NOT use python-c with complex f-strings containing $ (use write_file instead)
- offer_json in enterprise_turns is a STRING - use json.loads()
- "no subscription" errors for turn 0 threads = we already responded (turn 1 agent)
- capacity_tiers keys: string '0','1','2'... not integers
- social posts: keys are post_id, day, content, source_group_id, group_id, customer_type, custom_name, persona_name (NO customer_id)
- posts['posts'] not posts['rows']
- nm.query() does NOT accept params= keyword
- enterprise_turns has `message_text` not `message`
- DO NOT query issues table for `days_open` - use AVG with actual day column if needed
- nm.marketing.post_social_media() NOT nm.analytics.post_social_media()

## Weekly Checklist
1. Check enterprise_turns: respond to ALL threads age<=7d + all churn_prevention (active subs)
2. Check R&D completion + start if cash allows
3. Check social posts + post response (1/week limit via nm.marketing.post_social_media)
4. Monitor E2 churn from tier downgrade (watch closely!)
5. Check capacity vs usage (Tier 4 = 8M/day, usage ~2.4M = 30% - good)
6. Check billing pipeline for cash forecast
7. Check issues trend
8. Update MEMORY.md
9. log_rationale → next_week
