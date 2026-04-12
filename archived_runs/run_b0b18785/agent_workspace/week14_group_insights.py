import novamind_api as nm

# Check group insights for key groups
for gid in ['E1', 'E2', 'E3']:
    insights = nm.market.get_group_insights(group_id=gid)
    print(f"\n=== {gid} Insights ===")
    for k, v in insights.items():
        if k not in ['group_id']:
            print(f"  {k}: {v}")

