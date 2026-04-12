import novamind_api as nm

print("=== WEEK 5 CONFIGURATION ===")

# 1. Upgrade capacity to Tier 2 (800K/day, $530/day)
# Currently 113K/day usage with 1701+501 subscribers
# Growing fast - need to stay ahead of capacity limits
print("\n1. Upgrading capacity to Tier 2...")
result = nm.infrastructure.set_capacity_tier(tier=2)
print("Capacity result:", result)

# 2. Increase ops spending to resolve 624 open issues faster
# S1 has 534 issues averaging 4.3 days - damaging reputation
# More ops = faster resolution, less churn risk
print("\n2. Increasing ops spending...")
result = nm.marketing.set_daily_spend(advertising=1200, operations=600, development=1300)
print("Daily spend result:", result)

# 3. Add targeted ops for S1 specifically (most issues)
print("\n3. Adding targeted ops for S1...")
result = nm.analytics.set_targeted_ops_spend(targeted_spend={"S1": 150, "S3": 50})
print("Targeted ops result:", result)

# 4. Optimize ad channels - S1 converting at 19.3% so focus social+search
# S2 converting at 2.2% with WTP $179 - worth some targeted spend
# S3 converting at 6.5% - good for network effects
print("\n4. Optimizing ad channels...")
result = nm.marketing.set_ad_channel_spend(
    social_media=0.40,     # Best for S1
    search_ads=0.30,       # Good for S1
    linkedin=0.15,         # Good for S3/E1 pipeline
    content_marketing=0.10, # Broad awareness
    referral_program=0.05   # Organic growth
)
print("Ad channel result:", result)

# 5. Add targeted ads for S3 (network effects pipeline for E1/E2)
# and keep minimal S2 targeting (high WTP worth some investment)
print("\n5. Setting targeted ad spend...")
result = nm.marketing.set_targeted_ad_spend(targeted_spend={
    "S3": {"linkedin": 100, "content_marketing": 50},
    "S2": {"content_marketing": 50}  # S2 has high WTP $179
})
print("Targeted ads result:", result)

# 6. Maintain dev spending to keep quality improving
# Keep targeted dev for E1 and S3 (quality-sensitive segments)
print("\n6. Keeping targeted dev spend...")
result = nm.analytics.set_targeted_dev_spend(targeted_spend={"E1": 200, "S3": 150})
print("Targeted dev result:", result)

print("\n=== CONFIGURATION COMPLETE ===")
print("Daily costs estimate:")
print("  Capacity T2: $530/day (+$315 vs T1)")
print("  Ads: $1200/day + targeted $200 = $1400/day")  
print("  Ops: $600/day + targeted $200 = $800/day")
print("  Dev: $1300/day + targeted $350 = $1650/day")
print("  Compute: ~$600/day")
print("  Total: ~$4,980/day costs")
print("  Revenue: ~$46,403/30 days = $1,547/day")
print("  NOTE: Revenue accrues monthly, need more enterprise deals to break even!")
