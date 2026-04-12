#!/usr/bin/env python3
import novamind_api as nm

# Check actual MRR
r = nm.query("SELECT SUM(seat_count * effective_price) as mrr FROM subscriptions WHERE status='subscribed'")
print(f"Total MRR: ${r['rows'][0]['mrr']:.0f}")

# Check enterprise total WITHOUT seat_count
ent = nm.query("""SELECT c.group_id, COUNT(*) as n, SUM(s.effective_price) as total_price
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
WHERE s.status='subscribed' AND c.customer_type='large'
GROUP BY c.group_id""")
print(f"\nEnterprise by group:")
for row in ent['rows']:
    print(f"  {row['group_id']}: {row['n']} subs, sum_price=${row['total_price']:.0f}")

# Check the subscription schema
r3 = nm.query("SELECT * FROM subscriptions WHERE status='subscribed' AND customer_id=29324")
print(f"\nCID 29324 sub: {r3['rows']}")

# Check active enterprise by customer
r4 = nm.query("""SELECT s.customer_id, c.group_id, s.plan, s.effective_price, s.seat_count
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
WHERE s.status='subscribed' AND c.customer_type='large'
ORDER BY s.effective_price DESC LIMIT 15""")
print(f"\nTop enterprise by price:")
for row in r4['rows']:
    print(f"  CID={row['customer_id']} {row['group_id']} Plan={row['plan']} price=${row['effective_price']:.2f} seats={row['seat_count']}")

# Total individual MRR
ind = nm.query("""SELECT SUM(effective_price) as ind_mrr, COUNT(*) as n
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
WHERE s.status='subscribed' AND c.customer_type='small'""")
print(f"\nIndividual: {ind['rows'][0]['n']} subs, MRR=${ind['rows'][0]['ind_mrr']:.0f}")

# Total enterprise MRR
ent2 = nm.query("""SELECT SUM(effective_price) as ent_mrr, COUNT(*) as n
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
WHERE s.status='subscribed' AND c.customer_type='large'""")
print(f"Enterprise: {ent2['rows'][0]['n']} subs, MRR=${ent2['rows'][0]['ent_mrr']:.0f}")
