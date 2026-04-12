import novamind_api as nm

# Budget analysis
r1_cost = 166667
r2_cost = 333333
remaining = 1000000 - r1_cost - r2_cost
daily_cap = 215  # tier 1 capacity
daily_ops = 300
daily_dev = 500
daily_ads = 300
daily_total = daily_cap + daily_ops + daily_dev + daily_ads

print(f'R&D tier 1 + 2 cost: ${r1_cost+r2_cost:,}')
print(f'Remaining after R&D 1+2: ${remaining:,}')
print(f'Daily burn: ${daily_total:,}/day = ${daily_total*7:,}/week')
print(f'Weeks of runway (no revenue): {remaining/(daily_total*7):.1f}')

# Quality analysis
# base = 0.20, tier 1 = 0.6x -> delivered = 0.12
# S1 q_min ~0.08: 0.12 > 0.08 -> can serve S1 NOW at low price!
# S2 q_min ~0.37: need delivered > 0.37
# S3 q_min ~0.15: need delivered > 0.15
# E1 q_min ~0.29: need delivered > 0.29

print('\nQuality thresholds:')
print(f'S1 q_min ~0.08, current delivered = 0.12 - CAN SERVE')
print(f'S3 q_min ~0.15, current delivered = 0.12 - CANNOT SERVE')
print(f'E1 q_min ~0.29, current delivered = 0.12 - CANNOT SERVE')

# With tier 2 (0.75x) and dev bonus: base+bonus * 0.75
# To serve S3: need (base+bonus)*0.75 > 0.15 -> base+bonus > 0.20 (ok with current base)
# Wait: 0.20 * 0.75 = 0.15 -> borderline for S3!

print(f'\nWith tier 2: 0.20 * 0.75 = {0.20*0.75:.3f}')
print(f'S3 needs {0.145:.3f} -> tier 2 at base just barely meets it')

# With tier 3 (0.9x): 0.20 * 0.9 = 0.18 > 0.15 for S3
print(f'With tier 3: 0.20 * 0.9 = {0.20*0.9:.3f} -> can serve S3 easily')

# Plan structure:
# Plan A: tier 2, price $20-25 -> S1 (WTP $26)
# Plan B: tier 3, price $50-99 -> S3 (WTP $193), enterprise E1 (WTP $20/seat * seats)
# Plan C: tier 4, price $120-150 -> S2 (WTP $179), E2/E3

# For enterprise, we negotiate. Base pricing in the plan is for individual customers.
# Enterprise deals are seat-based.

# Key insight: need to raise quality fast to capture higher-paying S2 and enterprise
# S1 is low-hanging fruit (large market, low quality requirement)
# but revenue per S1 customer is low ($20-25/mo)
# vs E2/E3 which are potentially $88-104/seat * 100s-1000s of seats = massive revenue

print('\n--- Revenue potential ---')
print(f'S1: ~$20/mo * market cap 800k = massive volume but low ARPU')
print(f'S2: ~$150/mo * market cap 492k = high value')
print(f'E3: ~$80/seat * 600 seats avg = $48k/mo per enterprise customer')
print(f'   Market cap 253 * 10% conversion = ~25 customers * $48k = $1.2M MRR potential')
