import novamind_api as nm

# Get full enterprise customer details for all open threads
print("=== ENTERPRISE CUSTOMER DETAILS ===")
r = nm.query("""
SELECT DISTINCT et.customer_id, et.seat_count, et.thread_type, et.thread_id,
       c.group_id, c.budget_per_seat
FROM enterprise_turns et
JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed = 0
ORDER BY et.customer_id
""")
for row in r['rows']:
    print(row)

print("\n=== LATEST MESSAGE PER THREAD ===")
r = nm.query("""
SELECT et.thread_id, et.customer_id, et.thread_type, 
       MAX(et.turn_number) as max_turn,
       et.seat_count
FROM enterprise_turns et
WHERE et.closed = 0
GROUP BY et.thread_id, et.customer_id, et.thread_type, et.seat_count
ORDER BY et.thread_id
""")
for row in r['rows']:
    print(row)

print("\n=== THREAD STATUS SUMMARY ===")
# Get the latest message for each thread
r = nm.query("""
SELECT thread_id, customer_id, thread_type, turn_number, sender, message_text, day, seat_count
FROM enterprise_turns
WHERE closed = 0
AND (thread_id, turn_number) IN (
    SELECT thread_id, MAX(turn_number) FROM enterprise_turns WHERE closed=0 GROUP BY thread_id
)
ORDER BY thread_id
""")
for row in r['rows']:
    print(f"Thread {row['thread_id']}: cid={row['customer_id']}, type={row['thread_type']}, turn={row['turn_number']}, sender={row['sender']}, day={row['day']}, seats={row['seat_count']}")
    if row['message_text']:
        print(f"  Message: {row['message_text'][:150]}")

print("\n=== CURRENT QUALITY ===")
print("E1 q_min estimate: 0.258 (±40% noise from info level 2)")
print("Plan A (T2=0.75x): (0.20 + 0.1199 + 0.0124) * 0.75 = 0.2492")
print("Plan B (T4=1.00x): (0.20 + 0.1199 + 0.0124) * 1.00 = 0.3322")
print("Plan B > E1 q_min - GOOD for enterprise deals!")
print("Current E1 subscribers: 2 seats @ Plan B $15")
