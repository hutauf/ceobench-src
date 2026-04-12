import novamind_api as nm

# Check ledger with correct columns
print("--- Recent ledger ---")
r2 = nm.query("""SELECT category, note, SUM(amount) as total, COUNT(*) as n
FROM ledger WHERE day >= 50
GROUP BY category, note 
ORDER BY total ASC""")
for row in r2['rows']:
    print(f"  {row['category']} - {row['note']}: ${row['total']:,.0f} ({row['n']} entries)")

# Cost analysis
# Plan C compute: 222 units/seat/day × $0.030 = $6.66/seat/day = $199.80/seat/mo
# We're charging E2 only $40/seat → LOSING $159.80/seat in compute alone!
# With 608 seats: losing ~$97K/mo in compute, getting $24K/mo in revenue
# NET: -$73K/mo just for this one customer!

# E2 at Plan A would be better:
# Plan A compute: 222 × $0.002 = $0.444/seat/day = $13.32/seat/mo
# Charge E2 Plan A at $20/seat → $12,160/mo revenue, $8,100/mo compute → break even
# BUT Plan A quality = 0.263 vs E2 q_min = 0.625 → they'd churn anyway

# STRATEGIC DECISION: The E2 customer MUST be managed
# 1. Check if they'll churn at next billing (quality below q_min)
# 2. If they renew → we LOSE money. Consider offering Plan B which is cheaper per unit.
# 3. Actually need to check if the $0.030 model tier applies to all usage or just excess

# Check total compute cost this week
print("\n--- Compute cost analysis ---")
r3 = nm.query("""SELECT category, SUM(amount) as total 
FROM ledger WHERE day >= 49 AND category='compute'
GROUP BY category""")
print(f"  Compute last 7 days: {r3['rows']}")

# Daily compute: $20,377 / 7 = $2,911/day
# That's just for 598K units/day at blended rate
# If E2 alone uses 608 × 222 = 134,976 units/day at $0.030 = $4,049/day
# But total compute is only $2,911/day → E2 isn't actually that high?
# Maybe usage_volume is different from what the insight says
# Let me check actual usage model

# Actually, usage_volume is the TOTAL daily usage per customer, not per seat
# E2 estimate: 222 usage units per customer per day (not per seat)
# So E2 (21828) uses 222 units/day × $0.030 = $6.66/day → $199.80/mo
# Much more reasonable!

print("\nRe-analysis assuming usage is PER CUSTOMER not per seat:")
usage_per_customer = 222  # units/day, per customer
e2_compute_per_day = usage_per_customer * 0.030
e2_compute_per_mo = e2_compute_per_day * 30
e2_revenue_per_mo = 608 * 40  # $24,320/mo
print(f"  E2 compute: {usage_per_customer} × $0.030 = ${e2_compute_per_day:.2f}/day = ${e2_compute_per_mo:.2f}/mo")
print(f"  E2 revenue: ${e2_revenue_per_mo:,}/mo")
print(f"  E2 profit: ${e2_revenue_per_mo - e2_compute_per_mo:.2f}/mo")
print("  → PROFITABLE if usage is per customer!")

# Check S3 usage: 524.2 units/day × 870 subs = 456K/day... this seems to match the 598K daily total
# So usage IS per customer per day
# Total S1: 5,035 subs × 91 units = 458K/day... but total is only 598K
# Mixed: Let's assume about 70-80 average units/customer/day

# E2 at 222 units/day: $0.030 × 222 = $6.66/day
# Revenue: $40/seat × 608 / 30 = $811/day → PROFITABLE by ~$804/day
print("\nActual E2 assessment: PROFITABLE if usage_volume is per customer")

# What about quality? E2 q_min = 0.625 but delivering 0.386 (Plan C)
# RISK: E2 subscriber might churn at next billing due to quality not meeting expectations
# Need R&D T3+T4 to hit 0.625+ 
# Current total = 0.386. After T3 (+0.11) = 0.496. After T4 (+0.16) = 0.656 ✓
# Need to accelerate R&D!

print("\n--- Quality unlock path for E2 ---")
print(f"  Current Plan C E2: 0.3856")
print(f"  After T3 (+0.11): 0.4956")
print(f"  After T4 (+0.16): 0.6556 → ≥ E2 q_min 0.625 ✓")
print(f"  Cash needed: $500K (T3) + $667K (T4) = $1.17M")
print(f"  Current cash: $194K → need to grow cash first")
