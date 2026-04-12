import novamind_api as nm

# Week 8 Summary
print("=== WEEK 8 FINANCIAL SUMMARY ===")
print()

# Costs this week (from ledger)
weekly_costs = {
    "compute": 22837,  # updated from ledger
    "advertising": 8400 + 1260,  # base + targeted = 9660
    "development": 7000 + 2800,  # base + targeted = 9800
    "operations": 5600 + 6650,  # base + targeted = 12250
    "capacity": 3710,
    "lead_acquisition": 7534,
}
total_weekly_cost = sum(weekly_costs.values())
print(f"Total weekly costs: ${total_weekly_cost:,}")
print(f"Weekly revenue: $46,982")
print(f"Weekly profit/loss: ${46982 - total_weekly_cost:,}")
print()

# NEW cost structure
print("NEW daily cost structure:")
new_daily = {
    "capacity_t3": 1330,      # upgraded from 530
    "base_ops": 1500,         # increased from 800
    "base_dev": 1000,
    "base_ads": 1200,
    "targeted_ops": 2300,     # S1=1500+S2=300+S3=300+E1=100+E2=100
    "targeted_dev": 800,      # S2=300+S3=200+E1=100+E2=200
    "targeted_ads": 500,      # S3=250+S2=250
    "compute_est": 3300,      # based on ~$22.8K/week / 7 = $3,257/day
    "leads_est": 1076,        # $7,534/7
}
total_new_daily = sum(new_daily.values())
print(f"  " + "\n  ".join([f"{k}: ${v:,}/day" for k, v in new_daily.items()]))
print(f"  TOTAL: ${total_new_daily:,}/day")
print()

# Revenue
print("Revenue:")
print(f"  MRR: $182,331/mo = $6,077/day")
print(f"  Net daily: $6,077 - ${total_new_daily:,} = ${6077 - total_new_daily:,}/day")
print(f"  STILL BURNING: ${total_new_daily - 6077:,}/day")
print()

# If enterprise deals close (E1 batch at $14-20/seat)
# E1 WTP = $33. 10+ new E1 leads × ~300 seats avg = 3000 seats at $12-14 = $36-42K/mo
# Plus churn prevention keeps existing 940 seats
print("Enterprise potential (if deals close):")
print(f"  Existing: 940 E1 seats + 608 E2 seats = $14K + $24K = $38K/mo")
print(f"  New E1 (10 leads × 350 avg seats × $12): $42K/mo")
print(f"  Total enterprise potential: ~$80K/mo additional")
print()

# Quality assessment - S2 conversion
# S2 q_min = 0.37, delivering 0.363 (barely below!)
# S2 has 71 Plan B subs (conversion), group bonus growing
# Need about +0.007 more quality for S2 → targeted dev should help
print("Quality check:")
print(f"  S2 Plan B: 0.3629 vs q_min=0.37 → {0.3629-0.37:.4f} (BARELY BELOW by 0.007!)")
print(f"  S2 group bonus: +0.0124 (from targeted dev)")
print(f"  Total S2 quality: 0.2629 + 0.1506 + 0.0124 = {0.2629+0.1506+0.0124:.4f} (base + global + group)")
print(f"  Wait: dashboard says S2 Plan B = 0.3629 with group_bonus +0.0124")
print(f"  S2 q_min estimate with ±65% noise: 0.37 × 0.35 to 0.37 × 1.65 = 0.130 to 0.611")
print(f"  Even at estimate, S2 has subs → must be meeting quality for some customers!")
print()

# S2 has 71 Plan B subs at $79! → S2 is converting some customers
# This means some S2 customers have lower actual q_min
# Increasing quality further will improve conversion rate

# Plan A price raise opportunity
print("Plan A price analysis:")
print(f"  Current: 5,955 Plan A subs × $19 = $113,145/mo")
print(f"  At $22: 5,955 × $22 = $131,010/mo → +$17,865/mo (if no churn)")
print(f"  Risk: S1 WTP = $25.87, raising to $22 still well below WTP")
print(f"  DO IT: Raise Plan A to $22")
print()

# Check social posts to gauge sentiment
posts = nm.analytics.get_social_posts(days=7, limit=10)
print("--- Recent Social Posts ---")
for p in posts[:8]:
    print(f"  [{p.get('day','?')}] {p.get('group_id','?')}: {p.get('content','')[:120]}")
