import novamind_api as nm

day = nm.vars.current_day
print(f"=== WEEK 17 CHECK (Day {day}) ===\n")

# 1. Enterprise threads - pending responses
print("=== ENTERPRISE THREADS (pending) ===")
r = nm.query("""
SELECT et.customer_id, et.thread_type, et.turn_number, et.sender, 
       et.message_text, et.offer_json, et.day, et.closed, c.group_id
FROM enterprise_turns et JOIN customers c ON et.customer_id=c.customer_id
WHERE et.closed=0 AND et.sender IN ('customer', 'system') AND et.turn_number >= 1
ORDER BY et.day DESC LIMIT 30
""")
for row in r['rows']:
    print(f"  Cust {row['customer_id']} ({row['group_id']}) | {row['thread_type']} | turn {row['turn_number']} | day {row['day']} | {row['sender']}")
    print(f"    msg: {row['message_text'][:120] if row['message_text'] else 'N/A'}")
    print(f"    offer: {row['offer_json']}")

# 2. Active enterprise subscriptions
print("\n=== ACTIVE ENTERPRISE SUBS ===")
r = nm.query("""
SELECT s.customer_id, s.plan, s.effective_price, s.contract_end_day, s.billing_day_mod30, c.group_id
FROM subscriptions s JOIN customers c ON s.customer_id=c.customer_id
WHERE s.status='subscribed' AND c.customer_type='large'
ORDER BY s.contract_end_day
""")
for row in r['rows']:
    print(f"  Cust {row['customer_id']} ({row['group_id']}) plan={row['plan']} price={row['effective_price']} contract_end={row['contract_end_day']} billing_mod30={row['billing_day_mod30']}")

# 3. Individual sub counts
print("\n=== INDIVIDUAL SUBS BY GROUP ===")
r = nm.query("""
SELECT c.group_id, COUNT(*) as n, AVG(s.effective_price) as avg_price
FROM subscriptions s JOIN customers c ON s.customer_id=c.customer_id
WHERE s.status='subscribed' AND c.customer_type='small'
GROUP BY c.group_id
""")
for row in r['rows']:
    print(f"  {row['group_id']}: {row['n']} subs @ avg ${row['avg_price']:.2f}")

# 4. Lead conversions this week
print("\n=== LEAD CONVERSIONS (last 7 days) ===")
r = nm.query(f"""
SELECT s.status, c.group_id, COUNT(*) as n
FROM subscriptions s JOIN customers c ON s.customer_id=c.customer_id
WHERE s.start_day >= {day-7}
GROUP BY s.status, c.group_id
ORDER BY s.status, c.group_id
""")
for row in r['rows']:
    print(f"  {row['status']} | {row['group_id']}: {row['n']}")

# 5. Issues
print("\n=== OPEN ISSUES BY GROUP ===")
r = nm.query("""
SELECT group_id, COUNT(*) as n, AVG(days_open) as avg_days
FROM issues WHERE status='open' GROUP BY group_id ORDER BY n DESC
""")
for row in r['rows']:
    print(f"  {row['group_id']}: {row['n']} issues, avg {row['avg_days']:.1f} days open")

# 6. Compute costs last 7 days
print(f"\n=== COMPUTE/CAPACITY COSTS (last 7 days) ===")
r = nm.query(f"""
SELECT day, category, SUM(amount) as total 
FROM ledger WHERE category IN ('compute','capacity','operations','development','advertising') 
AND day >= {day-7} GROUP BY day, category ORDER BY day, category
""")
for row in r['rows']:
    print(f"  Day {row['day']} | {row['category']}: ${row['total']:.0f}")

# 7. Cash flow check - recent revenue
print(f"\n=== RECENT PAYMENTS ===")
r = nm.query(f"""
SELECT day, category, SUM(amount) as total
FROM ledger WHERE day >= {day-7}
GROUP BY day, category ORDER BY day DESC
LIMIT 40
""")
for row in r['rows']:
    print(f"  Day {row['day']} | {row['category']}: ${row['total']:.0f}")
