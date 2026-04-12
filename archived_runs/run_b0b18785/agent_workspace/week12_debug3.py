#!/usr/bin/env python3
import novamind_api as nm

# The MRR calculation is correct - $601K total
# The per-sub prices show per-seat prices, MRR = seat_count * effective_price
# CID=29324 has 1875 seats @ $20 = $37,500/mo

# Let me check the full enterprise breakdown properly
r = nm.query("""SELECT s.customer_id, c.group_id, s.plan, s.seat_count, s.effective_price,
    (s.seat_count * s.effective_price) as monthly
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
WHERE s.status='subscribed' AND c.customer_type='large'
ORDER BY (s.seat_count * s.effective_price) DESC""")
print("Enterprise subs:")
total_ent_mrr = 0
for row in r['rows']:
    monthly = row['seat_count'] * row['effective_price'] if row['seat_count'] else row['effective_price']
    total_ent_mrr += monthly  
    print(f"  CID={row['customer_id']} {row['group_id']} {row['seat_count']}x{row['plan']} ${row['effective_price']:.2f} = ${monthly:.0f}/mo")
print(f"\nEnterprise MRR: ${total_ent_mrr:.0f}")

# Individual
r2 = nm.query("""SELECT c.group_id, s.plan, COUNT(*) as n, SUM(s.effective_price) as mrr
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id  
WHERE s.status='subscribed' AND c.customer_type='small'
GROUP BY c.group_id, s.plan ORDER BY c.group_id""")
print("\nIndividual subs:")
ind_mrr = 0
for row in r2['rows']:
    ind_mrr += row['mrr']
    print(f"  {row['group_id']} Plan{row['plan']}: {row['n']} subs, ${row['mrr']:.0f}/mo")
print(f"Individual MRR: ${ind_mrr:.0f}")
