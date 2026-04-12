import novamind_api as nm

# E2 customer 21828: 608 seats @ $40/seat Plan C (T5 = 1.10x quality, $0.030/unit)
# Usage per seat = 222 units/day (E2 estimate)  
# Compute: 608 × 222 × $0.030 = $4,049/day
# Revenue: 608 × $40/mo / 30 = $811/day
# NET: -$3,238/day LOSING MONEY

# BUT WAIT: Plan C quality = 0.3856. E2 q_min = 0.625.
# This customer subscribed BELOW their quality floor - means they'll churn at next billing!
# We should try to keep them but on Plan B (cheaper compute)
# Plan B (T4) compute: 608 × 222 × $0.012 = $1,620/day, revenue $811/day still negative
# Plan B revenue needs to be higher

# REAL ISSUE: E2 model tier 5 is extremely expensive
# $0.030/unit × 222K usage/day for enterprise = huge costs
# The E2 customer at ANY plan is unprofitable with high usage

# Let me check actual usage from the E2 customer
print("--- E2 Customer Analysis ---")
r = nm.query("""SELECT c.customer_id, c.group_id, s.plan, s.effective_price, s.seat_count,
    s.seat_count * s.effective_price as mrr
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
WHERE c.group_id = 'E2' AND s.status = 'subscribed'""")
for row in r['rows']:
    print(f"  {row}")

# Check weekly ledger detail for compute
print("\n--- Recent ledger breakdown ---")
r2 = nm.query("""SELECT category, description, SUM(amount) as total, COUNT(*) as n
FROM ledger WHERE day >= 50
GROUP BY category, description 
ORDER BY total ASC""")
for row in r2['rows']:
    print(f"  {row['category']} - {row['description']}: ${row['total']:,.0f} ({row['n']} entries)")

# STRATEGY:
# Option 1: Send E2 customer new offer on Plan B instead of C → reduces compute cost
# But E2 quality on Plan B = 0.3506, their q_min ~0.625 - will fail quality check
# They might reject or churn anyway

# Option 2: Accept they'll likely churn and just limit damage  
# Not acceptable since they're already bleeding us on compute

# Option 3: Change model tier for Plan C to reduce compute cost
# But T5 is needed for Plan C quality (1.10x multiplier)
# Could drop Plan C tier to T4: quality becomes 1.00x × (0.20+0.1506+0) = 0.351
# That's actually WORSE quality and may reduce value

# Option 4: Renegotiate E2 to Plan B at higher price
# If E2 customer subscribes to Plan B @ $60/seat: $60 × 608 / 30 = $1,216/day
# Compute Plan B: 608 × 222 × $0.012 = $1,620/day
# Still negative! The problem is E2's high usage volume (222 units/seat/day)

# CONCLUSION: E2 enterprise customers are loss-making at current compute costs
# Unless we price them much higher or reduce their usage

# Revenue needed to break even on compute:
plan_c_compute_per_seat_per_day = 222 * 0.030
plan_b_compute_per_seat_per_day = 222 * 0.012
print(f"\n--- E2 compute cost per seat per day ---")
print(f"  Plan C (T5): 222 × $0.030 = ${plan_c_compute_per_seat_per_day:.2f}/seat/day = ${plan_c_compute_per_seat_per_day*30:.2f}/seat/mo")
print(f"  Plan B (T4): 222 × $0.012 = ${plan_b_compute_per_seat_per_day:.2f}/seat/day = ${plan_b_compute_per_seat_per_day*30:.2f}/seat/mo")
print(f"\nBreak-even price per seat per month:")
print(f"  Plan C: ${plan_c_compute_per_seat_per_day*30:.2f}/mo minimum (just compute!)")
print(f"  Plan B: ${plan_b_compute_per_seat_per_day*30:.2f}/mo minimum")

# So for Plan C to break even on compute alone: $199.80/seat/mo
# We're charging $40! Far too low.
# The usage_volume of 222 units/seat/day is a HUGE problem.

# What about Plan A for E2?
plan_a_compute = 222 * 0.002
print(f"  Plan A (T2): 222 × $0.002 = ${plan_a_compute:.2f}/seat/day = ${plan_a_compute*30:.2f}/seat/mo")
