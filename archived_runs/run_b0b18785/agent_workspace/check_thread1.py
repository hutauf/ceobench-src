import novamind_api as nm

# Thread 1 - cid=1972 - status shows 'lost' but thread still open
# This thread is on turn 3 (agent sent), customer hasn't replied
# Deadline: day 14 + 7 = day 21 ... but it's day 35! 
# Customer is already lost - but should we try to re-engage?

# Check cid=1972 details
r = nm.query("SELECT * FROM customers WHERE customer_id=1972")
print("Customer 1972:", r['rows'])

# Also check cid=14075 and 16858 (also lost)
r2 = nm.query("SELECT customer_id, group_id, company_size_descriptor, company_primary_concern FROM customers WHERE customer_id IN (1972, 14075, 16858)")
print("\nLost customers:", r2['rows'])

# Current E1 revenue analysis
print("\n=== CURRENT E1 REVENUE ===")
r3 = nm.query("SELECT customer_id, plan, effective_price, seat_count FROM subscriptions WHERE customer_id IN (2471, 11449) AND status='subscribed'")
for row in r3['rows']:
    monthly = row['effective_price'] * row['seat_count']
    print(f"cid={row['customer_id']}: {row['seat_count']} seats × ${row['effective_price']} = ${monthly}/mo")

# Check capacity - how much usage per day
print("\n=== USAGE ANALYSIS ===")
print("Week 5: 790,059 total / 7 days = ~112,866/day")
print("Tier 1 cap: 200,000/day → We have headroom")
print("But growing: 1701 individual + 501 enterprise seats")
print("At 2000 individual + 800 enterprise, usage could hit 150K-200K/day")
print("Need to upgrade to Tier 2 soon (800K/day cap, $530/day)")

# Check actual daily breakdown of costs
r4 = nm.query("SELECT day, category, amount FROM ledger WHERE day >= 28 AND category='capacity' ORDER BY day")
for row in r4['rows']:
    print(f"Day {row['day']}: capacity=${row['amount']}")
