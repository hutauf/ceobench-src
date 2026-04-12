import novamind_api as nm

print("=== WEEK 3 STRATEGIC ACTIONS ===")
print()

# KEY INSIGHTS THIS WEEK:
# 1. S1 converts at 11.2% (best ROI) - WTP $26, q_min 0.081 (already met!)
# 2. S2 converts at 0.7% (poor) - q_min too high for current quality
# 3. S3 converts at 1.3% (ok) - q_min 0.185, Plan B already meets it
# 4. E1 WTP $33/seat (higher than expected), q_min 0.258
# 5. R&D T1+T2 still not complete (high variance) - quality boost delayed
# 6. group_research was $120K last week - too expensive, won't repeat

# === SPENDING REBALANCE ===
# Current: Ads=$1000, Ops=$600, Dev=$1000, Targeted=$250 (S3)
# Issue: $600/day ops is expensive when no outages/overloads
# Reduce ops to $300/day, redirect $300 to dev for faster quality growth
# Keep ads at $1000, but reallocate channels

# Reduce ops (no outages, no overload)
nm.marketing.set_daily_spend(advertising=1000, operations=300, development=1300)
print("Set spending: ads=$1000, ops=$300, dev=$1300/day")

# === AD CHANNEL REBALANCE ===  
# S1 converts best -> focus on social_media and search_ads (S1 channels)
# Keep linkedin for S3 (power users, network effects) 
# Reduce content (seems less effective for conversions)
nm.marketing.set_ad_channel_spend(
    social_media=0.40,    # Up from 30% - S1 is on social media
    search_ads=0.30,      # Up from 25% - S1 searches for tools
    linkedin=0.15,        # Down from 25% - keep for S3/enterprise
    content_marketing=0.10, # Down from 15%
    referral_program=0.05   # Keep minimal
)
print("Ad channels: social=40%, search=30%, linkedin=15%, content=10%, referral=5%")

# === TARGETED AD SPEND ===
# Remove S3 targeted spend (low conversion, network effects not yet valuable at low S3 count)
# Instead, keep general mix and let S1 dominate
# Actually - keep small S3 spend for network effects seeding
nm.marketing.set_targeted_ad_spend(targeted_spend={"S3": {"linkedin": 100, "content_marketing": 50}})
print("Targeted: S3 linkedin=$100, content=$50/day")
print()

# === PLAN PRICING ===
# S1 WTP: $26, current Plan A = $19 (73% of WTP, good)
# S3 WTP: $188, current Plan B = $59 (31% of WTP - we're underpriced!)
# Consider raising Plan B price for S3 segment
# But careful - S2 and S3 share the same Plan B price
# S2 WTP: $179, S3 WTP: $188 - both high, Plan B at $59 is too cheap
# However raising price will reduce conversions... need quality first
# Keep prices same for now, focus on quality improvement

print("Prices unchanged: A=$19, B=$59, C=$149")
print()

# === QUALITY IMPROVEMENT ===
# E1 q_min = 0.258 (info level 2, ±40%)
# Current Plan B = 0.226 (below threshold!)
# After R&D T1+T2 (+0.11): Plan B = 0.336 (well above!)
# Need R&D to complete before E1 deals stick at billing

# Add targeted dev spend to E1 and S3 for group-specific quality boost
# This accumulates PERMANENTLY and is 5x more effective than global
nm.analytics.set_targeted_dev_spend(targeted_spend={
    "E1": 200,   # Group-specific quality for enterprise
    "S3": 150    # Keep S3 quality high for network effects
})
print("Targeted dev: E1=$200/day, S3=$150/day")
print()

# Check current quality vs thresholds
print("=== QUALITY CHECK ===")
print(f"Current: base=0.20, global_bonus=0.0258")
print(f"Plan A (T2, 0.75x): {(0.20+0.0258)*0.75:.4f} vs S1 q_min 0.081 ✓")
print(f"Plan B (T4, 1.00x): {(0.20+0.0258)*1.00:.4f} vs S3 q_min 0.185 ✓")
print(f"Plan B (T4, 1.00x): {(0.20+0.0258)*1.00:.4f} vs E1 q_min 0.258 ✗ (need R&D)")
print()
print("After R&D T1+T2 (+0.11):")
rnd_base = 0.20 + 0.0258 + 0.11
print(f"Plan A: {rnd_base*0.75:.4f} vs E1 q_min 0.258 ✗ (still below)")
print(f"Plan B: {rnd_base*1.00:.4f} vs E1 q_min 0.258 ✓ (meets threshold)")
print(f"Plan C: {rnd_base*1.10:.4f} vs E1 q_min 0.258 ✓ (well above)")
print()

# With targeted dev for E1 (+200/day), additional quality boost per day:
# 0.030 * ln(1 + 200/5000) = 0.030 * 0.0392 = 0.00118/day
# Over 7 days: +0.00826 quality bonus for E1
print("E1 targeted dev (+$200/day) adds ~+0.00118/day quality for E1 group")
print("After 7 days: E1 gets extra +0.00826 quality bonus")
print()

# === NO MORE MARKET RESEARCH ===
# We wasted $170K on research last week
# Only research again when cash > $500K
print("NO market research this week - conserving cash")
print()

print("=== WEEK 3 SUMMARY ===")
print("- Enterprise deals sent: 2471 (Plan A $9.50, Plan B $14), 11449 (Plan A $13, Plan B $16)")
print("- Reduced ops to $300/day (save $300/day = $2,100/week)")
print("- Increased dev to $1,300/day (faster quality improvement)")
print("- Targeted dev: E1 $200/day, S3 $150/day")
print("- Ad channels shifted toward S1 (social/search)")
print("- Watching: R&D T1+T2 completion, enterprise deal responses")
