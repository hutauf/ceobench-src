import novamind_api as nm

day = nm.vars.current_day

# Check what's in enterprise_turns for large customers
large_subs = nm.query("""SELECT customer_id, plan, seat_count, effective_price,
    seat_count*effective_price as mrr
FROM subscriptions 
WHERE status='subscribed' AND seat_count >= 400
ORDER BY mrr DESC LIMIT 20""")

print("Large subs and their thread status:")
for r in large_subs['rows']:
    cid = r['customer_id']
    # Check open threads for this customer
    threads = nm.query(f"""SELECT customer_id, thread_type, closed, turn_number, sender, day
    FROM enterprise_turns WHERE customer_id={cid} AND closed=0 ORDER BY turn_number DESC LIMIT 3""")
    
    thread_info = "no open thread"
    if threads['rows']:
        t = threads['rows'][0]
        thread_info = f"{t['thread_type']} turn={t['turn_number']} sender={t['sender']} day={t['day']}"
    
    print(f"  CID={cid} Plan{r['plan']} {r['seat_count']}seats @${r['effective_price']:.2f} = ${r['mrr']:,.0f}/mo | {thread_info}")

