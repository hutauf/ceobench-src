#!/usr/bin/env python3
"""Week 12 enterprise handler v2 - handle fresh threads, skip expired"""
import novamind_api as nm
import json

current_day = nm.vars.current_day
print(f"=== Enterprise Handler v2 - Day {current_day} ===")

# Get threads - focus on FRESH ones (within 7 days) and active subs
threads = nm.query("""SELECT et.customer_id, c.group_id, et.thread_type, 
    et.turn_number, et.sender, et.day, et.offer_json, et.message_text
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0 AND et.sender != 'agent'
ORDER BY et.customer_id ASC, et.turn_number DESC""")

# Latest thread per customer
cust_threads = {}
for t in threads['rows']:
    cid = t['customer_id']
    if cid not in cust_threads:
        cust_threads[cid] = t

print(f"Total customers needing response: {len(cust_threads)}")

# Separate by age: fresh (<=7d) vs old (>7d)
fresh = {}
old = {}
for cid, t in cust_threads.items():
    age = current_day - t['day']
    if age <= 7:
        fresh[cid] = t
    else:
        old[cid] = t

print(f"Fresh (<=7d): {len(fresh)} | Old (>7d, likely expired): {len(old)}")

# Get active subscriptions efficiently
active_subs_q = nm.query("""SELECT customer_id, plan, seat_count, effective_price
FROM subscriptions WHERE status='subscribed' AND seat_count >= 50
ORDER BY seat_count DESC""")
active_subs = {}
for row in active_subs_q['rows']:
    if row['customer_id'] not in active_subs:
        active_subs[row['customer_id']] = row

print(f"Active enterprise subs (>=50 seats): {len(active_subs)}")

# === Process fresh threads ===
all_deals = []  # (cid, deals_list)

for cid, t in fresh.items():
    group = t['group_id']
    thread_type = t['thread_type']
    turn = t['turn_number']
    
    # Parse offer price
    offer_price = None
    if t['offer_json']:
        try:
            offer_data = json.loads(t['offer_json']) if isinstance(t['offer_json'], str) else t['offer_json']
            if isinstance(offer_data, dict):
                offer_price = offer_data.get('price', offer_data.get('price_per_seat'))
        except:
            pass
    
    if thread_type in ['churn_prevention', 'renegotiation']:
        # MUST retain - give discount
        if cid in active_subs:
            sub = active_subs[cid]
            current_plan = sub['plan']
            current_price = sub['effective_price']
            if current_plan == 'C':
                new_price = max(30.0, current_price * 0.85)
            elif current_plan == 'B':
                new_price = max(12.0, current_price * 0.85)
            else:
                new_price = max(7.0, current_price * 0.85)
            all_deals.append((cid, group, thread_type, [[current_plan, new_price]]))
        else:
            # Standard offer
            if group == 'E2':
                all_deals.append((cid, group, thread_type, [["C", 36.0], ["B", 22.0]]))
            elif group == 'E3':
                all_deals.append((cid, group, thread_type, [["B", 17.0], ["A", 10.0]]))
            else:
                all_deals.append((cid, group, thread_type, [["B", 17.0], ["A", 10.0]]))
    
    elif offer_price is not None and turn >= 2:
        # Counter offer - respond
        if group == 'E1':
            if offer_price >= 12.0:
                all_deals.append((cid, group, 'counter', [["B", offer_price]]))
            elif offer_price >= 8.0:
                all_deals.append((cid, group, 'counter', [["B", offer_price], ["A", offer_price]]))
            elif offer_price >= 5.0:
                if turn >= 4:
                    all_deals.append((cid, group, 'counter', [["A", offer_price]]))
                else:
                    all_deals.append((cid, group, 'counter', [["B", 14.0], ["A", 8.0]]))
            else:
                if turn >= 4:
                    # Last chance - accept if >3
                    if offer_price >= 3.0:
                        all_deals.append((cid, group, 'counter', [["A", offer_price]]))
                else:
                    all_deals.append((cid, group, 'counter', [["B", 14.0], ["A", 8.0]]))
        
        elif group == 'E2':
            if offer_price >= 15.0:
                all_deals.append((cid, group, 'counter', [["B", offer_price]]))
            elif offer_price >= 10.0:
                all_deals.append((cid, group, 'counter', [["B", offer_price]]))
            elif offer_price >= 5.0:
                if turn >= 4:
                    all_deals.append((cid, group, 'counter', [["A", offer_price]]))
                else:
                    all_deals.append((cid, group, 'counter', [["C", 36.0], ["B", 20.0]]))
            else:
                all_deals.append((cid, group, 'counter', [["C", 36.0], ["B", 20.0]]))
        
        elif group == 'E3':
            if offer_price >= 12.0:
                all_deals.append((cid, group, 'counter', [["B", offer_price]]))
            elif offer_price >= 7.0:
                all_deals.append((cid, group, 'counter', [["B", offer_price]]))
            elif turn >= 4 and offer_price >= 4.0:
                all_deals.append((cid, group, 'counter', [["A", offer_price]]))
            else:
                all_deals.append((cid, group, 'counter', [["B", 17.0], ["A", 10.0]]))
    
    else:
        # New lead - make offer
        if group == 'E1':
            all_deals.append((cid, group, 'new_lead', [["B", 20.0], ["A", 12.0]]))
        elif group == 'E2':
            all_deals.append((cid, group, 'new_lead', [["C", 40.0], ["B", 25.0]]))
        elif group == 'E3':
            all_deals.append((cid, group, 'new_lead', [["B", 20.0], ["A", 12.0]]))

print(f"\nDeals to send for fresh threads: {len(all_deals)}")

# Also process EXISTING active enterprise customers with churn prevention from OLD threads
# Focus on the big value ones
old_churn = [(cid, t) for cid, t in old.items() 
             if t['thread_type'] in ['churn_prevention', 'renegotiation'] 
             and cid in active_subs]
print(f"Old churn prevention still active: {len(old_churn)}")
for cid, t in old_churn:
    sub = active_subs[cid]
    current_plan = sub['plan']
    current_price = sub['effective_price']
    sc = sub['seat_count']
    if current_plan == 'C':
        new_price = max(28.0, current_price * 0.82)
    elif current_plan == 'B':
        new_price = max(11.0, current_price * 0.82)
    else:
        new_price = max(6.5, current_price * 0.82)
    print(f"  Retaining CID={cid} {t['group_id']} {sc}x{current_plan} ${current_price:.2f} → ${new_price:.2f}")
    all_deals.append((cid, t['group_id'], 'old_churn_retain', [[current_plan, new_price]]))

print(f"\nTotal deals: {len(all_deals)}")

# Send in batches, handling errors gracefully
success_count = 0
error_count = 0

for i in range(0, len(all_deals), 20):
    batch = all_deals[i:i+20]
    deals_payload = [[d[0], d[3]] for d in batch]
    
    try:
        result = nm.enterprise.send_enterprise_deal(deals=deals_payload)
        for r in result.get('results', []):
            if r.get('success'):
                success_count += 1
            else:
                error_count += 1
        if i % 100 == 0:
            print(f"  Batch {i//20+1}: sent {len(batch)}, success so far: {success_count}")
    except Exception as e:
        err_str = str(e)
        # Count partial successes if batch partially failed
        error_count += len(batch)
        print(f"  Batch {i//20+1} ERROR: {err_str[:100]}")

print(f"\nResult: {success_count} success, {error_count} errors")
print("=== COMPLETE ===")
