import novamind_api as nm

day = nm.vars.current_day
print(f"=== EXECUTING WEEK 17 ACTIONS (Day {day}) ===\n")

# ACTION 1: Upgrade Plan A from T2 to T3 (0.75x → 0.90x)
# This improves S1 quality from 0.2359 → 0.2830
# Compute cost increase: T3=$0.006 vs T2=$0.002 (+$0.004/unit)
# Estimated additional cost: ~$240/day (manageable)
print("Action 1: Upgrade Plan A model tier T2 → T3")
nm.pricing.set_model_tiers(A=3, B=4, C=4)
print("  ✓ Plan A=T3, Plan B=T4, Plan C=T4")

# ACTION 2: Increase global ops spending to reduce issue backlog
# S1 has 2758 issues averaging 24.3 days - massive churn driver
print("\nAction 2: Increase global ops spending")
nm.marketing.set_daily_spend(advertising=0, operations=800, development=500)
print("  ✓ Ops $500→$800/day, Dev $300→$500/day, Ads stay $0")

# ACTION 3: Increase targeted ops for S1 (main issue backlog)
print("\nAction 3: Increase targeted ops (S1 focus)")
nm.analytics.set_targeted_ops_spend(targeted_spend={"S1": 400, "E1": 100})
print("  ✓ S1: $200→$400/day, E1: $100/day (unchanged)")

# ACTION 4: Increase targeted dev for S1 quality accumulation
# S1 needs group bonus to grow: currently +0.0125, need +0.031+
# At $300/day targeted: 0.030 × ln(1 + 300/5000) = 0.030 × ln(1.06) = 0.030 × 0.0583 = 0.00175/day
# S1 quality with T3: needs grp_bonus > 0.031
# Currently 0.0125 → need 0.0185 more → at $300/day: 0.0185/0.00175 = ~10.6 days
print("\nAction 4: Increase targeted dev for S1")
nm.analytics.set_targeted_dev_spend(targeted_spend={"E3": 200, "S1": 300, "S2": 100, "S3": 100})
print("  ✓ S1: $100→$300/day, E3: $200/day, S2: $100/day, S3: $100/day")

# ACTION 5: Set S1 lead promotion to help new leads convert
# 25% discount on Plan A for S1 leads: $22 × 0.75 = $16.50
# This doesn't affect existing subscribers
# May help borderline S1 leads who can't afford $22 but can afford $16.50
print("\nAction 5: Set S1 lead promotion (25% discount)")
nm.marketing.set_lead_promotion(global_promotion=0, by_group={"S1": 20})
print("  ✓ S1 leads see Plan A at $22 × 0.80 = $17.60 (20% off)")

# ACTION 6: Proactively renew 23656 (E3, 1767 seats @ $20/seat)
# Contract ended Day 118, payment received Day 119 ($35,340)
# The renegotiation thread (57) is still open - I've sent 2 offers (Day 98, Day 112)
# Customer hasn't replied to renegotiation thread (they're just auto-paying)
# Send another renewal offer to maintain the relationship and lock in pricing
print("\nAction 6: Renew 23656 renegotiation")
try:
    result = nm.enterprise.send_enterprise_deal(
        deals=[[23656, [["C", 20.0]]]]
    )
    print(f"  ✓ Sent 23656 renewal at $20.00/seat: {result}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Check if 32405 churn_prevention thread needs response
# 32405: cancelled (sub_status=None), thread still open from Day 105
# This customer is ALREADY CANCELLED - can skip
print("\nAction 7: Handle 32405 (already cancelled, thread expired)")
# Don't respond to 32405 - already lost, waste of time
# Stale threads: 32045, 27484, 33184 (all cancelled) - skip

# Check for any new enterprise leads we should respond to
print("\nChecking for actionable new enterprise leads...")
r = nm.query("""
SELECT et.customer_id, et.thread_type, et.turn_number, et.sender, 
       et.message_text, et.offer_json, et.day, c.group_id
FROM enterprise_turns et JOIN customers c ON et.customer_id=c.customer_id
WHERE et.closed=0 AND et.sender IN ('customer','system') AND et.turn_number >= 1
AND et.day >= 110
ORDER BY et.day DESC
""")
print(f"Open actionable threads (since day 110):")
for row in r['rows']:
    print(f"  Cust {row['customer_id']} ({row['group_id']}) | {row['thread_type']} | turn {row['turn_number']} | day {row['day']}")
    if row['message_text']:
        print(f"    {row['message_text'][:100]}")

print("\n=== SUMMARY ===")
print("Plan A: T2→T3 (+20% quality for individual)")
print("Ops: $500→$800 global + S1 $200→$400 targeted")
print("Dev: $300→$500 global + S1 $100→$300 targeted")
print("Lead promo: S1 gets 20% off Plan A (new leads only)")
print("Enterprise: 23656 renewal sent at $20/seat")
print("Estimated new daily cost: ~$4,730/day")
print("Revenue: ~$3,320/day (plus lumpy enterprise billing)")
print("Net: sustainable with upcoming enterprise payments")
