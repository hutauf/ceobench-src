import novamind_api as nm

print("=== CURRENT ACTIVE SUBS FOR ENTERPRISE CUSTOMERS ===")
r = nm.query("""
SELECT s.customer_id, s.plan, s.effective_price, s.seat_count, s.status, s.start_day, s.billing_day_mod30
FROM subscriptions s
WHERE s.customer_id IN (1972, 2471, 11449, 14075, 16858, 18724, 21828, 22828)
""")
for row in r['rows']:
    print(row)

print("\n=== OPEN THREADS SUMMARY (for agent action) ===")
print("Thread 1 (cid=1972): E1, 331 seats - last agent offer day 14, customer countered $9.30, we replied $12. Waiting customer reply. Day=14+")
print("  -> Customer HASN'T replied yet. This thread may be stale/lost")
print("Thread 4 (cid=14075): E1, 432 seats - NEW LEAD, turn 0, day 23. MUST REPLY - OVERDUE")
print("Thread 5 (cid=16858): E1, 130 seats - NEW LEAD, turn 0, day 27. MUST REPLY - OVERDUE")
print("Thread 6 (cid=18724): E1, 315 seats - NEW LEAD, turn 0, day 29. MUST REPLY NOW (deadline day 36)")
print("Thread 7 (cid=11449): E1, 115 seats - CHURN PREVENTION, customer replied day 30. CRITICAL MUST REPLY")
print("Thread 8 (cid=21828): E2, 608 seats - NEW LEAD, turn 0, day 32. MUST REPLY (deadline day 39)")
print("Thread 9 (cid=22828): E1, 455 seats - NEW LEAD, turn 0, day 34. MUST REPLY (deadline day 41)")
