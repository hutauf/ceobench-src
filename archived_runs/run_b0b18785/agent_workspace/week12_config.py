#!/usr/bin/env python3
"""Week 12 configuration adjustments"""
import novamind_api as nm

current_day = nm.vars.current_day
print(f"=== Week 12 Config - Day {current_day} ===")

# Raise quotas to fix E1 quota complaints
nm.pricing.set_usage_quotas(A=6000, B=30000, C=80000)
print("Quotas: A=6000, B=30000, C=80000")

# Reduce advertising to save cash - too many issues to worry about growth
nm.marketing.set_daily_spend(advertising=400, operations=3000, development=800)
print("Daily spend: Ads=400, Ops=3000, Dev=800")

# Keep targeted ops high for S1 issues
nm.analytics.set_targeted_ops_spend(targeted_spend={
    "S1": 4000,
    "S2": 500,
    "S3": 500,
    "E1": 300,
    "E2": 300
})
print("Targeted ops: S1=4000, S2=500, S3=500, E1=300, E2=300 = 5600 total")

# Reduce targeted dev slightly
nm.analytics.set_targeted_dev_spend(targeted_spend={
    "S2": 100,
    "S3": 100,
    "E1": 150,
    "E2": 200
})
print("Targeted dev: S2=100, S3=100, E1=150, E2=200 = 550/day")

# Ad channel mix
nm.marketing.set_ad_channel_spend(
    social_media=0.25,
    search_ads=0.25,
    linkedin=0.20,
    content_marketing=0.20,
    referral_program=0.10
)
print("Ad channels updated")

print("Config complete!")
