import novamind_api as nm

day = nm.vars.current_day
print(f"=== QUALITY vs QMIN ANALYSIS Day {day} ===\n")

# Current quality from dashboard:
# S1 Plan A T2: 0.2359, Plan B T4: 0.3145
# S2 Plan A T2: 0.3154, Plan B T4: 0.4205
# S3 Plan A T2: 0.3037, Plan B T4: 0.4049
# E1 Plan C T4: 0.3544
# E3 Plan C T4: 0.4214

# With info_level=1 and ±65% noise, estimates are very unreliable
# But from behaviors we can infer:
# - 0% conversion means ALL new leads require quality > what we deliver
# - S1 has simplest needs, but 1047 existing subs retained (so old q_min was lower)
# - New leads must have higher q_min requirements (post-competitor event)

# Key question: what q_min do we need to convert new leads?
# S1 existing subs: billing day varies, some will churn at next billing
# The cancellations this week: 655 total

# From info_level=1 estimates (±65%):
# S1 q_min estimate: 0.081 (with ±65% noise = real value 0.028-0.134? useless)
# But we know S1 has 0% conversion with quality 0.2359 (Plan A T2)
# This means current q_min for new S1 leads > 0.2359

# Post-competitor events raised q_min for all groups
# Our quality needs to be ABOVE the individual's q_min
# The competitor events added +0.2657 + 0.2657*2 + 0.2657 approximately

# Current: 1047 S1 subs survived (were subscribed before competitor event)
# Their existing q_min was met. New leads: higher q_min, 0% conversion

# Let's look at the individual sub billing schedule
r = nm.query(f"""
SELECT c.group_id, COUNT(*) as count, 
       MIN(s.billing_day_mod30) as min_bill,
       AVG(s.billing_day_mod30) as avg_bill
FROM subscriptions s JOIN customers c ON s.customer_id=c.customer_id
WHERE s.status='subscribed' AND c.customer_type='small'
GROUP BY c.group_id
""")
print("=== INDIVIDUAL SUB BILLING SCHEDULE ===")
for row in r['rows']:
    print(f"  {row['group_id']}: {row['count']} subs | billing_day_mod30 avg={row['avg_bill']:.1f}")

# Check billing_day_mod30 distribution for S1 to see when next big billing event
r = nm.query(f"""
SELECT s.billing_day_mod30, COUNT(*) as n
FROM subscriptions s JOIN customers c ON s.customer_id=c.customer_id
WHERE s.status='subscribed' AND c.customer_type='small' AND c.group_id='S1'
GROUP BY s.billing_day_mod30
ORDER BY s.billing_day_mod30
""")
print("\n=== S1 BILLING DAY DISTRIBUTION (mod30) ===")
mod30 = day % 30
print(f"  Today mod30 = {mod30} (day {day})")
for row in r['rows']:
    days_until = (row['billing_day_mod30'] - mod30) % 30
    print(f"  billing_mod30={row['billing_day_mod30']:2d}: {row['n']:4d} subs | days_until={days_until}")

# How much revenue can we expect from individual subs per week?
print(f"\n=== INDIVIDUAL SUB MONTHLY REVENUE ===")
r = nm.query("""
SELECT c.group_id, COUNT(*) as n, AVG(s.effective_price) as avg_price, 
       SUM(s.effective_price) as total_monthly
FROM subscriptions s JOIN customers c ON s.customer_id=c.customer_id
WHERE s.status='subscribed' AND c.customer_type='small'
GROUP BY c.group_id
""")
total = 0
for row in r['rows']:
    total += row['total_monthly']
    print(f"  {row['group_id']}: {row['n']} subs × ${row['avg_price']:.2f} = ${row['total_monthly']:.0f}/mo")
print(f"  TOTAL INDIVIDUAL: ${total:.0f}/mo = ${total/30:.0f}/day")

# What about the 23656 renegotiation thread - is it really still open?
r = nm.query("""
SELECT et.message_id, et.thread_id, et.thread_type, et.turn_number, et.sender, 
       et.day, et.closed, et.close_reason, et.offer_json
FROM enterprise_turns et
WHERE et.customer_id=23656 AND et.thread_id=57
ORDER BY et.turn_number
""")
print("\n=== 23656 RENEGOTIATION THREAD 57 ===")
for row in r['rows']:
    print(f"  turn {row['turn_number']} | {row['sender']} | day {row['day']} | closed={row['closed']} | close_reason={row['close_reason']}")
    if row['offer_json'] and row['offer_json'] != '{}':
        print(f"    offer: {row['offer_json']}")

# Check contract end day - it was 118, we're at 119
# The payment happened. Did the contract auto-extend?
r = nm.query("""
SELECT customer_id, plan, effective_price, contract_end_day, status, start_day, billing_day_mod30
FROM subscriptions WHERE customer_id=23656 ORDER BY start_day DESC LIMIT 3
""")
print("\n=== 23656 SUBSCRIPTION HISTORY ===")
for row in r['rows']:
    print(f"  plan={row['plan']} price=${row['effective_price']} start={row['start_day']} end={row['contract_end_day']} status={row['status']}")

# Does 23656 need a NEW renegotiation sent?
# contract_end=118, today=119 - it paid $35,340 so it's extended somehow
# The renegotiation thread (tid=57) is still open at turn 1 (my offer)
# This means customer hasn't replied yet to my proactive renegotiation
# But they auto-renewed at month-to-month... interesting

print("\n=== COST ANALYSIS ===")
# What are actual costs?
r = nm.query(f"""
SELECT category, SUM(amount) as total
FROM ledger WHERE day >= {day-7}
GROUP BY category ORDER BY total
""")
for row in r['rows']:
    print(f"  {row['category']}: ${row['total']:.0f}")
