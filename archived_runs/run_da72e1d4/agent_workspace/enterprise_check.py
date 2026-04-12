import novamind_api as nm

day = nm.vars.current_day

# Check 13886 - contract ends Day 133, should we proactively negotiate?
# And 34622 contract ends Day 125 - close, should prepare
print("=== ENTERPRISE CONTRACT RENEWALS UPCOMING ===")
print(f"Day {day} (today)")
print()
print("Cust 34622 (E1, ~209 seats @$13.50): contract_end=125 (6 days from now)")
print("  → Start renegotiation soon? Or wait for natural renewal?")
print()
print("Cust 13886 (E1, ~420 seats @$14.00): contract_end=133 (14 days from now)")
print("  → Still have time")
print()

# Get seats from ledger (payments) to confirm seat counts
r = nm.query("""
SELECT note, amount 
FROM ledger 
WHERE category='subscription_payment' 
AND (note LIKE '%13886%' OR note LIKE '%34622%' OR note LIKE '%24156%')
AND amount > 0
ORDER BY day DESC LIMIT 10
""")
for row in r['rows']:
    print(f"  ${row['amount']:.0f} | {row['note']}")

# Check if 34622 or 13886 have any open threads that need attention
r = nm.query("""
SELECT et.customer_id, et.thread_type, et.turn_number, et.sender, 
       et.day, et.closed, c.group_id
FROM enterprise_turns et JOIN customers c ON et.customer_id=c.customer_id
WHERE et.customer_id IN (13886, 34622, 24156)
AND et.closed=0
ORDER BY et.customer_id, et.day DESC
""")
print("\n=== 13886/34622/24156 OPEN THREADS ===")
for row in r['rows']:
    print(f"  Cust {row['customer_id']} ({row['group_id']}) | {row['thread_type']} | turn {row['turn_number']} | {row['sender']} | day {row['day']}")
