import novamind_api as nm
import json

day = nm.vars.current_day
print(f"Day {day} - Sending urgent new lead deals")

# Get open new_lead threads
threads = nm.query("""SELECT et.customer_id, c.group_id, et.thread_type, 
    et.turn_number, et.sender, et.day, et.offer_json
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0 AND et.sender != 'agent' AND et.thread_type='new_lead'
    AND et.day >= {day_threshold}
ORDER BY et.customer_id ASC, et.turn_number DESC""".replace("{day_threshold}", str(day-6)))

# Latest thread per customer
cust_threads = {}
for t in threads['rows']:
    cid = t['customer_id']
    if cid not in cust_threads:
        cust_threads[cid] = t

print(f"Recent new_lead threads (last 6 days): {len(cust_threads)}")

# Check subscriptions to exclude already-subbed
subs = nm.query("SELECT customer_id FROM subscriptions WHERE status='subscribed' LIMIT 5000")
subbed_set = {r['customer_id'] for r in subs['rows']}

def make_offer(group_id, customer_offer_price):
    """Make competitive offer based on group"""
    if group_id == 'E1':
        if customer_offer_price and customer_offer_price > 0:
            counter_b = max(8.0, round(customer_offer_price * 1.15, 2))
            counter_a = max(5.0, round(counter_b * 0.6, 2))
            return [["A", counter_a], ["B", counter_b]]
        return [["A", 12.0], ["B", 20.0]]
    elif group_id == 'E2':
        if customer_offer_price and customer_offer_price > 0:
            counter_c = max(15.0, round(customer_offer_price * 1.15, 2))
            counter_b = max(10.0, round(counter_c * 0.65, 2))
            return [["B", counter_b], ["C", counter_c]]
        return [["B", 25.0], ["C", 40.0]]
    elif group_id == 'E3':
        if customer_offer_price and customer_offer_price > 0:
            counter_b = max(9.0, round(customer_offer_price * 1.15, 2))
            counter_a = max(6.0, round(counter_b * 0.6, 2))
            return [["A", counter_a], ["B", counter_b]]
        return [["A", 12.0], ["B", 20.0]]
    else:
        return [["B", 20.0]]

# Build deals for urgent threads (not already subscribed)
deals = []
for cid, t in cust_threads.items():
    if cid in subbed_set:
        continue  # skip already subscribed
    group_id = t['group_id']
    offer_price = 0
    if t['offer_json']:
        try:
            offer_data = json.loads(t['offer_json'])
            offer_price = offer_data.get('price', 0)
        except:
            pass
    
    plans = make_offer(group_id, offer_price)
    deals.append([cid, plans])

print(f"Deals to send: {len(deals)}")

# Show breakdown by group
from collections import defaultdict
grp_count = defaultdict(int)
for d in deals:
    cid = d[0]
    t = cust_threads[cid]
    grp_count[t['group_id']] += 1

for g, n in sorted(grp_count.items()):
    print(f"  {g}: {n} deals")

# Send in batches of 50
batch_size = 50
total_success = 0
for i in range(0, len(deals), batch_size):
    batch = deals[i:i+batch_size]
    result = nm.enterprise.send_enterprise_deal(deals=batch)
    success = sum(1 for r in result['results'] if r.get('success'))
    total_success += success
    print(f"Batch {i//batch_size+1}: {success}/{len(batch)} succeeded")

print(f"\nTotal: {total_success}/{len(deals)} deals sent successfully")

