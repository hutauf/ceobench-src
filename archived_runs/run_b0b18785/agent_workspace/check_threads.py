import novamind_api as nm

# Check if threads 1-5 are really still open or just showing as closed=0
print("=== ALL ENTERPRISE THREADS - COMPLETE STATUS ===")
r = nm.query("""
SELECT thread_id, customer_id, turn_number, sender, day, seat_count, closed, close_reason
FROM enterprise_turns
ORDER BY thread_id, turn_number
""")
for row in r['rows']:
    print(row)

print("\n=== CURRENT ACTIVE SUBS FOR ENTERPRISE CUSTOMERS ===")
r = nm.query("""
SELECT s.customer_id, s.plan, s.effective_price, s.seat_count, s.status, s.billing_day
FROM subscriptions s
WHERE s.customer_id IN (1972, 2471, 11449, 14075, 16858, 18724, 21828, 22828)
""")
for row in r['rows']:
    print(row)
