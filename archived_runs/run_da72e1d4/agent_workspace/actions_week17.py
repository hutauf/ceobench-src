import novamind_api as nm

day = nm.vars.current_day
print(f"=== ACTIONS Week 17 (Day {day}) ===\n")

# PRIORITY 1: Dramatically increase ops to resolve issue backlog
# S1 has 2758 open issues averaging 24 days - this is KILLING churn
# Need to accelerate resolution significantly
# Current: global ops $500/day + targeted S1=$200, E1=$100 = $800/day total
# Need: much more ops targeting S1

# PRIORITY 2: Quality is still too low for new leads  
# S1 quality Plan A T2 = 0.2359 — need to understand what q_min actually is
# The issue: competitor events raised q_min massively
# Options: upgrade Plan A to T3, reduce price, or just let existing subs churn slowly

# PRIORITY 3: 23656 renegotiation thread still open (turn 1, my offer at $20)
# Contract "ended" day 118 but payment processed day 119 ($35,340)
# Subscription still shows "subscribed" with end=118
# This customer is month-to-month, billing on mod30=29
# The renegotiation thread is open - I should send another offer to maintain relationship

# Let's increase ops spending significantly - the issue backlog is the #1 churn driver
# Current: $800/day total ops
# Increase global ops to $2000/day, targeted S1 to $500/day
# This costs more but reduces churn which saves revenue

print("=== CURRENT SPEND ANALYSIS ===")
print("Current daily costs:")
print("  Capacity T2: $530/day")
print("  Global ops: $500/day")
print("  Global dev: $300/day")
print("  Targeted ops (S1=$200, E1=$100): $300/day")
print("  Targeted dev (E3=$200, S1=$100, S2=$100, S3=$100): $500/day")
print("  Compute: ~$1,400/day")
print("  Total: ~$3,530/day")
print()
print("Revenue: ~$3,320/day (MRR $99,612/30)")
print("  Enterprise: ~$2,200/day")
print("  Individual: ~$1,008/day")
print()
print("Net: ~-$210/day (slightly negative without enterprise lumpy payments)")

# The issue: we need quality improvement to stop churn
# Plan: 
# 1. Increase global ops to $1500/day (was $500) - resolve issues faster
# 2. Increase targeted S1 ops to $500/day (was $200)
# 3. Keep dev spending same
# 4. Maybe increase dev spend for S1 to improve quality faster

# New costs: $530 + $1500 + $300 + ($500+$100) + ($200+$100+$100+$100) + $1400 = $4,830/day
# Revenue: $3,320/day
# Net: -$1,510/day — too aggressive!

# Alternative: 
# Increase global ops to $1000/day (was $500) - cost increase $500/day
# Increase targeted S1 ops to $500/day (was $200)
# New total: $530 + $1000 + $300 + ($500+$100) + ($200+$100+$100+$100) + $1400 = $4,330/day
# Net: -$1,010/day — still negative

# Cash is $31,159. At -$1,010/day, lasts ~31 days before zero
# But enterprise billing is lumpy - next payments:
# Day 122: billing_mod30=2 - customer 761 (476 seats @ $12.50 = $5,950)
# Day 124: billing_mod30=4 - customer 34622? 
# Let's be conservative: increase ops to $1000 global + S1=$400

# Actually look at this more carefully:
# Revenue per day from enterprise (excluding individual):
# 761: 476 seats × $12.50 = $5,950/mo = $198/day
# 13886: 420 seats × $14.00 = $5,880/mo = $196/day  
# 15824: 264 seats × $14.00 = $3,696/mo = $123/day
# 23656: 1767 seats × $20.00 = $35,340/mo = $1,178/day
# 24156: 252 seats × $14.00 = $3,528/mo = $118/day
# 28088: 470 seats × $13.00 = $6,110/mo = $204/day
# 33183: 465 seats × $13.00 = $6,045/mo = $201/day
# 34622: 209 seats × $13.50 = $2,822/mo = $94/day
# Total enterprise: ~$2,312/day

# Individual: $1,008/day
# Total: $3,320/day
# Costs: $3,530/day → net -$210/day

# If I increase ops by $700/day → costs $4,230 → net -$910/day
# Cash of $31k lasts 34 days at that rate
# But next enterprise payments: Day 120 (24156, ~$3,528), Day 122 (761, ~$5,950), Day 125 (13886 ~$5,880), etc.

print("\n=== PLAN: MODEST OPS INCREASE + QUALITY FOCUS ===")
print("1. Increase global ops: $500 → $800/day (+$300)")
print("2. Increase targeted S1 ops: $200 → $400/day (+$200)")  
print("3. Increase global dev: $300 → $400/day (+$100)")
print("4. Keep targeted dev same ($500/day)")
print("5. Net new daily cost: ~$4,130 vs current $3,530 → -$600/day more")
print("This is sustainable with enterprise payments")

# Actually check - the 4 churn_prev deals closed means those customers renewed
# 761: 476 seats, 15824: 264, 33183: 465, 28088: 470 = 1,675 seats retained!
# That's ~$22k/month in saved revenue

# Plan A price reduction: if we drop from $22 to $17-18, more leads might convert
# But with 0% conversion, it's likely quality that's the barrier, not price
# S1 q_min estimate (with ±65% noise) was 0.081 - but post-competitor event it's higher
# Our quality is 0.2359 for Plan A... why are they not converting?
# 
# Wait - let me re-read the quality formula:
# Delivered Quality = (base + q_shared + q_group_bonus) × tier_multiplier + penalties
# For S1, Plan A T2:
# base=0.20, global_bonus=0.1020, grp_bonus=+0.0125
# quality = (0.20 + 0.1020 + 0.0125) × 0.75 = 0.3145 × 0.75 = 0.2359 ✓
# 
# The competitor events pushed q_min up. Multiple events at +0.2657 each
# q_min was maybe ~0.08 for S1. Now it's maybe ~0.08 + 3×0.07 = ~0.29?
# Our quality 0.2359 < 0.29 → all new leads lost
#
# To serve S1 new leads we need quality > ~0.29
# Plan B T4: 0.3145 — that might work IF they can afford $79
# Plan A T2: 0.2359 — insufficient
# 
# If we upgrade Plan A to T3 (0.90x):
# S1 Plan A T3 = (0.20 + 0.1020 + 0.0125) × 0.90 = 0.3145 × 0.90 = 0.2830
# Still might not be enough
#
# Plan A T4 (1.00x):
# S1 Plan A T4 = 0.3145 × 1.00 = 0.3145
# This might work! But compute cost = $0.012/unit vs $0.002 for T2
# At 1,224,701/week usage currently... T4 would cost 6x more than T2
# That's $10,602 × 6 = ~$63,000/week on compute — CATASTROPHIC
# 
# NO! Can't upgrade Plan A to T4 — compute costs are 6x T2
# At current usage T4 would cost ~$18,000/day in compute vs $1,400/day → DEATH

# Better approach: 
# 1. Focus on quality improvement through dev spend (accumulates)
# 2. Group bonus for S1 needs to increase substantially
# 3. Currently S1 grp_bonus = +0.0125 (very low)
# 4. Increase targeted S1 dev to $500/day → more group bonus accumulation
# 5. This is free (sunk cost) and accumulates permanently

print("\nS1 quality gap:")
print("  Current Plan A T2: 0.2359")
print("  Need: ~0.29+ for new leads to convert")
print("  Gap: ~0.053 quality points needed")
print()
print("  Dev spend accumulation rate for targeted: 0.030 × ln(1 + spend/5000) per day")
print("  At $500/day: 0.030 × ln(1 + 500/5000) = 0.030 × ln(1.1) = 0.030 × 0.0953 = 0.00286/day")
print("  To gain 0.053: needs 0.053/0.00286 × 0.75 = ~18.5 days of $500/day targeted")
print("  But wait: quality with T2 = bonus × 0.75, so need bonus to be higher")
print()
print("  With T3 (0.90x) and same quality level:")
print("  Need (0.20 + 0.1020 + grp_bonus) × 0.90 > 0.30")
print("  0.3020 + grp_bonus > 0.333")
print("  grp_bonus > 0.031 (currently 0.0125)")
print("  Need 0.0185 more in grp_bonus")
print("  At $500/day targeted: 0.00286/day × 0.90 = 0.00257/day effective in T3")
print("  Days needed: 0.0185/0.00286 = 6.5 days — achievable!")
print()
print("PLAN: Upgrade Plan A from T2 to T3!")
print("  This increases quality 20% (0.75x → 0.90x)")
print("  Compute cost increase: T3=$0.006 vs T2=$0.002 = 3x more compute")
print("  At 1.2M/week usage: currently $10,600/week → T3 = $31,800/week = $4,500/day")
print("  That adds $3,100/day in compute costs — TOO EXPENSIVE at current cash")
