# NovaMind AI - CEO Strategy Notes

## Current Status (Updated Weekly)
- **Last updated**: Week 2 (Day 14)
- **Cash**: ~$-12,600
- **Subscribers**: 111 (108 S1/Plan A, 2 S1/Plan B, 1 S2/Plan A)
- **MRR**: $1,386 (avg $12.49/sub)
- **Weekly burn**: ~$6,500-7,000

## CRITICAL ERRORS TO AVOID
1. **Enterprise deal timeout = 7 days** - must respond within 1 week or lose customer PERMANENTLY
2. **log_rationale() MUST be called exactly once per week before next_week**
3. **send_enterprise_deal format**: deals=[[customer_id, [["plan", price_per_seat]]]] - no 3rd arg needed
4. **subscriptions table uses status='subscribed' NOT 'active'**
5. **ledger table uses 'category' NOT 'type' column**
6. **Do NOT use dollar signs in print() statements** - causes terminal display issues
7. **issues table columns**: issue_id, customer_id, group_id, open_day, days_open, status, resolved_day, resolution_type (NO description column!)
8. **Market research costs $25K PER ATTEMPT** - we can't afford it yet (cash negative)

## S3 CRITICAL PROBLEM - 0 Conversions
- Week 1+2: 380 S3 customers created, 0 subscriptions
- Plan B quality = 0.195, Plan C quality = 0.217
- Estimated S3 q_min = 0.145 BUT info level 1 has ±65% noise
- **CONCLUSION**: Real S3 q_min is likely ~0.22-0.30 (above our current quality ceiling of 0.217)
- **EVIDENCE**: S2 customer subscribed at Plan A quality 0.158 (proves S2 q_min is much lower than estimated 0.37)
- **FIX**: Wait for R&D T1+T2 to complete → quality jumps to 0.32+ → S3 should unlock
- **After R&D T1 (~Day 16-20)**: Plan C quality ≈ 0.257 → might unlock S3
- **After R&D T2 (~Day 22-28)**: Plan C quality ≈ 0.327 → definitely unlocks S3

## S3 Profitability Warning
- S3 uses 571 units/day → at T3 model: $103/mo compute cost
- S3 WTP only $193/mo → Plan B $39 loses $64/mo per customer!
- **SOLUTION**: When S3 unlocks, price at $149-189/mo (Plan C or new pricing)
- Or use T2 model (0.75x, $0.002/unit = $34/mo compute): profitable at $39 BUT quality may be too low
- DO NOT attract S3 customers at unprofitable prices!
- If S3 subscribes, immediately raise Plan B/C prices or target S3 higher tiers

## S1 Unit Economics (EXCELLENT)
- Conversion rate: ~19% (S1-focused channels)
- CAC: ~$5.24 per S1 subscriber  
- LTV: ~$72 (6 months @ $12/mo)
- LTV/CAC: 13.7x
- **Strategy**: Keep ads running, S1-focused channels

## Current Configuration (End of Week 2)
- **Prices**: A=$12, B=$39, C=$89
- **Model Tiers**: A=2 (0.75x), B=3 (0.90x), C=4 (1.0x)
- **Quotas**: A=400 (raised from 250!), B=800, C=3000 units/day
- **Capacity**: Tier 0 ($85/day, 50K units/day)
- **Daily Spend**: Ads=$150, Ops=$350, Dev=$200
- **S3 Targeted Dev**: $150/day
- **Lead Promotion**: $8 global (reduced from $15 to save cash)
- **Ad Channels**: social=50%, search=35%, linkedin=2%, content=8%, referral=5%
- **Social media post**: Posted about usage limit improvements (post_id=3)

## Active R&D Projects
- **T1**: Prompt Engineering (+0.04 mean) - started Day 0, STILL IN PROGRESS at Day 14 (mean 12 days, 50% CV)
- **T2**: Evaluation & Testing (+0.07 mean) - started Day 0, in progress (mean 17 days)
- **T3**: Caching & Latency (+0.11 mean) - started Day 0, in progress (mean 23 days)
- NOTE: All have 50% CV - actual results highly variable!

## Quality Analysis (Day 14)
- **Base**: 0.20 + 0.0104 (global bonus) = 0.2104
- **Plan A (T2 0.75x)**: 0.158 → serves S1 (q_min ~0.08-0.15) ✓
- **Plan B (T3 0.90x)**: 0.195 → NOT serving S3 (real q_min likely 0.22-0.30)
- **Plan C (T4 1.0x)**: 0.217 → NOT serving S3 (real q_min likely 0.22-0.30)
- **S3 group bonus**: +0.0062 (from targeted dev)

### Quality Milestones
- **Day ~16-20** (R&D T1 +0.04): Plan C ≈ 0.257 → TEST S3 conversion
- **Day ~22-28** (R&D T2 +0.07): Plan C ≈ 0.327 → S3 LIKELY unlocked!
- **Day ~28-35** (R&D T3 +0.11): Plan C ≈ 0.437 → S2, E1, E3 can subscribe!

## Customer Segment Knowledge (Info Level 1, ±65%)
| Group | WTP/mo | Usage/day | Quality Floor (est) | Notes |
|-------|--------|-----------|---------------------|-------|
| S1 | $26 | 91 | ~0.08 | Working! 19% conversion, HUGE market |
| S2 | $179 | 232 | ~0.37 (NOISY - actual may be lower) | 1 subscriber proves real q_min is much lower |
| S3 | $193 | 571 | ~0.145 (NOISY - actual likely 0.22-0.30) | 0 conversions despite qual > est q_min |
| E1 | $20/seat | 52 | ~0.294 | Need quality ~0.30, achievable after T1+T2 |
| E2 | $88/seat | 222 | ~0.625 | Need T4+T5+T6 quality, S3 referral channel |
| E3 | $104/seat | 138 | ~0.401 | Strategic partners, 18 rounds, 23.8 days |

## Network Effects (KEY STRATEGIC PRIORITY)
- **S3 → E2**: 0.01 leads/sub/day (HUGE!)
- **S3 → E1**: 0.004 leads/sub/day
- **S3 → S2**: 0.003 leads/sub/day
- S3 reputation strongly affects S1 (0.465) - happy S3 users boost S1 leads
- Build S3 base → unlock E2 enterprise pipeline

## Lead Acquisition Cost Problem
- Week 1+2: 1,804 leads at $1 each = $1,804 wasted on leads
- Only 111 subscribed = $38 blended CAC (terrible!)
- S1 ONLY CAC = $5.24 (excellent)
- S2 and S3 leads = $0 conversion = pure waste
- **FIX**: Redirect ads to S1-friendly channels (done) until S2/S3 unlock

## Strategy Overview

### Phase 1 (Weeks 1-4): Wait for R&D, Build S1 Base  
- Grow S1 at $12/Plan A (working, 19% conversion)
- ALL S2/S3 leads lost until R&D boosts quality
- S1-focused ad channels (social 50%, search 35%)
- Minimized costs: lead promo $8, ops $350, dev $200

### Phase 2 (Weeks 4-7): R&D Complete → Unlock S3 and S2
- **When R&D T1+T2 complete (~Day 22-28)**: S3 should start converting
- **CRITICAL S3 pricing**: Must price Plan B/C at $149+ for S3 to be profitable!
  - T3 compute: 571 * $0.006 * 30 = $103/mo per S3 customer
  - Need revenue > $103, so Plan B should be $149+ when targeting S3
  - Consider creating separate pricing for S3 via targeted promotions
- **When R&D T3 complete (~Day 28-35)**: S2, E1, E3 unlock at Plan C quality ~0.44

### Phase 3 (Weeks 7+): Enterprise & Scale
- E1 enterprise sales (quality ~0.44 exceeds 0.294 requirement)
- E3 strategic partnerships (VERY long cycle: 18 rounds!)
- E2 via S3 referrals (needs quality 0.625 - very far out)
- Market research for hidden segments when cash positive

## Financial Model
- Daily fixed: ads $150 + ops $350 + dev $200 + capacity $85 + S3 dev $150 = $935/day
- Compute costs: ~$50/day (111 subs at avg usage)  
- Lead costs: ~$115/day (800 leads/week)
- Total burn: ~$1,100/day = $7,700/week
- Revenue: $1,386 MRR = $46/day

## Billing Schedule (Important!)
- Day 1 subs (35): Already billed once (first_billing_done=1). Next billing: Day ~31
- Day 8-14 subs (76): Next billing: Day ~38-44  
- Cash positive milestone: Need ~250+ subs at avg $15/mo for break-even

## Weekly Checklist
1. Read dashboard for key metrics
2. Check enterprise_turns (WHERE closed=0) for pending deals (MUST respond within 7 days!)
3. Check social posts for issues/reputation
4. Check R&D status (list_research_projects)
5. Adjust spending/pricing based on metrics
6. Respond to enterprise negotiations
7. Update MEMORY.md
8. log_rationale() then next_week

## Key Formulas
- Global quality gain/day: 0.006 × ln(1 + spend/5000)
- Targeted quality gain/day: 0.030 × ln(1 + targeted_spend/5000) [5x, cumulative per group]
- Delivered quality = (base + q_shared + q_group_bonus) × tier_multiplier
- At $200 dev/day: global quality gain = 0.006 * ln(1.04) = 0.000235/day
- At $150 S3 targeted: 0.030 * ln(1.03) = 0.000887/day cumulative S3 bonus

## Important Notes
- Quality estimates at info_level 1 have ±65% noise - ACTUAL values could differ HUGELY
- S2 subscriber at Plan A quality 0.158 PROVES real S2 q_min << 0.37
- S3 real q_min likely 0.22-0.30 based on 0 conversions at quality 0.217
- DO NOT run market research until cash positive ($25K per attempt, negative ROI now)
- DO NOT lower Plan C price below $149 when S3 unlocks (compute cost = $103/mo at T3!)
