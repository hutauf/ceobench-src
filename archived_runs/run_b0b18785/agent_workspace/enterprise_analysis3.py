import novamind_api as nm

print("=== ACTIVE ENTERPRISE SUBSCRIPTIONS ===")
r = nm.query("""
SELECT s.customer_id, c.group_id, s.plan, s.effective_price, s.seat_count, s.status
FROM subscriptions s
JOIN customers c ON s.customer_id = c.customer_id
WHERE c.group_id IN ('E1','E2','E3') AND s.status = 'subscribed'
""")
for row in r['rows']:
    print(row)

print("\n=== THREAD TIMING ANALYSIS ===")
print("Day 35 now. 7-day deadline = must reply within 7 days of arrival")
print()
threads = [
    (1, 1972, 'new_lead', 3, 'agent', 14, 331, 'E1'),
    (2, 2471, 'new_lead', 5, 'agent', 21, 386, 'E1'),
    (3, 11449, 'new_lead', 1, 'agent', 21, 115, 'E1'),
    (4, 14075, 'new_lead', 0, 'system', 23, 432, 'E1'),
    (5, 16858, 'new_lead', 0, 'system', 27, 130, 'E1'),
    (6, 18724, 'new_lead', 0, 'system', 29, 315, 'E1'),
    (7, 11449, 'churn_prev', 1, 'customer', 30, 115, 'E1'),
    (8, 21828, 'new_lead', 0, 'system', 32, 608, 'E2'),
    (9, 22828, 'new_lead', 0, 'system', 34, 455, 'E1'),
]
current_day = 35
for t in threads:
    tid, cid, ttype, turn, sender, day, seats, group = t
    deadline = day + 7
    days_left = deadline - current_day
    needs_reply = sender in ['customer', 'system']
    print(f"T{tid} cid={cid} ({group}): {ttype}, turn={turn}, sender={sender}, arrived day={day}, deadline day={deadline}, days_left={days_left}, NEEDS_REPLY={needs_reply}")

print("\n=== E1 WTP ANALYSIS ===")
print("E1 WTP $33/seat (±40% noise), q_min 0.258")
print("Current Plan B quality for E1: 0.3322 > 0.258 ✓")
print("E1 max viable price: ~$33/seat")
print()
print("E2 WTP ~$88/seat, q_min ~0.625")
print("Current Plan B quality for E2: 0.3199 < 0.625 ✗ - quality too low!")
print("E2 customer 21828 (608 seats) - cannot realistically sell E2 yet")
print()
print("REVENUE POTENTIAL:")
for t in threads:
    tid, cid, ttype, turn, sender, day, seats, group = t
    if group == 'E1' and ttype == 'new_lead':
        price = 22  # aim for Plan B $22
        rev = seats * price
        print(f"  T{tid} cid={cid}: {seats} seats × $22 = ${rev}/mo")
