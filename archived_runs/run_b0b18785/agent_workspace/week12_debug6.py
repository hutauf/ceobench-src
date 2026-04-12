#!/usr/bin/env python3
import novamind_api as nm

# Use subscriptions table directly without join
r = nm.query("""SELECT customer_id, plan, seat_count, effective_price
FROM subscriptions 
WHERE status='subscribed'
ORDER BY seat_count DESC LIMIT 50""")
print(f"Top subs by seat count:")
for row in r['rows'][:20]:
    sc = row['seat_count']
    monthly = sc * row['effective_price']
    print(f"  CID={row['customer_id']} seats={sc} plan={row['plan']} ${row['effective_price']:.2f} = ${monthly:.0f}/mo")

# Total enterprise by querying differently
r2 = nm.query("""SELECT s.customer_id, s.plan, s.seat_count, s.effective_price
FROM subscriptions s
WHERE s.status='subscribed' AND s.customer_id IN (
    SELECT customer_id FROM customers WHERE customer_type='large'
)""")
print(f"\nEnterprise subs: {len(r2['rows'])}")
total = 0
for row in r2['rows']:
    sc = row['seat_count']
    monthly = sc * row['effective_price']
    total += monthly
    if sc > 100:
        print(f"  CID={row['customer_id']} seats={sc} {row['plan']} ${row['effective_price']:.2f} = ${monthly:.0f}/mo")
print(f"Enterprise MRR: ${total:.0f}")

# Cash position
cash = nm.query("SELECT SUM(amount) as cash FROM ledger")
print(f"\nCash: ${cash['rows'][0]['cash']:.0f}")

# Cost info
cost = nm.infrastructure.get_cost_info()
print(f"Tier: {cost.get('current_tier')}")
print(f"Usage: {cost.get('current_usage_per_day', 'N/A')} units/day")
print(f"Capacity: {cost.get('capacity_per_day', 'N/A')}")
