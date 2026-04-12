import novamind_api as nm

# Get seat counts from turn 0 for all active threads  
print("--- Seat counts from initial thread (turn=0) ---")
r = nm.query("""SELECT et.customer_id, c.group_id, et.seat_count, et.day
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0 AND et.turn_number=0
ORDER BY c.group_id, et.seat_count DESC""")
# seat_count might be NULL or have different name
print(f"First row columns: {list(r['rows'][0].keys()) if r['rows'] else 'none'}")
for row in r['rows'][:10]:
    print(f"  {row}")

# Check if seat_count exists on turn 0 messages  
print("\n--- All columns in enterprise_turns ---")
r2 = nm.query("SELECT * FROM enterprise_turns LIMIT 1")
if r2['rows']:
    print(f"Columns: {list(r2['rows'][0].keys())}")
    print(f"Row: {r2['rows'][0]}")

# Group insights - quality thresholds
print("\n--- Group Insights ---")
for gid in ['E1', 'E2', 'E3', 'S1', 'S2', 'S3']:
    try:
        ins = nm.market.get_group_insights(group_id=gid)
        print(f"  {gid}: {ins}")
    except Exception as e:
        print(f"  {gid}: ERROR {e}")
