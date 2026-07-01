# k-Structure Corridor Report

This is a finite observational corridor profile, not a mechanism.
Exit distance is a coordinate, not a cause.
Zone candidates are descriptive groupings, not causal thresholds.
No proof, causality, counterexample, or global Collatz claim is made.

## Scope

- Distance window: exit_distance 12-30.
- This is treated separately from the miss-front region at exit_distance 3-8.
- Main object: k distribution along distance, not miss type.

## Requested Landmark Context

| distance | events | dominant k | second k | top2 share | k1 | k2 | k3 | k4 | k>=4 | entropy |
|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| 15 | 2456 | 3 | 1 | 0.838762 | 0.247964 | 0.107899 | 0.590798 | 0.026059 | 0.053339 | 1.630913 |
| 18 | 2222 | 1 | 2 | 0.915392 | 0.823582 | 0.091809 | 0.035104 | 0.028353 | 0.049505 | 1.018212 |
| 23 | 2228 | 1 | 2 | 0.89991 | 0.763914 | 0.135996 | 0.047127 | 0.024237 | 0.052962 | 1.214953 |
| 27 | 2035 | 1 | 2 | 0.925307 | 0.808354 | 0.116953 | 0.040295 | 0.013759 | 0.034398 | 1.020928 |

## Corridor Zone Candidates

| zone | distance | events | signature | dominant/second | entropy | support |
|---|---|---:|---|---|---:|---|
| approach_to_k3_spike_12_14 | 12-14 | 5136 | 12:1/2 -> 13:1/2 -> 14:2/1 | 1/2 | 1.722308 | supported |
| k3_spike_15 | 15-15 | 2456 | 15:3/1 | 3/1 | 1.630913 | supported |
| k2_to_k1_reset_16_18 | 16-18 | 5950 | 16:1/2 -> 17:2/1 -> 18:1/2 | 1/2 | 1.661174 | supported |
| k1_plateau_with_k4_tail_19_21 | 19-21 | 5699 | 19:1/2 -> 20:1/2 -> 21:1/2 | 1/2 | 1.374752 | supported |
| k2_k1_flip_22_23 | 22-23 | 4456 | 22:2/1 -> 23:1/2 | 1/2 | 1.51307 | supported |
| outer_k1_k2_flip_24_27 | 24-27 | 7398 | 24:1/2 -> 25:1/2 -> 26:2/1 -> 27:1/2 | 1/2 | 1.469256 | supported |
| outer_mixed_tail_28_30 | 28-30 | 3470 | 28:1/2 -> 29:2/1 -> 30:1/2 | 2/1 | 1.747264 | supported |

## Reading

- Distance 15 is the clearest local spike: k=3 is dominant and reaches 0.590798 share.
- Distance 18 is not a k3 point; it is a reset-like k1-heavy point after the 16-17 transition.
- Distances 22-23 show a k2/k1 flip: distance 22 is k2-heavy, distance 23 is k1-heavy.
- Distances 26-27 show a similar outer flip: distance 26 is k2-heavy, distance 27 is k1-heavy.
- The 12-30 corridor is not a single smooth gradient. It is better described as alternating local regimes.
- The zone split is supported descriptively, but should not be treated as a mechanism or threshold model.

## Output Files

- `k_structure_corridor_12_30.csv`
- `k_structure_corridor_zone_candidates.csv`
- `k_structure_corridor_heatmap.png`
