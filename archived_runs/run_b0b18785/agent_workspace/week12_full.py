#!/usr/bin/env python3
"""Week 12 full analysis"""
import novamind_api as nm
import json

current_day = nm.vars.current_day
print(f"=== Week 12 Full Analysis - Day {current_day} ===")

# Enterprise subs
print("\n--- ENTERPRISE SUBS ---")
ent_subs = nm.query("""SELECT s.customer_id, c.group_id, s.plan, s.seat_count, s.effective_price
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
WHERE s.status='subscribed' AND c.customer_type='large'
ORDER BY (s.seat_count * s.effective_price) DESC""")
print(f"Enterprise subs count: {len(ent_subs['rows'])}")
total_ent_mrr = 0
for row in ent_subs['rows']:
    sc = row.get('seat_count', 1)
    monthly = sc * row['effective_price']
    total_ent_mrr += monthly
    print(f"  CID={row['customer_id']} {row['group_id']} {sc}x{row['plan']} @ ${row['effective_price']:.2f} = ${monthly:.0f}/mo")
print(f"ENTERPRISE MRR: ${total_ent_mrr:.0f}/mo")

# Individual subs
print("\n--- INDIVIDUAL SUBS ---")
ind_subs = nm.query("""SELECT c.group_id, s.plan, COUNT(*) as n, 
    AVG(s.effective_price) as avg_price,
    SUM(s.effective_price) as mrr
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
WHERE s.status='subscribed' AND c.customer_type='small'
GROUP BY c.group_id, s.plan ORDER BY c.group_id""")
ind_mrr = 0
for row in ind_subs['rows']:
    ind_mrr += row['mrr']
    print(f"  {row['group_id']} Plan {row['plan']}: {row['n']} subs @ avg ${row['avg_price']:.2f} = ${row['mrr']:.0f}/mo")
print(f"INDIVIDUAL MRR: ${ind_mrr:.0f}/mo")

# Open enterprise threads
print("\n--- ENTERPRISE THREADS ---")
threads = nm.query("""SELECT et.customer_id, c.group_id, et.thread_type, 
    et.turn_number, et.sender, et.day, et.offer_json, et.message_text
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0 AND et.sender != 'agent'
ORDER BY et.customer_id ASC, et.turn_number DESC""")

cust_threads = {}
for t in threads['rows']:
    cid = t['customer_id']
    if cid not in cust_threads:
        cust_threads[cid] = t

print(f"Customers needing response: {len(cust_threads)}")
for cid, t in sorted(cust_threads.items(), key=lambda x: x[1]['day']):
    offer_str = ""
    if t['offer_json']:
        try:
            offer_data = json.loads(t['offer_json']) if isinstance(t['offer_json'], str) else t['offer_json']
            if isinstance(offer_data, dict):
                price = offer_data.get('price', offer_data.get('price_per_seat', '?'))
                offer_str = f" offer_price=${price}"
        except:
            offer_str = f" raw={str(t['offer_json'])[:40]}"
    days_old = current_day - t['day']
    urgency = " ⚠️URGENT(>5d)" if days_old >= 5 else (" ⚠️WARNING(3d)" if days_old >= 3 else "")
    print(f"  CID={cid} {t['group_id']} {t['thread_type']} turn={t['turn_number']} day={t['day']} age={days_old}d{offer_str}{urgency}")
    if t.get('message_text'):
        print(f"    msg: {t['message_text'][:100]}")

# R&D
print("\n--- R&D STATUS ---")
r = nm.research.list_research_projects()
for tier_info in r['tiers'][:8]:
    status = "DONE✓" if tier_info['completed'] else ("IN PROGRESS" if tier_info['in_progress'] else "not started")
    print(f"  T{tier_info['tier']}: {tier_info['name']} - {status} cost=${tier_info['cost']:.0f} qual={tier_info['mean_quality_boost']:.3f} total_boost={tier_info['total_quality_boost']:.4f}")

# Social posts
print("\n--- SOCIAL POSTS (last 7 days) ---")
posts = nm.analytics.get_social_posts(days=7, limit=15)
for p in posts:
    print(f"  [{p.get('group_id','?')}] Day {p.get('day','?')}: {p.get('content','')[:130]}")

# Costs breakdown
print("\n--- COST BREAKDOWN (last 7 days) ---")
ledger = nm.query(f"""SELECT category, SUM(amount) as total, SUM(amount)/7.0 as daily_avg 
FROM ledger WHERE day >= {current_day - 7} 
GROUP BY category ORDER BY total""")
for row in ledger['rows']:
    print(f"  {row['category']}: ${row['total']:.0f} (${row['daily_avg']:.0f}/day)")
