#!/usr/bin/env python3
import novamind_api as nm

r = nm.query("""SELECT s.customer_id, c.group_id, s.plan, s.seat_count, s.effective_price
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
WHERE s.status='subscribed' AND c.customer_type='large'""")
print(f"Rows: {len(r['rows'])}")
if r['rows']:
    print(f"First row keys: {list(r['rows'][0].keys())}")
    print(f"First row: {r['rows'][0]}")
