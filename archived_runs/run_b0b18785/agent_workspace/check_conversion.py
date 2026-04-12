import novamind_api as nm

# Check which plan new S3 subscribers are choosing
print("=== S3 PLAN SELECTION (recent) ===")
r = nm.query("""
SELECT s.plan, COUNT(*) as n, AVG(s.effective_price) as avg_price
FROM subscriptions s
JOIN customers c ON s.customer_id=c.customer_id
WHERE c.group_id='S3' AND s.status='subscribed' AND s.start_day >= 21
GROUP BY s.plan
""")
for row in r['rows']:
    print(row)

print("\n=== S2 PLAN SELECTION (recent) ===")
r = nm.query("""
SELECT s.plan, COUNT(*) as n, AVG(s.effective_price) as avg_price
FROM subscriptions s
JOIN customers c ON s.customer_id=c.customer_id
WHERE c.group_id='S2' AND s.status='subscribed' AND s.start_day >= 21
GROUP BY s.plan
""")
for row in r['rows']:
    print(row)

print("\n=== S1 PLAN SELECTION (recent) ===")
r = nm.query("""
SELECT s.plan, COUNT(*) as n, AVG(s.effective_price) as avg_price
FROM subscriptions s
JOIN customers c ON s.customer_id=c.customer_id
WHERE c.group_id='S1' AND s.status='subscribed' AND s.start_day >= 21
GROUP BY s.plan
""")
for row in r['rows']:
    print(row)

print("\n=== GROWTH RATE ANALYSIS ===")
r = nm.query("""
SELECT c.group_id, 
       SUM(CASE WHEN s.start_day >= 28 THEN 1 ELSE 0 END) as subs_week5,
       SUM(CASE WHEN s.start_day >= 21 AND s.start_day < 28 THEN 1 ELSE 0 END) as subs_week4
FROM subscriptions s
JOIN customers c ON s.customer_id=c.customer_id
WHERE s.status='subscribed'
GROUP BY c.group_id
""")
for row in r['rows']:
    print(row)

print("\n=== PLAN C SUBSCRIBERS ===")
r = nm.query("""
SELECT c.group_id, COUNT(*) as n FROM subscriptions s
JOIN customers c ON s.customer_id=c.customer_id
WHERE s.plan='C' AND s.status='subscribed'
GROUP BY c.group_id
""")
print(r['rows'])
