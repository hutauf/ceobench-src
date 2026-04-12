import novamind_api as nm

# Handle old threads - check which ones have received customer responses
# The threads listed still open with sender=agent at old days
# BUT we already saw from analysis5b that some customers DID respond:
# - 27076 counter day=43: $18.49 Plan B
# - 29322 counter day=45: $9.08 Plan A
# - 28062 counter day=47: $13.29 Plan B
# - 28061 counter day=49: $2.06 Plan A
# - 18724 counter day=50: $4.17 Plan A

# Let me re-check all currently pending (sender=customer or system) threads
print("--- All open threads latest status ---")
r = nm.query("""SELECT et.message_id, et.customer_id, c.group_id, et.thread_type,
    et.turn_number, et.sender, et.day, et.message_text, et.offer_json
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0 
GROUP BY et.customer_id
HAVING et.turn_number = MAX(et.turn_number)
ORDER BY et.sender DESC, et.day ASC""")
print(f"Total open: {len(r['rows'])}")
waiting_customer = [r for r in r['rows'] if r['sender'] in ('customer', 'system') and r['day'] >= 43]
print(f"\nAwaiting our response (sender=customer/system, day>=43): {len(waiting_customer)}")
for row in waiting_customer:
    msg = row['message_text'][:100] if row['message_text'] else ''
    print(f"  C{row['customer_id']} ({row['group_id']}) {row['thread_type']} turn={row['turn_number']} day={row['day']}: {msg}")

# Check if the old E1 leads that timed out (14075, 16858) are really gone
print("\n--- Checking stale leads (old new_lead threads from day 14-35) ---")
r2 = nm.query("""SELECT et.customer_id, c.group_id, et.thread_type, et.turn_number, et.sender, et.day
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0 AND et.day < 36
GROUP BY et.customer_id
HAVING et.turn_number = MAX(et.turn_number)""")
for row in r2['rows']:
    print(f"  C{row['customer_id']} ({row['group_id']}) {row['thread_type']} turn={row['turn_number']} day={row['day']}")

# 1972: turn=3, sender=agent, day=14 → we sent offer, no response in 42 days → DEAD
# 2471: turn=5, sender=agent, day=21 → max turns probably 6, this is old → check subscription
# 14075: turn=0 day=23 → timed out  
# 16858: turn=0 day=27 → timed out
# 11449: churn_prevention turn=2 agent day=35 → might have churned
# 21828: new_lead turn=1 agent day=35 → BUT they're now subscribed! (E2, 608 seats, $40)

# Check subscriptions for these customers
print("\n--- Subscription status for old thread customers ---")
r3 = nm.query("""SELECT s.customer_id, c.group_id, s.plan, s.effective_price, s.status, s.seat_count
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
WHERE s.customer_id IN (1972, 2471, 14075, 16858, 11449, 21828)""")
for row in r3['rows']:
    print(f"  C{row['customer_id']} ({row['group_id']}): {row['seat_count']} seats Plan {row['plan']} @ ${row['effective_price']} - {row['status']}")
