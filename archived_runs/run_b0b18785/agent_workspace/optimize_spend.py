import novamind_api as nm

# FINANCIAL ANALYSIS:
# Revenue: $182K MRR / 30 = $6,077/day
# But with Plan A raised to $22: +$17,865/mo / 30 = +$595/day → $6,672/day
# (Some churns expected from price raise, so maybe $6,400/day net)

# Cost problem: I'm spending $13K/day! Way too much.
# The $8.9K/week ops cost (from ledger) = $1,271/day before my changes
# I just increased ops from $800 + $950 = $1,750 to $1,500 + $2,300 = $3,800/day!
# That's +$2,050/day in ops alone

# However: issues crisis (3,811 open) is destroying customer satisfaction and will cause churn
# Need to balance: enough ops to resolve issues, but not bankrupt

# REVISED PLAN:
# - Base ops: reduce to $1,000 (still higher than before)
# - S1 targeted ops: reduce to $1,000 (was $800, need more but not $1,500)
# - S2/S3 targeted ops: $150 each (reduce from $300)
# - E1/E2: keep $100 each (critical enterprise)

# This gives: $1,000 + $1,000 + $150 + $150 + $100 + $100 = $2,500/day in ops
# vs current $3,800/day savings of $1,300/day

# REVISED dev targets: S2 most important (+0.007 needed)
# - targeted_dev: S2=$300, S3=$100, E2=$100, E1=$50 = $550/day
# - base dev: $800 (reduce from $1,000 to save $200/day)
# Actually dev is important for quality competition... keep at $1,000

# REVISED ads: can reduce slightly since we have good conversion
# - base ads: $800 (reduce from $1,200 - save $400/day)
# Actually leads were 7,486/week = decent. Don't want to lose momentum.
# Keep at $1,200 but reduce targeted ads to $200/day (save $300/day)

# NEW COST ESTIMATE:
print("=== REVISED COST STRUCTURE ===")
new_daily = {
    "capacity_t3": 1330,
    "base_ops": 1000,          # reduced from 1500
    "base_dev": 1000,
    "base_ads": 1200,
    "targeted_ops_S1": 1000,   # reduced from 1500
    "targeted_ops_S2_S3": 300, # $150 each, reduced from $600
    "targeted_ops_E": 200,     # E1+E2 = $100 each
    "targeted_dev": 550,       # S2=300, S3=100, E2=100, E1=50
    "targeted_ads": 250,       # reduced from 500
    "compute_est": 3300,
    "leads_est": 1076,
}
total = sum(new_daily.values())
revenue_day = 182331 / 30 + 17865 / 30  # adjusted for price raise
print(f"Total daily costs: ${total:,}/day")
print(f"Estimated daily revenue (post-price-raise): ${revenue_day:.0f}/day")
print(f"Net: ${revenue_day - total:.0f}/day")
print()

# APPLY REVISED SETTINGS
print("Applying revised spending...")
nm.marketing.set_daily_spend(advertising=1200, operations=1000, development=1000)
print("  Base: ads=$1200, ops=$1000, dev=$1000")

nm.analytics.set_targeted_ops_spend(targeted_spend={
    "S1": 1000,   # S1 primary issues (3035 issues) 
    "S2": 150,    # 295 issues
    "S3": 150,    # 476 issues
    "E1": 100,    # 4 issues
    "E2": 100,    # 1 issue (paying $40/seat!)
})
print("  Targeted ops: S1=$1000, S2=$150, S3=$150, E1=$100, E2=$100")

nm.analytics.set_targeted_dev_spend(targeted_spend={
    "S2": 300,    # S2 quality borderline - need group bonus
    "S3": 100,    # S3 doing well
    "E2": 100,    # Keep E2 happy
    "E1": 50,     # Small boost
})
print("  Targeted dev: S2=$300, S3=$100, E2=$100, E1=$50")

nm.marketing.set_targeted_ad_spend(targeted_spend={
    "S3": {"linkedin": 100, "content_marketing": 50},  # High-value S3
    "S2": {"content_marketing": 100},                   # Quality-focused S2
})
print("  Targeted ads: S3=$150, S2=$100")

# Total ops: $1000 + $1000+$150+$150+$100+$100 = $2,500/day
# Total dev: $1000 + $550 = $1,550/day
# Total ads: $1200 + $250 = $1,450/day
# Capacity: $1,330/day
# Compute + leads: ~$4,376/day (estimate)
# TOTAL: ~$11,206/day (saving $1,800/day vs original plan)
new_total = 1330 + 1000 + 1000 + 1200 + 1500 + 550 + 250 + 3300 + 1076
print(f"\nRevised daily costs: ~${new_total:,}/day")
print(f"Revenue: ~${revenue_day:.0f}/day")
print(f"Net burn: ~${new_total - revenue_day:.0f}/day")
print(f"At this rate, $194K lasts ~{194000/(new_total-revenue_day):.0f} days")
print()

# CONCLUSION: We're still burning cash, but the MRR growth from enterprise deals closing
# should bridge the gap. When 20+ E1 customers close (est 5,000 seats × $13 = $65K/mo),
# that adds $2,167/day → net burn drops to ~$4,000/day
# With Plan A at $22 (+$595/day) → ~$3,400/day burn
print("Survival timeline:")
print("  Current: $194K cash, ~$6K/day burn (before new ops) = 32 days")
print("  With enterprise: +$65K/mo expected over next 4 weeks")
print("  With price raise: +$18K/mo") 
print("  Net MRR could reach $265K/mo → $8,833/day")
print("  Break-even at ~$11.5K/day spend (tight)")
