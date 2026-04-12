import novamind_api as nm

# Check subscription for existing enterprise subs
print("--- Enterprise Subscriptions (full detail) ---")
r2 = nm.query("""SELECT s.customer_id, c.group_id, s.plan, s.effective_price,
    s.effective_price as mrr_per_unit
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id 
WHERE s.status='subscribed' AND c.group_id LIKE 'E%'
ORDER BY mrr_per_unit DESC""")
print(f"Columns: {list(r2['rows'][0].keys()) if r2['rows'] else 'none'}")
for row in r2['rows']:
    print(f"  {row}")

# Check subscriptions table schema
print("\n--- Subscriptions columns ---")
r3 = nm.query("SELECT * FROM subscriptions LIMIT 1")
if r3['rows']:
    print(f"  Columns: {list(r3['rows'][0].keys())}")
    print(f"  Row: {r3['rows'][0]}")

# Market overview
print("\n--- Market Overview ---")
overview = nm.market.get_market_overview()
print(f"Keys: {list(overview.keys())}")
for group_id, info in overview.get('known_groups', {}).items():
    print(f"  {group_id}: {info}")
