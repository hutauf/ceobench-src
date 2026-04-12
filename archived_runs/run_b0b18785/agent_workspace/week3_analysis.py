import novamind_api as nm

# Revenue analysis
print('Revenue analysis for enterprise deals:')
print(f'2471 (386 seats) at $8.58/seat: {386*8.58:.0f}/month')
print(f'2471 (386 seats) at $9.00/seat: {386*9.00:.0f}/month')
print(f'2471 (386 seats) at $9.50/seat: {386*9.50:.0f}/month')
print(f'11449 (115 seats) at $12/seat: {115*12:.0f}/month')
print(f'11449 (115 seats) at $10/seat: {115*10:.0f}/month')
print()

# Quality check - will enterprise customers churn at 30-day billing?
# E1 q_min ~0.29 (noisy)
# Current best: Plan C = 0.2483
# After R&D T1+T2 (+0.11): base = 0.20 + 0.0258 + 0.11 = 0.3358
# Plan B after R&D: 0.3358 * 1.00 = 0.336 (above E1 q_min 0.29)
# Plan A after R&D: 0.3358 * 0.75 = 0.252 (below 0.29 - risky!)

print('Quality projections after R&D T1+T2:')
base_after = 0.20 + 0.0258 + 0.11
print(f'  Base+bonus+R&D = {base_after:.4f}')
print(f'  Plan A (T2, 0.75x): {base_after*0.75:.4f}')
print(f'  Plan B (T4, 1.00x): {base_after*1.00:.4f}')
print(f'  Plan C (T5, 1.10x): {base_after*1.10:.4f}')
print(f'  E1 q_min estimate: ~0.29 (noisy)')
print()

# Decision: offer Plan B at $9 for 2471, $11 for 11449
# Offer Plan A as secondary option at lower price
# This ensures quality check passes after R&D completes
print('DECISION:')
print('  2471: Counter at $9.50/seat Plan A (meet halfway from their $8.58)')
print('  11449: New lead - offer $13/seat Plan A, $16/seat Plan B')
print()

# Check current cash burn
print('Cash position:')
print(f'  Cash: $268,477')
print(f'  Daily burn: ~$3,100/day = $21,700/week')
print(f'  Weeks of runway: {268477/21700:.1f} weeks')
print(f'  MRR: $8,533/month')
print(f'  Monthly revenue from MRR: ~$8,533')
print(f'  Monthly costs: ~$21,700*4.33 = ~$94K')
print(f'  Monthly deficit: ~$85K/month')
print()

# If enterprise closes:
# 2471 at $9.50: 386*9.5 = $3,667/mo
# 11449 at $13: 115*13 = $1,495/mo
# Total additional: $5,162/mo - still in deficit but improving
print('Enterprise revenue impact:')
print(f'  2471@$9.50: {386*9.5:.0f}/month')
print(f'  11449@$13: {115*13:.0f}/month')
print(f'  Additional MRR: {386*9.5+115*13:.0f}/month')
print(f'  Total MRR: {8533+386*9.5+115*13:.0f}/month')
