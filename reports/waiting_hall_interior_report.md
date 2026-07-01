# Waiting Hall Interior Report

This is a finite-sample observational map. It does not claim a mechanism, proof, or global Collatz result.

## Scope

- Object: band-internal event rows from first entry to first pass.
- Position: `remaining_K_before - band_lower_edge` is treated as distance from the exit.
- `exit_layer`: distance 0-2, matching the previous exit-layer audit width.
- `lower_hall / mid_hall / upper_hall`: the non-exit part of the band split by within-band distance ratio.
- No new miss type is created. Existing `A/B/C1/C2/C3/C_unassigned` labels are reused as-is.

## Zone Summary

| zone | events | mean wait | median wait | k movement | near behavior | miss types |
|---|---:|---:|---:|---|---|---|
| upper_hall | 16322 | 23.467 | 22.0 | up:4702 down:4367 flat:4859 | drift:15729; wait:593 |  |
| mid_hall | 22555 | 22.183 | 22 | up:6732 down:6346 flat:8450 | drift:21729; wait:826 |  |
| lower_hall | 27456 | 18.876 | 19.0 | up:8957 down:9023 flat:8531 | drift:26178; wait:1050; miss:228 | B:85; A:64; C_unassigned:50; C1:13; C2:10; C3:6 |
| exit_layer | 10197 | 17.489 | 20 | up:2346 down:1372 flat:6363 | exit:10197 |  |

## Requested Comparisons

- upper_hall k movement: flat:4859; up:4702; down:4367
- lower_hall k movement: down:9023; up:8957; flat:8531
- `mid_band_wait_then_drop` has 3553 mid_hall events. By zone: lower_hall:4986; mid_hall:3553; exit_layer:1301; upper_hall:55
- First observed zone for `drift_down` trajectories: upper_hall:2278; lower_hall:762; mid_hall:535
- Miss event zone distribution: lower_hall:228
- A/B/C/C_unassigned coarse type x zone: ('B', 'lower_hall'):85; ('A', 'lower_hall'):64; ('C_unassigned', 'lower_hall'):50; ('C', 'lower_hall'):29

## Reading

Inside the hall, events are distributed across lower/mid/upper positions as well as the exit layer. `near_behavior` is an observational label derived from position plus existing behavior/miss joins; it is not a new type.

`drift_down` is kept as a candidate-overlap context item, consistent with the previous audit. It is not promoted to a direct event-level causal relation.

## Outputs

- `waiting_hall_interior_detail.csv`
- `waiting_hall_zone_summary.csv`
- `waiting_hall_k_summary.csv`
- `waiting_hall_type_distribution.csv`
- `waiting_hall_interior_map.png`
- `band_position_flow_map.png`
- `k_by_hall_zone_heatmap.png`
