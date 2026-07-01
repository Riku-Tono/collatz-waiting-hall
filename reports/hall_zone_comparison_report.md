# Hall Zone Comparison Report: miss-front 3-8 vs k-structure corridor 12-30

This is a finite observational hall-zone comparison, not a mechanism.
Exit distance is a coordinate, not a cause.
Zone labels are descriptive groupings, not causal thresholds.
No proof, causality, counterexample, or global Collatz claim is made.

## Zone Summary

| zone | distance | events | miss | miss_rate | dominant k | k distribution | behavior | reading |
|---|---|---:|---:|---:|---|---|---|---|
| miss_front_3_8 | 3-8 | 14743 | 228 | 0.015465 | 1 | 1:9142; 2:3358; 3:1433; 4:358; 5:306; 6:90; 7:37; 8:11; 9:6; 11:1; 10:1 | drift:13953; wait:562; miss:228 | miss-zone |
| k_structure_corridor_12_30 | 12-30 | 34565 | 0 | 0.0 | 1 | 1:18891; 2:9825; 3:3732; 4:1213; 5:458; 6:263; 7:106; 8:33; 9:29; 10:11; 11:2; 12:1; 13:1 | drift:33299; wait:1266 | k-structure-zone |

## Direct Difference

- k-distribution L1 difference: 0.16214.
- miss-front miss_rate: 0.015465.
- k-structure corridor miss_rate: 0.0.
- Because the 12-30 zone has zero miss events here, it should be treated as a k-structure-zone, not a miss-zone.

## Similar Distance Pairs

| miss-front distance | corridor distance | k L1 |
|---:|---:|---:|
| 3 | 27 | 0.037578 |
| 4 | 27 | 0.051519 |
| 4 | 18 | 0.058957 |
| 3 | 19 | 0.070469 |
| 3 | 18 | 0.079244 |
| 3 | 23 | 0.08997 |
| 4 | 23 | 0.095589 |
| 7 | 29 | 0.109923 |
| 7 | 26 | 0.116698 |
| 4 | 19 | 0.119456 |

## Reading

- The two regions are not the same phenomenon in this finite profile.
- 3-8 combines nonzero miss events with a mostly k1/k2/k3 near-exit mix.
- 12-30 has no miss events and instead shows alternating k-regimes, including k3 spike at 15 and k1/k2 flips around 22-23 and 26-27.
- Some individual distances can look k-similar, but the zone-level miss and behavior profiles separate them.

## Output Files

- `hall_zone_comparison_3_8_vs_12_30.csv`
- `hall_zone_k_distribution_comparison.csv`
- `hall_zone_miss_type_comparison.csv`
- `hall_zone_behavior_comparison.csv`
