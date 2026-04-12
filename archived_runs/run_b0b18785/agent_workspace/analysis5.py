import novamind_api as nm

# Check all threads - use message_id and correct columns  
# enterprise_turns columns: message_id, customer_id, thread_type, turn_number, sender, message_text, offer_json, day, email, seat_count, closed, close_reason

print("--- Thread Summary (active, day >= 43) ---")
r2 = nm.query("""SELECT et.message_id, et.customer_id, c.group_id, et.thread_type, 
    et.turn_number, et.sender, et.day, et.seat_count, et.message_text, et.offer_json
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0 
AND et.day >= 43
GROUP BY et.customer_id
HAVING et.turn_number = MAX(et.turn_number)
ORDER BY et.day ASC
LIMIT 60""")
print(f"Rows: {len(r2['rows'])}")
for row in r2['rows']:
    msg = row['message_text'][:100] if row['message_text'] else ''
    offer = row['offer_json'][:60] if row['offer_json'] else ''
    print(f"  Msg{row['message_id']} C{row['customer_id']} ({row['group_id']}) {row['thread_type']} turn={row['turn_number']} from={row['sender']} day={row['day']} seats={row['seat_count']}")
    if msg:
        print(f"    msg: '{msg}'")
    if offer:
        print(f"    offer: {offer}")
