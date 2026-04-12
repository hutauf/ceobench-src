import novamind_api as nm

day = nm.vars.current_day
print(f"=== VERIFICATION Day {day} ===\n")

# Verify current config
r = nm.query("""
SELECT day, category, SUM(amount) as total
FROM ledger WHERE day = (SELECT MAX(day) FROM ledger)
GROUP BY category
""")
print("=== TODAY'S COSTS ===")
for row in r['rows']:
    print(f"  {row['category']}: ${row['total']:.0f}")

# Verify quality after T3 upgrade
print("\n=== EXPECTED NEW QUALITY (Plan A T3=0.90x) ===")
# base=0.20, global_bonus=0.1020 (from dashboard)
base = 0.20
global_bonus = 0.1020
group_bonuses = {'S1': 0.0125, 'S2': 0.1185, 'S3': 0.1029, 'E1': 0.0524, 'E3': 0.1194}
tiers = {'A': 0.90, 'B': 1.00, 'C': 1.00}  # T3, T4, T4

for group, gb in group_bonuses.items():
    total_base = base + global_bonus + gb
    qa = total_base * tiers['A']
    qb = total_base * tiers['B']
    print(f"  {group}: Plan A T3={qa:.4f} | Plan B/C T4={qb:.4f} | base_q={total_base:.4f}")

# Upcoming enterprise billing
print("\n=== UPCOMING ENTERPRISE BILLING ===")
r = nm.query(f"""
SELECT s.customer_id, s.effective_price, s.contract_end_day, s.billing_day_mod30, c.group_id
FROM subscriptions s JOIN customers c ON s.customer_id=c.customer_id
WHERE s.status='subscribed' AND c.customer_type='large'
ORDER BY s.contract_end_day
""")
print(f"Today: Day {day} (mod30={day%30})")
for row in r['rows']:
    # When is next billing?
    mod30_today = day % 30
    mod30_bill = row['billing_day_mod30']
    days_until_bill = (mod30_bill - mod30_today) % 30
    next_bill_day = day + days_until_bill
    if days_until_bill == 0:
        days_until_bill = 30
        next_bill_day = day + 30
    print(f"  Cust {row['customer_id']} ({row['group_id']}) ${row['effective_price']}/seat | contract_end={row['contract_end_day']} | bill_mod30={mod30_bill} | next_bill=Day {next_bill_day} (in {days_until_bill} days)")

# Check 23656 thread after our renewal
print("\n=== 23656 THREAD STATUS AFTER RENEWAL ===")
r = nm.query("""
SELECT et.message_id, et.thread_id, et.thread_type, et.turn_number, et.sender, 
       et.day, et.closed, et.close_reason, et.offer_json
FROM enterprise_turns et
WHERE et.customer_id=23656 AND et.thread_id=57
ORDER BY et.turn_number DESC LIMIT 5
""")
for row in r['rows']:
    print(f"  turn {row['turn_number']} | {row['sender']} | day {row['day']} | closed={row['closed']} | close_reason={row['close_reason']}")
    if row['offer_json'] and row['offer_json'] != '{}':
        print(f"    offer: {row['offer_json']}")

# Check current configuration
print("\n=== CURRENT CONFIG (from get_cost_info) ===")
ci = nm.infrastructure.get_cost_info()
print(f"  Capacity tier: {ci.get('current_tier')}")
print(f"  Tier details: {ci.get('tier_details', {})}")
