import novamind_api as nm

# === ENTERPRISE DEAL STRATEGY ===
# Current quality: Plan C = 0.386 (E2/E3), Plan A = 0.279 (E1)
# E1: q_min=0.258, WTP=$33/seat -> Plan A at $10-15 works
# E2: q_min=0.625, WTP=$88/seat -> Plan C at 0.386 BELOW threshold - can't close legitimately
#   BUT customer 21828 (E2) already subscribed at $40/seat Plan C - keep them!
# E3: q_min=0.401, WTP=$104/seat -> Plan C at 0.411 barely ABOVE for S3 (E3 gets ~same)
#   E3 group bonus = 0 currently, so Plan C for E3 = 0.3856... might be below!
#   Actually looking at the dashboard: S3 Plan C = 0.4112 but E3 = 0.3856
#   E3 q_min=0.401 vs delivery 0.3856 → BELOW. Can't close E3 currently.

# === CRITICAL: Respond to churn prevention threads FIRST ===
# 30370 (E1, 485 seats, $12/seat = $5,820/mo) - wants price reduction
# 22828 (E1, 455 seats, $9/seat = $4,095/mo) - wants price reduction  

# Both are at low prices already. Give them modest discount to keep them.
# 30370: currently $12/seat → offer $11/seat Plan A (still good)
# 22828: currently $9/seat → offer $9/seat Plan A (keep same, they're already cheap)

# === Active negotiations (customer countered) ===
# 27076 (E2, 445 seats): Counter $18.49 Plan B. E2 needs q_min=0.625, we deliver 0.35. Can't meet quality.
#   But they already countered... maybe they can subscribe at current quality? Customer 21828 did.
#   Risk: if they subscribe and quality is below their expectation, they churn quickly.
#   Still, better to try. Counter at $22 Plan B (they asked $18.49).
# 29322 (E1, 410 seats): Counter $9.08 Plan A. WTP=$33, we can do better. Counter $13 Plan A.  
# 28062 (E1, 200 seats): Counter $13.29 Plan B. Plan B quality 0.35 > E1 q_min 0.258 ✓. Counter $17 Plan B.
# 28061 (E1, 144 seats): Counter $2.06 Plan A. Way too low. Counter $10 Plan A (final).
# 18724 (E1, 315 seats): Counter $4.17 Plan A, turn 4 (out of 6). Counter $10 Plan A.

# === New leads (turn 0, need to respond with opening offer) ===
# E1 new leads: give Plan A at $18 as opening offer
# E2 new leads: give Plan C at $45, Plan B at $25 (they may not qualify on quality but let's try)  
# E3 new leads: give Plan C at $50, Plan B at $30 (quality 0.386 borderline for E3 q_min=0.401)

# === BATCH SEND DEALS ===
print("Sending churn prevention responses...")

# PRIORITY 1: Churn prevention (respond immediately)
result1 = nm.enterprise.send_enterprise_deal(deals=[
    [30370, [["A", 11.0]]],   # Churn prevention: 485 seats, keep at $11 (was $12)
    [22828, [["A", 9.0]]],    # Churn prevention: 455 seats, keep at $9 (already low)
])
print(f"Churn prevention: {result1}")

print("\nSending active negotiation counters...")

# PRIORITY 2: Active negotiations (customer has countered, need our reply)
result2 = nm.enterprise.send_enterprise_deal(deals=[
    [29322, [["A", 13.0], ["B", 19.0]]],  # E1, 410 seats, counter was $9.08 Plan A
    [28062, [["B", 16.0], ["A", 11.0]]],  # E1, 200 seats, counter was $13.29 Plan B
    [28061, [["A", 10.0]]],               # E1, 144 seats, counter was $2.06 Plan A (last chance)
    [18724, [["A", 10.0], ["B", 16.0]]], # E1, 315 seats, counter was $4.17, turn 4/6
])
print(f"Active negotiations: {result2}")

print("\nSending offers to new E1 leads (turn=0)...")

# PRIORITY 3: New E1 leads (lots of them!)
# E1 WTP=$33, q_min=0.258, Plan A quality=0.279 barely above. Plan B=0.372 well above.
# Strategy: offer Plan B at $20 + Plan A at $14 as options
e1_new_leads = [31531, 32822, 34110, 34111, 34112, 35246, 35875, 35876, 35877,
                36570, 36571, 36572, 37639, 37640, 38854, 38855, 38856,
                40180, 40181, 41484, 41485, 41486, 41487, 41488, 41489,
                42641, 42642, 42643, 43320, 43321, 43324, 44026, 44029,
                45174, 45175]

deals_e1 = [[cid, [["B", 20.0], ["A", 14.0]]] for cid in e1_new_leads]
result3 = nm.enterprise.send_enterprise_deal(deals=deals_e1)
print(f"E1 new leads: {result3}")

print("\nSending offers to new E2/E3 leads...")

# E2 new leads: quality 0.386 vs q_min=0.625 (±65% = 0.219-1.031) - very uncertain
# Some E2 may have lower q_min. Customer 21828 subscribed at Plan C. Try Plan C $40.
e2_new_leads = [31533, 34114, 38857, 40183, 40185, 40186, 41490, 42645, 44026, 45177, 45178]
deals_e2 = [[cid, [["C", 45.0], ["B", 25.0]]] for cid in e2_new_leads]
result4 = nm.enterprise.send_enterprise_deal(deals=deals_e2)
print(f"E2 new leads: {result4}")

# E3 new leads: q_min=0.401, Plan C delivery = 0.386 (BELOW), but ±65% variance
# Some E3 may have q_min as low as 0.140. Risk but worth trying.
e3_new_leads = [37643, 38861, 43324, 44029]
deals_e3 = [[cid, [["C", 50.0], ["B", 30.0]]] for cid in e3_new_leads]
result5 = nm.enterprise.send_enterprise_deal(deals=deals_e3)
print(f"E3 new leads: {result5}")
