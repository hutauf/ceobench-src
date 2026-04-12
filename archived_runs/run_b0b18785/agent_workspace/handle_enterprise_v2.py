#!/usr/bin/env python3
"""Handle enterprise deals - corrected v2"""
import novamind_api as nm

current_day = nm.vars.current_day
print(f"=== Enterprise Deals Handler v2 - Day {current_day} ===")

# Get ALL open threads (not just latest per customer) to understand full state
r = nm.query('''SELECT et.customer_id, c.group_id, et.thread_type, et.turn_number, 
    et.sender, et.day, et.message_text, et.offer_json
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0
ORDER BY et.customer_id, et.turn_number ASC''')

all_threads = r['rows']
print(f"Total open thread entries: {len(all_threads)}")

# Group by customer_id to find latest state per customer
from collections import defaultdict
customer_threads = defaultdict(list)
for t in all_threads:
    customer_threads[t['customer_id']].append(t)

print(f"Unique customers with open threads: {len(customer_threads)}")

# For each customer, get latest message that's NOT from agent
# And determine what type of response is needed
def get_latest_non_agent_message(threads):
    """Get the latest message not from agent"""
    non_agent = [t for t in threads if t['sender'] != 'agent']
    if not non_agent:
        return None
    return max(non_agent, key=lambda t: t['turn_number'])

# Get active subscriptions
active = nm.query('''SELECT s.customer_id, c.group_id, s.plan, s.seat_count, s.effective_price
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
WHERE s.status='subscribed' AND s.seat_count >= 50''')
active_subs = {row['customer_id']: row for row in active['rows']}
print(f"Active enterprise subs: {len(active_subs)}")

# Categorize
churn_cases = {}
counter_cases = {}
fresh_lead_cases = {}

for cid, threads in customer_threads.items():
    latest = get_latest_non_agent_message(threads)
    if not latest:
        continue
    
    thread_type = latest['thread_type']
    turn = latest['turn_number']
    offer = latest['offer_json']
    group = latest['group_id']
    day = latest['day']
    
    if thread_type in ['churn_prevention', 'renegotiation']:
        churn_cases[cid] = latest
    elif turn >= 2 and offer and isinstance(offer, dict) and offer.get('price'):
        counter_cases[cid] = latest
    else:
        fresh_lead_cases[cid] = latest

print(f"Churn/renegotiation: {len(churn_cases)}")
print(f"Counter-offers pending: {len(counter_cases)}")
print(f"Fresh leads (no counter): {len(fresh_lead_cases)}")

# ===== 1. HANDLE CHURN PREVENTION =====
print("\n--- CHURN PREVENTION ---")
churn_deals = []
for cid, t in churn_cases.items():
    group = t['group_id']
    if cid in active_subs:
        sub = active_subs[cid]
        plan = sub['plan']
        price = sub['effective_price']
        # 10-15% retention discount
        if plan == 'C':
            new_price = round(max(35.0, price * 0.88), 2)
        elif plan == 'B':
            new_price = round(max(14.0, price * 0.88), 2)
        else:
            new_price = round(max(8.0, price * 0.88), 2)
        churn_deals.append([cid, [[plan, new_price]]])
        print(f"  {cid} {group} Plan {plan}: \${price:.2f} → \${new_price:.2f}")
    else:
        # Not subscribed - give standard offer
        if group == 'E2':
            churn_deals.append([cid, [["C", 40.0], ["B", 25.0]]])
        elif group == 'E3':
            churn_deals.append([cid, [["B", 20.0], ["A", 12.0]]])
        else:
            churn_deals.append([cid, [["B", 18.0], ["A", 10.0]]])
        print(f"  {cid} {group} not subscribed - standard offer")

if churn_deals:
    res = nm.enterprise.send_enterprise_deal(deals=churn_deals)
    successes = sum(1 for r in res['results'] if r.get('success'))
    errors = [r for r in res['results'] if r.get('error')]
    print(f"Churn prevention: {successes} success, {len(errors)} errors")
    for e in errors:
        print(f"  Error CID={e['customer_id']}: {e['error']}")

# ===== 2. HANDLE COUNTER-OFFERS =====
print("\n--- COUNTER-OFFERS ---")
counter_deals = []
for cid, t in counter_cases.items():
    group = t['group_id']
    turn = t['turn_number']
    offer = t['offer_json']
    counter_price = offer.get('price', 0) if isinstance(offer, dict) else 0
    
    if group == 'E1':
        # E1 WTP ~$33/seat, Plan B = value service
        if counter_price >= 10.0:
            print(f"  ACCEPT {cid} E1 Plan B \${counter_price:.2f}/seat (turn {turn})")
            counter_deals.append([cid, [["B", counter_price]]])
        elif counter_price >= 7.0:
            print(f"  ACCEPT {cid} E1 as Plan A \${counter_price:.2f}/seat (turn {turn})")
            counter_deals.append([cid, [["A", counter_price]]])
        elif turn >= 4:
            # Final turn - accept whatever to close
            if counter_price >= 5.0:
                print(f"  FINAL ACCEPT {cid} E1 \${counter_price:.2f}/seat (turn {turn})")
                counter_deals.append([cid, [["A", counter_price]]])
            else:
                print(f"  FINAL REJECT {cid} E1 \${counter_price:.2f}/seat (too low, turn {turn})")
                # Don't add - let expire
        else:
            print(f"  COUNTER {cid} E1 offered \${counter_price:.2f} → counter \$12/B or \$8/A (turn {turn})")
            counter_deals.append([cid, [["B", 12.0], ["A", 8.0]]])
    
    elif group == 'E2':
        # E2 WTP ~$88/seat - be more aggressive with pricing
        if counter_price >= 15.0:
            print(f"  ACCEPT {cid} E2 Plan B \${counter_price:.2f}/seat (turn {turn})")
            counter_deals.append([cid, [["B", counter_price]]])
        elif counter_price >= 10.0:
            # Low but can work with Plan B at discount
            print(f"  COUNTER {cid} E2 \${counter_price:.2f} → offer \$20/B or \$12/A (turn {turn})")
            counter_deals.append([cid, [["B", 20.0], ["A", 12.0]]])
        elif turn >= 4:
            if counter_price >= 8.0:
                print(f"  FINAL ACCEPT {cid} E2 Plan A \${counter_price:.2f} (turn {turn})")
                counter_deals.append([cid, [["A", counter_price]]])
            else:
                print(f"  FINAL REJECT {cid} E2 \${counter_price:.2f} (too low, turn {turn})")
        else:
            print(f"  COUNTER {cid} E2 offered \${counter_price:.2f} → counter \$25/C or \$18/B (turn {turn})")
            counter_deals.append([cid, [["C", 25.0], ["B", 18.0]]])
    
    elif group == 'E3':
        # E3 WTP ~$104/seat
        if counter_price >= 14.0:
            print(f"  ACCEPT {cid} E3 Plan B \${counter_price:.2f}/seat (turn {turn})")
            counter_deals.append([cid, [["B", counter_price]]])
        elif counter_price >= 10.0:
            print(f"  COUNTER {cid} E3 \${counter_price:.2f} → \$16/B (turn {turn})")
            counter_deals.append([cid, [["B", 16.0], ["A", 12.0]]])
        elif turn >= 4:
            if counter_price >= 8.0:
                print(f"  FINAL ACCEPT {cid} E3 \${counter_price:.2f} (turn {turn})")
                counter_deals.append([cid, [["B", counter_price]]])
        else:
            print(f"  COUNTER {cid} E3 \${counter_price:.2f} → \$18/B (turn {turn})")
            counter_deals.append([cid, [["B", 18.0]]])

if counter_deals:
    for i in range(0, len(counter_deals), 20):
        batch = counter_deals[i:i+20]
        res = nm.enterprise.send_enterprise_deal(deals=batch)
        successes = sum(1 for r in res['results'] if r.get('success'))
        errors = [r for r in res['results'] if r.get('error')]
        print(f"Counter batch {i//20+1}: {successes}/{len(batch)} success")
        for e in errors:
            print(f"  Error CID={e['customer_id']}: {e['error']}")

# ===== 3. HANDLE FRESH LEADS =====
print("\n--- FRESH LEADS ---")
new_lead_deals = []
for cid, t in fresh_lead_cases.items():
    group = t['group_id']
    if group == 'E1':
        new_lead_deals.append([cid, [["B", 20.0], ["A", 12.0]]])
    elif group == 'E2':
        new_lead_deals.append([cid, [["C", 40.0], ["B", 25.0]]])
    elif group == 'E3':
        new_lead_deals.append([cid, [["B", 20.0], ["A", 12.0]]])

print(f"Fresh leads to offer: {len(new_lead_deals)}")
total_success = 0
total_errors = 0
for i in range(0, len(new_lead_deals), 20):
    batch = new_lead_deals[i:i+20]
    res = nm.enterprise.send_enterprise_deal(deals=batch)
    s = sum(1 for r in res['results'] if r.get('success'))
    e = sum(1 for r in res['results'] if r.get('error'))
    total_success += s
    total_errors += e

print(f"Fresh leads: {total_success} success, {total_errors} errors (errors=expired/no thread)")

print("\n=== COMPLETE ===")
