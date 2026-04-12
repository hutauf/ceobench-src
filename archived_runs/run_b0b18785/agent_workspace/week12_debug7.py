#!/usr/bin/env python3
import novamind_api as nm

# Get enterprise cust IDs first
e_cids = nm.query("SELECT customer_id FROM customers WHERE customer_type='large'")
cid_list = [str(r['customer_id']) for r in e_cids['rows']]
print(f"Enterprise customers: {len(cid_list)}")

# Get all subscriptions
all_subs = nm.query("""SELECT customer_id, plan, seat_count, effective_price
FROM subscriptions WHERE status='subscribed' ORDER BY seat_count DESC""")
print(f"Total active subs: {len(all_subs['rows'])}")

cid_set = set(int(c) for c in cid_list)
ent_mrr = 0
ind_mrr = 0
for row in all_subs['rows']:
    cid = row['customer_id']
    sc = row['seat_count']
    monthly = sc * row['effective_price']
    if cid in cid_set:
        ent_mrr += monthly
    else:
        ind_mrr += monthly

print(f"Enterprise MRR: ${ent_mrr:.0f}/mo")
print(f"Individual MRR: ${ind_mrr:.0f}/mo")
print(f"Total MRR: ${ent_mrr + ind_mrr:.0f}/mo")

# Cash
cash = nm.query("SELECT SUM(amount) as cash FROM ledger")
print(f"\nCash: ${cash['rows'][0]['cash']:.0f}")

# Cost breakdown
costs = nm.query("""SELECT category, SUM(amount)/7.0 as daily_avg 
FROM ledger WHERE day >= 77 GROUP BY category ORDER BY daily_avg""")
print("\nDaily costs (last 7 days):")
for row in costs['rows']:
    print(f"  {row['category']}: ${row['daily_avg']:.0f}/day")

# R&D
r = nm.research.list_research_projects()
for t in r['tiers'][:4]:
    status = "DONE✓" if t['completed'] else ("IN PROGRESS" if t['in_progress'] else "not started")
    print(f"T{t['tier']} {t['name']}: {status}")
