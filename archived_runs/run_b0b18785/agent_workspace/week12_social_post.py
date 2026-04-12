#!/usr/bin/env python3
import novamind_api as nm

# Post addressing quota complaints and support lag
# Quota complaints are from E1 (Jennifer Walsh, Robert Chen)
# Support lag complaints from E2, E3

content = "We hear you on quota limits. We've just 2x'd quota caps across all plans (Plan B: 30K/day, Plan C: 80K/day). On support: additional ops resources deployed—avg resolution time improving. Enterprise customers, your AE will reach out this week. Thank you for your patience."

result = nm.marketing.post_social_media(content=content)
print(f"Post result: {result}")
print(f"Content length: {len(content)}")
