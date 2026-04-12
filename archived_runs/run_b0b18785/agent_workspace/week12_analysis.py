#!/usr/bin/env python3
"""Week 12 comprehensive analysis"""
import novamind_api as nm
import json

current_day = nm.vars.current_day
print(f"=== Week 12 Analysis - Day {current_day} ===")

# 1. Cash and financials
print("\n--- FINANCIALS ---")
ledger = nm.query(f"""SELECT category, SUM(amount) as total, SUM(amount)/7.0 as daily_avg 
FROM ledger WHERE day >= {current_day - 7} 
GROUP BY category ORDER BY total DESC""")
total_rev = 0
total_cost = 0
for row in ledger['rows']:
    print(f"  {row['category']}: ${row['total']:.0f} (${row['daily_avg']:.0f}/day)")
    if row['total'] > 0:
        total_rev += row['total']
    else:
        total_cost += abs(row['total'])
print(f"  NET: ${total_rev - total_cost:.0f} (last 7 days)")

# 2. Issues status
print("\n--- ISSUES STATUS ---")
issues = nm.query("""SELECT group_id, COUNT(*) as n, AVG(days_open) as avg_days, 
    MAX(days_open) as max_days
FROM issues WHERE status='open' GROUP BY group_id ORDER BY n DESC""")
total_issues = 0
for row in issues['rows']:
    print(f"  {row['group_id']}: {row['n']} open, avg {row['avg_days']:.1f} days, max {row['max_days']:.0f} days")
    total_issues += row['n']
print(f"  TOTAL: {total_issues} open issues")

# 3. Active enterprise subscriptions  
print("\n--- ENTERPRISE SUBS ---")
ent_subs = nm.query("""SELECT s.customer_id, c.group_id, s.plan, s.seat_count, s.effective_price,
    s.seat_count * s.effective_price as monthly_rev
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
WHERE s.status='subscribed' AND s.seat_count >= 50
ORDER BY s.seat_count * s.effective_price DESC""")
total_mrr = 0
for row in ent_subs['rows']:
    monthly = row['monthly_rev']
    total_mrr += monthly
    print(f"  CID={row['customer_id']} {row['group_id']} {row['seat_count']}x{row['plan']} @ ${row['effective_price']:.2f} = ${monthly:.0f}/mo")
print(f"  ENTERPRISE MRR: ${total_mrr:.0f}/mo")

# 4. Individual subs
print("\n--- INDIVIDUAL SUBS ---")
ind_subs = nm.query("""SELECT c.group_id, s.plan, COUNT(*) as n, 
    AVG(s.effective_price) as avg_price,
    SUM(s.effective_price) as mrr
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
WHERE s.status='subscribed' AND s.seat_count < 50
GROUP BY c.group_id, s.plan ORDER BY c.group_id""")
ind_mrr = 0
for row in ind_subs['rows']:
    ind_mrr += row['mrr']
    print(f"  {row['group_id']} Plan {row['plan']}: {row['n']} subs @ avg ${row['avg_price']:.2f} = ${row['mrr']:.0f}/mo")
print(f"  INDIVIDUAL MRR: ${ind_mrr:.0f}/mo")

# 5. Open enterprise threads (what needs response)
print("\n--- ENTERPRISE THREADS (AWAITING RESPONSE) ---")
threads = nm.query("""SELECT et.customer_id, c.group_id, et.thread_type, 
    et.turn_number, et.sender, et.day, et.offer_json
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0 AND et.sender != 'agent'
ORDER BY et.day ASC""")

# Group by customer (take latest per customer)
cust_threads = {}
for t in threads['rows']:
    cid = t['customer_id']
    if cid not in cust_threads or t['turn_number'] > cust_threads[cid]['turn_number']:
        cust_threads[cid] = t

print(f"Total customers needing response: {len(cust_threads)}")
for cid, t in sorted(cust_threads.items(), key=lambda x: x[1]['day']):
    offer_str = ""
    if t['offer_json']:
        try:
            offer_data = json.loads(t['offer_json']) if isinstance(t['offer_json'], str) else t['offer_json']
            if isinstance(offer_data, dict):
                offer_str = f" offer=${offer_data.get('price', '?')}"
        except:
            pass
    urgency = "⚠️ URGENT" if (current_day - t['day']) >= 5 else ""
    print(f"  CID={cid} {t['group_id']} {t['thread_type']} turn={t['turn_number']} day={t['day']}{offer_str} {urgency}")

# 6. R&D status
print("\n--- R&D STATUS ---")
r = nm.research.list_research_projects()
for tier_info in r['tiers'][:6]:  # First 6 tiers
    status = "DONE✓" if tier_info['completed'] else ("IN PROGRESS" if tier_info['in_progress'] else "not started")
    print(f"  Tier {tier_info['tier']}: {tier_info['name']} - {status} (cost=${tier_info['cost']:.0f}, mean_quality={tier_info['mean_quality_boost']:.3f})")

# 7. Social posts
print("\n--- RECENT SOCIAL POSTS ---")
posts = nm.analytics.get_social_posts(days=7, limit=10)
for p in posts:
    print(f"  [{p.get('group_id','?')}] Day {p.get('day','?')}: {p.get('content','')[:120]}")

# 8. Quality vs thresholds
print("\n--- QUALITY ANALYSIS ---")
insights_e1 = nm.market.get_group_insights(group_id="E1")
insights_e2 = nm.market.get_group_insights(group_id="E2")
insights_s1 = nm.market.get_group_insights(group_id="S1")
print("E1 insights:", json.dumps(insights_e1, indent=2)[:500])
print("E2 insights:", json.dumps(insights_e2, indent=2)[:300])
print("S1 insights:", json.dumps(insights_s1, indent=2)[:300])

# 9. Capacity check
print("\n--- CAPACITY ---")
cost_info = nm.infrastructure.get_cost_info()
print(f"Current tier: {cost_info.get('current_tier')}")
print(f"Usage this week: 8,231,727 units")

print("\n=== ANALYSIS COMPLETE ===")
