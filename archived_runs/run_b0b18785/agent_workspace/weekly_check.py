import novamind_api as nm

print("=== ENTERPRISE TURNS (open) ===")
r = nm.query("SELECT * FROM enterprise_turns WHERE closed=0 ORDER BY day DESC LIMIT 20")
for row in r['rows']:
    print(row)

print("\n=== R&D STATUS ===")
projects = nm.research.list_research_projects()
for p in projects['tiers']:
    print(p)

print("\n=== SUBSCRIPTIONS BY GROUP + PLAN ===")
r = nm.query("SELECT c.group_id, s.plan, COUNT(*) as n, AVG(s.effective_price) as avg_price FROM subscriptions s JOIN customers c ON s.customer_id=c.customer_id WHERE s.status='subscribed' GROUP BY c.group_id, s.plan ORDER BY c.group_id, s.plan")
for row in r['rows']:
    print(row)

print("\n=== RECENT LEDGER (last 7 days) ===")
r = nm.query("SELECT category, SUM(amount) as total FROM ledger WHERE day >= 28 GROUP BY category ORDER BY total DESC")
for row in r['rows']:
    print(row)

print("\n=== ISSUES SUMMARY ===")
r = nm.query("SELECT group_id, COUNT(*) as n FROM issues WHERE status='open' GROUP BY group_id ORDER BY n DESC")
for row in r['rows']:
    print(row)

print("\n=== SOCIAL POSTS (last 7 days) ===")
posts = nm.analytics.get_social_posts(days=7, limit=10)
for p in posts['posts'][:5]:
    print(f"Day {p.get('day')}: {p.get('content','')[:100]}")

print("\n=== CURRENT DAY ===")
print(f"Day: {nm.vars.current_day}")
