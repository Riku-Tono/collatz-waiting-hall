# Minimal Miss-Only Selector Audit

Source table: `C:\Users\yauki\Documents\Codex\2026-06-30\task-waiting-hall-interior-map-audit\outputs\waiting_hall_interior_detail.csv`

## Validation

- Total rows in event table: 76530
- Total miss count: 228
- Non-miss background rows included: 76302
- Candidate coordinates present: exit_distance, remaining_K_before, residue_pair_mod32, transition_k
- Output files written as CSV/MD in this task's `outputs` directory.

## 1. Single Coordinates

Single-coordinate selectors do not identify miss-only cells when each selector is defined as the set of values observed among the 228 miss events.

| coordinate | selector_values | matched_events | miss_count | non_miss_count | miss_rate |
| --- | --- | --- | --- | --- | --- |
| exit_distance | 6 | 14743 | 228 | 14515 | 0.015465 |
| remaining_K_before | 14 | 13802 | 228 | 13574 | 0.016519 |
| residue_pair_mod32 | 18 | 275 | 228 | 47 | 0.829091 |
| transition_k | 8 | 4946 | 228 | 4718 | 0.046098 |

The most informative single coordinate by lowest non-miss leakage is `residue_pair_mod32`: it matches 228 miss events and 47 non-miss events.

## 2. Two-Coordinate Selectors

| coordinate_set | tuple_count | matched_events | miss_count | non_miss_count | miss_rate | number_of_miss_only_tuples | number_of_mixed_tuples |
| --- | --- | --- | --- | --- | --- | --- | --- |
| exit_distance + residue_pair_mod32 | 18 | 228 | 228 | 0 | 1.0 | 18 | 0 |
| exit_distance + transition_k | 18 | 228 | 228 | 0 | 1.0 | 18 | 0 |
| remaining_K_before + residue_pair_mod32 | 33 | 228 | 228 | 0 | 1.0 | 33 | 0 |
| remaining_K_before + transition_k | 33 | 228 | 228 | 0 | 1.0 | 33 | 0 |
| residue_pair_mod32 + transition_k | 18 | 275 | 228 | 47 | 0.829091 | 8 | 10 |
| exit_distance + remaining_K_before | 14 | 13802 | 228 | 13574 | 0.016519 | 0 | 14 |

Four 2-coordinate pairs capture all 228 miss events with 0 non-miss events in this table.

## 3. Three-Coordinate Selectors

| coordinate_set | tuple_count | matched_events | miss_count | non_miss_count | miss_rate | number_of_miss_only_tuples | number_of_mixed_tuples |
| --- | --- | --- | --- | --- | --- | --- | --- |
| exit_distance + remaining_K_before + residue_pair_mod32 | 33 | 228 | 228 | 0 | 1.0 | 33 | 0 |
| exit_distance + remaining_K_before + transition_k | 33 | 228 | 228 | 0 | 1.0 | 33 | 0 |
| exit_distance + residue_pair_mod32 + transition_k | 18 | 228 | 228 | 0 | 1.0 | 18 | 0 |
| remaining_K_before + residue_pair_mod32 + transition_k | 33 | 228 | 228 | 0 | 1.0 | 33 | 0 |

All tested 3-coordinate selectors match 228 miss events with 0 non-miss events.

## 4. Coordinate-Level Comparison

| coordinate_level | coordinate_set | tuple_count | matched_events | miss_count | non_miss_count | miss_rate | all_miss_captured | zero_non_miss_leakage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | exit_distance | 6 | 14743 | 228 | 14515 | 0.015465 | True | False |
| 1 | remaining_K_before | 14 | 13802 | 228 | 13574 | 0.016519 | True | False |
| 1 | residue_pair_mod32 | 18 | 275 | 228 | 47 | 0.829091 | True | False |
| 1 | transition_k | 8 | 4946 | 228 | 4718 | 0.046098 | True | False |
| 2 | exit_distance + residue_pair_mod32 | 18 | 228 | 228 | 0 | 1.0 | True | True |
| 2 | exit_distance + transition_k | 18 | 228 | 228 | 0 | 1.0 | True | True |
| 2 | remaining_K_before + residue_pair_mod32 | 33 | 228 | 228 | 0 | 1.0 | True | True |
| 2 | remaining_K_before + transition_k | 33 | 228 | 228 | 0 | 1.0 | True | True |
| 2 | residue_pair_mod32 + transition_k | 18 | 275 | 228 | 47 | 0.829091 | True | False |
| 2 | exit_distance + remaining_K_before | 14 | 13802 | 228 | 13574 | 0.016519 | True | False |
| 3 | exit_distance + remaining_K_before + residue_pair_mod32 | 33 | 228 | 228 | 0 | 1.0 | True | True |
| 3 | exit_distance + remaining_K_before + transition_k | 33 | 228 | 228 | 0 | 1.0 | True | True |
| 3 | exit_distance + residue_pair_mod32 + transition_k | 18 | 228 | 228 | 0 | 1.0 | True | True |
| 3 | remaining_K_before + residue_pair_mod32 + transition_k | 33 | 228 | 228 | 0 | 1.0 | True | True |
| 4 | exit_distance + remaining_K_before + residue_pair_mod32 + transition_k | 33 | 228 | 228 | 0 | 1.0 | True | True |

Miss-only full selectors first appear at coordinate level 2.

## 5. Minimal Selector Candidates

The 2-coordinate minimal full selector candidates are: exit_distance + residue_pair_mod32; exit_distance + transition_k; remaining_K_before + residue_pair_mod32; remaining_K_before + transition_k.

The 4-coordinate tuple is redundant for this finite-sample separation because 2-coordinate selectors already match 228 miss events with 0 non-miss events.

The result shows coordinate redundancy in this scan.

## 6. Careful Reading

These are finite-sample selector cells, not causal rules.

Miss-only does not mean necessary, sufficient, or mechanistic outside this dataset.

No proof, causality, counterexample, or global Collatz claim is made.
