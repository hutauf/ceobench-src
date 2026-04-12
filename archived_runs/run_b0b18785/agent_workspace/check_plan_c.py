import novamind_api as nm

print("=== PLAN C SUBSCRIBERS ===")
r = nm.query("""
SELECT c.group_id, COUNT(*) as n FROM subscriptions s
JOIN customers c ON s.customer_id=c.customer_id
WHERE s.plan='C' AND s.status='subscribed'
GROUP BY c.group_id
""")
print(r['rows'])

print("\n=== WEEK 5 GROWTH ANALYSIS ===")
print("S1: 789 new subs this week! (up from 283 last week)")
print("S2: 77 new subs this week! (up from 10 last week)")
print("S3: 146 new subs this week! (up from 31 last week)")
print()
print("AMAZING growth! R&D completion (T1+T2) pushed quality over thresholds")
print("S2 now converting (62 Plan A + 25 Plan B from last 14 days)")
print("  - S2 q_min estimate 0.37, current B quality 0.3199")
print("  - Wait... S2 IS converting at 2.2% despite quality gap?")
print("  - Maybe S2 q_min is lower than estimated (info level 1 ±65% noise)")
print("  - Could be actual q_min is much lower, like 0.13-0.62 range")
print()
print("KEY INSIGHT: S2 has WTP $179 and they ARE subscribing!")
print("  If we raise Plan B to $79: 25 subs × $20 more = $500/mo extra immediately")
print("  New S2 leads: more revenue at $79 vs $59")
print("  RISK: May kill some S2 conversions if their q_min is borderline")
print()
print("Decision: RAISE Plan B to $79 - S3 WTP $188 and S2 WTP $179 can both handle it")

print("\n=== PROMOTION ANALYSIS ===")
print("No active promotions. Consider lead promotions for S3?")
print("S3 is 6.5% conversion rate - high value (Plan B mostly)")
print("A 5% lead promotion would make Plan B effectively $56 for leads")
print("Better to invest in higher Plan B price and let quality attract them")
