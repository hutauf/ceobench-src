import novamind_api as nm

# Check subscriptions for old customers (without seat_count)
print("--- Subscription check ---")
r = nm.query("""SELECT s.customer_id, c.group_id, s.plan, s.effective_price, s.status
FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id
WHERE s.customer_id IN (1972, 2471, 14075, 16858, 11449, 21828)""")
for row in r['rows']:
    print(f"  C{row['customer_id']} ({row['group_id']}): Plan {row['plan']} @ ${row['effective_price']} - {row['status']}")

# Need to respond to the threads that are awaiting our response:
# 1. Old turn=0 threads from days 43-49 - these should still be valid (within 7 days)
# Actually day 43-49 = 7-13 days ago... some may have expired!
# Current day is 56. Day 43 + 7 = day 50 → threads from day 43 EXPIRED!
# Day 49 + 7 = day 56 → threads from day 49 are at limit TODAY!
# Day 50+ are still valid

# Let me check which threads are still within 7-day window
print("\n--- Thread deadline analysis (current day=56) ---")
# Threads that are still live (day >= 56-7 = 49)
live_day_cutoff = 56 - 7  # = 49
print(f"Threads from day >= {live_day_cutoff} are potentially still alive")

# Based on our analysis, these customer threads have NOT been responded to yet:
# C31531 (E1) turn=0 day=43 → EXPIRED (43+7=50 < 56)
# C31533 (E2) turn=0 day=43 → EXPIRED
# C32822 (E1) turn=0 day=44 → EXPIRED
# C34110, 34111, 34112 (E1) day=45 → EXPIRED
# C34114 (E2) day=45 → EXPIRED
# C35246 (E1) day=46 → EXPIRED
# C35875, 35876, 35877 (E1) day=47 → EXPIRED
# C36570, 36571, 36572 (E1) day=48 → EXPIRED
# C37639, 37640 (E1) day=49 → AT LIMIT TODAY (day 56)
# C37643 (E3) day=49 → AT LIMIT TODAY

# The ones we already sent offers to (from enterprise_deals.py):
# 38854, 38855, 38856 etc. (day 50-56) → those should still be open

# The ones we MISSED responding to (no subscription = error):
# 31531, 32822, 34110, 34111, 34112, 35246, 35875, 35876, 35877,
# 36570, 36571, 36572, 37639, 37640 → these got "no subscription" error
# This means the open threads from old system messages didn't have matching subscription
# The error "no subscription" means the API couldn't match these as having an open thread we can respond to

# Actually re-reading docs: "send_enterprise_deal auto-detects: if a customer has an open thread, 
# it replies; if no open thread, it initiates a renegotiation"
# "no subscription" error = customer has no existing subscription AND no open lead thread
# → These customers either expired already OR didn't have an open thread we could access

# So the real situation: most old leads are DEAD. Need to focus on active ones.
# The ones we SUCCESSFULLY replied to in enterprise_deals.py are the active ones.

# Let me try the remaining ones that might still be live
remaining_unresponded = [37639, 37640, 37643]  # day 49, at limit today
print(f"\nAttempting to respond to day-49 threads (at deadline)...")
try:
    result = nm.enterprise.send_enterprise_deal(deals=[
        [37639, [["B", 20.0], ["A", 14.0]]],  # E1
        [37640, [["B", 20.0], ["A", 14.0]]],  # E1
        [37643, [["C", 50.0], ["B", 30.0]]],  # E3
    ])
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")

# Check 27076 (E2) - counter at $18.49 Plan B (turn=2 day=43)
# This is OVERDUE but the counter came on day 43 and we're now day 56 → likely expired
# BUT let's try since it's showing in our open threads
print("\nTrying to respond to negotiation counters (may be expired)...")
try:
    result2 = nm.enterprise.send_enterprise_deal(deals=[
        [27076, [["B", 22.0], ["C", 40.0]]],  # E2, counter was $18.49
    ])
    print(f"27076 (E2): {result2}")
except Exception as e:
    print(f"27076 error: {e}")

try:
    result3 = nm.enterprise.send_enterprise_deal(deals=[
        [29322, [["A", 13.0], ["B", 18.0]]],  # E1, counter was $9.08
    ])
    print(f"29322 (E1): {result3}")
except Exception as e:
    print(f"29322 error: {e}")

try:
    result4 = nm.enterprise.send_enterprise_deal(deals=[
        [28062, [["B", 15.0], ["A", 11.0]]],  # E1, counter was $13.29
    ])
    print(f"28062 (E1): {result4}")
except Exception as e:
    print(f"28062 error: {e}")

try:
    result5 = nm.enterprise.send_enterprise_deal(deals=[
        [28061, [["A", 10.0]]],  # E1, counter was $2.06 (too low)
    ])
    print(f"28061 (E1): {result5}")
except Exception as e:
    print(f"28061 error: {e}")
