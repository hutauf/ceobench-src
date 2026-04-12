import novamind_api as nm
import json

day = nm.vars.current_day
print(f"Day {day} - Handling new leads")

# Get ALL open new_lead threads (recent ones - within 7 days must respond NOW)
threads = nm.query("""SELECT et.customer_id, c.group_id, et.thread_type, 
    et.turn_number, et.sender, et.day, et.offer_json
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0 AND et.sender != 'agent' AND et.thread_type='new_lead'
ORDER BY et.customer_id ASC, et.turn_number DESC""")

# Latest thread per customer
cust_threads = {}
for t in threads['rows']:
    cid = t['customer_id']
    if cid not in cust_threads:
        cust_threads[cid] = t

print(f"Total new_lead threads: {len(cust_threads)}")

# Categorize by urgency (days since thread started)
urgent = {}  # thread must be answered NOW (within 7 days)
old_not_subbed = {}
already_subbed = {}

# Check which customers are already subscribed
subs = nm.query("SELECT customer_id FROM subscriptions WHERE status='subscribed'")
subbed_set = {r['customer_id'] for r in subs['rows']}

for cid, t in cust_threads.items():
    thread_age = day - t['day']
    if cid in subbed_set:
        already_subbed[cid] = t
    elif thread_age <= 6:  # within 7 days, must respond
        urgent[cid] = t
    else:
        old_not_subbed[cid] = t  # expired already

print(f"Already subscribed (handle as upsell): {len(already_subbed)}")
print(f"Urgent (must respond, <=6 days): {len(urgent)}")
print(f"Old/expired (>7 days, not subscribed): {len(old_not_subbed)}")

# Build deals for urgent threads
# E1: offer B$20/A$12 starting point, counter with minimum B$8/A$5
# E2: offer C$40/B$25, counter minimum B$10
# E3: offer B$20/A$12, counter minimum B$9

def get_offer_for_group_and_counter(group_id, customer_offer_price, turn_number):
    """Determine our offer price based on group and negotiation state"""
    if group_id == 'E1':
        base_b = 20.0
        base_a = 12.0
        min_b = 8.0
        min_a = 5.0
        # If they countered low, meet in the middle
        if customer_offer_price and customer_offer_price > 0:
            # They made an offer, counter at 10% above their offer but not below min
            counter_b = max(min_b, customer_offer_price * 1.1)
            counter_a = max(min_a, counter_b * 0.6)
            return [["A", round(counter_a, 2)], ["B", round(counter_b, 2)]]
        else:
            return [["A", base_a], ["B", base_b]]
    elif group_id == 'E2':
        base_c = 40.0
        base_b = 25.0
        min_b = 10.0
        min_c = 15.0
        if customer_offer_price and customer_offer_price > 0:
            counter_c = max(min_c, customer_offer_price * 1.1)
            counter_b = max(min_b, counter_c * 0.65)
            return [["B", round(counter_b, 2)], ["C", round(counter_c, 2)]]
        else:
            return [["B", base_b], ["C", base_c]]
    elif group_id == 'E3':
        base_b = 20.0
        base_a = 12.0
        min_b = 9.0
        min_a = 6.0
        if customer_offer_price and customer_offer_price > 0:
            counter_b = max(min_b, customer_offer_price * 1.1)
            counter_a = max(min_a, counter_b * 0.6)
            return [["A", round(counter_a, 2)], ["B", round(counter_b, 2)]]
        else:
            return [["A", base_a], ["B", base_b]]
    else:
        return [["B", 20.0]]

# Process urgent new leads
urgent_deals = []
for cid, t in urgent.items():
    group_id = t['group_id']
    offer_price = 0
    if t['offer_json']:
        try:
            offer_data = json.loads(t['offer_json'])
            offer_price = offer_data.get('price', 0)
        except:
            pass
    
    plans = get_offer_for_group_and_counter(group_id, offer_price, t['turn_number'])
    urgent_deals.append([cid, plans])

print(f"\nBuilding {len(urgent_deals)} urgent deals...")

# Show sample
for d in urgent_deals[:5]:
    cid = d[0]
    t = urgent[cid]
    print(f"  CID={cid} {t['group_id']} turn={t['turn_number']} day={t['day']} → {d[1]}")

