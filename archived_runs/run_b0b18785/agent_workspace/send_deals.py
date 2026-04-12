import novamind_api as nm

# CURRENT QUALITY STATUS:
# E1 Plan B: 0.3322 (well above E1 q_min 0.258) ✓
# E2 Plan B: 0.3199 (well below E2 q_min 0.625) ✗
# E1 WTP: ~$33/seat (±40% noise)
# E2 WTP: ~$88/seat (±40% noise)

# STRATEGY FOR EACH THREAD:
# Thread 6 (cid=18724): E1, 315 seats, budget-compliance concern, mid-market
#   -> Offer Plan B $25, Plan A $15 (start high, room to negotiate)
# Thread 7 (cid=11449): E1, 115 seats, CHURN PREVENTION - they said pricing doesn't work
#   -> They're on Plan B @ $16. Offer to keep $16 or sweeten slightly to keep them
#   -> Offer Plan B $14, Plan A $10 (show willingness to work with them)
# Thread 8 (cid=21828): E2, 608 seats, compliance concern
#   -> Quality is too low for E2 but we can still make an offer for Plan B/C
#   -> They may reject due to quality but worth trying Plan C which is highest quality
#   -> Plan C quality: 0.3519 still << E2 q_min 0.625 - likely won't accept
#   -> Offer Plan B $30, Plan C $45 (aspirational pricing, they'll counter or reject)
#   -> Actually better to offer reasonable price to at least close something
# Thread 9 (cid=22828): E1, 455 seats, budget-compliance, regional
#   -> Offer Plan B $25, Plan A $14

print("=== SENDING ENTERPRISE DEALS ===")

# Thread 6 - cid=18724, E1, 315 seats, budget-compliance
# Thread 7 - cid=11449, E1, 115 seats, churn prevention (need to retain at $14-16)  
# Thread 8 - cid=21828, E2, 608 seats (quality too low but let's offer Plan C)
# Thread 9 - cid=22828, E1, 455 seats, budget-compliance

result = nm.enterprise.send_enterprise_deal(deals=[
    [18724, [["B", 25.0], ["A", 15.0]]],     # T6: E1, 315 seats, start $25/seat Plan B
    [11449, [["B", 14.0], ["A", 10.0]]],     # T7: E1, churn prevention - keep at $14, offer A at $10
    [21828, [["C", 40.0], ["B", 28.0]]],     # T8: E2, 608 seats - offer premium plans
    [22828, [["B", 25.0], ["A", 14.0]]],     # T9: E1, 455 seats, start $25/seat Plan B
])
print("Send deals result:", result)
