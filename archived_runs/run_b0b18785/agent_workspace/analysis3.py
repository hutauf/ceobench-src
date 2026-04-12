import novamind_api as nm

# Check group details for enterprise threads
print("--- Enterprise Customer Groups ---")
r = nm.query("""SELECT c.customer_id, c.group_id, c.customer_type, c.email
FROM customers c 
WHERE c.customer_id IN (21828, 30370, 22828, 27076, 18724, 28061, 28062, 29322, 25899, 29324, 25898, 40186, 40181, 38861, 37637, 37643, 41486)
ORDER BY c.group_id""")
for row in r['rows']:
    print(f"  Cust {row['customer_id']} ({row['group_id']}, {row['customer_type']})")

# Check subscription for existing enterprise subs
print("\n--- Enterprise Subscriptions (full detail) ---")
r2 = nm.query("""SELECT s.customer_id, c.group_id, s.plan, s.effective_price, s.seat_count,
    s.seat_count * s.effective_price as mrr
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id 
WHERE s.status='subscribed' AND c.group_id LIKE 'E%'
ORDER BY mrr DESC""")
for row in r2['rows']:
    print(f"  Cust {row['customer_id']} ({row['group_id']}): {row['seat_count']} seats @ ${row['effective_price']:.2f} Plan {row['plan']} = ${row['mrr']:,.0f}/mo")

# Check which customer IDs are from new threads this week (day 51-56)
print("\n--- New Enterprise Threads This Week (day 51-56, turn=0) ---")
r3 = nm.query("""SELECT et.thread_id, et.customer_id, c.group_id, et.seat_count, et.day
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0 AND et.turn_number=0 AND et.day >= 51
ORDER BY et.day ASC, et.seat_count DESC""")
for row in r3['rows']:
    print(f"  Thread {row['thread_id']}: Cust {row['customer_id']} ({row['group_id']}), {row['seat_count']} seats, day={row['day']}")

# Check market overview for group quality thresholds
print("\n--- Market Overview ---")
overview = nm.market.get_market_overview()
for group_id, info in overview.get('known_groups', {}).items():
    q_min = info.get('q_min', 'N/A')
    wtp = info.get('price_max', 'N/A')
    cap = info.get('market_cap', 'N/A')
    print(f"  {group_id}: q_min={q_min}, wtp={wtp}, market_cap={cap}")
