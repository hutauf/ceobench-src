import novamind_api as nm

print("=== WEEK 8 ANALYSIS ===")
print(f"Current day: {nm.vars.current_day}")
print(f"Cash: from dashboard $194,332")

# 1. Revenue breakdown by group
print("\n--- Revenue by Group ---")
r = nm.query("""SELECT c.group_id, s.plan, COUNT(*) as n, 
    SUM(s.seat_count) as seats,
    SUM(s.seat_count * s.effective_price) as total_revenue
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id 
WHERE s.status='subscribed'
GROUP BY c.group_id, s.plan ORDER BY c.group_id, s.plan""")
for row in r['rows']:
    print(f"  {row['group_id']} Plan {row['plan']}: {row['n']} subs, {row['seats']} seats, ${row['total_revenue']:,.0f}/mo")

# 2. Total MRR
r2 = nm.query("SELECT SUM(seat_count * effective_price) as mrr FROM subscriptions WHERE status='subscribed'")
print(f"\nTotal MRR: ${r2['rows'][0]['mrr']:,.0f}")

# 3. Enterprise details
print("\n--- Enterprise Subscriptions ---")
r3 = nm.query("""SELECT c.customer_id, c.group_id, s.plan, s.seat_count, s.effective_price, 
    s.seat_count * s.effective_price as monthly_rev
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id 
WHERE s.status='subscribed' AND c.customer_type='large'
ORDER BY monthly_rev DESC""")
if r3['rows']:
    for row in r3['rows']:
        print(f"  Cust {row['customer_id']} ({row['group_id']}): {row.get('seat_count','?')} seats @ ${row.get('effective_price','?')}/seat Plan {row['plan']} = ${row.get('monthly_rev',0):,.0f}/mo")
else:
    # Maybe customer_type is different - let's check
    r3b = nm.query("SELECT DISTINCT customer_type FROM customers LIMIT 5")
    print(f"  No large customers found. Types: {r3b['rows']}")
    # Check by group
    r3c = nm.query("""SELECT c.customer_id, c.group_id, c.customer_type, s.plan, s.effective_price
    FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id 
    WHERE s.status='subscribed' AND c.group_id LIKE 'E%' LIMIT 10""")
    for row in r3c['rows']:
        print(f"  Cust {row['customer_id']} ({row['group_id']}, type={row['customer_type']}): Plan {row['plan']} @ ${row['effective_price']}")

# 4. Enterprise turns - CRITICAL: respond within 1 week
print("\n--- Open Enterprise Threads (closed=0, latest turn) ---")
r4 = nm.query("""SELECT thread_id, customer_id, thread_type, turn_number, sender, message_text, day, seat_count
FROM enterprise_turns WHERE closed=0
AND turn_number = (SELECT MAX(turn_number) FROM enterprise_turns et2 WHERE et2.thread_id = enterprise_turns.thread_id AND et2.closed=0)
ORDER BY day ASC""")
for row in r4['rows']:
    print(f"  Thread {row['thread_id']}: Cust {row['customer_id']} ({row['thread_type']}) turn {row['turn_number']}, sender={row['sender']}, day={row['day']}, seats={row['seat_count']}")
    print(f"    Msg: {row['message_text'][:150]}")

print(f"\nTotal open threads: {len(r4['rows'])}")

# 5. Issues
print("\n--- Open Issues by Group ---")
r5 = nm.query("""SELECT group_id, COUNT(*) as n, AVG(days_open) as avg_days 
FROM issues WHERE status='open' 
GROUP BY group_id ORDER BY n DESC""")
for row in r5['rows']:
    print(f"  {row['group_id']}: {row['n']} issues, avg {row['avg_days']:.1f} days open")

r5b = nm.query("SELECT COUNT(*) as total FROM issues WHERE status='open'")
print(f"  TOTAL: {r5b['rows'][0]['total']}")

# 6. R&D status
print("\n--- R&D Projects ---")
projects = nm.research.list_research_projects()
for tier_id, tier_data in projects['tiers'].items():
    status = tier_data.get('status', 'not_started')
    if status != 'not_started':
        print(f"  {tier_id}: {status}, quality_boost={tier_data.get('quality_boost', 'N/A')}, days_remaining={tier_data.get('days_remaining', 'N/A')}")
    else:
        print(f"  {tier_id}: not started, cost=${tier_data.get('cost',0):,.0f}, est_quality={tier_data.get('mean_quality_boost','N/A')}")

# 7. Recent social posts
print("\n--- Recent Social Posts (last 7 days) ---")
posts = nm.analytics.get_social_posts(days=7, limit=20)
for p in posts[:10]:
    print(f"  [Day {p.get('day','?')}] Cust {p.get('customer_id','?')} ({p.get('group_id','?')}): {p.get('content','')[:120]}")

# 8. Cost breakdown
print("\n--- Recent Ledger (last 7 days) ---")
r6 = nm.query("""SELECT category, SUM(amount) as total 
FROM ledger WHERE day >= 50
GROUP BY category ORDER BY total ASC""")
for row in r6['rows']:
    print(f"  {row['category']}: ${row['total']:,.0f}")
