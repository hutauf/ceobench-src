import novamind_api as nm

# === CRITICAL: Issues backlog is 3,811 (was 1,149 last week) - CATASTROPHIC ===
# S1: 3,035 issues avg 7.6 days. With 5,035 S1 subs that's 60% have open issues!
# Need to massively increase ops spending

# Also: MRR = $182K → revenue/day = $6,077
# Current costs: need to check what changed
# Revenue per day $6,077 vs costs ~$7,900/day → still burning
# But if enterprise deals close we can approach break-even

# === CHECK CURRENT CAPACITY ===
print("--- Infrastructure ---")
cost_info = nm.infrastructure.get_cost_info()
print(f"Current tier: {cost_info.get('current_tier')}")
print(f"Usage today: {cost_info.get('current_usage')}")

# Usage was 4,185,194 weekly = 598K/day. Tier 2 = 800K/day. At 74.7% utilization!
# Need to upgrade to Tier 3 soon before overload

# === ADJUST SPENDING ===
# Issues crisis: need MASSIVE ops boost
# S1 targeted ops must go way up; S2, S3 also need help

print("\n--- Updating spending ---")

# Base ops: increase from $800 to $1500/day (crisis level)
# Dev: maintain $1000/day  
# Ads: maintain $1200/day (leads are coming in well - 7486 this week)
nm.marketing.set_daily_spend(advertising=1200, operations=1500, development=1000)
print("Base spending: ads=$1200, ops=$1500, dev=$1000")

# Targeted ops: S1 needs massive boost, S2 and S3 also
nm.analytics.set_targeted_ops_spend(targeted_spend={
    "S1": 1500,  # S1 has 3,035 issues - primary crisis  
    "S2": 300,   # S2 has 295 issues
    "S3": 300,   # S3 has 476 issues
    "E1": 100,   # E1 has 4 issues
    "E2": 100,   # E2 has 1 issue - keep happy (paying $40/seat!)
})
print("Targeted ops: S1=$1500, S2=$300, S3=$300, E1=$100, E2=$100")

# Dev spending: focus on global quality + S2 (need q_min breakthrough)
# S2 q_min = 0.37, delivering 0.363. Need +0.007 more quality for S2
nm.analytics.set_targeted_dev_spend(targeted_spend={
    "S2": 300,   # S2 quality is borderline, needs group bonus
    "S3": 200,   # S3 doing well but keep improving
    "E1": 100,   # E1 has some issues with churn prevention
    "E2": 200,   # E2 is paying well, keep them happy
})
print("Targeted dev: S2=$300, S3=$200, E1=$100, E2=$200")

# Targeted ads: optimize for high-value conversion
nm.marketing.set_targeted_ad_spend(targeted_spend={
    "S3": {"linkedin": 150, "content_marketing": 100},  # S3 = $79-149/mo, high value
    "S2": {"content_marketing": 150, "search_ads": 100},  # S2 quality gated but building pipeline
})
print("Targeted ads: S3 linkedin+content, S2 content+search")

# Ad channels: keep balanced
nm.marketing.set_ad_channel_spend(
    social_media=0.30, search_ads=0.25, linkedin=0.15, 
    content_marketing=0.15, referral_program=0.15
)
print("Ad channels: social=30%, search=25%, linkedin=15%, content=15%, referral=15%")

# === CAPACITY: Check if we need to upgrade ===
# Usage: 4,185,194/week = 598,000/day. Tier 2 capacity = 800K/day
# 74.7% utilization - getting close! With 1,911 new subs/week, usage will grow
# Upgrade to Tier 3 to be safe
print("\n--- Upgrading capacity ---")
result = nm.infrastructure.set_capacity_tier(tier=3)
print(f"Capacity upgrade: {result}")

print("\n--- Cost info after upgrade ---")
cost_info2 = nm.infrastructure.get_cost_info()
print(f"New tier: {cost_info2.get('current_tier')}")
current_tiers = cost_info2.get('capacity_tiers', {})
if isinstance(current_tiers, dict):
    for k in ['2', '3', '4']:
        t = current_tiers.get(k, {})
        print(f"  Tier {k}: capacity={t.get('daily_capacity')}, cost=${t.get('daily_cost')}/day")
