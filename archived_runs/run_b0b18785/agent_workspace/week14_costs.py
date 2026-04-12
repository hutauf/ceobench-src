import novamind_api as nm

day = nm.vars.current_day

# Check capacity vs usage
print(f"Usage this week: 9,201,712 units = {9201712/7:,.0f}/day")
cost_info = nm.infrastructure.get_cost_info()
print(f"\nCapacity tiers:")
for tier_id, info in cost_info['capacity_tiers'].items():
    print(f"  Tier {tier_id}: {info['capacity_units']:,} units/day, ${info['cost_per_day']:,}/day")

print(f"\nCurrent tier: 3 (capacity: ~{cost_info['capacity_tiers']['3']['capacity_units']:,}/day)")
print(f"Current usage: {9201712/7:,.0f}/day")
print(f"Utilization: {(9201712/7)/cost_info['capacity_tiers']['3']['capacity_units']*100:.1f}%")

# Should we upgrade? Check tier 4 cost vs benefits
t3 = cost_info['capacity_tiers']['3']
t4 = cost_info['capacity_tiers']['4']
print(f"\nTier 3 vs Tier 4:")
print(f"  T3: {t3['capacity_units']:,} units/day @ ${t3['cost_per_day']:,}/day")
print(f"  T4: {t4['capacity_units']:,} units/day @ ${t4['cost_per_day']:,}/day")
print(f"  Extra cost: ${t4['cost_per_day']-t3['cost_per_day']:,}/day")

# Check current enterprise subscriber count and expected growth
ent_subs = nm.query("SELECT COUNT(*) as n, SUM(seat_count) as total_seats FROM subscriptions WHERE status='subscribed' AND seat_count >= 10")
print(f"\nEnterprise subs: {ent_subs['rows'][0]['n']} customers, {ent_subs['rows'][0]['total_seats']:,} total seats")

