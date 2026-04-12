import novamind_api as nm

print("=== Week 0 Initial Setup ===")
print(f"Current day: {nm.vars.current_day}")
print(f"Cash: $1,000,000")

# === PRICING STRATEGY ===
# Plan A: tier 2 (0.75x multiplier), target S1 at low price
# Plan B: tier 3 (0.90x multiplier), target S3/power users
# Plan C: tier 4 (1.0x multiplier), target S2/quality seekers and enterprise
# 
# Quality analysis:
# base = 0.20, delivered = base * tier_mult
# Plan A: 0.20 * 0.75 = 0.150 -> meets S1 (q_min ~0.08) and barely S3 (q_min ~0.15)
# Plan B: 0.20 * 0.90 = 0.180 -> meets S1, S3 
# Plan C: 0.20 * 1.00 = 0.200 -> meets S1, S3, approaching E1 (q_min ~0.29)
# Need R&D to boost quality for S2 (q_min ~0.37) and E1 (q_min ~0.29)

# S1: WTP ~$26, price-sensitive -> Plan A at $19-22
# S3: WTP ~$193, power users -> Plan B at $49
# S2: WTP ~$179, quality-focused (need more quality first) -> Plan C at $99
# Enterprise: negotiate separately

result = nm.pricing.set_prices(A=19, B=49, C=99)
print(f"Prices set: {result['current']}")

# Model tiers: A=2 (0.75x), B=3 (0.90x), C=4 (1.0x)
result = nm.pricing.set_model_tiers(A=2, B=3, C=4)
print(f"Model tiers set: {result['current']}")

# Usage quotas - reasonable per-day limits
# S1: low usage (~91 units/day), S3: high usage (~571/day)
result = nm.pricing.set_usage_quotas(A=200, B=600, C=2000)
print(f"Quotas set: {result['quotas']}")

# === INFRASTRUCTURE ===
# Capacity tier 1: 200k units/day at $215/day
# Should be plenty for initial customers
result = nm.infrastructure.set_capacity_tier(tier=1)
print(f"Capacity tier: {result}")

# === SPENDING ===
# Ops $400/day: critical to reduce outage risk from 3% to ~1%
# Dev $600/day: improves quality for all groups
# Ads $400/day: drive leads
result = nm.marketing.set_daily_spend(advertising=400, operations=400, development=600)
print(f"Daily spend: {result['current']}")

# Ad channel allocation: 
# S1 is price-sensitive -> social media, search
# S3 power users -> content marketing (technical)
# Enterprise -> linkedin
result = nm.marketing.set_ad_channel_spend(
    social_media=0.25, 
    search_ads=0.25, 
    linkedin=0.25, 
    content_marketing=0.15, 
    referral_program=0.10
)
print(f"Ad channels: {result['allocations']}")

# Targeted dev spend for enterprise groups (higher quality needed)
# Focus on E1 (easiest to reach quality threshold) and S2 (high WTP)
result = nm.analytics.set_targeted_dev_spend(targeted_spend={"E1": 200, "S2": 200})
print(f"Targeted dev spend: {result}")

# Targeted ops for enterprise (faster issue resolution = better retention)
result = nm.analytics.set_targeted_ops_spend(targeted_spend={"E1": 100, "E2": 100, "E3": 100})
print(f"Targeted ops spend: {result}")

# === R&D ===
# Start Tier 1 (Prompt Engineering Opt): $167k, mean 12 days, +0.04 quality
# This is our quickest quality boost
result = nm.research.start_research_project(tier=1)
print(f"R&D Tier 1 started: {result}")

# Start Tier 2 (Eval & Testing Pipeline): $333k, mean 17 days, +0.07 quality
result = nm.research.start_research_project(tier=2)
print(f"R&D Tier 2 started: {result}")

# Check remaining cash
print(f"\nR&D investments: ${166667 + 333333:,}")
print(f"Estimated remaining cash: ~${1000000 - 166667 - 333333:,}")
print(f"Daily burn: ~${400+400+600+215+300+200+200+100+100+100:.0f}")

# === SOCIAL MEDIA ===
# Post an engaging launch message
result = nm.marketing.post_social_media(
    content="NovaMind AI is live! Our AI platform delivers cutting-edge capabilities for businesses of all sizes. Early access pricing available. #AI #SaaS #ProductLaunch"
)
print(f"Social post: {result}")

print("\n=== Setup Complete ===")
print("Strategy: Build quality via R&D, capture S1 immediately, grow to S2/S3/Enterprise as quality improves")
