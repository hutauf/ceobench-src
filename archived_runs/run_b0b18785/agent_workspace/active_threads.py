import novamind_api as nm

# Get threads we SUCCESSFULLY responded to (day 50+)
print("--- Successfully sent deals this session ---")
r = nm.query("""SELECT et.message_id, et.customer_id, c.group_id, et.thread_type,
    et.turn_number, et.sender, et.day, et.message_text, et.offer_json
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0 AND et.day >= 50
GROUP BY et.customer_id
HAVING et.turn_number = MAX(et.turn_number)
ORDER BY et.sender, et.day DESC""")
print(f"Active threads with responses: {len(r['rows'])}")
for row in r['rows']:
    offer = str(row['offer_json'])[:80] if row['offer_json'] else ''
    msg = row['message_text'][:80] if row['message_text'] else ''
    print(f"  C{row['customer_id']} ({row['group_id']}) {row['thread_type']} turn={row['turn_number']} sender={row['sender']} day={row['day']}")
    if msg:
        print(f"    msg: {msg}")
    if offer and offer != '{}':
        print(f"    offer: {offer}")

# Check 18724 E1 - we sent counter this session
print("\n--- 18724 (E1) thread detail ---")
r2 = nm.query("""SELECT message_id, turn_number, sender, day, message_text, offer_json
FROM enterprise_turns WHERE customer_id=18724 AND closed=0
ORDER BY turn_number ASC""")
for row in r2['rows']:
    print(f"  Turn {row['turn_number']}: sender={row['sender']}, day={row['day']}")
    if row['message_text']:
        print(f"    {row['message_text'][:100]}")
    if row['offer_json'] and row['offer_json'] != '{}':
        print(f"    offer: {row['offer_json']}")

print("\n--- Subscription count by group ---")
r3 = nm.query("""SELECT c.group_id, s.plan, COUNT(*) as n
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
WHERE s.status = 'subscribed'
GROUP BY c.group_id, s.plan ORDER BY c.group_id, s.plan""")
for row in r3['rows']:
    print(f"  {row['group_id']} Plan {row['plan']}: {row['n']} subs")
