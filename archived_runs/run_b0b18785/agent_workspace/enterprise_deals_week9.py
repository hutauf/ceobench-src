import novamind_api as nm

print(f"Current day: {nm.vars.current_day}")

# === CHURN PREVENTION (active subscribers needing retention) ===
# 41484: 385 seats Plan A $14 → offer $12/seat Plan A (keep them)
# 41486: 399 seats Plan A $14 → offer $12/seat Plan A (keep them)  
# 41488: 84 seats Plan B $20 → offer $16/seat Plan B or $12/seat Plan A (give options)
print("\n=== CHURN PREVENTION ===")
try:
    result = nm.enterprise.send_enterprise_deal(deals=[
        [41484, [["A", 12.0]]],
        [41486, [["A", 12.0]]],
        [41488, [["B", 16.0], ["A", 10.0]]],
    ])
    print("Churn prevention sent:", result)
except Exception as e:
    print(f"Error churn prevention: {e}")

# === COUNTER-OFFERS FROM CUSTOMERS ===
# E1 WTP ~$33/seat. Reasonable counter threshold: accept if >$8, counter at $11-13 if moderate

# 29322 (E1 established-regional): countered $9.08 Plan A → accept at $11 Plan A (good enough)
# 28062 (E1 mid-market): countered $13.29 Plan B → accept at $13.29 Plan B! 
# 43321 (E1 regional): countered $13.67 Plan B → accept at $13.67!
# 42642 (E1 growing): countered $4.04 Plan A → too low, counter at $10 Plan A
# 25899 (E3 industry-leader): countered $14.19 Plan B → E3 WTP ~$104, accept at $14!
# 27076 (E2 established): countered $18.49 Plan B → E2 WTP ~$88, accept at $20 Plan B
# 28061 (E1 growing): countered $2.06 Plan A → very low, counter at $9 Plan A (final)
# 40180 (E1 multi-location): countered $5.47 Plan B → counter at $12 Plan A
# 40181 (E1 multi-location): countered $1.83 Plan A → very low, counter at $9 Plan A (final)
# 42641 (E1 growing): countered $3.31 Plan B → counter at $10 Plan A
# 43320 (E1 multi-location): countered $2.92 Plan B → counter at $10 Plan A

print("\n=== COUNTER-OFFERS ===")

# Accept good counters
accept_deals = [
    [28062, [["B", 13.29]]],      # Accepting their counter $13.29/seat Plan B
    [43321, [["B", 13.67]]],      # Accepting their counter $13.67/seat Plan B
    [25899, [["B", 14.19]]],      # E3 industry-leader at $14.19/seat Plan B (good!)
    [27076, [["B", 20.0]]],       # E2 established - offering $20 Plan B (was $18.49)
    [29322, [["A", 11.0]]],       # E1 established-regional at $11
]

try:
    result = nm.enterprise.send_enterprise_deal(deals=accept_deals)
    print("Accepted counters sent:", result)
except Exception as e:
    print(f"Error accepting counters: {e}")

# Counter very low bids with firm lower prices
low_counter_deals = [
    [28061, [["A", 9.0]]],        # E1 growing - firm at $9 (was $2.06)
    [40180, [["A", 12.0], ["B", 16.0]]],  # E1 multi-loc - $12 Plan A or $16 Plan B
    [40181, [["A", 9.0]]],        # E1 multi-loc - firm at $9 (was $1.83)
    [42641, [["A", 10.0]]],       # E1 growing - $10 Plan A
    [42642, [["A", 10.0]]],       # E1 growing - $10 Plan A (was $4.04)
    [43320, [["A", 10.0], ["B", 14.0]]],  # E1 multi-loc - $10 Plan A or $14 Plan B
]

try:
    result = nm.enterprise.send_enterprise_deal(deals=low_counter_deals)
    print("Low counter responses sent:", result)
except Exception as e:
    print(f"Error low counters: {e}")

# === NEW E1 LEADS (Turn 0, need first offer) ===
# Days 57-63 should be valid (within 7 day timeout from day 63)
# Days before 56 are likely expired - skip those risky ones, try anyway
e1_new_leads_recent = [
    46585, 46586, 46587,  # Day 57
    47987, 47988,  # Day 58
    49410, 49411, 49412, 49413, 49414, 49415, 49416,  # Day 59
    50750, 50751, 50752, 50753, 50754, 50755,  # Day 60
    51544, 51545, 51546, 51547,  # Day 61
    52384, 52385, 52386, 52387,  # Day 62
    53606, 53607, 53608, 53609,  # Day 63
]

# Older leads (may be expired but try)
e1_old_leads = [14075, 16858, 31531, 32822, 34110, 34111, 34112, 35246, 35875, 35876, 35877, 36570, 36571, 36572, 37639, 37640]

print("\n=== E1 NEW LEADS - RECENT ===")
e1_deals = [[cid, [["B", 20.0], ["A", 12.0]]] for cid in e1_new_leads_recent]
try:
    result = nm.enterprise.send_enterprise_deal(deals=e1_deals)
    print(f"E1 recent leads ({len(e1_new_leads_recent)}):", result)
except Exception as e:
    print(f"Error E1 recent: {e}")

print("\n=== E1 NEW LEADS - OLDER (may be expired) ===")
for cid in e1_old_leads:
    try:
        result = nm.enterprise.send_enterprise_deal(deals=[[cid, [["B", 20.0], ["A", 12.0]]]])
        print(f"  {cid}: OK")
    except Exception as e:
        print(f"  {cid}: EXPIRED - {e}")

# === NEW E2 LEADS ===
e2_new_leads_recent = [
    46588, 46589, 46594,  # Day 57
    47989, 47991, 47992,  # Day 58
    49417, 49420,  # Day 59
    51550,  # Day 61
    52389,  # Day 62
    53613, 53616,  # Day 63
]
e2_old_leads = [31533, 34114]

print("\n=== E2 NEW LEADS ===")
# E2 quality is 0.399 (Plan C). WTP ~$88. Their q_min is uncertain but 21828 subscribed.
# Offer Plan C $40 (same as current sub) + Plan B $25 as fallback
e2_deals = [[cid, [["C", 40.0], ["B", 25.0]]] for cid in e2_new_leads_recent]
try:
    result = nm.enterprise.send_enterprise_deal(deals=e2_deals)
    print(f"E2 recent leads ({len(e2_new_leads_recent)}):", result)
except Exception as e:
    print(f"Error E2 recent: {e}")

for cid in e2_old_leads:
    try:
        result = nm.enterprise.send_enterprise_deal(deals=[[cid, [["C", 40.0], ["B", 25.0]]]])
        print(f"  E2 old {cid}: OK")
    except Exception as e:
        print(f"  E2 old {cid}: EXPIRED - {e}")

# === NEW E3 LEADS ===
e3_new_leads_recent = [
    47993, 47995,  # Day 58
    49423,  # Day 59
    52390, 52391,  # Day 62
]
e3_old_leads = [37643]

print("\n=== E3 NEW LEADS ===")
# E3 quality is 0.396 (Plan C). WTP ~$104. q_min ~0.401 (borderline)
# Plan B quality 0.3599 - below E3 q_min. Plan C 0.3959 also below but close
# Offer Plan C $45 as our best - some may accept
e3_deals = [[cid, [["C", 45.0], ["B", 25.0]]] for cid in e3_new_leads_recent]
try:
    result = nm.enterprise.send_enterprise_deal(deals=e3_deals)
    print(f"E3 recent leads ({len(e3_new_leads_recent)}):", result)
except Exception as e:
    print(f"Error E3 recent: {e}")

for cid in e3_old_leads:
    try:
        result = nm.enterprise.send_enterprise_deal(deals=[[cid, [["C", 45.0], ["B", 25.0]]]])
        print(f"  E3 old {cid}: OK")
    except Exception as e:
        print(f"  E3 old {cid}: EXPIRED - {e}")

print("\n=== DONE ===")
