import novamind_api as nm

day = nm.vars.current_day

# FINAL CONFIG DECISIONS:
# 
# 1. Ops: Increase S1 targeted ops to $8K/day (from $4K) for aggressive test
#    BUT: This pushes total costs to ~$30K/day. With MRR at $30K/day, barely break even.
#    ALTERNATIVE: Try $6K/day for S1 - balanced approach
#
# 2. Ads: Keep at $400/day but SHIFT channel allocation
#    S1 new subs are coming in and creating new issues faster than we resolve
#    → Consider reducing S1 acquisition while focusing on enterprise
#    → LinkedIn is best for enterprise, social_media for S1
#    → Shift more to linkedin/content_marketing for enterprise leads
#
# 3. Cash: $270K due in next 7 days - will be fine
#
# Let me recalculate costs with new ops:
# Targeted ops: S1=$6K, S2=$800, S3=$800, E1=$500, E2=$400, E3=$200 = $8,700
# Base ops: $3,000
# Total ops: $11,700/day (was ~$9,800)
# + compute: $12,000/day  
# + dev: $1,543/day
# + capacity: $1,330/day
# + ads: $400/day
# + lead acq: ~$500/day
# = ~$27,500/day
# MRR run rate: $30,884/day
# Net: +$3,400/day (when billing hits) - OK!

# Update targeted ops more conservatively  
nm.analytics.set_targeted_ops_spend(targeted_spend={
    "S1": 6000.0,  # Was 4000, increase to 6000 - more aggressive
    "S2": 800.0,
    "S3": 800.0,
    "E1": 500.0,
    "E2": 400.0,
    "E3": 200.0,
})
print("Targeted ops updated: S1=$6K, others as planned")

# Shift ad channel to favor enterprise (LinkedIn, content_marketing)
nm.marketing.set_ad_channel_spend(
    social_media=0.1,      # was higher, cut S1/consumer channels
    search_ads=0.2,
    linkedin=0.4,          # boost LinkedIn for enterprise leads  
    content_marketing=0.2, # content marketing attracts enterprise
    referral_program=0.1
)
print("Ad channels shifted to favor enterprise (LinkedIn 40%, content 20%)")

# Keep daily spend: $400 ads, $3000 ops base, $800 dev
# No changes needed since targeted spend handles the rest

print("\nFinal cost estimate:")
print("  Ops total: $3000 base + $6000+$800+$800+$500+$400+$200 = $11,700")
print("  Compute: ~$12,000")
print("  Dev: $800 base + $200+$150+$150+$200+$300 = $800+$1000 = ~$1,800")
print("  Capacity: $1,330")
print("  Ads: $400")
print("  Lead acq: ~$500")
print("  TOTAL: ~$27,730/day")
print("  MRR/day: $30,884")
print("  Net: ~+$3,154/day")

