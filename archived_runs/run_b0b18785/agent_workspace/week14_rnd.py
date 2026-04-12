import novamind_api as nm

# Check R&D status and consider starting Tier 1 again since it was "done" but 
# memory says not_started now - something changed

projects = nm.research.list_research_projects()
print("=== R&D Status ===")
for t in projects['tiers'][:8]:
    status = t.get('status', 'not_started')
    in_prog = t.get('in_progress', False)
    print(f"  T{t['tier']}: {t['name']}")
    print(f"    Status: {status} | In-progress: {in_prog}")
    print(f"    Cost: ${t['cost']:,} | Mean quality: {t.get('mean_quality_boost',0):.3f}")
    if status == 'completed':
        print(f"    Actual boost: {t.get('actual_quality_boost', 'N/A')}")

