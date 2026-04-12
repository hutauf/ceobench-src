import novamind_api as nm

print("=== LEAD CONVERSION BY GROUP (last 14 days) ===")
r = nm.query("""
SELECT c.group_id, COUNT(*) as leads, 
       SUM(CASE WHEN s.status='subscribed' THEN 1 ELSE 0 END) as subs
FROM customers c 
LEFT JOIN subscriptions s ON c.customer_id = s.customer_id 
WHERE c.created_day >= 21
GROUP BY c.group_id
ORDER BY c.group_id
""")
for row in r['rows']:
    pct = row['subs']/row['leads']*100 if row['leads'] > 0 else 0
    print(f"{row['group_id']}: {row['leads']} leads, {row['subs']} subs ({pct:.1f}%)")

print("\n=== MRR BREAKDOWN ===")
r = nm.query("""
SELECT c.group_id, s.plan, COUNT(*) as n, 
       SUM(s.effective_price) as mrr,
       SUM(CASE WHEN c.customer_type='large' THEN s.effective_price * s.seat_count ELSE s.effective_price END) as total_mrr
FROM subscriptions s
JOIN customers c ON s.customer_id = c.customer_id
WHERE s.status='subscribed'
GROUP BY c.group_id, s.plan
ORDER BY c.group_id, s.plan
""")
for row in r['rows']:
    print(row)

print("\n=== OPEN ISSUES BY GROUP + DAYS ===")
r = nm.query("""
SELECT group_id, 
       COUNT(*) as total_open,
       AVG(days_open) as avg_days,
       MAX(days_open) as max_days
FROM issues WHERE status='open'
GROUP BY group_id
""")
for row in r['rows']:
    print(row)

print("\n=== FINANCIAL SUMMARY ===")
print("Cash: $241,771")
print("MRR: $46,403 (incl enterprise)")
print("Daily costs: $215 cap + $530 ops (300+30 = but wait...)")
r = nm.query("SELECT category, SUM(amount)/7 as daily_avg FROM ledger WHERE day >= 28 GROUP BY category ORDER BY daily_avg")
for row in r['rows']:
    print(f"  {row['category']}: ${row['daily_avg']:.0f}/day")

print("\n=== S3 SUBSCRIBERS (network effect pipeline) ===")
r = nm.query("SELECT plan, COUNT(*) as n, AVG(effective_price) as avg_price FROM subscriptions WHERE customer_id IN (SELECT customer_id FROM customers WHERE group_id='S3') AND status='subscribed' GROUP BY plan")
for row in r['rows']:
    print(row)
