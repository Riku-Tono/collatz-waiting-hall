from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
DETAIL = OUT / "waiting_hall_interior_detail.csv"
MISS_EVENT_DETAIL = Path(
    r"C:\Users\yauki\Documents\Codex\2026-06-29\exit-layer-immediate-exit-exit-layer\outputs\miss_event_detail.csv"
)

MISS_TYPES = ["A", "B", "C1", "C2", "C3", "C_unassigned"]
PAIR_REQUESTS = [(3, 27), (4, 27), (4, 18), (4, 23)]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    if not fields:
        rows = [{"status": "no_rows"}]
        fields = ["status"]
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def pct(num: int, den: int) -> float:
    return round(num / den, 6) if den else 0.0


def top_counts(counter: Counter[str], n: int = 10) -> str:
    return "; ".join(f"{k}:{v}" for k, v in counter.most_common(n))


def dist(counter: Counter[str]) -> dict[str, float]:
    total = sum(counter.values())
    if total == 0:
        return {}
    return {k: counter[k] / total for k in counter}


def l1(a: Counter[str], b: Counter[str]) -> float:
    da = dist(a)
    db = dist(b)
    keys = set(da) | set(db)
    return round(sum(abs(da.get(k, 0.0) - db.get(k, 0.0)) for k in keys), 6)


def zone_for_distance(distance: int) -> str:
    if 3 <= distance <= 8:
        return "miss_front_3_8"
    if 12 <= distance <= 30:
        return "k_structure_corridor_12_30"
    return ""


def load_miss_detail() -> dict[tuple[str, str, str], dict[str, str]]:
    rows = read_csv(MISS_EVENT_DETAIL)
    return {(r["sample_id"], r["trajectory_id"], r["miss_event_index"]): r for r in rows}


def load_events() -> list[dict[str, object]]:
    miss_lookup = load_miss_detail()
    events = []
    for row in read_csv(DETAIL):
        distance = int(row["distance_from_exit"])
        zone = zone_for_distance(distance)
        if not zone:
            continue
        r_before = int(row["remaining_K_before"])
        r_after = int(row["remaining_K_after"])
        key = (row["sample_id"], row["trajectory_id"], row["event_index"])
        miss = miss_lookup.get(key, {})
        int_residue_pair_mod16 = ""
        int_residue_pair_mod32 = ""
        expanded_parity = ""
        if miss:
            int_residue_pair_mod16 = f"{miss['miss_before_mod_16']}->{miss['miss_after_mod_16']}"
            int_residue_pair_mod32 = f"{miss['miss_before_mod_32']}->{miss['miss_after_mod_32']}"
            expanded_parity = miss.get("collatz_miss_step_parity_pattern", "")
        events.append(
            {
                "zone": zone,
                "exit_distance": distance,
                "event_count_unit": 1,
                "miss_event": int(row["miss_event"]),
                "miss_local_type": row["miss_local_type"] if row["miss_local_type"] in MISS_TYPES else "",
                "transition_k": row["transition_k"],
                "near_behavior": row["near_behavior"],
                "band_jump": f"{row['band']}->{row['band_after']}",
                "band_before": row["band"],
                "band_after": row["band_after"],
                "remaining_K_before": str(r_before),
                "remaining_K_after": str(r_after),
                "R_residue_pair_mod16": f"{r_before % 16}->{r_after % 16}",
                "R_residue_pair_mod32": f"{r_before % 32}->{r_after % 32}",
                "R_before_mod16": str(r_before % 16),
                "R_before_mod32": str(r_before % 32),
                "integer_residue_pair_mod16": int_residue_pair_mod16,
                "integer_residue_pair_mod32": int_residue_pair_mod32,
                "expanded_parity_miss_only": expanded_parity,
            }
        )
    return events


def counter_for(events: list[dict[str, object]], feature: str) -> Counter[str]:
    return Counter(str(e[feature]) for e in events if str(e.get(feature, "")) != "")


def summarize_group(label: str, events: list[dict[str, object]]) -> dict[str, object]:
    miss_count = sum(int(e["miss_event"]) for e in events)
    row: dict[str, object] = {
        "group": label,
        "event_count": len(events),
        "miss_count": miss_count,
        "miss_rate": pct(miss_count, len(events)),
        "transition_k_distribution": top_counts(counter_for(events, "transition_k"), 14),
        "behavior_distribution": top_counts(counter_for(events, "near_behavior")),
        "band_jump_distribution": top_counts(counter_for(events, "band_jump"), 14),
        "remaining_K_before_distribution": top_counts(counter_for(events, "remaining_K_before"), 14),
        "R_residue_pair_mod16_distribution": top_counts(counter_for(events, "R_residue_pair_mod16"), 14),
        "R_residue_pair_mod32_distribution": top_counts(counter_for(events, "R_residue_pair_mod32"), 14),
        "miss_type_distribution": top_counts(counter_for(events, "miss_local_type")),
        "integer_residue_pair_mod16_miss_only": top_counts(counter_for(events, "integer_residue_pair_mod16")),
        "integer_residue_pair_mod32_miss_only": top_counts(counter_for(events, "integer_residue_pair_mod32")),
        "expanded_parity_miss_only": top_counts(counter_for(events, "expanded_parity_miss_only")),
        "coordinate_scope_note": "R_residue_pair is available for all events; integer residue and expanded parity are available only for miss events",
    }
    return row


def zone_coordinate_contrast(events: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        groups[str(event["zone"])].append(event)
    rows = []
    for zone in ["miss_front_3_8", "k_structure_corridor_12_30"]:
        rows.append(summarize_group(zone, groups[zone]))
    return rows


def feature_gap_rows(events_a: list[dict[str, object]], events_b: list[dict[str, object]], label_a: str, label_b: str) -> list[dict[str, object]]:
    features = [
        ("transition_k", "all_events"),
        ("near_behavior", "all_events"),
        ("band_jump", "all_events"),
        ("remaining_K_before", "all_events"),
        ("R_residue_pair_mod16", "all_events_remaining_K_coordinate"),
        ("R_residue_pair_mod32", "all_events_remaining_K_coordinate"),
        ("miss_local_type", "miss_events_only"),
        ("integer_residue_pair_mod16", "miss_events_only_integer_coordinate"),
        ("integer_residue_pair_mod32", "miss_events_only_integer_coordinate"),
        ("expanded_parity_miss_only", "miss_events_only"),
    ]
    rows = []
    for feature, scope in features:
        ca = counter_for(events_a, feature)
        cb = counter_for(events_b, feature)
        rows.append(
            {
                "left_group": label_a,
                "right_group": label_b,
                "feature": feature,
                "coordinate_scope": scope,
                "left_event_count_with_feature": sum(ca.values()),
                "right_event_count_with_feature": sum(cb.values()),
                "feature_l1_gap": l1(ca, cb),
                "left_distribution": top_counts(ca, 14),
                "right_distribution": top_counts(cb, 14),
                "dominant_difference_reading": "high gap separates groups" if l1(ca, cb) >= 1.0 else "partial overlap or unavailable on one side",
            }
        )
    return rows


def matched_pair_contrast(events: list[dict[str, object]]) -> list[dict[str, object]]:
    by_distance: dict[int, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        by_distance[int(event["exit_distance"])].append(event)
    rows = []
    for left_d, right_d in PAIR_REQUESTS:
        left = by_distance[left_d]
        right = by_distance[right_d]
        gaps = feature_gap_rows(left, right, f"distance_{left_d}", f"distance_{right_d}")
        non_k_gap = sum(
            float(r["feature_l1_gap"])
            for r in gaps
            if r["feature"] in {"near_behavior", "band_jump", "remaining_K_before", "R_residue_pair_mod16", "R_residue_pair_mod32"}
        ) / 5
        k_gap = [r for r in gaps if r["feature"] == "transition_k"][0]["feature_l1_gap"]
        rows.append(
            {
                "left_distance": left_d,
                "right_distance": right_d,
                "left_event_count": len(left),
                "right_event_count": len(right),
                "left_miss_count": sum(int(e["miss_event"]) for e in left),
                "right_miss_count": sum(int(e["miss_event"]) for e in right),
                "left_miss_rate": pct(sum(int(e["miss_event"]) for e in left), len(left)),
                "right_miss_rate": pct(sum(int(e["miss_event"]) for e in right), len(right)),
                "k_l1_gap": k_gap,
                "non_k_coordinate_gap_mean": round(non_k_gap, 6),
                "left_transition_k_distribution": top_counts(counter_for(left, "transition_k")),
                "right_transition_k_distribution": top_counts(counter_for(right, "transition_k")),
                "left_band_jump_distribution": top_counts(counter_for(left, "band_jump")),
                "right_band_jump_distribution": top_counts(counter_for(right, "band_jump")),
                "left_R_pair_mod16_distribution": top_counts(counter_for(left, "R_residue_pair_mod16")),
                "right_R_pair_mod16_distribution": top_counts(counter_for(right, "R_residue_pair_mod16")),
                "left_integer_residue_pair_mod16_miss_only": top_counts(counter_for(left, "integer_residue_pair_mod16")),
                "right_integer_residue_pair_mod16_miss_only": top_counts(counter_for(right, "integer_residue_pair_mod16")),
                "left_expanded_parity_miss_only": top_counts(counter_for(left, "expanded_parity_miss_only")),
                "right_expanded_parity_miss_only": top_counts(counter_for(right, "expanded_parity_miss_only")),
                "ranking_note": "k-similar but miss-different pair; non-k gap summarizes behavior/band/R-coordinate differences",
            }
        )
    return sorted(rows, key=lambda r: (float(r["k_l1_gap"]), -float(r["non_k_coordinate_gap_mean"])))


def build_report(zone_rows, pair_rows, gap_rows) -> None:
    top_gaps = sorted(gap_rows, key=lambda r: -float(r["feature_l1_gap"]))[:8]
    lines = [
        "# Zone Coordinate Contrast Report",
        "",
        "This is a finite observational coordinate contrast, not a mechanism.",
        "Exit distance and residues are coordinates, not causes.",
        "Integer residue/parity fields are available only for miss events; all-event residue pairs here use remaining_K coordinates.",
        "No proof, causality, counterexample, or global Collatz claim is made.",
        "",
        "## Zone-Level Contrast",
        "",
        "| group | events | miss | miss_rate | k | behavior | band jump | R mod16 pair | miss integer residue/parity |",
        "|---|---:|---:|---:|---|---|---|---|---|",
    ]
    for row in zone_rows:
        lines.append(
            f"| {row['group']} | {row['event_count']} | {row['miss_count']} | {row['miss_rate']} | "
            f"{row['transition_k_distribution']} | {row['behavior_distribution']} | {row['band_jump_distribution']} | "
            f"{row['R_residue_pair_mod16_distribution']} | {row['integer_residue_pair_mod16_miss_only']} / {row['expanded_parity_miss_only']} |"
        )
    lines.extend(
        [
            "",
            "## Matched k-Similar Distance Pairs",
            "",
            "| left | right | k L1 | non-k gap mean | left miss | right miss | key non-k difference |",
            "|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in pair_rows:
        lines.append(
            f"| {row['left_distance']} | {row['right_distance']} | {row['k_l1_gap']} | {row['non_k_coordinate_gap_mean']} | "
            f"{row['left_miss_count']} | {row['right_miss_count']} | band: {row['left_band_jump_distribution']} vs {row['right_band_jump_distribution']} |"
        )
    lines.extend(["", "## Largest Feature Gaps", "", "| feature | scope | L1 gap | left | right |", "|---|---|---:|---|---|"])
    for row in top_gaps:
        lines.append(
            f"| {row['feature']} | {row['coordinate_scope']} | {row['feature_l1_gap']} | {row['left_distribution']} | {row['right_distribution']} |"
        )
    lines.extend(
        [
            "",
            "## Reading",
            "",
            "- k-similar distance pairs can still differ sharply in miss occurrence.",
            "- The clearest all-event separators are exit_distance/remaining_K coordinates and band-jump context.",
            "- For miss-front events, integer residue/parity coordinates are populated and structured; for the 12-30 corridor there are no miss events, so those fields are absent rather than contradictory.",
            "- Therefore the contrast is not explained by k alone. The miss-front is a near-exit remaining_K/band-jump region with miss-specific residue/parity structure; the 12-30 corridor is a k-structure region without miss rows.",
            "",
            "## Output Files",
            "",
            "- `zone_coordinate_contrast.csv`",
            "- `matched_k_distance_pair_contrast.csv`",
            "- `miss_front_vs_k_corridor_feature_gap.csv`",
        ]
    )
    (OUT / "zone_coordinate_contrast_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    events = load_events()
    zone_rows = zone_coordinate_contrast(events)
    groups = defaultdict(list)
    for event in events:
        groups[str(event["zone"])].append(event)
    gap_rows = feature_gap_rows(
        groups["miss_front_3_8"],
        groups["k_structure_corridor_12_30"],
        "miss_front_3_8",
        "k_structure_corridor_12_30",
    )
    pair_rows = matched_pair_contrast(events)
    write_csv(OUT / "zone_coordinate_contrast.csv", zone_rows)
    write_csv(OUT / "matched_k_distance_pair_contrast.csv", pair_rows)
    write_csv(OUT / "miss_front_vs_k_corridor_feature_gap.csv", gap_rows)
    build_report(zone_rows, pair_rows, gap_rows)
    print(f"events={len(events)} zone_rows={len(zone_rows)} pairs={len(pair_rows)} feature_gaps={len(gap_rows)}")


if __name__ == "__main__":
    main()
