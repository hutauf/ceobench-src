import novamind_api as nm
import json

day = nm.vars.current_day
print(f"Day {day} - Enterprise Batch Response")

# Strategy:
# E1: Plan B @ $20/seat (or A @ $12 for price-sensitives)
# E2: Plan C @ $40/seat (or B @ $25)
# E3: Plan C @ $40/seat (or B @ $25)
# 
# For negotiations (turn >= 2 with customer offer):
#   If their offered price < our floor, counter at floor
#   If their price is reasonable, accept at 1.15x or floor
#   E1 floor: B=$8, A=$5
#   E2 floor: C=$15, B=$10
#   E3 floor: C=$15, B=$10

E1_INITIAL = [["B", 20.0], ["A", 12.0]]
E2_INITIAL = [["C", 40.0], ["B", 25.0]]
E3_INITIAL = [["C", 40.0], ["B", 25.0]]

E1_FLOOR_B = 8.0
E1_FLOOR_A = 5.0
E2_FLOOR_C = 15.0
E2_FLOOR_B = 10.0
E3_FLOOR_C = 15.0
E3_FLOOR_B = 10.0

def get_counter_offer(group_id, their_price, turn_number):
    """Generate counter offer based on their price and negotiation turn."""
    if group_id == 'E1':
        # High turns (late negotiation) - be more flexible
        if turn_number >= 4:
            floor_b = max(E1_FLOOR_B, their_price * 1.05)
            floor_a = max(E1_FLOOR_A, their_price * 0.85)
            return [["B", round(floor_b, 2)], ["A", round(floor_a, 2)]]
        counter_b = max(E1_FLOOR_B, their_price * 1.15)
        counter_a = max(E1_FLOOR_A, their_price * 0.9)
        return [["B", round(counter_b, 2)], ["A", round(counter_a, 2)]]
    elif group_id == 'E2':
        if turn_number >= 4:
            floor_c = max(E2_FLOOR_C, their_price * 1.05)
            floor_b = max(E2_FLOOR_B, their_price * 0.85)
            return [["C", round(floor_c, 2)], ["B", round(floor_b, 2)]]
        counter_c = max(E2_FLOOR_C, their_price * 1.15)
        counter_b = max(E2_FLOOR_B, their_price * 0.9)
        return [["C", round(counter_c, 2)], ["B", round(counter_b, 2)]]
    else:  # E3
        if turn_number >= 4:
            floor_c = max(E3_FLOOR_C, their_price * 1.05)
            floor_b = max(E3_FLOOR_B, their_price * 0.85)
            return [["C", round(floor_c, 2)], ["B", round(floor_b, 2)]]
        counter_c = max(E3_FLOOR_C, their_price * 1.15)
        counter_b = max(E3_FLOOR_B, their_price * 0.9)
        return [["C", round(counter_c, 2)], ["B", round(counter_b, 2)]]

# Get the latest thread per customer (only one response per customer)
threads = nm.query("""SELECT et.customer_id, c.group_id, et.thread_type, 
    et.turn_number, et.sender, et.day, et.offer_json, et.message_id
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0 AND et.sender != 'agent'
ORDER BY et.customer_id ASC, et.turn_number DESC""")

cust_threads = {}
for t in threads['rows']:
    cid = t['customer_id']
    if cid not in cust_threads:
        cust_threads[cid] = t

print(f"Total unique customers with open threads: {len(cust_threads)}")

# Prioritize:
# 1. Fresh threads (age <= 7) - URGENT, will be lost
# 2. Churn prevention for existing high-value subs - prevent revenue loss
# 3. Old new_lead threads where customer IS subscribed (renegotiation needed)

# Check subscribed status for churn prevention customers
churn_cids = [cid for cid, t in cust_threads.items() if t['thread_type'] == 'churn_prevention']
print(f"\nChurn prevention customers: {len(churn_cids)}")

# Build deals list
deals = []
responded = []

for cid, t in sorted(cust_threads.items()):
    group_id = t['group_id']
    thread_type = t['thread_type']
    turn = t['turn_number']
    age = day - t['day']
    offer = json.loads(t['offer_json']) if t['offer_json'] else {}
    their_price = offer.get('price', None)
    
    # Decision logic:
    # Skip old new_lead threads for non-subscribed (permanently expired)
    # But we still need to respond to keep threads from counting against us
    
    is_churn = thread_type == 'churn_prevention'
    is_fresh = age <= 7
    
    if not is_fresh and not is_churn:
        # Old new_lead - skip (expired, no point)
        continue
    
    # Determine offer to make
    if their_price is not None:
        # They made a counter offer - respond with our counter
        offer_plans = get_counter_offer(group_id, their_price, turn)
    else:
        # Initial offer from us
        if group_id == 'E1':
            offer_plans = E1_INITIAL
        elif group_id == 'E2':
            offer_plans = E2_INITIAL
        else:  # E3
            offer_plans = E3_INITIAL
    
    deals.append([cid, offer_plans])
    responded.append((cid, group_id, thread_type, age, their_price, offer_plans))

print(f"\nDeals to send: {len(deals)}")
for r in responded[:20]:
    print(f"  CID {r[0]} ({r[1]}) | {r[2]} | age {r[3]}d | their: {r[4]} -> our: {r[5]}")
if len(responded) > 20:
    print(f"  ... and {len(responded)-20} more")

# Send in batches of 50 to avoid timeouts
BATCH_SIZE = 50
total_sent = 0
for i in range(0, len(deals), BATCH_SIZE):
    batch = deals[i:i+BATCH_SIZE]
    print(f"\nSending batch {i//BATCH_SIZE + 1}: {len(batch)} deals...")
    try:
        result = nm.enterprise.send_enterprise_deal(deals=batch)
        print(f"  Result: {result}")
        total_sent += len(batch)
    except Exception as e:
        print(f"  ERROR: {e}")
        # Try individual sends for failed batch
        for deal in batch:
            try:
                r = nm.enterprise.send_enterprise_deal(deals=[deal])
                total_sent += 1
            except Exception as e2:
                print(f"    Failed CID {deal[0]}: {e2}")

print(f"\nTotal sent: {total_sent}/{len(deals)}")
