import novamind_api as nm

print("=== WEEK 3 ACTIONS ===")
print()

# 1. ADJUST AD CHANNEL SPEND
# Current: social=30%, search=25%, linkedin=25%, content=15%, referral=5%
# S1 leads mainly from social_media and search (individual users)
# S3 leads from linkedin and content (power users)
# Shift more to S1-effective channels (social, search) for better ROI
# Keep some linkedin for S3 (network effects value)

# Check channel effectiveness via insights
s1_insights = nm.market.get_group_insights(group_id='S1')
print('S1 insights:', s1_insights)
print()
