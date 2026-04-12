#!/usr/bin/env python3
import novamind_api as nm
r = nm.analytics.get_social_posts(days=7, limit=15)
print(type(r), r)
