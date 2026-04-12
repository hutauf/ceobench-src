import novamind_api as nm

# Post social media response addressing support issues
# Key complaints from posts:
# 1. Support responsiveness - 8 days for critical bug
# 2. E1 quota complaints  
# 3. General support quality
# Keep under 280 chars

post = nm.marketing.post_social_media(
    content="We hear you—our support response times are unacceptable. We've doubled our ops team allocation, prioritized critical bugs to <24hr SLA, and are clearing the backlog now. If you have an open ticket, reply with your ID for immediate escalation. #NovaMindAI"
)
print(f"Social post result: {post}")

