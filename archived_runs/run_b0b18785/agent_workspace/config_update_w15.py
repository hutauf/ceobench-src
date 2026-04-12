import novamind_api as nm

print("=== Week 15 Configuration Updates ===")

# 1. Raise quotas - E1 customer complained about hitting usage cap
print("\n1. Raising quotas...")
nm.pricing.set_usage_quotas(A=20000, B=150000, C=500000)
print("   A=20000, B=150000, C=500000 (significant increase)")

# 2. Reduce individual ops spending - issues not improving despite high spend
# S1 issues: 7970->7900 (basically flat despite $6K/day ops)
# S3 issues: 2095->2147 (getting worse)  
# S2 issues: 1438->1521 (getting worse)
# These are structural - issue generation rate > resolution rate
# Save $5800/day by cutting individual ops
print("\n2. Reducing individual ops spending (issues not responding)...")
nm.analytics.set_targeted_ops_spend(targeted_spend={
    "S1": 1000.0,   # down from 6000 (save $5000/day)
    "S2": 400.0,    # down from 800 (save $400/day)
    "S3": 400.0,    # down from 800 (save $400/day)
    "E1": 500.0,    # keep (enterprise important)
    "E2": 400.0,    # keep
    "E3": 200.0     # keep
})
print("   S1: $6000->$1000, S2/S3: $800->$400/day each")
print("   Savings: $5800/day = $40600/week")

# 3. Also reduce base ops a bit since enterprise E1/E2 issues are fine (22/4)
# Keep at $3000 for now - it supports all groups

# 4. Check and possibly adjust ads
# Current: $400/day total ads - very low
# LinkedIn 40%, content 20%, search 20%, social 10%, referral 10%
# Individual subs are declining - maybe cut ads for individuals
# and focus on enterprise via LinkedIn
print("\n3. Adjusting ad channels for enterprise focus...")
nm.marketing.set_ad_channel_spend(
    social_media=0.05,        # down from 10% - S1 declining anyway
    search_ads=0.15,          # down from 20% 
    linkedin=0.50,            # up from 40% - best for enterprise
    content_marketing=0.20,   # keep
    referral_program=0.10     # keep
)
print("   LinkedIn: 40%->50%, social: 10%->5%, search: 20%->15%")

# 5. Keep dev spending the same - quality is maintaining well
# base $800 + targeted $1000 = $1800/day total

print("\n=== Summary ===")
print("Key changes:")
print("  - Quotas raised 3-6x to prevent usage cap complaints")
print("  - Individual ops cut $5800/day (issues unresponsive to ops)")
print("  - Ads shifted more to LinkedIn (enterprise focus)")
print("  - Net savings: ~$5800/day = $40,600/week")
print("  - Cash trajectory improved: ~$412K billing in next 7d")
print("  - Will enable R&D T1 start when cash > $200K (~Day 112)")
