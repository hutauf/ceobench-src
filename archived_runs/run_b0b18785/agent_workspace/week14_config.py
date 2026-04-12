import novamind_api as nm

# Issues crisis analysis: S1 issues growing despite $4K/day targeted ops
# Root cause: S1 has 6,031 subs - even low issue rate × large base = many issues
# Options: 
#   1. Massively increase ops for S1 (costly)
#   2. Accept S1 is low-margin volume business with chronic issues
#   3. Stop adding S1 customers (reduce ads) to stabilize base
#   4. Investigate if there are also S2/S3 issues contributing

# Financial situation: $76K cash, $270K due in 7 days → will be fine
# Costs: $26K/day is too high. MRR $30K/day is profitable but barely
# 
# Key cost items to cut:
# - Operations: $9,829/day (was $9,229/day - somehow went UP!)
# - Compute: $11,980/day - this is high! Was $7,384/day
# - Development: $1,543/day

# Compute cost doubling is concerning - now at $12K/day vs $7.4K before
# This must be due to much more usage (enterprise growth from ~15K to ~30K seats)
# Usage: 9.2M units/week = 1.3M/day
# At Tier 3 compute cost, that's ~$11-12K/day makes sense

# DECISION: 
# 1. Try dramatically increasing ops for S1 (to $8K/day targeted) - aggressive test
#    This costs $4K/day more but might save the S1 base
# 2. OR: accept S1 issues are chronic and focus on high-value enterprise 
# 3. Actually let's think about this differently:
#    - S1 has 6,031 subs and DECLINING (was 6,757). Issues are hurting retention
#    - S1 contributes $130K MRR vs enterprise $665K MRR
#    - Enterprise is 72% of MRR now and growing
#    - S1 issues might be causing reputation damage that hurts enterprise too
#    
# DECISION: Increase S1 ops to $8K/day for one more week to test
# If no improvement next week, drop S1 targeted ops and accept attrition

# Also: consider STOPPING S1 ads entirely to slow new issue generation
# S1 new subs are probably generating issues too

print("Updating ops spending...")

# Increase S1 targeted ops significantly
nm.analytics.set_targeted_ops_spend(targeted_spend={
    "S1": 8000.0,  # was $4000 - DOUBLE
    "S2": 800.0,   # was $500
    "S3": 800.0,   # was $500
    "E1": 500.0,   # was $300
    "E2": 400.0,   # was $300
    "E3": 200.0,   # new
})
print("Targeted ops updated")

# Development: focus on quality for enterprise groups (they have high WTP)
nm.analytics.set_targeted_dev_spend(targeted_spend={
    "S2": 150.0,
    "S3": 150.0,
    "E1": 200.0,
    "E2": 300.0,
    "E3": 200.0,
})
print("Targeted dev updated")

# Base ops: keep at $3000/day (unchanged)
# Total new ops: $3000 base + $8000+$800+$800+$500+$400+$200 = $3000 + $10700 = $13,700/day
# Wait, that's very high. Let me rethink.
# At $13K ops + $12K compute + $1.5K dev + $1.3K capacity + $400 ads = $28K/day
# Revenue run rate: $30K/day → barely break even

# Actually: the S1 situation might be a "dead end" - let's try MAX ops for 1 week
# and if S1 issues still grow, we cut ops and let S1 attrit naturally
# The enterprise growth is so much more valuable

print("Config updated. Let's also check if we should stop S1 ads entirely...")

# Stop S1 specific ads, keep general ads low
# Current ads: $400/day total
# Channel split: no changes needed since ads are already minimal

# Check cost_info for base operations
cost_info = nm.infrastructure.get_cost_info()
print(f"Base ops cost: {cost_info.get('operations_base_cost', 'N/A')}")

