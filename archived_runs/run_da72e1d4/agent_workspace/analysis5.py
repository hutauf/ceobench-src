import novamind_api as nm

day = nm.vars.current_day
print(f"=== SEAT COUNT FIX Day {day} ===\n")

# The seat count query is wrong - it needs to count employees, not subscription rows
# Let me check customers table for enterprise customers
r = nm.query("""
SELECT c.customer_id, c.group_id, c.email
FROM customers c
WHERE c.customer_type='large' AND c.customer_id IN (761, 13886, 15824, 23656, 24156, 28088, 33183, 34622)
ORDER BY c.customer_id
""")
for row in r['rows']:
    print(f"  Cust {row['customer_id']} ({row['group_id']}): {row['email']}")

# Check the subscriptions table structure for enterprise
r = nm.query("""
SELECT s.customer_id, s.plan, s.effective_price, s.contract_end_day, s.status,
       s.billing_day_mod30, s.start_day
FROM subscriptions s
WHERE s.customer_id IN (761, 13886, 15824, 23656, 24156, 28088, 33183, 34622)
AND s.status='subscribed'
ORDER BY s.customer_id
""")
for row in r['rows']:
    print(f"  Cust {row['customer_id']}: plan={row['plan']} price=${row['effective_price']} end={row['contract_end_day']} start={row['start_day']}")

# What is MRR from each enterprise customer?
# MRR = subscriptions with status=subscribed should show enterprise revenue
# Let's look at recent payments per enterprise customer
r = nm.query("""
SELECT s.customer_id, s.effective_price, l.amount, l.day, l.note
FROM ledger l
JOIN subscriptions s ON CAST(l.note AS TEXT) LIKE '%' || CAST(s.customer_id AS TEXT) || '%'
WHERE l.category='subscription_payment' AND l.day >= 88 AND l.amount > 5000
ORDER BY l.day DESC LIMIT 20
""")
print("\n=== LARGE SUBSCRIPTION PAYMENTS ===")
for row in r['rows']:
    print(f"  Day {row['day']}: ${row['amount']:.0f} | note: {row['note']}")

# Better approach: get all large payments  
r = nm.query(f"""
SELECT day, amount, note
FROM ledger
WHERE category='subscription_payment' AND amount > 3000 AND day >= 88
ORDER BY day DESC LIMIT 30
""")
print("\n=== ALL LARGE PAYMENTS (>$3k) ===")
for row in r['rows']:
    print(f"  Day {row['day']}: ${row['amount']:.0f} | {row['note']}")
