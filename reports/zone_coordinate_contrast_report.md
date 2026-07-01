# Zone Coordinate Contrast Report

This is a finite observational coordinate contrast, not a mechanism.
Exit distance and residues are coordinates, not causes.
Integer residue/parity fields are available only for miss events; all-event residue pairs here use remaining_K coordinates.
No proof, causality, counterexample, or global Collatz claim is made.

## Zone-Level Contrast

| group | events | miss | miss_rate | k | behavior | band jump | R mod16 pair | miss integer residue/parity |
|---|---:|---:|---:|---|---|---|---|---|
| miss_front_3_8 | 14743 | 228 | 0.015465 | 1:9142; 2:3358; 3:1433; 4:358; 5:306; 6:90; 7:37; 8:11; 9:6; 11:1; 10:1 | drift:13953; wait:562; miss:228 | 32-63->32-63:9704; 64-127->64-127:4143; 128-255->128-255:668; 32-63->16-31:159; 64-127->32-63:53; 128-255->64-127:16 | 3->2:2404; 8->7:1792; 4->3:1789; 5->4:1686; 7->5:1599; 7->6:768; 6->5:703; 5->3:510; 5->2:468; 6->3:388; 3->1:369; 8->6:364; 6->4:306; 8->5:300 | 3->15:64; 4->15:47; 3->14:38; 4->14:18; 5->15:13; 3->13:13; 4->13:8; 6->15:6; 3->12:4; 8->15:3 / OEEEEEO:85; OEEEEO:64; OEEEEEEO:44; OEEEEEEEO:19; OEEEEEEEEO:8; OEEEEEEEEEO:6; OEEEEEEEEEEEO:1; OEEEEEEEEEEO:1 |
| k_structure_corridor_12_30 | 34565 | 0 | 0.0 | 1:18891; 2:9825; 3:3732; 4:1213; 5:458; 6:263; 7:106; 8:33; 9:29; 10:11; 11:2; 12:1; 13:1 | drift:33299; wait:1266 | 32-63->32-63:22547; 64-127->64-127:10863; 128-255->128-255:1155 | 12->11:2474; 2->1:1830; 4->3:1747; 3->2:1744; 7->6:1702; 11->10:1645; 8->7:1639; 1->15:1628; 6->4:1482; 15->12:1451; 10->8:1391; 13->11:1214; 14->13:1010; 13->12:965 |  /  |

## Matched k-Similar Distance Pairs

| left | right | k L1 | non-k gap mean | left miss | right miss | key non-k difference |
|---:|---:|---:|---:|---:|---:|---|
| 3 | 27 | 0.037577 | 1.256115 | 122 | 0 | band: 32-63->32-63:1856; 64-127->64-127:884; 128-255->128-255:112; 32-63->16-31:86; 64-127->32-63:25; 128-255->64-127:11 vs 32-63->32-63:1472; 64-127->64-127:523; 128-255->128-255:40 |
| 4 | 27 | 0.051519 | 1.268966 | 75 | 0 | band: 32-63->32-63:1751; 64-127->64-127:277; 128-255->128-255:116; 32-63->16-31:56; 64-127->32-63:17; 128-255->64-127:2 vs 32-63->32-63:1472; 64-127->64-127:523; 128-255->128-255:40 |
| 4 | 18 | 0.058957 | 1.258654 | 75 | 0 | band: 32-63->32-63:1751; 64-127->64-127:277; 128-255->128-255:116; 32-63->16-31:56; 64-127->32-63:17; 128-255->64-127:2 vs 32-63->32-63:1629; 64-127->64-127:522; 128-255->128-255:71 |
| 4 | 23 | 0.09559 | 1.265075 | 75 | 0 | band: 32-63->32-63:1751; 64-127->64-127:277; 128-255->128-255:116; 32-63->16-31:56; 64-127->32-63:17; 128-255->64-127:2 vs 32-63->32-63:1628; 64-127->64-127:553; 128-255->128-255:47 |

## Largest Feature Gaps

| feature | scope | L1 gap | left | right |
|---|---|---:|---|---|
| remaining_K_before | all_events | 2.0 | 35:1942; 39:1924; 37:1848; 36:1807; 40:1745; 69:911; 67:909; 70:794; 72:759; 38:597; 71:529; 68:294; 134:127; 131:123 | 44:1774; 49:1760; 47:1701; 56:1650; 54:1642; 52:1630; 50:1629; 55:1628; 58:1610; 51:1606; 59:1472; 61:1220; 76:853; 81:796 |
| R_residue_pair_mod32 | all_events_remaining_K_coordinate | 2.0 | 3->2:2404; 8->7:1792; 4->3:1789; 5->4:1686; 7->5:1599; 7->6:768; 6->5:703; 5->3:510; 5->2:468; 6->3:388; 3->1:369; 8->6:364; 6->4:306; 8->5:300 | 12->11:2000; 18->17:1830; 20->19:1747; 19->18:1744; 23->22:1702; 27->26:1645; 24->23:1639; 17->15:1628; 22->20:1482; 15->12:1451; 26->24:1391; 29->27:1049; 17->16:659; 15->14:609 |
| R_residue_pair_mod16 | all_events_remaining_K_coordinate | 1.333071 | 3->2:2404; 8->7:1792; 4->3:1789; 5->4:1686; 7->5:1599; 7->6:768; 6->5:703; 5->3:510; 5->2:468; 6->3:388; 3->1:369; 8->6:364; 6->4:306; 8->5:300 | 12->11:2474; 2->1:1830; 4->3:1747; 3->2:1744; 7->6:1702; 11->10:1645; 8->7:1639; 1->15:1628; 6->4:1482; 15->12:1451; 10->8:1391; 13->11:1214; 14->13:1010; 13->12:965 |
| miss_local_type | miss_events_only | 1.0 | B:85; A:64; C_unassigned:50; C1:13; C2:10; C3:6 |  |
| integer_residue_pair_mod16 | miss_events_only_integer_coordinate | 1.0 | 3->15:64; 4->15:47; 3->14:38; 4->14:18; 5->15:13; 3->13:13; 4->13:8; 6->15:6; 3->12:4; 8->15:3; 3->11:3; 5->13:3; 4->12:2; 5->12:2 |  |
| integer_residue_pair_mod32 | miss_events_only_integer_coordinate | 1.0 | 3->31:64; 4->31:47; 3->30:38; 4->30:18; 5->31:13; 3->29:13; 4->29:8; 6->31:6; 3->28:4; 8->31:3; 3->27:3; 5->29:3; 4->28:2; 5->28:2 |  |
| expanded_parity_miss_only | miss_events_only | 1.0 | OEEEEEO:85; OEEEEO:64; OEEEEEEO:44; OEEEEEEEO:19; OEEEEEEEEO:8; OEEEEEEEEEO:6; OEEEEEEEEEEEO:1; OEEEEEEEEEEO:1 |  |
| transition_k | all_events | 0.162141 | 1:9142; 2:3358; 3:1433; 4:358; 5:306; 6:90; 7:37; 8:11; 9:6; 11:1; 10:1 | 1:18891; 2:9825; 3:3732; 4:1213; 5:458; 6:263; 7:106; 8:33; 9:29; 10:11; 11:2; 12:1; 13:1 |

## Reading

- k-similar distance pairs can still differ sharply in miss occurrence.
- The clearest all-event separators are exit_distance/remaining_K coordinates and band-jump context.
- For miss-front events, integer residue/parity coordinates are populated and structured; for the 12-30 corridor there are no miss events, so those fields are absent rather than contradictory.
- Therefore the contrast is not explained by k alone. The miss-front is a near-exit remaining_K/band-jump region with miss-specific residue/parity structure; the 12-30 corridor is a k-structure region without miss rows.

## Output Files

- `zone_coordinate_contrast.csv`
- `matched_k_distance_pair_contrast.csv`
- `miss_front_vs_k_corridor_feature_gap.csv`
