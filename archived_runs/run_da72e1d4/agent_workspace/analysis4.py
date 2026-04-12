import novamind_api as nm

day = nm.vars.current_day
print(f"=== MARKET + QUALITY ANALYSIS Day {day} ===\n")

# Market overview
overview = nm.market.get_market_overview()
print("=== MARKET OVERVIEW (known groups) ===")
for seg in overview.get('segments', []):
    gid = seg.get('group_id', '')
    if gid in ['S1', 'S2', 'S3', 'E1', 'E2', 'E3']:
        print(f"  {gid}: subscribers={seg.get('subscribers',0)} cap={seg.get('market_cap',0)} info_level={seg.get('info_level',0)}")
        # Print any available estimates
        for k, v in seg.items():
            if k not in ['group_id', 'subscribers', 'market_cap', 'info_level']:
                print(f"    {k}: {v}")

# Check group insights for S1, S2, S3, E1, E3
for gid in ['S1', 'S2', 'S3', 'E1', 'E3']:
    try:
        insights = nm.market.get_group_insights(group_id=gid)
        print(f"\n=== GROUP INSIGHTS: {gid} ===")
        for k, v in insights.items():
            if k != 'network_effects':
                print(f"  {k}: {v}")
        if 'network_effects' in insights:
            print(f"  network_effects: {insights['network_effects']}")
    except Exception as e:
        print(f"\n  {gid} insights error: {e}")

# Cash flow projection
print("\n=== CASH FLOW PROJECTION ===")
print(f"Current cash: $31,159 (Day {day})")
print(f"Daily costs: ~$3,530/day (ops $800 + dev $800 + cap $530 + compute $1,400)")
print(f"Net daily: ~-$1,630 (without revenue)")
print(f"\nActive enterprise subs:")
r = nm.query("""
SELECT s.customer_id, s.plan, s.effective_price, s.contract_end_day, s.billing_day_mod30, c.group_id
FROM subscriptions s JOIN customers c ON s.customer_id=c.customer_id
WHERE s.status='subscribed' AND c.customer_type='large'
ORDER BY s.contract_end_day
""")
total_monthly = 0
for row in r['rows']:
    # Need seat count - check customers table
    print(f"  Cust {row['customer_id']} ({row['group_id']}) ${row['effective_price']}/seat end={row['contract_end_day']} billing_mod={row['billing_day_mod30']}")

# Get seat counts
print("\n=== ENTERPRISE SEAT COUNTS ===")
r = nm.query("""
SELECT s.customer_id, s.effective_price, s.contract_end_day,
       COUNT(*) as seats
FROM subscriptions s JOIN customers c ON s.customer_id=c.customer_id
WHERE s.status='subscribed' AND c.customer_type='large'
GROUP BY s.customer_id, s.effective_price, s.contract_end_day
""")
for row in r['rows']:
    revenue = row['effective_price'] * row['seats']
    print(f"  Cust {row['customer_id']}: {row['seats']} seats @ ${row['effective_price']:.2f} = ${revenue:.0f}/mo | end={row['contract_end_day']}")

# R&D check
print("\n=== R&D STATUS ===")
projects = nm.research.list_research_projects()
for t in projects.get('tiers', []):
    print(f"  Tier {t.get('tier')}: status={t.get('status')} cost=${t.get('cost',0):,.0f} duration={t.get('estimated_duration','?')} quality_boost={t.get('estimated_quality_boost','?')}")
