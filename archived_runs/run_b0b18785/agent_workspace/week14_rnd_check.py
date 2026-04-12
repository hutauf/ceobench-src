import novamind_api as nm

# Hmm - my memory says T1 and T2 are DONE but list shows not_started
# Let me check the current quality state which should reflect any completed R&D
# The global_bonus of 0.1843 is much higher than base 0.20 + any R&D boost would give
# Current global_bonus = 0.1843 (from dev spending)
# T1 = +0.04, T2 = +0.07 mean boosts
# global_bonus 0.1843 + potential R&D = quality already quite decent

# Actually I think my memory was WRONG about T1/T2 being done
# The quality bonus of 0.1843 is entirely from development spending
# This makes sense: dev spending has been running for ~12+ weeks

# With no R&D done, we have room to add significant quality:
# T1: +0.04 → 0.2243 global bonus
# T2: +0.07 → 0.2543 global bonus
# T3: +0.11 → 0.2943 global bonus

# But we can't afford them right now at $76K cash
# T1 at $167K needs us to have >$200K to be safe

# Expected cash in next 7 days: $76K + $270K - $27.7K*7 = $76K + $270K - $194K = $152K
# Expected cash in 14 days: $76K + $627K - $194K*2 = $76K + $627K - $388K = $315K

print("Cash projection:")
print(f"  Current: $76,432")
print(f"  Next 7 days revenue: $270,850")
print(f"  Next 7 days costs: ~${27730*7:,}")
print(f"  Cash in 7 days: ${76432 + 270850 - 27730*7:,}")
print()
print(f"  Days 7-14 revenue: ${627950-270850:,}")
print(f"  Days 7-14 costs: ~${27730*7:,}")
print(f"  Cash in 14 days: ${76432 + 627950 - 27730*14:,}")

# T1 R&D: $167K → can start after ~7 days when cash hits ~$150K
# But safer to wait until $300K+ buffer
# At +0.04 quality, might not move needle much given competitor drift

# Decision: Start T1 R&D as soon as cash > $200K (probably after the big billing wave in ~7-10 days)
# This will add quality boost while we accumulate for T2/T3

