import novamind_api as nm

day = nm.vars.current_day

# Key metrics summary
print("=== WEEK 14 STRATEGIC ANALYSIS ===")
print(f"Day: {day}")
print(f"Cash: $76,432")

print("\nMRR: $926,520/mo = $30,884/day")
print("Daily costs: ~$26,155/day")
print("Net profit: ~$4,729/day (POSITIVE! MRR > costs when billed)")
print("BUT: Billing is lumpy, this week was -$21K net loss ($132K rev vs $153K costs)")

print("\n=== MRR BREAKDOWN ===")
print("E1: $306,342/mo (62 subs, 17,339 seats) ← MASSIVE GROWTH from Week 12!")
print("E2: $281,009/mo (16 subs, 8,481 seats) ← HUGE growth!")
print("S1: $130,495/mo (6,031 subs - DOWN from 6,757!)")
print("S3: $84,472/mo (1,634 subs)")
print("E3: $77,500/mo (2 subs, 3,875 seats)")
print("S2: $46,701/mo (1,394 subs)")

print("\n=== ISSUES STATUS ===")
print("S1: 7,970 (was 6,781) - STILL GROWING! avg 22.7 days (was 16.4!)")
print("S3: 2,095 (was 1,542) - growing")
print("S2: 1,438 (was 1,005) - growing")
print("E1: 23 - OK")
print("Total: 11,531 (was 9,347) - worsening!")
print("CRITICAL: Despite $4K/day targeted ops for S1, issues are growing!")

print("\n=== CAPACITY ===")
print("Usage: 1.3M/day vs capacity 2.5M/day - 52.6% utilized, OK for now")
print("With 80 enterprise customers (29,695 seats) - usage will grow")
print("Need to watch - may need Tier 4 upgrade if usage hits 2M/day")

print("\n=== KEY DECISIONS ===")
print("1. Issues crisis: S1 targeted ops at $4K/day not helping - consider different approach")
print("2. Cash: $76K is LOW. Need to conserve. Billing cycle may help soon")  
print("3. Enterprise growth: Massive! E1 now 62 subs (was ~40), E2 now 16 subs (was ~5)")
print("4. S1 subscribers dropped from 6,757 → 6,031 = losing 726 S1 subs")
print("5. Quality drift concern: competitor events will increase expectations over time")

# Check when big enterprise payments are due
upcoming = nm.query("""SELECT s.customer_id, s.plan, s.seat_count, s.effective_price, 
    s.seat_count*s.effective_price as monthly_rev,
    s.last_billing_day, (s.last_billing_day + 30) as next_billing_day
FROM subscriptions s
WHERE s.status='subscribed' AND s.seat_count >= 200
ORDER BY s.seat_count*s.effective_price DESC LIMIT 20""")

print("\n--- Upcoming Large Enterprise Billing (seats >= 200) ---")
for r in upcoming['rows']:
    next_bill = r['next_billing_day']
    days_til = next_bill - day if next_bill else 0
    print(f"  CID={r['customer_id']} Plan{r['plan']} {r['seat_count']}seats @${r['effective_price']:.2f} = ${r['monthly_rev']:,.0f}/mo | next_bill={next_bill} (in {days_til} days)")

