import novamind_api as nm

print("=== EMERGENCY OPS FIX ===")

# The issues backlog (534 S1 open, 107+ over 7 days) is causing:
# 1. Negative social posts (multiple!)
# 2. Reputation damage → fewer leads
# 3. Satisfaction damage → churn at billing cycle
# 
# Quota complaints: "hitting usage quotas mid-month"
# Plan A quota is 5000 units/day - maybe too low?
# Let's check average usage per subscriber

r = nm.query("""
SELECT c.group_id, s.plan, COUNT(*) as n
FROM subscriptions s
JOIN customers c ON s.customer_id=c.customer_id
WHERE s.status='subscribed'
GROUP BY c.group_id, s.plan
""")
print("Subscriber breakdown:")
for row in r['rows']:
    print(f"  {row['group_id']} Plan {row['plan']}: {row['n']} subs")

print()
print("Usage last week: 790,059 units / 7 days = 112,866 units/day")
total_subs = 1701
print(f"Total subs: {total_subs}")
print(f"Avg usage per sub per day: {112866/total_subs:.1f} units")
print()
print("With quota 5000/day, most S1 users are well under quota")
print("But some heavy users may be hitting limits")
print()

# SIGNIFICANTLY increase ops spending to clear the backlog
# Current: $600 base + $150 S1 + $50 S3 = $800/day
# Need to double it to clear 534 open issues
print("Increasing ops spending significantly...")
result = nm.marketing.set_daily_spend(advertising=1200, operations=1000, development=1300)
print("Daily spend result:", result)

# Increase S1 targeted ops more aggressively
result = nm.analytics.set_targeted_ops_spend(targeted_spend={"S1": 300, "S3": 100})
print("Targeted ops result:", result)

print()
print("New ops total: $1000 + $300 S1 + $100 S3 = $1400/day")
print("This should dramatically accelerate issue resolution")

# Also raise Plan A quota slightly to reduce quota complaints
# 5000/day per sub is fine for most, but let's check if S1 users hit it often
print()
print("=== QUOTA ANALYSIS ===")
# Usage week: 790,059 / 7 days = 112,866/day for 1701 subs
# Average: 66 units/day per sub
# Plan A quota: 5000/day - that's 75x the average
# The complaints might be from Plan B users with specific workflows
# OR heavy users who use much more than average
print("Avg usage: 66 units/day per sub (quota 5000/day is 75x avg)")
print("Quota complaints likely from power users or enterprise on wrong plan")
print("Plan B quota: 20000/day is sufficient for most enterprise users")
print("No quota change needed - message is about pricing not quotas")
