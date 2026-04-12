import novamind_api as nm

# Get all enterprise threads with latest turn
r = nm.query('''SELECT et.customer_id, c.group_id, MAX(et.turn_number) as max_turn,
    MAX(et.day) as last_day
FROM enterprise_turns et 
JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0 
GROUP BY et.customer_id
ORDER BY c.group_id, et.customer_id''')

print(f'Total open threads: {len(r["rows"])}')

# Get subscriptions for enterprise customers
subs = nm.query('''SELECT s.customer_id, s.seat_count, s.plan, s.effective_price
FROM subscriptions s
WHERE s.status='subscribed' AND s.seat_count > 1''')
sub_dict = {row['customer_id']: row for row in subs['rows']}

# Get latest message for each thread (customer messages need replies)
latest = nm.query('''SELECT et.customer_id, c.group_id, et.turn_number, et.sender, et.thread_type,
    et.day, et.message_text, et.offer_json
FROM enterprise_turns et
JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0
ORDER BY et.customer_id, et.turn_number DESC''')

# Group by customer_id, take latest
latest_by_cust = {}
for row in latest['rows']:
    cid = row['customer_id']
    if cid not in latest_by_cust:
        latest_by_cust[cid] = row

print('\n=== CUSTOMER REPLIES NEEDING OUR RESPONSE ===')
needs_response = []
for cid, row in sorted(latest_by_cust.items()):
    if row['sender'] == 'customer':
        sub = sub_dict.get(cid, {})
        seats = sub.get('seat_count', '?')
        plan = sub.get('plan', 'LEAD')
        price = sub.get('effective_price', '?')
        offer = row.get('offer_json', '')
        print(f"ID:{cid} Grp:{row['group_id']} Type:{row['thread_type']} T{row['turn_number']} Day:{row['day']} | Sub:{plan}@${price} seats:{seats}")
        print(f"  Counter: {offer}")
        needs_response.append((cid, row))

print(f'\n=== NEW LEADS (Turn 0, need first offer) ===')
new_leads = []
for cid, row in sorted(latest_by_cust.items()):
    if row['sender'] == 'system' and row['turn_number'] == 0:
        print(f"ID:{cid} Grp:{row['group_id']} Day:{row['day']}")
        new_leads.append((cid, row))

print(f'\nCustomer replies needing response: {len(needs_response)}')
print(f'New leads needing first offer: {len(new_leads)}')
