import novamind_api as nm
import json

day = nm.vars.current_day
print(f"Day {day} - Enterprise thread analysis")

# Get all open threads not yet responded to
threads = nm.query("""SELECT et.customer_id, c.group_id, et.thread_type, 
    et.turn_number, et.sender, et.day, et.offer_json, et.message_id
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0 AND et.sender != 'agent'
ORDER BY et.customer_id ASC, et.turn_number DESC""")

# Get the latest thread per customer
cust_threads = {}
for t in threads['rows']:
    cid = t['customer_id']
    if cid not in cust_threads:
        cust_threads[cid] = t

print(f"Unique customers with open threads: {len(cust_threads)}")

# Group by thread type
from collections import defaultdict
by_type = defaultdict(list)
for cid, t in cust_threads.items():
    by_type[t['thread_type']].append(t)

for ttype, lst in by_type.items():
    print(f"\n{ttype}: {len(lst)} customers")
    for t in lst[:5]:
        offer = {}
        if t['offer_json']:
            try:
                offer = json.loads(t['offer_json'])
            except:
                pass
        print(f"  CID={t['customer_id']} grp={t['group_id']} turn={t['turn_number']} day={t['day']} offer={offer}")

