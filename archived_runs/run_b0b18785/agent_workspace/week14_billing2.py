import novamind_api as nm

day = nm.vars.current_day
day_mod30 = day % 30
print(f"Today: day {day}, day_mod30={day_mod30}")

# Revenue due in next 7 days
soon = nm.query(f"""SELECT SUM(seat_count*effective_price) as rev_due, COUNT(*) as n
FROM subscriptions 
WHERE status='subscribed' 
  AND ((billing_day_mod30 - {day_mod30} + 30) % 30) <= 7""")
print(f"Revenue due in next 7 days: ${soon['rows'][0]['rev_due']:,.0f} from {soon['rows'][0]['n']} subs")

next14 = nm.query(f"""SELECT SUM(seat_count*effective_price) as rev_due, COUNT(*) as n
FROM subscriptions
WHERE status='subscribed' 
  AND ((billing_day_mod30 - {day_mod30} + 30) % 30) <= 14""")
print(f"Revenue due in next 14 days: ${next14['rows'][0]['rev_due']:,.0f} from {next14['rows'][0]['n']} subs")

# Large upcoming bills
big_soon = nm.query(f"""SELECT customer_id, plan, seat_count, effective_price, 
    seat_count*effective_price as monthly_rev,
    billing_day_mod30,
    ((billing_day_mod30 - {day_mod30} + 30) % 30) as days_until
FROM subscriptions
WHERE status='subscribed' AND seat_count >= 200
ORDER BY monthly_rev DESC LIMIT 20""")

print("\nLarge subs billing schedule:")
for r in big_soon['rows']:
    print(f"  CID={r['customer_id']} {r['seat_count']}seats Plan{r['plan']} @${r['effective_price']:.2f} = ${r['monthly_rev']:,.0f}/mo | in {r['days_until']} days")

