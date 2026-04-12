import novamind_api as nm

print("=== OPEN ISSUES DETAIL ===")
r = nm.query("""
SELECT group_id, status, 
       COUNT(*) as n,
       AVG(days_open) as avg_days,
       SUM(CASE WHEN days_open > 7 THEN 1 ELSE 0 END) as stale_7plus,
       SUM(CASE WHEN days_open > 14 THEN 1 ELSE 0 END) as stale_14plus
FROM issues WHERE status='open'
GROUP BY group_id, status
""")
for row in r['rows']:
    print(row)

print("\n=== ISSUE RESOLUTION RATE ===")
r = nm.query("""
SELECT group_id, 
       SUM(CASE WHEN status='resolved' THEN 1 ELSE 0 END) as resolved,
       SUM(CASE WHEN status='open' THEN 1 ELSE 0 END) as open_now,
       COUNT(*) as total
FROM issues
WHERE open_day >= 21
GROUP BY group_id
""")
for row in r['rows']:
    print(row)

print("\n=== SATISFACTION RISK ANALYSIS ===")
print("534 S1 issues open, avg 4.3 days")
print("Issues > 7 days are causing SEVERE satisfaction damage")
print("Each unresolved issue can cause churn + negative social posts")
print()
print("CURRENT OPS SPENDING: $600/day base + $150 S1 + $50 S3 = $800/day")
print("Is this enough?")
print()
print("Recommendation: Check if ops spend needs to increase more")

print("\n=== SOCIAL POSTS FOR REPUTATION ===")
posts = nm.analytics.get_social_posts(days=14, limit=20)
neg_keywords = ['slow', 'broken', 'quota', 'issue', 'problem', 'poor', 'terrible', 'bad', 'wait', 'queue']
pos_keywords = ['great', 'amazing', 'love', 'excellent', 'fast', 'awesome', 'helpful', 'good']
for p in posts['posts']:
    content = p.get('content', '').lower()
    is_neg = any(k in content for k in neg_keywords)
    is_pos = any(k in content for k in pos_keywords)
    sentiment = "NEG" if is_neg else ("POS" if is_pos else "NEU")
    print(f"Day {p.get('day')}: [{sentiment}] {p.get('content','')[:120]}")
