import novamind_api as nm
import json

day = nm.vars.current_day

# Proactively renegotiate with top enterprise customers who don't have open threads
# Focus on big E2/E3 customers to upsell or retain at higher rates

# Get top enterprise subs without open threads
all_threads = nm.query("""SELECT DISTINCT customer_id FROM enterprise_turns 
WHERE closed=0""")
thread_cids = {r['customer_id'] for r in all_threads['rows']}

# Get large subscribers (>300 seats) not in active thread
large_no_thread = nm.query("""SELECT customer_id, plan, seat_count, effective_price,
    seat_count*effective_price as mrr
FROM subscriptions 
WHERE status='subscribed' AND seat_count >= 300
ORDER BY mrr DESC LIMIT 30""")

print("Large subs without pending threads (potential proactive renegotiation):")
renegotiate = []
for r in large_no_thread['rows']:
    if r['customer_id'] not in thread_cids:
        print(f"  CID={r['customer_id']} Plan{r['plan']} {r['seat_count']}seats @${r['effective_price']:.2f} = ${r['mrr']:,.0f}/mo")
        renegotiate.append(r)

print(f"\n{len(renegotiate)} candidates for proactive outreach")

# For large E2/E3 customers at $40/seat, offer to maintain or consider upsell opportunity
# But since cash is tight, let's not rock the boat - just retain top ones
# Actually let's check which ones were recently acquired vs older

# Check the billing days for these customers
if renegotiate:
    cids = [r['customer_id'] for r in renegotiate[:10]]
    cid_str = ','.join(str(c) for c in cids)
    sched = nm.query(f"""SELECT customer_id, billing_day_mod30, start_day
    FROM subscriptions WHERE customer_id IN ({cid_str}) AND status='subscribed'""")
    for r in sched['rows']:
        days_since_start = day - r['start_day']
        days_til_billing = (r['billing_day_mod30'] - day % 30 + 30) % 30
        print(f"  CID={r['customer_id']} started day {r['start_day']} ({days_since_start}d ago), next bill in {days_til_billing}d")

