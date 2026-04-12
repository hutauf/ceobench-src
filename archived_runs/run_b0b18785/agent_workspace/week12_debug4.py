#!/usr/bin/env python3
import novamind_api as nm

# Query without computed column in SELECT
r = nm.query("""SELECT s.customer_id, c.group_id, s.plan, s.seat_count, s.effective_price
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
WHERE s.status='subscribed' AND c.customer_type='large'""")
print("Enterprise subs:")
total_ent_mrr = 0
for row in r['rows']:
    sc = row['seat_count'] if row['seat_count'] else 1
    monthly = sc * row['effective_price']
    total_ent_mrr += monthly  
    print(f"  CID={row['customer_id']} {row['group_id']} {sc}x{row['plan']} ${row['effective_price']:.2f} = ${monthly:.0f}/mo")
print(f"\nEnterprise MRR: ${total_ent_mrr:.0f}")
