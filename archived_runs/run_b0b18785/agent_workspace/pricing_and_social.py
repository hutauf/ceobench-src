import novamind_api as nm

# === RAISE PLAN A PRICE ===
# S1 WTP = $25.87. Current Plan A = $19. With 5,955 Plan A subs, raising to $22 = +$17K/mo
# S2 WTP = $178.59, S3 WTP = $187.99 → raising Plan A to $22 still way below their WTP
# Risk: Some existing subs at $19 may not meet their quality threshold if expectations shifted
# BUT Plan A quality = 0.263 (well above S1 q_min = 0.081)
# Decision: Raise to $22

print("Raising Plan A price to $22...")
result = nm.pricing.set_prices(A=22, B=79, C=149)
print(f"Price update: {result}")

# === POST SOCIAL MEDIA RESPONSE ===
# Address support crisis directly - acknowledge the issue and commit to improvement
print("\nPosting social media response...")
post_result = nm.marketing.post_social_media(
    content="We hear you on support response times - this is unacceptable and we're fixing it now. We've tripled our support ops budget and are hiring. Goal: <24hr responses for all tickets. Current queue being worked through now. DM us your ticket# for priority attention. 🙏"
)
print(f"Social post: {post_result}")

# === CHECK IF OLD THREADS NEED REJECTION ===
# Some threads from day 14-42 may be stale/expired
# Let me check threads that are old but still open
print("\nChecking stale threads...")
r = nm.query("""SELECT et.message_id, et.customer_id, c.group_id, et.thread_type,
    et.turn_number, et.sender, et.day
FROM enterprise_turns et JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0 AND et.day < 43
GROUP BY et.customer_id
HAVING et.turn_number = MAX(et.turn_number)
ORDER BY et.day ASC""")
print(f"Old threads still open ({len(r['rows'])}):")
for row in r['rows']:
    print(f"  C{row['customer_id']} ({row['group_id']}) {row['thread_type']} turn={row['turn_number']} day={row['day']} sender={row['sender']}")
