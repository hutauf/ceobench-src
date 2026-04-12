import novamind_api as nm

day = nm.vars.current_day

# Check upcoming billing using billing_day_mod30
upcoming = nm.query("""SELECT s.customer_id, s.plan, s.seat_count, s.effective_price, 
    s.seat_count*s.effective_price as monthly_rev,
    s.billing_day_mod30, 
    (s.billing_day_mod30 - (? % 30) + 30) % 30 as days_until_billing
FROM subscriptions s
WHERE s.status='subscribed' AND s.seat_count >= 200
ORDER BY monthly_rev DESC LIMIT 20""", params=[day])

print("--- Large Enterprise Billing Cycle ---")
print(f"Today is day {day}, mod30 = {day % 30}")
for r in upcoming['rows']:
    print(f"  CID={r['customer_id']} Plan{r['plan']} {r['seat_count']}seats @${r['effective_price']:.2f} = ${r['monthly_rev']:,.0f}/mo | billing_mod30={r['billing_day_mod30']} | days_til={r['days_until_billing']}")

# Summary of billing coming in next 7 days
soon = nm.query("""SELECT SUM(s.seat_count*s.effective_price) as rev_due, COUNT(*) as n
FROM subscriptions s
WHERE s.status='subscribed' 
  AND ((s.billing_day_mod30 - (? % 30) + 30) % 30) <= 7""", params=[day])
print(f"\nRevenue due in next 7 days: ${soon['rows'][0]['rev_due']:,.0f} from {soon['rows'][0]['n']} subs")

next14 = nm.query("""SELECT SUM(s.seat_count*s.effective_price) as rev_due, COUNT(*) as n
FROM subscriptions s
WHERE s.status='subscribed' 
  AND ((s.billing_day_mod30 - (? % 30) + 30) % 30) <= 14""", params=[day])
print(f"Revenue due in next 14 days: ${next14['rows'][0]['rev_due']:,.0f} from {next14['rows'][0]['n']} subs")

