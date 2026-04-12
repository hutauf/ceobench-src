import novamind_api as nm

print("=== LATEST MESSAGE PER THREAD (open) ===")
r = nm.query("""
SELECT thread_id, customer_id, thread_type, turn_number, sender, message_text, day, seat_count
FROM enterprise_turns
WHERE closed = 0
AND turn_number = (
    SELECT MAX(turn_number) FROM enterprise_turns et2 WHERE et2.thread_id = enterprise_turns.thread_id AND et2.closed = 0
)
ORDER BY thread_id
""")
for row in r['rows']:
    print(f"Thread {row['thread_id']}: cid={row['customer_id']}, type={row['thread_type']}, turn={row['turn_number']}, sender={row['sender']}, day={row['day']}, seats={row['seat_count']}")
    if row['message_text']:
        print(f"  Msg: {row['message_text'][:200]}")

print("\n=== ENTERPRISE CUSTOMER GROUPS ===")
r = nm.query("""
SELECT DISTINCT et.customer_id, c.group_id, c.company_size_descriptor, c.company_primary_concern
FROM enterprise_turns et
JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed = 0
ORDER BY et.customer_id
""")
for row in r['rows']:
    print(row)

print("\n=== ACTIVE ENTERPRISE SUBSCRIPTIONS ===")
r = nm.query("""
SELECT s.customer_id, c.group_id, s.plan, s.effective_price, s.seat_count, s.status
FROM subscriptions s
JOIN customers c ON s.customer_id = c.customer_id
WHERE c.customer_type = 'enterprise' AND s.status = 'subscribed'
""")
for row in r['rows']:
    print(row)
