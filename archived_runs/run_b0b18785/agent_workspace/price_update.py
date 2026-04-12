import novamind_api as nm

print("=== UPDATING PLAN PRICES ===")

# Raise Plan B from $59 to $79
# S3 WTP $188 → $79 is only 42% of WTP (safe)
# S2 WTP $179 → $79 is 44% of WTP (safe)
# Risk: existing subs re-evaluate at 30-day billing
# Current S3 Plan B subs: 122 (mostly recent, started days 21-35)
# Their billing cycles will hit around day 51-65
# Quality 0.3292 well above S3 q_min 0.185 → they'll stay

# Keep Plan A at $19 - S1 converting at 19.3%, don't risk it
# Plan C stays at $149 - no subs yet, but keep it as upsell option

result = nm.pricing.set_prices(A=19, B=79, C=149)
print("Price update result:", result)

print("\n=== POSTING SOCIAL MEDIA ===")
# Post something positive about our quality improvements
result = nm.marketing.post_social_media(
    content="🚀 NovaMind AI just shipped major model quality upgrades! Our AI engine is now faster and smarter. Existing subscribers get the improvement automatically — no action needed. #AIProductivity #SaaS"
)
print("Social post result:", result)
