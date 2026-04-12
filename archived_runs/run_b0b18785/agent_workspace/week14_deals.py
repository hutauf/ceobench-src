import novamind_api as nm
import json

day = nm.vars.current_day
print(f"Day {day} - Sending enterprise deals")

# === CHURN PREVENTION FOR EXISTING SUBSCRIBERS ===
# Strategy: offer slight discount to retain, but keep profitable
# E1 Plan A subscribers: offer B$17/A$8.98 (maintain current or slight raise)
# E1 Plan B subscribers: keep at current price or offer small discount
# E2 Plan C subscribers: keep at current
# E3 Plan B subscribers: keep at current

churn_deals = [
    # E1 - Plan A subscribers (30370, 41484, 41486, 46585) 
    [30370, [["A", 8.98], ["B", 17.00]]],   # 485 seats Plan A @$7.94 → offer B$17/A$8.98
    [41484, [["A", 8.98], ["B", 17.00]]],   # 385 seats Plan A @$8.66
    [41486, [["A", 8.98], ["B", 17.00]]],   # 399 seats Plan A @$8.66
    [46585, [["A", 8.98], ["B", 17.00]]],   # 410 seats Plan A @$8.98
    # E1 - Plan B subscribers
    [52387, [["A", 8.98], ["B", 14.43]]],   # 471 seats Plan B @$14.43 - keep
    [62808, [["A", 8.66], ["B", 17.00]]],   # 244 seats Plan B @$17.00 - keep
    [65556, [["A", 8.66], ["B", 17.00]]],   # 178 seats Plan B @$17.00 - keep
    [69424, [["A", 10.20], ["B", 17.00]]],  # 113 seats Plan A @$10.20 - keep
    [69427, [["A", 8.66], ["B", 17.00]]],   # 91 seats Plan B @$17.00 - keep
    [75423, [["A", 8.66], ["B", 20.00]]],   # 156 seats Plan B @$20.00 - keep
    # E2 - Plan C and B subscribers
    [46588, [["B", 22.00], ["C", 28.86]]],  # 871 seats Plan C @$28.86 - keep
    [46594, [["B", 22.00], ["C", 28.86]]],  # 692 seats Plan C @$28.86 - keep
    [52389, [["B", 18.04], ["C", 35.00]]],  # 301 seats Plan B @$18.04 - keep
    [66815, [["B", 22.00], ["C", 40.00]]],  # 809 seats Plan C @$40.00 - keep at full
    [72455, [["B", 22.00], ["C", 40.00]]],  # 455 seats Plan C @$40.00 - keep
    [72456, [["B", 25.00], ["C", 40.00]]],  # 842 seats Plan B @$25.00 - keep
    # E3 - Plan B subscribers
    [29324, [["B", 20.00], ["C", 40.00]]],  # 1875 seats Plan B @$20.00 - keep
    [68260, [["B", 20.00], ["C", 40.00]]],  # 2000 seats Plan B @$20.00 - keep
]

print(f"Sending {len(churn_deals)} churn prevention deals...")
result = nm.enterprise.send_enterprise_deal(deals=churn_deals)
print(f"Result: {result}")

