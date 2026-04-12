import novamind_api as nm

# Get exact seat counts from payments
# 34622: paid $1,776 at $13.50/seat = 131.6 seats ≈ 132 seats
# 13886: paid $5,880 at $14.00/seat = 420 seats (confirmed)
# 24156: paid $2,268 at $14.00/seat = 162 seats
# 761: paid $6,188 at $13.00/seat = 476 seats (confirmed)
# 33183: closed at $13.00, 465 seats (confirmed)
# 28088: closed at $13.00, 470 seats (confirmed)
# 15824: closed at $14.00, 264 seats (confirmed)

print("=== CONFIRMED SEAT COUNTS FROM DEAL CLOSURES ===")
print("761:   476 seats @ $12.50 = $5,950/mo")
print("13886: 420 seats @ $14.00 = $5,880/mo")
print("15824: 264 seats @ $14.00 = $3,696/mo")
print("23656: 1767 seats @ $20.00 = $35,340/mo")
print("24156: 162 seats @ $14.00 = $2,268/mo")  # from payment
print("28088: 470 seats @ $13.00 = $6,110/mo")
print("33183: 465 seats @ $13.00 = $6,045/mo")
print("34622: ~132 seats @ $13.50 = $1,782/mo")  # from payment $1,776

total = 5950 + 5880 + 3696 + 35340 + 2268 + 6110 + 6045 + 1782
print(f"\nTotal enterprise MRR: ${total:,.0f}/mo = ${total/30:,.0f}/day")
print(f"Individual MRR: ~$30,242/mo = $1,008/day")
print(f"Total MRR: ~${(total+30242):,.0f}/mo")

# 34622 contract ends Day 125 - should we proactively renegotiate?
# Current price: $13.50/seat
# E1 WTP estimate: $19.62 (±65% = ~$7-33 range)
# Their current contract is fine, just needs renewal
# Send a proactive renewal at same price to lock it in
day = nm.vars.current_day
print(f"\nDay {day}: 34622 contract ends Day 125 (6 days)")
print("Will proactively send renewal at $13.50/seat (same price)")
result = nm.enterprise.send_enterprise_deal(
    deals=[[34622, [["C", 13.5]]]]
)
print(f"  ✓ 34622 renewal sent: {result}")

# Also proactively renew 13886 (contract ends Day 133, 14 days away)
print("Day {}: 13886 contract ends Day 133 (14 days)")
result = nm.enterprise.send_enterprise_deal(
    deals=[[13886, [["C", 14.0]]]]
)
print(f"  ✓ 13886 renewal sent: {result}")
