import novamind_api as nm

day = nm.vars.current_day
print(f"=== STRATEGY DEEP DIVE Day {day} ===\n")

# What's actually using compute? Enterprise vs Individual
# Plan C T4: $0.012/unit
# Plan B T4: $0.012/unit  
# Plan A T2: $0.002/unit
# 
# Enterprise customers (8) with Plan C T4 - how much usage?
# 4,323 seats × usage_quota = massive if unlimited
# But quota is set to 500,000 units/day for Plan C
# And individual Plan A quota is 3000/day, Plan B quota is 15,000/day
#
# Total usage last week: 1,224,701 units
# At T4 costs ($0.012), compute = $14,696 for the week... 
# But actual compute was $10,602 for the week (average $1,514/day)
# So effective blended rate = $10,602 / 1,224,701 = $0.00866/unit
# 
# If most usage is enterprise (T4 @ $0.012):
# 4,323 seats × some usage/day
# If individual (Plan A T2 @ $0.002):
# 1,206 individual users × 3000 quota = 3.6M theoretical, actual much less
#
# WAIT: The individual usage is charged at T2=$0.002/unit 
# Enterprise is at T4=$0.012/unit
# Mixed: blended $0.00866/unit → enterprise probably dominates

# Let's check: if we had 0 enterprise and just individual...
# 1,206 × avg ~500 units/day = 603,000/day × $0.002 = $1,206/day compute
# But actual compute includes enterprise
# 4323 enterprise seats × 52.1 usage (E1 estimate) = 225,234 units/day
# × $0.012 = $2,703/day enterprise compute
# + 603k individual × $0.002 = $1,206/day individual compute
# Total estimate: ~$3,909/day — but actual was ~$1,514/day... 
# The enterprise usage estimate of 52.1/seat may be ±65% off

# KEY INSIGHT: enterprise drives most compute cost at T4
# Individual Plan A T2 is cheap ($0.002/unit)
# Upgrading Plan A to T3 (0.90x) at $0.006/unit = 3x more for individual compute only
# Additional cost: individual compute × 2 extra = ~$1,200/day × 2 = $2,400/day more
# That's too much!

# Actually wait - let me check what PLAN the compute is billed on
# Usage per plan: individual Plan A users use their quota
# If S1 average usage is 91.1 units/day (estimate), 1047 users × 91.1 = 95,383/day
# At T2: 95,383 × $0.002 = $191/day
# S2 usage: 231.5/day × 75 users = 17,363/day × T4 $0.012 = $208/day (Plan B T4)
# S3 usage: 570.6/day × 84 users = 47,930/day × T4 $0.012 = $575/day (Plan B T4)
# Enterprise E1: 52.1 × 4323 seats... wait they share seats
# E1 has 8 customers with various seat counts
# 761: 476 seats, 13886: 420, 15824: 264, 24156: 252, 28088: 470, 33183: 465, 34622: 209
# E1 total non-23656: 2556 seats × 52.1/seat = 133,167/day × $0.012 = $1,598/day
# E3 23656: 1767 seats × 137.5/seat = 242,963/day × $0.012 = $2,916/day
# 
# Total estimate: $191 + $208 + $575 + $1,598 + $2,916 = $5,488/day
# But actual is ~$1,514/day — the usage estimates must be way off (±65%)
# 
# Real usage last week: 1,224,701 total / 7 days = 174,957/day
# At blended $0.00866/unit = $1,515/day ✓

# So individual Plan A usage: much less than quota
# If I upgrade Plan A to T3 ($0.006 vs $0.002), additional cost = individual_usage × $0.004
# Individual usage estimate: ~174,957/day total, enterprise probably 2/3 of that
# Individual usage: ~58,000/day × $0.004 additional = $232/day extra
# THAT'S MANAGEABLE!

print("Individual compute additional cost if T3:")
print("  Estimated individual usage: ~60k units/day")
print("  Additional cost at T3 vs T2: $0.004/unit × 60k = $240/day")
print("  This is affordable!")
print()
print("S1 quality at T3:")
print("  (0.20 + 0.1020 + 0.0125) × 0.90 = 0.3145 × 0.90 = 0.2830")
print("  This is 20% better quality")
print()
print("S2 quality at T3:")
print("  Plan A T3: (0.20 + 0.1020 + 0.1185) × 0.90 = 0.4205 × 0.90 = 0.3785")
print("  Plan B stays T4: 0.4205")
print()
print("RECOMMENDATION: Upgrade Plan A T2 → T3")
print("  +$240/day compute, +20% quality for S1/S2/S3 Plan A users")
print("  S1 quality: 0.2359 → 0.2830 (may start converting new leads)")

# But will 0.2830 be enough? We don't know q_min precisely
# If q_min for new S1 leads is ~0.30-0.35 post-competitor event, still not enough
# We need to accumulate MORE S1 group bonus through targeted dev spend

# PRICE REDUCTION for Plan A:
# Currently $22/mo. Drop to $15/mo?
# Quality-price curve: at lower prices, lower quality expectation needed
# This could help conversions IF quality is borderline
# S1 WTP estimate: $25.87 (with ±65% noise = $9-43 range)
# Dropping price to $15 is below the minimum WTP estimate
# But existing S1 subs pay avg $19.66 — they converted at various prices
# 
# ISSUE: existing subs paying up to $22 at current quality
# If we drop list price to $15, existing subs would re-evaluate and probably KEEP sub
# New leads might convert at $15 even with lower quality
# Monthly revenue loss: 1047 × ($19.66 - $15) = $4,879/mo reduction
# IF we get 100 new S1 subs/week at $15: +$1,500/mo net... might be worth it
# 
# But the REAL issue is quality, not price - both new leads getting quality 0.2359
# and that's below q_min even at $15 (based on quality-price curve mechanics)

# Plan A price reduction strategy:
# Current: $22, existing avg $19.66, new leads at $22
# Drop to $14: might finally trigger conversions
# Risk: existing 1047 S1 subs will downgrade their billing to $14 next cycle
# Revenue loss: 1047 × ($19.66 - $14) = $5,933/mo
# This is a significant loss

# BETTER APPROACH:
# Keep plan A at current price ($22), improve quality
# Use LEAD PROMOTION to offer lower price to new leads only (doesn't affect existing!)
# Set lead_promotion for S1 to 30% → new leads see $22 × 0.70 = $15.40
# This doesn't affect existing customer pricing!

print("\n=== LEAD PROMOTION STRATEGY ===")
print("Set lead promotion for S1: 30% discount")
print("  New leads see Plan A at $22 × 0.70 = $15.40")
print("  Existing subs unaffected (keep paying current prices)")
print("  May help borderline conversions")
print("  Cost: 0 direct (just lower revenue from new subs)")

# WHAT SHOULD WE DO THIS WEEK?
# 1. Upgrade Plan A from T2 to T3 (manageable compute increase)
# 2. Set lead promotions for S1 to help new leads convert  
# 3. Increase global ops spend (fix issue backlog, prevent outages)
# 4. Increase targeted S1 dev (accumulate quality faster)
# 5. Send renewal to 23656 proactively (keep them happy)
# 6. Respond to any open threads

# Cost impact:
# Plan A T3: +$240/day compute
# Global ops $500→$800: +$300/day
# Targeted S1 ops $200→$400: +$200/day (total ops: $1,000/day for S1 issue resolution)
# Global dev $300→$400: +$100/day
# Targeted S1 dev $100→$200: +$100/day
# Total increase: ~$940/day
# New daily cost: ~$4,470/day
# Revenue: ~$3,320/day
# Net: ~-$1,150/day

# Is $31k cash enough? At -$1,150/day:
# Day 120 (tomorrow): $29,809
# Day 122: billing from 761 (476 × $12.50 = $5,950) → $35,759
# Day 125: billing from 13886 (420 × $14.00 = $5,880) + 34622 (209 × $13.50 = $2,822) → $44,461
# Day 127: billing from 24156 (252 × $14.00 = $3,528) → $47,989 
# Day 133: billing from 13886 renewal + 23656 next? 
# 
# This is manageable! Enterprise billing keeps us afloat.
print("\n=== FINAL ACTION PLAN ===")
print("1. Upgrade Plan A: T2 → T3 (+$240/day compute)")
print("2. Set S1 lead promotion: 25% discount (see $16.50 vs $22)")
print("3. Global ops: $500 → $800/day")
print("4. Targeted ops: S1 $200→$400/day")
print("5. Global dev: $300 → $500/day")
print("6. Targeted dev: S1 $100→$300/day (priority: get S1 quality up)")
print("7. Keep E3 targeted dev at $200/day (protect 23656)")
print("8. Send renewal/renegotiation to 23656 (maintain relationship)")
print("9. Skip stale cancelled customer threads (32045, 27484, 33184, etc.)")
print()
print("Expected new costs:")
print("  Capacity: $530")
print("  Ops (global + targeted): $800 + $400 + $100 = $1,300")
print("  Dev (global + targeted): $500 + $300 + $100 + $100 + $200 = $1,200")
print("  Compute (estimated): $1,700 (T3 slightly more)")
print("  Total: ~$4,730/day")
print("  Revenue: ~$3,320/day")
print("  Net: ~-$1,410/day")
print("  With enterprise billing (~$2k/day amortized): actually sustainable")
