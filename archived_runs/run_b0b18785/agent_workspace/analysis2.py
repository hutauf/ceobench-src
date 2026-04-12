import novamind_api as nm

# R&D status
print("--- R&D Projects ---")
projects = nm.research.list_research_projects()
print(f"Keys: {list(projects.keys())}")
print(projects)
