#!/usr/bin/env python3
"""Handle enterprise deals - focused on active threads only"""
import novamind_api as nm

current_day = nm.vars.current_day
print(f"=== Enterprise Deals Handler v3 - Day {current_day} ===")

# Get active subs
active = nm.query('''SELECT s.customer_id, c.group_id, s.plan, s.seat_count, s.effective_price
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
WHERE s.status='subscribed' AND s.seat_count >= 50''')
active_subs = {row['customer_id']: row for row in active['rows']}
print(f"Active enterprise subs: {len(active_subs)}")

# Strategy: Try to send deals to everyone with open threads.
# The API will reject expired ones. We'll handle the responses.

# Get all customers with open threads, grouped by type and last turn
r = nm.query('''SELECT et.customer_id, c.group_id, et.thread_type, et.turn_number, 
    et.sender, et.day, et.message_text, et.offer_json
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0
ORDER BY et.customer_id, et.turn_number ASC''')

from collections import defaultdict
customer_threads = defaultdict(list)
for t in r['rows']:
    customer_threads[t['customer_id']].append(t)

# For each customer, determine best response strategy
deals_to_send = []
counter_offer_deals = []
churn_deals = []

for cid, threads in customer_threads.items():
    # Find latest non-agent message
    non_agent = [t for t in threads if t['sender'] != 'agent']
    if not non_agent:
        continue
    latest = max(non_agent, key=lambda t: t['turn_number'])
    
    group = latest['group_id']
    thread_type = latest['thread_type']
    turn = latest['turn_number']
    offer = latest['offer_json']
    day = latest['day']
    counter_price = offer.get('price', 0) if isinstance(offer, dict) and offer else 0
    
    # CHURN PREVENTION / RENEGOTIATION
    if thread_type in ['churn_prevention', 'renegotiation']:
        if cid in active_subs:
            sub = active_subs[cid]
            plan = sub['plan']
            price = sub['effective_price']
            if plan == 'C':
                new_price = round(max(35.0, price * 0.88), 2)
            elif plan == 'B':
                new_price = round(max(14.0, price * 0.88), 2)
            else:
                new_price = round(max(8.0, price * 0.88), 2)
            churn_deals.append([cid, [[plan, new_price]]])
        else:
            if group == 'E2':
                churn_deals.append([cid, [["C", 38.0], ["B", 22.0]]])
            elif group == 'E3':
                churn_deals.append([cid, [["B", 17.0], ["A", 11.0]]])
            else:
                churn_deals.append([cid, [["B", 17.0], ["A", 10.0]]])
        continue
    
    # COUNTER-OFFERS (turn >= 2 with price)
    if turn >= 2 and counter_price > 0:
        if group == 'E1':
            if counter_price >= 10.0:
                counter_offer_deals.append([cid, [["B", counter_price]]])
                print(f"  ACCEPT E1 CID={cid} Plan B \${counter_price:.2f} (turn {turn})")
            elif counter_price >= 7.0:
                counter_offer_deals.append([cid, [["A", counter_price]]])
                print(f"  ACCEPT E1 CID={cid} Plan A \${counter_price:.2f} (turn {turn})")
            elif turn >= 4:
                if counter_price >= 5.0:
                    counter_offer_deals.append([cid, [["A", counter_price]]])
                    print(f"  FINAL ACCEPT E1 CID={cid} \${counter_price:.2f} (turn {turn})")
                else:
                    print(f"  SKIP E1 CID={cid} too low \${counter_price:.2f} (turn {turn})")
            else:
                counter_offer_deals.append([cid, [["B", 12.0], ["A", 8.0]]])
                print(f"  COUNTER E1 CID={cid} \${counter_price:.2f} → 12/8 (turn {turn})")
        elif group == 'E2':
            if counter_price >= 15.0:
                counter_offer_deals.append([cid, [["B", counter_price]]])
                print(f"  ACCEPT E2 CID={cid} Plan B \${counter_price:.2f} (turn {turn})")
            elif counter_price >= 10.0:
                counter_offer_deals.append([cid, [["B", 18.0], ["A", counter_price]]])
                print(f"  COUNTER E2 CID={cid} \${counter_price:.2f} → 18/low (turn {turn})")
            elif turn >= 3:
                if counter_price >= 8.0:
                    counter_offer_deals.append([cid, [["A", counter_price]]])
                    print(f"  FINAL ACCEPT E2 CID={cid} \${counter_price:.2f} (turn {turn})")
                else:
                    print(f"  SKIP E2 CID={cid} too low \${counter_price:.2f} (turn {turn})")
            else:
                counter_offer_deals.append([cid, [["C", 25.0], ["B", 18.0]]])
                print(f"  COUNTER E2 CID={cid} \${counter_price:.2f} → 25/18 (turn {turn})")
        elif group == 'E3':
            if counter_price >= 14.0:
                counter_offer_deals.append([cid, [["B", counter_price]]])
                print(f"  ACCEPT E3 CID={cid} Plan B \${counter_price:.2f} (turn {turn})")
            elif counter_price >= 10.0:
                counter_offer_deals.append([cid, [["B", 14.0], ["A", counter_price]]])
                print(f"  COUNTER E3 CID={cid} \${counter_price:.2f} → 14/low (turn {turn})")
            else:
                counter_offer_deals.append([cid, [["B", 16.0]]])
                print(f"  COUNTER E3 CID={cid} \${counter_price:.2f} → 16 (turn {turn})")
        continue
    
    # FRESH LEADS (turn 0 or early turns without counter price)
    if group == 'E1':
        deals_to_send.append([cid, [["B", 20.0], ["A", 12.0]]])
    elif group == 'E2':
        deals_to_send.append([cid, [["C", 40.0], ["B", 25.0]]])
    elif group == 'E3':
        deals_to_send.append([cid, [["B", 20.0], ["A", 12.0]]])

print(f"\nChurn deals: {len(churn_deals)}")
print(f"Counter offers: {len(counter_offer_deals)}")
print(f"Fresh leads: {len(deals_to_send)}")

# Send churn prevention
if churn_deals:
    print("\n--- Sending churn prevention ---")
    res = nm.enterprise.send_enterprise_deal(deals=churn_deals)
    s = sum(1 for r in res['results'] if r.get('success'))
    errs = [r for r in res['results'] if r.get('error')]
    print(f"  {s}/{len(churn_deals)} success")
    for e in errs:
        print(f"  Error {e['customer_id']}: {e['error']}")

# Send counter-offer responses
if counter_offer_deals:
    print("\n--- Sending counter-offer responses ---")
    for i in range(0, len(counter_offer_deals), 20):
        batch = counter_offer_deals[i:i+20]
        res = nm.enterprise.send_enterprise_deal(deals=batch)
        s = sum(1 for r in res['results'] if r.get('success'))
        errs = [r for r in res['results'] if r.get('error')]
        print(f"  Batch {i//20+1}: {s}/{len(batch)} success, {len(errs)} errors")
        for e in errs:
            print(f"    Error {e['customer_id']}: {e['error']}")

# Send fresh lead offers
if deals_to_send:
    print("\n--- Sending fresh lead offers ---")
    total_s = 0
    total_e = 0
    for i in range(0, len(deals_to_send), 20):
        batch = deals_to_send[i:i+20]
        try:
            res = nm.enterprise.send_enterprise_deal(deals=batch)
            s = sum(1 for r in res['results'] if r.get('success'))
            e = sum(1 for r in res['results'] if r.get('error'))
            total_s += s
            total_e += e
        except Exception as ex:
            # Some in batch failed - they were expired. Count as errors.
            total_e += len(batch)
            print(f"  Batch {i//20+1} EXCEPTION: {str(ex)[:100]}")
    print(f"  Fresh leads total: {total_s} success, {total_e} expired/errors")

print("\n=== DONE ===")
