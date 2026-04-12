import novamind_api as nm

print('=== COMPUTE PROFITABILITY ANALYSIS ===')

# E2 C plan: 6350 seats at T5 ($0.030/unit)
total_c_seats = 6350
avg_c_price = 38  # blended
total_c_rev = total_c_seats * avg_c_price
total_c_compute = total_c_seats * 67 * 30 * 0.030
print(f'Plan C (T5): {total_c_seats} seats')
print(f'  Revenue: ${total_c_rev:,}/month')
print(f'  Compute: ${total_c_compute:,.0f}/month') 
print(f'  Gross margin: ${total_c_rev - total_c_compute:,.0f}/month')

# Plan B T4
total_b_seats = 22938
avg_b_price = 21  # blended
total_b_rev = total_b_seats * avg_b_price
total_b_compute = total_b_seats * 67 * 30 * 0.012
print()
print(f'Plan B (T4): {total_b_seats} seats')
print(f'  Revenue: ${total_b_rev:,}/month')
print(f'  Compute: ${total_b_compute:,.0f}/month')
print(f'  Gross margin: ${total_b_rev - total_b_compute:,.0f}/month')

# What if B drops to T3?
total_b_compute_t3 = total_b_seats * 67 * 30 * 0.006
print()
print(f'Plan B if T3: compute = ${total_b_compute_t3:,.0f}/month')
print(f'  Savings: ${total_b_compute - total_b_compute_t3:,.0f}/month = ${(total_b_compute - total_b_compute_t3)/30:,.0f}/day')

# What if C drops to T4?
total_c_compute_t4 = total_c_seats * 67 * 30 * 0.012
print()
print(f'Plan C if T4: compute = ${total_c_compute_t4:,.0f}/month')
print(f'  Savings: ${total_c_compute - total_c_compute_t4:,.0f}/month = ${(total_c_compute - total_c_compute_t4)/30:,.0f}/day')

print()
print('Total daily savings if both downgraded:')
daily_b_savings = (total_b_compute - total_b_compute_t3) / 30
daily_c_savings = (total_c_compute - total_c_compute_t4) / 30
print(f'  B: T4->T3 saves ${daily_b_savings:,.0f}/day')
print(f'  C: T5->T4 saves ${daily_c_savings:,.0f}/day')
print(f'  Total: ${daily_b_savings + daily_c_savings:,.0f}/day = ${(daily_b_savings + daily_c_savings)*7:,.0f}/week')
