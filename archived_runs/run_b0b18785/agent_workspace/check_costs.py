import novamind_api as nm

# Check cost info structure
cost_info = nm.infrastructure.get_cost_info()
print(f"Cost info keys: {list(cost_info.keys())}")
print(cost_info)
