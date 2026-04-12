import novamind_api as nm

print("=== SUBSCRIPTION BILLING BREAKDOWN ===")
# When do billings hit?
r = nm.query("""
SELECT billing_day_mod30, COUNT(*) as n, SUM(effective_price * seat_count) as total_payment
FROM subscriptions
WHERE status='subscribed'
GROUP BY billing_day_mod30
ORDER BY billing_day_mod30
""")
for row in r['rows']:
    print(f"Day mod 30 = {row['billing_day_mod30']}: {row['n']} subs, ${row['total_payment']:.0f}")

print("\n=== RECENT REVENUE TREND ===")
r = nm.query("""
SELECT day, SUM(amount) as revenue
FROM ledger
WHERE category='subscription_payment' AND day >= 21
GROUP BY day
ORDER BY day
""")
for row in r['rows']:
    print(f"Day {row['day']}: ${row['revenue']:.0f}")

print("\n=== BREAK-EVEN ANALYSIS ===")
print("Daily costs at new config:")
print("  Capacity: $530")
print("  Ads: $1400 (incl targeted)")
print("  Ops: $800 (incl targeted)")
print("  Dev: $1650 (incl targeted)")
print("  Compute: ~$650 (growing)")
print("  Lead cost: ~$1000 (5825 leads/week = 832/day × $1)")
print("  TOTAL: ~$6,030/day")
print()
print("Revenue to break even at $6,030/day:")
print("  Need $6,030 × 30 = $180,900/month billing")
print("  Current MRR: $46,403")
print("  Gap: ~$134,500/mo")
print("  Need ~2,900 more Plan A subs or ~600 more S3 Plan B subs")
print()
print("KEY INSIGHT: Enterprise is the path to profitability:")
print("  If cid=18724 closes Plan B @$25: 315 seats × $25 = $7,875/mo")
print("  If cid=22828 closes Plan B @$25: 455 seats × $25 = $11,375/mo")
print("  If cid=21828 closes Plan B @$28: 608 seats × $28 = $17,024/mo (quality risk)")
print("  Total potential: $36,274/mo additional = $82,677 MRR total!")
print()
print("Cash runway at -$1,010/day net burn: ~239 days (34 weeks)")
print("But as subs grow, revenue increases - need to accelerate")
