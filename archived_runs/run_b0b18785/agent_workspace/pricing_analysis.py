import novamind_api as nm

print("=== PRICING OPPORTUNITY ANALYSIS ===")

# S3 has 122 Plan B subs at $59 and WTP is $188 (±40% noise)
# WTP range: $113 - $263 (±40% of $188)
# We're massively undercharging S3!
# Quality: Plan B = 0.3292 for S3, Plan C = 0.3621
# S3 q_min: 0.185

# S2 has 28 Plan B subs at $59 and WTP is $179 (±40% noise)
# S2 converting at 2.2% - but that's because quality was low before
# Now Plan B quality = 0.3199, S2 q_min ~0.37 - still barely works

# Current S1 Plan A $19, WTP $26 (±65% noise)
# Could increase S1 Plan A price slightly? Risk: lose conversion rate

print("Current Plan Prices: A=$19, B=$59, C=$149")
print()
print("S3 analysis:")
print("  WTP: $188 (±40% = $113-$263)")
print("  Plan B at $59 is 31% of WTP - HUGE undercharge!")
print("  Could raise Plan B to $89-$109 for S3 (still <$113 floor)")
print("  But: need careful analysis - don't want to churn existing subs")
print()
print("S1 analysis:")  
print("  WTP: $26 (±65% = $9-$43)")
print("  Plan A at $19 is 73% of WTP - reasonable")
print("  19.3% conversion rate - very healthy")
print("  Risk: raising price could hurt conversion significantly")
print()
print("S2 analysis:")
print("  WTP: $179 (±40% = $107-$251)")
print("  Plan B at $59 is 33% of WTP")
print("  q_min ~0.37, current quality 0.3199 - barely meeting threshold")
print("  Better to wait for more quality before raising price")
print()
print("PLAN B PRICE INCREASE OPTION:")
print("  Increase Plan B to $79 (vs current $59)")
print("  S3 WTP $188 → still affordable at $79 (42% WTP)")
print("  S2 WTP $179 → still affordable at $79 (44% WTP)")
print("  S1 WTP $26 → only Plan A is relevant for S1")
print("  Enterprise E1 @ Plan B: negotiated separately, not affected")
print()
print("  Revenue impact: 122 S3 Plan B × ($79-$59) = $2,440/mo extra")
print("                   28 S2 Plan B × ($79-$59) = $560/mo extra")
print("                   21 S1 Plan B × ($79-$59) = $420/mo extra")
print("                   TOTAL EXTRA: ~$3,420/mo")
print()
print("  BUT: Some existing S3/S2 Plan B subs may churn at next billing")
print("  Risk: 30-day billing cycle, churn could offset gains")
print()
print("RECOMMENDATION: Wait on price increase until more data on churn risk")
print("  Focus on: enterprise deals, growing subs count, R&D for quality")

print("\n=== PLAN C OPPORTUNITY ===")
print("Plan C at $149, quality 0.3621")
print("S3 WTP $188 → Plan C is 79% of WTP - GOOD for high-value S3 subs!")
print("Could we convert S3 Plan B users to Plan C?")
print("  Need Plan C quality to be clearly superior (ratio matters)")
print("  Plan C quality: 0.3621 vs Plan B: 0.3292 = 10% better quality")
print("  That's not a huge jump for $90 more/month")
print("  WAIT for R&D Tier 3 to make Plan C more attractive")
