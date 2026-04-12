import novamind_api as nm

# Check social posts
posts = nm.analytics.get_social_posts(days=7, limit=10)
print(f"Posts type: {type(posts)}")
if isinstance(posts, list):
    for p in posts:
        print(f"  [{p.get('day','?')}] {p.get('group_id','?')}: {p.get('content','')[:120]}")
elif isinstance(posts, dict):
    print(f"Keys: {list(posts.keys())}")
    items = posts.get('posts', posts.get('items', []))
    for p in items[:8]:
        print(f"  {p}")
