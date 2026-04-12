import novamind_api as nm

# Market overview
print("--- Market Overview ---")
overview = nm.market.get_market_overview()
print(f"Keys: {list(overview.keys())}")
print(f"known_groups type: {type(overview['known_groups'])}")
known = overview['known_groups']
if isinstance(known, list):
    for g in known:
        print(f"  {g}")
elif isinstance(known, dict):
    for gid, info in known.items():
        print(f"  {gid}: {info}")

# Check enterprise subscriptions with seat_count
print("\n--- Enterprise Subs with Seats ---")
r = nm.query("""SELECT customer_id, plan, effective_price, seat_count,
    seat_count * effective_price as mrr
FROM subscriptions 
WHERE status='subscribed' AND customer_id IN (21828, 30370, 22828, 2471)""")
for row in r['rows']:
    print(f"  {row}")

# Check all threads with customer data 
print("\n--- Thread Summary (active, non-stale) ---")
r2 = nm.query("""SELECT et.thread_id, et.customer_id, c.group_id, et.thread_type, 
    et.turn_number, et.sender, et.day, et.seat_count, et.is_final_turn
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0 
AND et.turn_number = (SELECT MAX(turn_number) FROM enterprise_turns et2 WHERE et2.thread_id = et.thread_id AND et2.closed=0)
AND et.day >= 43
ORDER BY et.day ASC, et.seat_count DESC
LIMIT 50""")
for row in r2['rows']:
    print(f"  T{row['thread_id']} Cust {row['customer_id']} ({row['group_id']}) {row['thread_type']} turn={row['turn_number']} sender={row['sender']} day={row['day']} seats={row['seat_count']} final={row['is_final_turn']}")
