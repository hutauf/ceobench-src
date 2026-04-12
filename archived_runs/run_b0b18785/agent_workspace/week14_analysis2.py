import novamind_api as nm
import json

day = nm.vars.current_day

# Large enterprise subs - query subscriptions directly without JOIN
large = nm.query("SELECT customer_id, plan, seat_count, effective_price, seat_count*effective_price as mrr FROM subscriptions WHERE status='subscribed' AND seat_count >= 100 ORDER BY mrr DESC LIMIT 20")
print("--- Large Enterprise Subs ---")
for r in large['rows']:
    print(f"  CID={r['customer_id']} Plan {r['plan']} {r['seat_count']}seats @${r['effective_price']:.2f} = ${r['mrr']:,.0f}/mo")

# Ledger costs last 7 days
costs = nm.query(f"SELECT category, SUM(amount)/7.0 as daily_avg FROM ledger WHERE day >= {day-7} AND amount < 0 GROUP BY category ORDER BY daily_avg ASC")
print("\n--- Daily Costs (Last 7 days) ---")
total_cost = 0
for r in costs['rows']:
    print(f"  {r['category']}: ${-r['daily_avg']:,.0f}/day")
    total_cost += -r['daily_avg']
print(f"  TOTAL COSTS: ${total_cost:,.0f}/day")

# Revenue last 7 days
rev = nm.query(f"SELECT SUM(amount)/7.0 as daily_avg FROM ledger WHERE day >= {day-7} AND amount > 0")
print(f"\n--- Daily Revenue (Last 7 days) ---")
print(f"  Revenue: ${rev['rows'][0]['daily_avg']:,.0f}/day")
print(f"  Net: ${rev['rows'][0]['daily_avg'] - total_cost:,.0f}/day")

# R&D status
import novamind_api as nm
projects = nm.research.list_research_projects()
print("\n--- R&D Status ---")
for t in projects['tiers'][:6]:
    status = t.get('status', 'not_started')
    print(f"  T{t['tier']}: {t['name']} | {status} | cost=${t['cost']:,} | mean_quality={t.get('mean_quality_boost',0):.3f}")

