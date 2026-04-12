#!/usr/bin/env python3
import novamind_api as nm
posts = nm.analytics.get_social_posts(days=7, limit=15)
print(f"Posts: {len(posts)}")
for p in posts:
    if isinstance(p, dict):
        print(f"  [{p.get('group_id','?')}] Day {p.get('day','?')}: {str(p.get('content',''))[:130]}")
    else:
        print(f"  {str(p)[:130]}")
