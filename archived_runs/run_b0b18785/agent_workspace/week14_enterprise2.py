import novamind_api as nm
import json

day = nm.vars.current_day

# Get all open threads
threads = nm.query("""SELECT et.customer_id, c.group_id, et.thread_type, 
    et.turn_number, et.sender, et.day, et.offer_json, et.message_id
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0 AND et.sender != 'agent'
ORDER BY et.customer_id ASC, et.turn_number DESC""")

# Get the latest thread per customer
cust_threads = {}
for t in threads['rows']:
    cid = t['customer_id']
    if cid not in cust_threads:
        cust_threads[cid] = t

# Get current subscriptions for all enterprise customers
subs = nm.query("SELECT customer_id, plan, seat_count, effective_price FROM subscriptions WHERE status='subscribed' AND seat_count >= 10")
sub_map = {}
for r in subs['rows']:
    sub_map[r['customer_id']] = r

# Get group_id for all customers with threads
customer_groups = {}
for cid, t in cust_threads.items():
    customer_groups[cid] = t['group_id']

# Print churn_prevention threads in detail
print("=== CHURN PREVENTION THREADS ===")
churn_threads = {cid: t for cid, t in cust_threads.items() if t['thread_type'] == 'churn_prevention'}
for cid, t in churn_threads.items():
    sub = sub_map.get(cid)
    offer = {}
    if t['offer_json']:
        try: offer = json.loads(t['offer_json'])
        except: pass
    sub_info = f"{sub['seat_count']}seats Plan{sub['plan']} @${sub['effective_price']:.2f}" if sub else "NOT_SUBSCRIBED"
    print(f"  CID={cid} grp={t['group_id']} turn={t['turn_number']} day={t['day']} | {sub_info} | offer={offer}")

# Print new_lead threads that are recent (within 7 days = day 91+)
print("\n=== RECENT NEW LEADS (day 91+) ===")
recent_leads = {cid: t for cid, t in cust_threads.items() 
                if t['thread_type'] == 'new_lead' and t['day'] >= day - 7}
by_group = {}
for cid, t in recent_leads.items():
    g = t['group_id']
    if g not in by_group:
        by_group[g] = []
    offer = {}
    if t['offer_json']:
        try: offer = json.loads(t['offer_json'])
        except: pass
    by_group[g].append({'cid': cid, 'turn': t['turn_number'], 'day': t['day'], 'offer': offer})

for g, lst in sorted(by_group.items()):
    print(f"\n{g}: {len(lst)} recent leads")
    for item in lst[:10]:
        print(f"  CID={item['cid']} turn={item['turn']} day={item['day']} offer={item['offer']}")

