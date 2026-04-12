#!/usr/bin/env python3
import novamind_api as nm

active = nm.query("""SELECT customer_id, plan, seat_count, effective_price
FROM subscriptions WHERE status='subscribed' AND seat_count >= 200
ORDER BY seat_count DESC""")
print(f"Large subs >=200 seats: {len(active['rows'])}")
for row in active['rows']:
    sc = row['seat_count']
    monthly = sc * row['effective_price']
    print(f"  CID={row['customer_id']} {sc}x{row['plan']} {row['effective_price']:.2f} = {monthly:.0f}/mo")

open_threads = nm.query("SELECT customer_id FROM enterprise_turns WHERE closed=0 GROUP BY customer_id")
open_cids = {r['customer_id'] for r in open_threads['rows']}
print(f"\nOpen thread CIDs: {len(open_cids)}")

no_thread = [r for r in active['rows'] if r['customer_id'] not in open_cids]
print(f"Large subs NO open thread: {len(no_thread)}")
for row in no_thread:
    sc = row['seat_count']
    monthly = sc * row['effective_price']
    print(f"  CID={row['customer_id']} {sc}x{row['plan']} {row['effective_price']:.2f} = {monthly:.0f}/mo")
