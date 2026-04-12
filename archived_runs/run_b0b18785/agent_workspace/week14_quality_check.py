import novamind_api as nm

# CRITICAL INSIGHT from group insights:
# E2 quality_floor_q_min = 0.625 (±65% noise → could be 0.22-1.03)
# Our current E2 quality: Plan C = 0.4551 
# E2 is subscribing but how? Their quality floor is supposedly 0.625 but we deliver 0.455?
# The ±65% noise means actual floor could be as low as 0.22, which we clear easily
# OR: E2 customers are on Plan C which at 1.10x tier delivers better
# 
# E3 quality_floor_q_min = 0.401 → we deliver Plan B=0.3843, Plan C=0.4227
# E3 barely makes it with Plan C only → need quality boost to enable E3 to use Plan B
#
# E1 quality_floor_q_min = 0.258 → we deliver Plan A=0.3197, Plan B=0.4262 → both good!
# This confirms E1 can use Plan A or B comfortably

# COMPETITOR DRIFT concern:
# "competitor events raise quality expectations permanently"
# "magnitude scales 1x to 4x over simulation duration"
# We're at week 14 of 71 → 1.4x scaling
# Need R&D to keep up with drifting expectations

# With $315K cash expected in 14 days:
# - T1 R&D ($167K): Start at ~$200K cash → +0.04 quality
# - This keeps us ahead of E3 quality floor (currently barely making it)
# - T2 R&D ($333K): Start when ~$500K → +0.07 additional quality
# - Critical for E2 long-term if their actual floor is ~0.40-0.50

print("Quality analysis:")
print("Current global quality bonus:", 0.1843)
print()
print("E2 analysis:")
print(f"  Current Plan C quality: {0.20 + 0.1843 + 0.0294:.4f} = {0.20 + 0.1843 + 0.0294 * 1.10:.4f} (with T5 tier mult)")
# Actually let me compute correctly:
# Plan C = T5 = 1.10x multiplier
# quality = (base + global_bonus + grp_bonus) * tier_mult
# E2 Plan C: (0.20 + 0.1843 + 0.0294) * 1.10 = 0.4137 * 1.10 = 0.4551 ✓ matches dashboard

# So E2 quality floor estimate of 0.625 at ±65% noise means:
# actual floor = 0.625 * (1 - 0.65) to 0.625 * (1 + 0.65) = 0.219 to 1.031
# With 16 subs actively subscribing, actual floor must be ≤ 0.4551
# So E2's floor is likely ~0.30-0.45

print()
print("Decision: R&D is urgent to prevent quality drift from losing E2/E3 customers")
print("With $316K projected at day 112, can start T1 R&D")
print("T1 = $167K → +0.04 global quality boost → helps all groups")

# Key question: should we also do market research to discover hidden segments?
# research_market = $25K, 30% chance to discover a group
# With $76K cash currently, spending $25K seems risky
# BUT in 7 days we'll have $153K → then safe to research

