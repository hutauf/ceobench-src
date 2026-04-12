#!/usr/bin/env python3
import novamind_api as nm

# Check actual MRR from query
r = nm.query("SELECT SUM(seat_count * effective_price) as mrr FROM subscriptions WHERE status='subscribed'")
print(f"Total MRR: ${r['rows'][0]['mrr']:.0f}")

# Check enterprise seat counts specifically
r2 = nm.query("""SELECT s.customer_id, c.group_id, s.plan, s.seat_count, s.effective_price,
    s.seat_count * s.effective_price as monthly
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
WHERE s.status='subscribed' AND c.customer_type='large'
ORDER BY monthly DESC LIMIT 20""")
print(f"\nTop enterprise subs:")
for row in r2['rows']:
    print(f"  CID={row['customer_id']} {row['group_id']} seats={row['seat_count']} {row['plan']} @ ${row['effective_price']:.2f} = ${row['monthly']:.0f}/mo")

ent_total = nm.query("""SELECT SUM(s.seat_count * s.effective_price) as mrr, SUM(s.seat_count) as seats, COUNT(*) as n
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
WHERE s.status='subscribed' AND c.customer_type='large'""")
print(f"\nEnterprise total: ${ent_total['rows'][0]['mrr']:.0f}/mo, {ent_total['rows'][0]['seats']} seats, {ent_total['rows'][0]['n']} subs")

# Check individual total
ind_total = nm.query("""SELECT SUM(s.seat_count * s.effective_price) as mrr, COUNT(*) as n
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
WHERE s.status='subscribed' AND c.customer_type='small'""")
print(f"Individual total: ${ind_total['rows'][0]['mrr']:.0f}/mo, {ind_total['rows'][0]['n']} subs")

# Cash check
cash = nm.query("SELECT SUM(amount) as cash FROM ledger")
print(f"\nTotal ledger balance: ${cash['rows'][0]['cash']:.0f}")

# Check recent revenue specifically
rev = nm.query("SELECT SUM(amount) as rev FROM ledger WHERE category='subscription_payment'")
print(f"Total subscription revenue ever: ${rev['rows'][0]['rev']:.0f}")

# Usage vs capacity
print("\n--- CAPACITY ---")
cost_info = nm.infrastructure.get_cost_info()
print(f"Current tier: {cost_info.get('current_tier')}")
for t in cost_info.get('capacity_tiers', []):
    if t.get('tier') in [2, 3, 4, 5]:
        print(f"  Tier {t['tier']}: {t['capacity_units']} units/day @ ${t['cost_per_day']}/day")
