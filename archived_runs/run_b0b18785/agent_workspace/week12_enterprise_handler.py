#!/usr/bin/env python3
"""Week 12 enterprise handler - handle ALL 264 open threads efficiently"""
import novamind_api as nm
import json

current_day = nm.vars.current_day
print(f"=== Enterprise Handler - Day {current_day} ===")

# Get all threads needing response (latest per customer)
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

print(f"Customers needing response: {len(cust_threads)}")

# Get active subscriptions
active_subs_q = nm.query("""SELECT customer_id, plan, seat_count, effective_price
FROM subscriptions WHERE status='subscribed'""")
active_subs = {}
for row in active_subs_q['rows']:
    # May have multiple subs, keep newest (last)
    active_subs[row['customer_id']] = row

print(f"Active subs: {len(active_subs)}")

# Categorize
churn_threads = []  # churn_prevention threads
new_lead_threads = []  # new_lead or renegotiation
counter_threads = []  # counters (turn >= 2 with offer price)

for cid, t in cust_threads.items():
    thread_type = t['thread_type']
    turn = t['turn_number']
    
    # Parse offer
    offer_price = None
    if t['offer_json']:
        try:
            offer_data = json.loads(t['offer_json']) if isinstance(t['offer_json'], str) else t['offer_json']
            if isinstance(offer_data, dict):
                offer_price = offer_data.get('price', offer_data.get('price_per_seat'))
        except:
            pass
    
    if thread_type in ['churn_prevention', 'renegotiation']:
        churn_threads.append((cid, t, offer_price))
    elif offer_price is not None and turn >= 2:
        counter_threads.append((cid, t, offer_price))
    else:
        new_lead_threads.append((cid, t, offer_price))

print(f"Churn/renegotiation: {len(churn_threads)}")
print(f"Counters to respond: {len(counter_threads)}")
print(f"New leads: {len(new_lead_threads)}")

# === HANDLE CHURN PREVENTION ===
print("\n=== CHURN PREVENTION ===")
churn_deals = []
for cid, t, offer_price in churn_threads:
    group = t['group_id']
    
    if cid in active_subs:
        sub = active_subs[cid]
        current_plan = sub['plan']
        current_price = sub['effective_price']
        sc = sub['seat_count']
        
        # Offer meaningful discount - retain at almost any price above floor
        if current_plan == 'C':
            new_price = max(32.0, current_price * 0.85)
        elif current_plan == 'B':
            new_price = max(14.0, current_price * 0.85)
        else:  # A
            new_price = max(7.5, current_price * 0.85)
        
        print(f"  CID={cid} {group} {sc}x{current_plan} ${current_price:.2f} → ${new_price:.2f}")
        churn_deals.append([cid, [[current_plan, new_price]]])
    else:
        # Not active - standard offer
        if group == 'E2':
            churn_deals.append([cid, [["C", 38.0], ["B", 23.0]]])
        elif group == 'E3':
            churn_deals.append([cid, [["B", 18.0], ["A", 11.0]]])
        else:  # E1
            churn_deals.append([cid, [["B", 18.0], ["A", 10.0]]])
        print(f"  CID={cid} {group} (not active) - standard offer")

if churn_deals:
    print(f"Sending {len(churn_deals)} churn prevention deals...")
    for i in range(0, len(churn_deals), 20):
        batch = churn_deals[i:i+20]
        result = nm.enterprise.send_enterprise_deal(deals=batch)
        print(f"  Batch {i//20+1}: {result}")

# === HANDLE COUNTERS ===
print("\n=== COUNTER OFFERS ===")
counter_deals = []
for cid, t, offer_price in counter_threads:
    group = t['group_id']
    turn = t['turn_number']
    
    if group == 'E1':
        if offer_price >= 12.0:
            counter_deals.append([cid, [["B", offer_price]]])
            print(f"  ACCEPT CID={cid} E1 B ${offer_price:.2f}")
        elif offer_price >= 8.0:
            counter_deals.append([cid, [["B", offer_price], ["A", offer_price]]])
            print(f"  ACCEPT CID={cid} E1 B/A ${offer_price:.2f}")
        elif offer_price >= 6.0:
            counter_deals.append([cid, [["A", offer_price]]])
            print(f"  ACCEPT CID={cid} E1 A ${offer_price:.2f}")
        elif turn >= 4:
            # Final turn - accept if viable
            if offer_price >= 4.0:
                counter_deals.append([cid, [["A", offer_price]]])
                print(f"  FINAL-ACCEPT CID={cid} E1 A ${offer_price:.2f}")
            else:
                print(f"  REJECT CID={cid} E1 ${offer_price:.2f} (too low, turn {turn})")
                # Don't add - let it expire
        else:
            # Counter back
            counter_deals.append([cid, [["B", 14.0], ["A", 8.0]]])
            print(f"  COUNTER CID={cid} E1 ${offer_price:.2f} → B$14/A$8")
    
    elif group == 'E2':
        if offer_price >= 18.0:
            counter_deals.append([cid, [["B", offer_price]]])
            print(f"  ACCEPT CID={cid} E2 B ${offer_price:.2f}")
        elif offer_price >= 12.0:
            counter_deals.append([cid, [["B", offer_price]]])
            print(f"  ACCEPT CID={cid} E2 B ${offer_price:.2f} (below ideal)")
        elif offer_price >= 8.0:
            counter_deals.append([cid, [["B", 15.0], ["A", offer_price]]])
            print(f"  COUNTER CID={cid} E2 ${offer_price:.2f} → B$15")
        elif turn >= 4:
            if offer_price >= 5.0:
                counter_deals.append([cid, [["A", offer_price]]])
                print(f"  FINAL-ACCEPT CID={cid} E2 A ${offer_price:.2f}")
            else:
                print(f"  REJECT CID={cid} E2 ${offer_price:.2f} (too low)")
        else:
            counter_deals.append([cid, [["C", 38.0], ["B", 22.0]]])
            print(f"  COUNTER CID={cid} E2 ${offer_price:.2f} → C$38/B$22")
    
    elif group == 'E3':
        if offer_price >= 14.0:
            counter_deals.append([cid, [["B", offer_price]]])
            print(f"  ACCEPT CID={cid} E3 B ${offer_price:.2f}")
        elif offer_price >= 9.0:
            counter_deals.append([cid, [["B", offer_price]]])
            print(f"  ACCEPT CID={cid} E3 B ${offer_price:.2f}")
        elif turn >= 4:
            if offer_price >= 5.0:
                counter_deals.append([cid, [["A", offer_price]]])
                print(f"  FINAL-ACCEPT CID={cid} E3 A ${offer_price:.2f}")
        else:
            counter_deals.append([cid, [["B", 18.0], ["A", 11.0]]])
            print(f"  COUNTER CID={cid} E3 ${offer_price:.2f} → B$18/A$11")

if counter_deals:
    print(f"\nSending {len(counter_deals)} counter responses...")
    for i in range(0, len(counter_deals), 20):
        batch = counter_deals[i:i+20]
        result = nm.enterprise.send_enterprise_deal(deals=batch)
        print(f"  Batch {i//20+1}: {result}")

# === HANDLE NEW LEADS ===
print("\n=== NEW LEADS ===")
new_deals = []
for cid, t, offer_price in new_lead_threads:
    group = t['group_id']
    if group == 'E1':
        new_deals.append([cid, [["B", 20.0], ["A", 12.0]]])
    elif group == 'E2':
        new_deals.append([cid, [["C", 40.0], ["B", 25.0]]])
    elif group == 'E3':
        new_deals.append([cid, [["B", 20.0], ["A", 12.0]]])

print(f"Sending {len(new_deals)} new lead offers...")
for i in range(0, len(new_deals), 20):
    batch = new_deals[i:i+20]
    result = nm.enterprise.send_enterprise_deal(deals=batch)
    print(f"  Batch {i//20+1} ({len(batch)} deals): {result}")

print("\n=== COMPLETE ===")
