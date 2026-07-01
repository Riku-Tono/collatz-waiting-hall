# State-Space Anatomy of the Waiting Hall

A finite-sample observational chapter on the interior geometry of the waiting
hall — the region a Collatz trajectory occupies **before** its first exit from a
`remaining_K` band.

---

## Summary

This chapter maps what the interior of the waiting hall looks like, using
`exit_distance` (how far an event sits from the lower-edge exit layer of its
band) as the central coordinate. Read along this coordinate, the hall is not a
single near-exit boundary but a small stacked **state space**: an exit layer
(`exit_distance 0-2`) with no miss events, a **miss-front** (`3-8`) that carries
all observed miss events, and a **k-structure corridor** (`12-30`) where the
valuation distribution varies but no miss events occur. A selector audit over
the full event table shows that no single coordinate isolates miss events
cleanly; miss-only cells first appear only when **one positional coordinate is
paired with one local-shape coordinate**. All of this is descriptive and
finite-sample; it is reported as observation, not as a rule, mechanism, or
proof.

**Dataset:** 76,530 band-internal event rows; 228 miss events; 76,302 non-miss
background rows.

---

## Key findings

- **Miss events occur only at `exit_distance 3-8`** (the miss-front). All 228
  miss events fall in this range, strongest near distance 3–4.
- **No miss events occur at `exit_distance 0-2`** (the exit layer).
- **`exit_distance 12-30` is a k-structure corridor with zero miss events.** It
  contains 34,565 events and 0 misses, and resolves into alternating local
  `k`-regimes (a k3 spike at 15; k1/k2 flips at 22→23 and 26→27) rather than a
  smooth gradient.
- **Single coordinates leak.** Each candidate coordinate can be made to contain
  all 228 miss events, but each also admits large numbers of non-miss
  background events.
- **Miss-only cells first appear at two-coordinate pairs.** Of the six possible
  coordinate pairs, four capture all 228 miss events with zero non-miss leakage.
- **The successful pairs are position + shape.** Every miss-only pair combines
  one positional coordinate (`exit_distance` or `remaining_K_before`) with one
  local-shape coordinate (`residue_pair_mod32` or `transition_k`). Pairs that
  stay on one side (position+position, or shape+shape) are not miss-only.

Region overview (continuous `exit_distance` reading):

| region | exit_distance | events | miss | miss_rate | dominant k |
|---|---|---:|---:|---:|---:|
| exit layer | 0–2 | — | 0 | — | — |
| miss-front | 3–8 | 14,743 | 228 | 0.015465 | 1 |
| k-structure corridor | 12–30 | 34,565 | 0 | 0.000000 | 1 |

The zone-level `k`-distribution L1 difference between the miss-front and the
corridor is `0.16214`: the two regions are close in `k` but differ decisively in
miss profile.

---

## What this chapter does not claim

This is a finite-sample, observational, band-internal study. It does **not**
claim, and should not be read as claiming:

- a mechanism or cause (`exit_distance` and residues are **coordinates**, not causes);
- a proof of any kind;
- a counterexample;
- any global Collatz result;
- that zone boundaries are thresholds (zones are **descriptive groupings**).

"Miss-only selector" cells are **finite-sample selector cells**, not rules.
A miss-only cell means only that, within this dataset, the cell contains misses
and no non-miss background. It does **not** mean a coordinate combination is
necessary, sufficient, or mechanistic outside this sample. No new miss type is
introduced; the existing `A / B / C1 / C2 / C3 / C_unassigned` labels are reused
as-is.

---

## Coordinate definitions

| coordinate | kind | meaning |
|---|---|---|
| `exit_distance` | positional | distance from the lower-edge exit layer of the band; `0` is the exit, larger is deeper inside the hall. Read as `remaining_K_before - band_lower_edge`. |
| `remaining_K_before` | positional | remaining valuation mass before the step. |
| `transition_k` | local-shape | the valuation `k` of the step. |
| `residue_pair` (e.g. `mod32`) | local-shape | the residue-pair coordinate of the event. |
| `miss local type` | label | existing `A / B / C1 / C2 / C3 / C_unassigned` labels, reused. |

"Near behavior" labels (`drift`, `wait`, `miss`, `exit`) are observational
labels derived from position plus existing behavior/miss joins, not new types.

---

## Main result table

Selector audit over 76,530 event rows (228 miss; 76,302 non-miss background).
A cell is "miss-only" when it contains all 228 miss events and 0 non-miss events.

**Single coordinates — all leak:**

| coordinate | matched | miss | non-miss | miss_rate | miss-only? |
|---|---:|---:|---:|---:|:---:|
| exit_distance | 14,743 | 228 | 14,515 | 0.015465 | no |
| remaining_K_before | 13,802 | 228 | 13,574 | 0.016519 | no |
| residue_pair_mod32 | 275 | 228 | 47 | 0.829091 | no |
| transition_k | 4,946 | 228 | 4,718 | 0.046098 | no |

**Two-coordinate pairs — miss-only cells first appear here:**

| pair | matched | miss | non-miss | miss-only? | pairing |
|---|---:|---:|---:|:---:|---|
| exit_distance + residue_pair_mod32 | 228 | 228 | 0 | yes | position + shape |
| exit_distance + transition_k | 228 | 228 | 0 | yes | position + shape |
| remaining_K_before + residue_pair_mod32 | 228 | 228 | 0 | yes | position + shape |
| remaining_K_before + transition_k | 228 | 228 | 0 | yes | position + shape |
| residue_pair_mod32 + transition_k | 275 | 228 | 47 | no | shape + shape |
| exit_distance + remaining_K_before | 13,802 | 228 | 13,574 | no | position + position |

Three- and four-coordinate selectors remain miss-only but add nothing once a
position–shape pair already separates the misses; the four-coordinate tuple is
redundant in this scan.

---

## Finite-sample selector identity

The selector audit above can be written compactly as a single statement about
two selectors over the audited event set. This is a way of compressing the
observation, not a claim beyond the finite sample.

**Definitions.** Let `Ω_N` be the audited set of band-internal event rows, and
let `M ⊂ Ω_N` be the observed miss-event set:

```
Ω_N = audited band-internal event rows,        |Ω_N| = 76,530
M   = observed miss-event set,    M ⊂ Ω_N,      |M|   = 228
```

Define the **miss-front position selector** and the **miss-supported local-shape
selector** (the latter built from the residue-pair values that the miss events
themselves occupy):

```
P_pos   = { x ∈ Ω_N : exit_distance(x) ∈ {3,4,5,6,7,8} }

R_M     = { residue_pair_mod32(x) : x ∈ M }
S_shape = { x ∈ Ω_N : residue_pair_mod32(x) ∈ R_M }
```

`S_shape` is defined on `residue_pair_mod32` alone. `transition_k` is **not**
added to the main definition: adding it does not remove the non-miss rows that
`S_shape` admits (the leakage stays at 47), so the shape side carries no extra
separating information here — the separation is supplied by the position side.

**Observation.** In this finite sample each selector contains all of `M`, but
neither alone isolates it:

```
M ⊂ P_pos,        |P_pos \ M|   = 14,515
M ⊂ S_shape,      |S_shape \ M| = 47
```

Their conjunction removes the excess rows exactly:

```
P_pos ∩ S_shape = M        (inside Ω_N)
```

We call this last line a **finite-sample selector identity**: an empirical
equality that holds inside `Ω_N`. It is not a claim of an out-of-sample
necessary or sufficient condition, and not a claim about why miss events occur;
it states only that, within the audited rows, the conjunction of these two
selectors picks out exactly the observed miss-event set.

**The 47 excess rows.** The rows in `S_shape \ M` are not diffuse noise. In this
sample all 47 lie **outside** the miss-front, at `exit_distance 35, 36, 37`, and
all carry `near_behavior = drift`:

```
S_shape \ M  ⊆ { x : exit_distance(x) ∈ {35,36,37} }
near_behavior(x) = drift   for all x ∈ S_shape \ M
```

So the same residue-pair shape that appears in the miss-front also appears at
these upper positions, but there it is realized as `drift` rather than `miss`.
Imposing `P_pos` removes exactly this upper-position drift counterpart, leaving
`P_pos ∩ S_shape = M`. (Adding `transition_k` to the shape selector does not
remove these rows; position does.)

**Interpretation (kept separate, and limited).** Read along the two axes of the
state space:

- *shape alone is miss-compatible but not miss-isolating* — the miss-supported
  residue shape also occurs away from the miss-front;
- *position alone is broad* — the `3-8` window contains 14,515 non-miss rows;
- *position + shape isolates the observed miss events inside `Ω_N`* — their
  conjunction is exactly `M`.

This is the same "where × how" reading as the rest of the chapter, written as an
equality that happens to hold in this finite sample. It carries no claim of
mechanism, cause, proof, counterexample, or global Collatz behavior.

---

## Figures / artifacts

| figure | role |
|---|---|
| `waiting_hall_interior_map.png` | the coarse four-box hall (upper / mid / lower / exit_layer) |
| `band_position_flow_map.png` | downward flow between hall zones and exits |
| `k_by_hall_zone_heatmap.png` | `k` distribution by coarse zone |
| `exit_distance_miss_rate_plot.svg` | miss rate vs continuous exit distance |
| `k_change_by_exit_distance.png` | k-change score per distance (landmarks 15 / 18 / 23 / 27) |
| `k_structure_corridor_heatmap.png` | per-distance `k` histogram for `12-30` |
| *selector diagram (suggested)* | position × shape miss-only cells |
| *state-space map (in chapter)* | stacked exit-layer / miss-front / corridor |

Chapter document: `state_space_anatomy_of_the_waiting_hall.md`.

---

## How to read the result

**Observation.** Along `exit_distance`, the waiting hall separates into three
regions. The exit layer (`0-2`) carries no miss events. The miss-front (`3-8`)
carries all 228 miss events, concentrated near distance 3–4. The corridor
(`12-30`) carries 34,565 events and 0 misses, and its `k` distribution changes
in alternating local regimes. In the selector audit, no single coordinate is
miss-only; the first miss-only cells appear at two coordinates, and every
successful pair combines one positional coordinate with one local-shape
coordinate.

**Interpretation (kept separate, and limited).** Read as a state space, the hall
has a "where" axis (exit distance / position) and a "how" axis (local shape:
`k`, residue, parity). In this sample a miss event is not pinned down by position
alone or by shape alone, but by the two together — it sits where a "where" and a
"how" coincide. This is a conceptual state-space map, not a boundary map, and it
is built from finite, miss-event-local observations only. It carries no claim of
mechanism, causality, proof, counterexample, or global Collatz behavior.

---

## Source reports used

This README and its chapter reorganize five finite-sample reports into a single
narrative (R1 → R6) rather than listing them report by report:

| report | section |
|---|---|
| `waiting_hall_interior_report.md` | R1 — coarse four-box hall |
| `hall_zone_comparison_report.md` | R2 — miss-front vs corridor |
| `zone_coordinate_contrast_report.md` | R2 / R4 — k-similar pairs, residue/parity |
| `k_structure_corridor_report.md` | R3 — the 12–30 corridor |
| `minimal_miss_selector_report.md` | R5 — minimal miss-only selectors |

This chapter is independent of, and does not modify, the Paradoxical-Sequence
chapter (first-pass faces at the `64-95 -> 32-63` boundary). It studies the
space **before** that boundary and can be linked from the existing README.

---

## Recommended citation / note

> *State-Space Anatomy of the Waiting Hall* — a finite-sample observational
> chapter on the interior geometry of the waiting hall before first exit
> (76,530 band-internal event rows; 228 miss events; 76,302 non-miss background
> rows). Findings are descriptive and coordinate-based. The "miss-only selector"
> cells are finite-sample selector cells, not rules. No mechanism, causality,
> proof, counterexample, or global Collatz result is claimed.
