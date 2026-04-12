import novamind_api as nm
import json

print("=== WEEK 16 ACTIONS ===")
day = nm.vars.current_day
print(f"Day: {day}")

# === 1. DOWNGRADE MODEL TIERS (CRITICAL - save $16K+/day) ===
# B: T4 -> T3 (saves ~$9K/day)
# C: T5 -> T4 (saves ~$8K/day)
print("\n1. Downgrading model tiers...")
result = nm.pricing.set_model_tiers(A=2, B=3, C=4)
print(f"   Model tiers set: A=2(0.75x), B=3(0.90x), C=4(1.00x): {result}")

# === 2. CUT OPERATIONS SPEND FURTHER ===
# Individual ops is not helping (issues growing despite spending)
# Cut all non-enterprise ops to minimum
print("\n2. Cutting operations spend...")
result = nm.marketing.set_daily_spend(advertising=400, operations=2000, development=800)
print(f"   Daily spend set: ads=$400, ops=$2000, dev=$800: {result}")

# Cut targeted ops - only keep enterprise
result = nm.analytics.set_targeted_ops_spend(targeted_spend={
    "E1": 500,
    "E2": 500,
    "E3": 300,
    "S1": 0,
    "S2": 0,
    "S3": 0
})
print(f"   Targeted ops (E only): E1=$500, E2=$500, E3=$300: {result}")

# === 3. CUT DEVELOPMENT SPEND FURTHER ===
# We don't have cash for R&D or heavy dev spending right now
# Keep minimal dev spending on enterprise only
result = nm.analytics.set_targeted_dev_spend(targeted_spend={
    "E1": 100,
    "E2": 150,
    "E3": 100,
    "S1": 0,
    "S2": 0,
    "S3": 0
})
print(f"   Targeted dev: {result}")

# === 4. ENTERPRISE DEALS ===
print("\n4. Processing enterprise deals...")

# Get all open threads
threads = nm.query("""SELECT et.customer_id, c.group_id, et.thread_type, 
    et.turn_number, et.sender, et.day, et.offer_json
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0 AND et.sender != 'agent'
ORDER BY et.customer_id ASC, et.turn_number DESC""")

cust_threads = {}
for t in threads['rows']:
    cid = t['customer_id']
    if cid not in cust_threads:
        cust_threads[cid] = t

def compute_offer_price(their_price, turn, group='E1'):
    if group == 'E1':
        floor_b = 8.0
        floor_a = 5.0
    elif group in ['E2', 'E3']:
        floor_b = 12.0
        floor_a = 8.0
    else:
        floor_b = 8.0
        floor_a = 5.0
    
    if turn >= 4:
        my_offer = max(their_price * 1.05, floor_b)
    elif turn >= 3:
        my_offer = max(their_price * 1.10, floor_b * 1.2)
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
    
    try:
        offer_data = json.loads(t['offer_json']) if t['offer_json'] else {}
        their_price = offer_data.get('price', None)
    except:
        their_price = None
    
    # Handle urgent new_lead threads (age <= 7 days)
    if thread_type == 'new_lead' and age <= 7:
        if turn == 0 or their_price is None:
            if group == 'E1':
                deal = [cid, [["B", 20.0], ["A", 12.0]]]
            elif group == 'E2':
                deal = [cid, [["C", 40.0], ["B", 25.0]]]
            else:  # E3
                deal = [cid, [["C", 45.0], ["B", 28.0]]]
        else:
            b_price = compute_offer_price(their_price, turn, group)
            if group == 'E1':
                a_price = round(b_price * 0.6, 2)
                deal = [cid, [["B", b_price], ["A", a_price]]]
            else:
                c_price = round(b_price * 1.5, 2)
                deal = [cid, [["C", c_price], ["B", b_price]]]
        urgent_deals.append(deal)
    
    # Handle renegotiations (age <= 7)
    elif thread_type in ['renegotiation', 'plan_change'] and age <= 7:
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
    
    # Handle churn prevention (active subscribers only)
    elif thread_type == 'churn_prevention':
        sub = nm.query(f"SELECT plan, seat_count, effective_price FROM subscriptions WHERE status='subscribed' AND customer_id = {cid}")
        if sub['rows']:
            r = sub['rows'][0]
            plan = r['plan']
            current_price = r['effective_price']
            if their_price is not None:
                new_price = max(their_price * 1.05, current_price * 0.88)
                new_price = round(new_price, 2)
            else:
                new_price = current_price
            deal = [cid, [[plan, new_price]]]
            churn_deals.append(deal)

print(f"   Urgent deals: {len(urgent_deals)}")
print(f"   Churn prevention deals: {len(churn_deals)}")

all_deals = urgent_deals + churn_deals
if all_deals:
    batch_size = 20
    total_sent = 0
    for i in range(0, len(all_deals), batch_size):
        batch = all_deals[i:i+batch_size]
        try:
            result = nm.enterprise.send_enterprise_deal(deals=batch)
            total_sent += len(batch)
        except Exception as e:
            print(f"   Batch {i//batch_size + 1} error: {e}")
            for deal in batch:
                try:
                    nm.enterprise.send_enterprise_deal(deals=[deal])
                    total_sent += 1
                except Exception as e2:
                    print(f"     Failed {deal[0]}: {e2}")
    print(f"   Total deals sent: {total_sent}")

# === 5. Check social media ===
print("\n5. Social media check...")
posts = nm.analytics.get_social_posts(days=7, limit=20)
if posts and 'posts' in posts:
    recent = posts['posts'][:5]
    for p in recent:
        content = p.get('content', '')[:100]
        print(f"   [{p.get('group_id','?')}] {content}")

print("\n=== ACTIONS COMPLETE ===")
