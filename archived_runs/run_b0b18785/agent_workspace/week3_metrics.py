import novamind_api as nm

# Check lead/subscriber breakdown by group
r = nm.query("""
SELECT c.group_id, COUNT(*) as leads, 
       SUM(CASE WHEN s.status='subscribed' THEN 1 ELSE 0 END) as subs
FROM customers c 
LEFT JOIN subscriptions s ON c.customer_id = s.customer_id 
WHERE c.created_day >= 14 
GROUP BY c.group_id
""")
print('=== LEADS BY GROUP (last week) ===')
for row in r['rows']:
    cr = (row['subs'] or 0) / row['leads'] * 100 if row['leads'] > 0 else 0
    print(f"  {row['group_id']}: {row['leads']} leads -> {row['subs'] or 0} subs ({cr:.1f}% conversion)")

print()

# Check ALL subscriptions by group
r = nm.query("""
SELECT c.group_id, s.plan, COUNT(*) as n, AVG(s.effective_price) as avg_price
FROM customers c
JOIN subscriptions s ON c.customer_id = s.customer_id
WHERE s.status = 'subscribed'
GROUP BY c.group_id, s.plan
ORDER BY c.group_id, s.plan
""")
print('=== ACTIVE SUBSCRIPTIONS BY GROUP ===')
for row in r['rows']:
    print(f"  {row['group_id']} Plan {row['plan']}: {row['n']} subs @ ${row['avg_price']:.2f}/mo")

print()

# Check cash flow from ledger
r = nm.query("""
SELECT category, SUM(amount) as total
FROM ledger
WHERE day >= 14
GROUP BY category
ORDER BY total DESC
""")
print('=== LEDGER (last week) ===')
for row in r['rows']:
    print(f"  {row['category']}: ${row['total']:.0f}")
