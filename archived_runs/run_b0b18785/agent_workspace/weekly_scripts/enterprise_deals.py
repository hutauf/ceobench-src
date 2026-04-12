import novamind_api as nm
import json

# === ENTERPRISE DEAL HANDLER ===
# Respond to all urgent threads (age <= 7 days)

day = nm.vars.current_day

threads = nm.query("""SELECT et.customer_id, c.group_id, et.thread_type, 
    et.turn_number, et.sender, et.day, et.offer_json
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0 AND et.sender != 'agent'
ORDER BY et.customer_id ASC, et.turn_number DESC""")

# Get latest thread per customer
cust_threads = {}
for t in threads['rows']:
    cid = t['customer_id']
    if cid not in cust_threads:
        cust_threads[cid] = t

def compute_offer_price(their_price, turn, group='E1'):
    if group in ['E1']:
        floor_b = 8.0
    elif group in ['E2', 'E3']:
        floor_b = 12.0
    else:
        floor_b = 8.0
    
    if turn >= 4:
        my_offer = max(their_price * 1.05, floor_b)
    else:
        my_offer = max(their_price * 1.15, floor_b * 1.5)
    
    return round(my_offer, 2)

urgent_deals = []
churn_deals = []

for cid, t in cust_threads.items():
    age = day - t['day']
    group = t['group_id']
    turn = t['turn_number']
    thread_type = t['thread_type']
    
    # Parse their offer
    try:
        offer_data = json.loads(t['offer_json']) if t['offer_json'] else {}
        their_price = offer_data.get('price', None)
    except:
        their_price = None
    
    # Handle urgent threads (age <= 7 days)
    if thread_type == 'new_lead' and age <= 7:
        if turn == 0 or their_price is None:
            # Fresh lead - make initial offer
            if group == 'E1':
                deal = [cid, [["B", 20.0], ["A", 12.0]]]
            elif group == 'E2':
                deal = [cid, [["C", 40.0], ["B", 25.0]]]
            else:  # E3
                deal = [cid, [["C", 40.0], ["B", 25.0]]]
        else:
            # Counter their offer
            b_price = compute_offer_price(their_price, turn, group)
            a_price = round(b_price * 0.6, 2)
            if group == 'E1':
                deal = [cid, [["B", b_price], ["A", a_price]]]
            else:
                c_price = round(b_price * 1.5, 2)
                deal = [cid, [["C", c_price], ["B", b_price]]]
        urgent_deals.append(deal)
    
    # Handle renegotiations and plan changes (age <= 7)
    elif thread_type in ['renegotiation', 'plan_change'] and age <= 7:
        # Check current subscription
        sub = nm.query(f"SELECT plan, seat_count, effective_price FROM subscriptions WHERE status='subscribed' AND customer_id = {cid}")
        if sub['rows']:
            r = sub['rows'][0]
            plan = r['plan']
            current_price = r['effective_price']
            
            if their_price is not None:
                new_price = compute_offer_price(their_price, turn, group)
            else:
                new_price = current_price
            
            deal = [cid, [[plan, new_price]]]
            urgent_deals.append(deal)
    
    # Handle churn prevention (respond to all active subs)
    elif thread_type == 'churn_prevention':
        sub = nm.query(f"SELECT plan, seat_count, effective_price FROM subscriptions WHERE status='subscribed' AND customer_id = {cid}")
        if sub['rows']:
            r = sub['rows'][0]
            plan = r['plan']
            current_price = r['effective_price']
            
            if their_price is not None:
                # They want a discount - offer small concession
                new_price = max(their_price * 1.05, current_price * 0.90)
                new_price = round(new_price, 2)
            else:
                new_price = current_price
            
            deal = [cid, [[plan, new_price]]]
            churn_deals.append(deal)

print(f"Urgent deals to send: {len(urgent_deals)}")
print(f"Churn prevention deals: {len(churn_deals)}")

all_deals = urgent_deals + churn_deals
if all_deals:
    # Send in batches of 20
    batch_size = 20
    for i in range(0, len(all_deals), batch_size):
        batch = all_deals[i:i+batch_size]
        try:
            result = nm.enterprise.send_enterprise_deal(deals=batch)
            print(f"Batch {i//batch_size + 1}: sent {len(batch)} deals")
        except Exception as e:
            print(f"Batch {i//batch_size + 1} error: {e}")
            # Try individually
            for deal in batch:
                try:
                    nm.enterprise.send_enterprise_deal(deals=[deal])
                except Exception as e2:
                    print(f"  Failed {deal[0]}: {e2}")
