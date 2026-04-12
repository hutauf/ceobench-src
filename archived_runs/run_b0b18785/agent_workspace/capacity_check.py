import novamind_api as nm

info = nm.infrastructure.get_cost_info()
print("=== CAPACITY TIERS ===")
for tid, tier in info['capacity_tiers'].items():
    print(f"Tier {tid}: {tier}")

print("\n=== CURRENT USAGE ===")
print("Week 5: 790,059 units - we are near or over Tier 1 capacity!")
print()
# Current tier 1 details
print("Need to check what tier 1 capacity limit is")
