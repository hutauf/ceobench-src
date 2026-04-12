import novamind_api as nm

day = nm.vars.current_day
print(f"=== DEEP ANALYSIS Day {day} ===\n")

# 1. Check the 4 new enterprise replies this week (day 112-119)
print("=== NEW ENTERPRISE REPLIES THIS WEEK (Days 112-119) ===")
r = nm.query("""
SELECT et.customer_id, et.thread_type, et.turn_number, et.sender, 
       et.message_text, et.offer_json, et.day, et.closed, et.close_reason, c.group_id
FROM enterprise_turns et JOIN customers c ON et.customer_id=c.customer_id
WHERE et.day >= 112
ORDER BY et.day, et.customer_id
""")
for row in r['rows']:
    print(f"  Day {row['day']} | Cust {row['customer_id']} ({row['group_id']}) | {row['thread_type']} | turn {row['turn_number']} | sender={row['sender']} | closed={row['closed']} | close_reason={row['close_reason']}")
    if row['message_text']:
        print(f"    msg: {row['message_text'][:150]}")
    if row['offer_json'] and row['offer_json'] != '{}':
        print(f"    offer: {row['offer_json']}")

# 2. Check 23656 status specifically
print("\n=== CUST 23656 (BIG E3) STATUS ===")
r = nm.query("""
SELECT s.customer_id, s.plan, s.effective_price, s.contract_end_day, s.status, s.billing_day_mod30
FROM subscriptions s WHERE s.customer_id=23656 ORDER BY s.start_day DESC LIMIT 5
""")
for row in r['rows']:
    print(f"  plan={row['plan']} price={row['effective_price']} end={row['contract_end_day']} status={row['status']} billing_mod30={row['billing_day_mod30']}")

# 3. What are these "stale" threads vs new ones
print("\n=== ALL OPEN THREADS - FRESH ONLY (day >= 105) ===")
r = nm.query("""
SELECT et.customer_id, et.thread_id, et.thread_type, et.turn_number, et.sender, 
       et.message_text, et.offer_json, et.day, et.closed, c.group_id
FROM enterprise_turns et JOIN customers c ON et.customer_id=c.customer_id
WHERE et.closed=0 AND et.day >= 105
ORDER BY et.customer_id, et.day, et.turn_number
""")
for row in r['rows']:
    print(f"  Day {row['day']} | Cust {row['customer_id']} ({row['group_id']}) tid={row['thread_id']} | {row['thread_type']} | turn {row['turn_number']} | {row['sender']}")
    if row['message_text']:
        print(f"    msg: {row['message_text'][:120]}")
    if row['offer_json'] and row['offer_json'] != '{}':
        print(f"    offer: {row['offer_json']}")

# 4. What did I send in week 16 (day 112)?
print("\n=== MY SENT OFFERS (Days 112-119, agent turns) ===")
r = nm.query("""
SELECT et.customer_id, et.thread_type, et.turn_number, et.sender, 
       et.message_text, et.offer_json, et.day, et.closed, et.close_reason, c.group_id
FROM enterprise_turns et JOIN customers c ON et.customer_id=c.customer_id
WHERE et.day >= 112 AND et.sender = 'agent'
ORDER BY et.day, et.customer_id
""")
for row in r['rows']:
    print(f"  Day {row['day']} | Cust {row['customer_id']} ({row['group_id']}) | {row['thread_type']} | turn {row['turn_number']} | closed={row['closed']} | close_reason={row['close_reason']}")
    print(f"    offer: {row['offer_json']}")

# 5. Social posts this week
print("\n=== SOCIAL POSTS (last 7 days) ===")
posts = nm.analytics.get_social_posts(days=7, limit=20)
for p in posts['posts']:
    print(f"  Day {p.get('day','?')} | cust {p.get('customer_id','?')} ({p.get('group_id','?')}) | viral={p.get('viral',False)}")
    print(f"    {p.get('content','')[:120]}")
