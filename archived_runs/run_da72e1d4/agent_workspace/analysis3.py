import novamind_api as nm

day = nm.vars.current_day
print(f"=== ADDITIONAL ANALYSIS Day {day} ===\n")

# Check 23656 - contract ended day 118, still "subscribed"? 
# It seems the renegotiation offer I sent didn't get a customer reply yet
# The contract_end=118 but today is 119 - has it auto-renewed or is it about to cancel?
print("=== CUST 23656 ALL THREADS ===")
r = nm.query("""
SELECT et.message_id, et.thread_id, et.thread_type, et.turn_number, et.sender, 
       et.message_text, et.offer_json, et.day, et.closed, et.close_reason
FROM enterprise_turns et
WHERE et.customer_id=23656
ORDER BY et.day, et.turn_number
""")
for row in r['rows']:
    print(f"  Day {row['day']} | tid={row['thread_id']} | {row['thread_type']} | turn {row['turn_number']} | {row['sender']} | closed={row['closed']} | close_reason={row['close_reason']}")
    if row['message_text']:
        print(f"    msg: {row['message_text'][:150]}")
    if row['offer_json'] and row['offer_json'] != '{}':
        print(f"    offer: {row['offer_json']}")

# Check 32405 status - was open thread with no reply
print("\n=== CUST 32405 STATUS ===")
r = nm.query("""
SELECT s.customer_id, s.plan, s.effective_price, s.contract_end_day, s.status, s.start_day
FROM subscriptions s WHERE s.customer_id=32405 ORDER BY s.start_day DESC LIMIT 3
""")
for row in r['rows']:
    print(f"  plan={row['plan']} price={row['effective_price']} end={row['contract_end_day']} status={row['status']} start={row['start_day']}")

# Check if any new enterprise leads came in
print("\n=== ALL OPEN THREADS (not closed) ===")
r = nm.query("""
SELECT DISTINCT et.customer_id, et.thread_type, MAX(et.turn_number) as max_turn, 
       MAX(et.day) as last_day, c.group_id,
       s.status as sub_status, s.contract_end_day
FROM enterprise_turns et 
JOIN customers c ON et.customer_id=c.customer_id
LEFT JOIN subscriptions s ON s.customer_id=et.customer_id AND s.status='subscribed'
WHERE et.closed=0
GROUP BY et.customer_id, et.thread_type
ORDER BY last_day DESC
""")
for row in r['rows']:
    print(f"  Cust {row['customer_id']} ({row['group_id']}) | {row['thread_type']} | max_turn={row['max_turn']} | last_day={row['last_day']} | sub_status={row['sub_status']} | contract_end={row['contract_end_day']}")

# What is my quality now vs q_min estimates?
print("\n=== MARKET OVERVIEW ===")
overview = nm.market.get_market_overview()
for seg in overview.get('segments', []):
    gid = seg.get('group_id', '')
    if gid in ['S1', 'S2', 'S3', 'E1', 'E2', 'E3']:
        print(f"  {gid}: subscribers={seg.get('subscribers',0)} cap={seg.get('market_cap',0)} info_level={seg.get('info_level',0)} q_min_est={seg.get('q_min_estimate','?')}")
