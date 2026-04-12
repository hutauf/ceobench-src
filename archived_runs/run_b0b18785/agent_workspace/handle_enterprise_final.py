#!/usr/bin/env python3
"""Handle enterprise deals - final corrected version"""
import novamind_api as nm
import json

current_day = nm.vars.current_day
print(f"=== Enterprise Deals Handler FINAL - Day {current_day} ===")

# Get active subs
active = nm.query('''SELECT s.customer_id, c.group_id, s.plan, s.seat_count, s.effective_price
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
WHERE s.status='subscribed' AND s.seat_count >= 50''')
active_subs = {row['customer_id']: row for row in active['rows']}
print(f"Active enterprise subs: {len(active_subs)}")

def parse_offer(offer_json):
    """Parse offer_json which might be a string or dict"""
    if not offer_json:
        return {}
    if isinstance(offer_json, str):
        try:
            return json.loads(offer_json)
        except:
            return {}
    return offer_json

# Get all open threads grouped by customer
r = nm.query('''SELECT et.customer_id, c.group_id, et.thread_type, et.turn_number, 
    et.sender, et.day, et.message_text, et.offer_json
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0
ORDER BY et.customer_id, et.turn_number ASC''')

from collections import defaultdict
customer_threads = defaultdict(list)
for t in r['rows']:
    customer_threads[t['customer_id']].append(t)

print(f"Unique customers with open threads: {len(customer_threads)}")

# Categorize
churn_deals = []
counter_offer_deals = []
fresh_lead_deals = []
skipped = []

for cid, threads in customer_threads.items():
    # Find latest non-agent message
    non_agent = [t for t in threads if t['sender'] != 'agent']
    if not non_agent:
        continue
    latest = max(non_agent, key=lambda t: t['turn_number'])
    
    group = latest['group_id']
    thread_type = latest['thread_type']
    turn = latest['turn_number']
    offer = parse_offer(latest['offer_json'])
    day = latest['day']
    counter_price = offer.get('price', 0)
    
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
            print(f"  CHURN {cid} {group} Plan {plan} \${price:.2f}→\${new_price:.2f}")
        else:
            if group == 'E2':
                churn_deals.append([cid, [["C", 38.0], ["B", 22.0]]])
            elif group == 'E3':
                churn_deals.append([cid, [["B", 17.0], ["A", 11.0]]])
            else:
                churn_deals.append([cid, [["B", 17.0], ["A", 10.0]]])
            print(f"  CHURN {cid} {group} not sub - standard")
        continue
    
    # COUNTER-OFFERS (turn >= 2 with price)
    if turn >= 2 and counter_price > 0:
        if group == 'E1':
            if counter_price >= 10.0:
                counter_offer_deals.append([cid, [["B", counter_price]]])
                print(f"  ACCEPT E1 {cid} B \${counter_price:.2f} t{turn}")
            elif counter_price >= 7.0:
                counter_offer_deals.append([cid, [["A", counter_price]]])
                print(f"  ACCEPT E1 {cid} A \${counter_price:.2f} t{turn}")
            elif turn >= 4:
                if counter_price >= 5.0:
                    counter_offer_deals.append([cid, [["A", counter_price]]])
                    print(f"  FINAL ACCEPT E1 {cid} \${counter_price:.2f} t{turn}")
                else:
                    skipped.append(cid)
                    print(f"  SKIP E1 {cid} \${counter_price:.2f} too low t{turn}")
            else:
                counter_offer_deals.append([cid, [["B", 12.0], ["A", 8.0]]])
                print(f"  COUNTER E1 {cid} \${counter_price:.2f}→12/8 t{turn}")
        elif group == 'E2':
            if counter_price >= 15.0:
                counter_offer_deals.append([cid, [["B", counter_price]]])
                print(f"  ACCEPT E2 {cid} B \${counter_price:.2f} t{turn}")
            elif counter_price >= 10.0:
                counter_offer_deals.append([cid, [["C", 25.0], ["B", counter_price]]])
                print(f"  ACCEPT E2 {cid} B \${counter_price:.2f} or C \$25 t{turn}")
            elif turn >= 3:
                if counter_price >= 8.0:
                    counter_offer_deals.append([cid, [["A", counter_price]]])
                    print(f"  FINAL ACCEPT E2 {cid} A \${counter_price:.2f} t{turn}")
                else:
                    skipped.append(cid)
                    print(f"  SKIP E2 {cid} \${counter_price:.2f} too low t{turn}")
            else:
                counter_offer_deals.append([cid, [["C", 30.0], ["B", 20.0]]])
                print(f"  COUNTER E2 {cid} \${counter_price:.2f}→30/20 t{turn}")
        elif group == 'E3':
            if counter_price >= 14.0:
                counter_offer_deals.append([cid, [["B", counter_price]]])
                print(f"  ACCEPT E3 {cid} B \${counter_price:.2f} t{turn}")
            elif counter_price >= 10.0:
                counter_offer_deals.append([cid, [["B", 14.0], ["A", counter_price]]])
                print(f"  COUNTER E3 {cid} \${counter_price:.2f}→14/low t{turn}")
            else:
                counter_offer_deals.append([cid, [["B", 16.0]]])
                print(f"  COUNTER E3 {cid} \${counter_price:.2f}→16 t{turn}")
        continue
    
    # FRESH LEADS
    if group == 'E1':
        fresh_lead_deals.append([cid, [["B", 20.0], ["A", 12.0]]])
    elif group == 'E2':
        fresh_lead_deals.append([cid, [["C", 40.0], ["B", 25.0]]])
    elif group == 'E3':
        fresh_lead_deals.append([cid, [["B", 20.0], ["A", 12.0]]])

print(f"\nChurn: {len(churn_deals)}, Counters: {len(counter_offer_deals)}, Fresh: {len(fresh_lead_deals)}, Skip: {len(skipped)}")

def send_batch(deals, label):
    total_s = 0
    total_e = 0
    error_details = []
    for i in range(0, len(deals), 20):
        batch = deals[i:i+20]
        try:
            res = nm.enterprise.send_enterprise_deal(deals=batch)
            s = sum(1 for r in res['results'] if r.get('success'))
            errs = [r for r in res['results'] if r.get('error')]
            total_s += s
            total_e += len(errs)
            error_details.extend(errs)
        except Exception as ex:
            total_e += len(batch)
    print(f"{label}: {total_s} success, {total_e} expired/error")
    for e in error_details[:5]:
        print(f"  Error {e['customer_id']}: {e['error']}")
    return total_s

send_batch(churn_deals, "Churn prevention")
send_batch(counter_offer_deals, "Counter offers")
send_batch(fresh_lead_deals, "Fresh leads")

print("\n=== DONE ===")
