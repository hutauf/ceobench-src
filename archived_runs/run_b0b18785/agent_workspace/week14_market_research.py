import novamind_api as nm

# Check market overview for discovered groups
market = nm.market.get_market_overview()
print("=== Market Overview ===")
print(f"Keys: {list(market.keys())}")
for k, v in market.items():
    if isinstance(v, list):
        print(f"{k}: {len(v)} items")
        for item in v[:5]:
            print(f"  {item}")
    else:
        print(f"{k}: {v}")

