import novamind_api as nm

# Cost analysis
print("=== COST ANALYSIS ===")
print("Revenue: $182,331 MRR / 30 = $6,077/day")
print()
print("Cost breakdown (NEW):")
print("  Capacity Tier 3: $1,330/day")
print("  Base Ops: $1,500/day")
print("  Base Dev: $1,000/day")
print("  Base Ads: $1,200/day")
print("  Targeted Ops: S1=$1500+S2=$300+S3=$300+E1=$100+E2=$100 = $2,300/day")
print("  Targeted Dev: S2=$300+S3=$200+E1=$100+E2=$200 = $800/day")
print("  Targeted Ads: S3=$250+S2=$250 = $500/day")
print("  Compute: ~$598K/day usage × model tier costs")

# Compute cost: 598K units/day
# Plan A uses Model Tier 2 = $0.002/unit
# Plan B uses Model Tier 4 = $0.012/unit
# Plan C uses Model Tier 5 = $0.030/unit
# Need to estimate by plan
r = nm.query("""SELECT s.plan, COUNT(*) as n, SUM(s.seat_count) as seats
FROM subscriptions s 
WHERE s.status='subscribed'
GROUP BY s.plan""")
print("\n--- Current subscriptions ---")
for row in r['rows']:
    print(f"  Plan {row['plan']}: {row['n']} subs, {row['seats']} seats")

# Compute cost estimates
# Plan A (T2): avg 91K usage/day per S1 sub * 5,035 = 458M... that's way too much
# Actually usage per customer is per month? Let me check
# Dashboard said 4,185,194 units this WEEK
# S1 uses ~91 units/day (from insights) × 5,035 subs = 458K/day for S1 plan A
# S2 uses ~231 units/day × 519 subs = 120K/day
# S3 uses ~524 units/day × 870 subs = 456K/day
# Enterprise uses ~55 units/day per seat × (940+608+455+485) = 2,488 seats × 55 = 137K/day
# Total: 458 + 120 + 456 + 137 = 1,171K/day → too high vs 598K/day
# Actually maybe usage_volume is monthly or per customer total
# Weekly: 4,185,194 / 7 = 598K/day

# Compute cost at current mix - rough estimate
# Most customers on Plan A (T2 model): 598K × $0.002 ≈ $1,196/day  
# But Plan C customers use T5 (×0.030) - very expensive per unit
# Plan B uses T4 (×0.012)
print("\n--- Compute cost estimate ---")
weekly_usage = 4185194
daily_usage = weekly_usage / 7
print(f"Daily usage: {daily_usage:,.0f} units")

# Most on plan A (T2 = $0.002) but with mix:
# S1: mostly T2 = $0.002
# S2/S3 Plan B: T4 = $0.012
# S3 Plan C: T5 = $0.030
# Enterprise: mixed

plan_a_subs = 5013 + 448 + 492 + 940  # S1+S2+S3+E1 Plan A
plan_b_subs = 22 + 71 + 368 + 0      # Plan B subs
plan_c_subs = 10 + 608                 # Plan C subs (E2 has 608 seats)

print(f"Plan A subs: {plan_a_subs}")
print(f"Plan B subs: {plan_b_subs}")
print(f"Plan C subs: {plan_c_subs}")

# Usage allocation - enterprise uses more per seat
# Individual Plan A: most of S1's 598K daily usage  
# E2 enterprise (608 seats) at T5 model = expensive!
# 608 seats × 222 usage/day (E2 usage) = 135K units/day × $0.030 = $4,050/day just for E2!
# That seems very expensive. At $24,320/mo = $811/day revenue vs $4,050/day compute cost...

print(f"\nE2 (21828): 608 seats × ~222 usage/day = {608*222:,}/day × $0.030 = ${608*222*0.030:,.0f}/day compute")
print(f"E2 revenue: $24,320/mo = ${24320/30:.0f}/day")
print("E2 is LOSING MONEY on compute alone!")

# Need to check actual ledger for compute cost
print("\n--- Ledger this week ---")
r3 = nm.query("""SELECT category, SUM(amount) as total 
FROM ledger WHERE day >= 50
GROUP BY category ORDER BY total ASC""")
for row in r3['rows']:
    print(f"  {row['category']}: ${row['total']:,.0f}")
