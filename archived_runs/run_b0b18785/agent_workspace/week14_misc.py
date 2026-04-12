import novamind_api as nm
import json

day = nm.vars.current_day

# Handle already-subscribed customers with open new_lead threads (upsell opportunity)
threads = nm.query("""SELECT et.customer_id, c.group_id, et.thread_type, 
    et.turn_number, et.sender, et.day, et.offer_json
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0 AND et.sender != 'agent' AND et.thread_type='new_lead'
ORDER BY et.customer_id ASC, et.turn_number DESC""")

cust_threads = {}
for t in threads['rows']:
    cid = t['customer_id']
    if cid not in cust_threads:
        cust_threads[cid] = t

subs = nm.query("SELECT customer_id, plan, seat_count, effective_price FROM subscriptions WHERE status='subscribed' AND seat_count >= 10")
sub_map = {r['customer_id']: r for r in subs['rows']}

# Already subscribed customers with open new_lead threads  
already_subbed_threads = {cid: t for cid, t in cust_threads.items() 
                          if cid in sub_map and t['day'] >= day - 6}

print(f"Already-subscribed with recent new_lead threads: {len(already_subbed_threads)}")
for cid, t in list(already_subbed_threads.items())[:5]:
    sub = sub_map[cid]
    print(f"  CID={cid} {t['group_id']} Plan{sub['plan']} {sub['seat_count']}seats @${sub['effective_price']:.2f}")

# For subscribed customers, send their current plan price as deal (confirm/renew)
upsell_deals = []
for cid, t in already_subbed_threads.items():
    sub = sub_map.get(cid)
    if sub:
        plan = sub['plan']
        price = sub['effective_price']
        # Offer same or slight increase  
        upsell_deals.append([cid, [[plan, price]]])

if upsell_deals:
    print(f"\nSending {len(upsell_deals)} renewal deals for existing subs...")
    result = nm.enterprise.send_enterprise_deal(deals=upsell_deals)
    success = sum(1 for r in result['results'] if r.get('success'))
    print(f"Success: {success}/{len(upsell_deals)}")

# Social media check
print("\n--- Social Posts (last 14 days) ---")
posts = nm.analytics.get_social_posts(days=14, limit=20)
for p in posts.get('posts', [])[:15]:
    print(f"  [Day {p.get('day','?')}] {p.get('customer_id','anon')}: {p.get('content','')[:120]}")

