from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
DETAIL = OUT / "waiting_hall_interior_detail.csv"
START_DISTANCE = 12
END_DISTANCE = 30
REQUESTED = {15, 18, 23, 27}


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


def entropy(counter: Counter[str]) -> float:
    total = sum(counter.values())
    if not total:
        return 0.0
    return round(-sum((count / total) * math.log2(count / total) for count in counter.values()), 6)


def load_events() -> list[dict[str, object]]:
    events = []
    for row in read_csv(DETAIL):
        distance = int(row["distance_from_exit"])
        if START_DISTANCE <= distance <= END_DISTANCE:
            events.append(
                {
                    "exit_distance": distance,
                    "transition_k": int(row["transition_k"]),
                    "near_behavior": row["near_behavior"],
                    "k_move": row["k_move_from_previous"],
                    "miss_event": int(row["miss_event"]),
                    "trajectory_behavior_class": row["trajectory_behavior_class"],
                }
            )
    return events


def profile_rows(events: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[int, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        groups[int(event["exit_distance"])].append(event)
    rows = []
    for distance in range(START_DISTANCE, END_DISTANCE + 1):
        vals = groups.get(distance, [])
        total = len(vals)
        k_counts = Counter(str(v["transition_k"]) for v in vals)
        top2 = k_counts.most_common(2)
        top1_k, top1_count = top2[0] if top2 else ("", 0)
        top2_k, top2_count = top2[1] if len(top2) > 1 else ("", 0)
        rows.append(
            {
                "exit_distance": distance,
                "requested_landmark": int(distance in REQUESTED),
                "event_count": total,
                "dominant_k": top1_k,
                "dominant_k_count": top1_count,
                "dominant_k_share": pct(top1_count, total),
                "second_k": top2_k,
                "second_k_count": top2_count,
                "second_k_share": pct(top2_count, total),
                "top2_k_pair": f"{top1_k}/{top2_k}" if top2_k else top1_k,
                "top2_share": pct(top1_count + top2_count, total),
                "distinct_k_count": len(k_counts),
                "k_entropy_bits": entropy(k_counts),
                "k_distribution": top_counts(k_counts, 14),
                "k1_share": pct(k_counts["1"], total),
                "k2_share": pct(k_counts["2"], total),
                "k3_share": pct(k_counts["3"], total),
                "k4_share": pct(k_counts["4"], total),
                "k_ge4_share": pct(sum(c for k, c in k_counts.items() if int(k) >= 4), total),
                "near_behavior_distribution": top_counts(Counter(str(v["near_behavior"]) for v in vals)),
                "k_move_distribution": top_counts(Counter(str(v["k_move"]) for v in vals if str(v["k_move"]) in {"up", "down", "flat"})),
                "miss_count": sum(int(v["miss_event"]) for v in vals),
            }
        )
    return rows


def zone_for_distance(distance: int) -> str:
    if 12 <= distance <= 14:
        return "approach_to_k3_spike_12_14"
    if distance == 15:
        return "k3_spike_15"
    if 16 <= distance <= 18:
        return "k2_to_k1_reset_16_18"
    if 19 <= distance <= 21:
        return "k1_plateau_with_k4_tail_19_21"
    if 22 <= distance <= 23:
        return "k2_k1_flip_22_23"
    if 24 <= distance <= 27:
        return "outer_k1_k2_flip_24_27"
    if 28 <= distance <= 30:
        return "outer_mixed_tail_28_30"
    return "outside_corridor"


def zone_rows(events: list[dict[str, object]], profile: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        groups[zone_for_distance(int(event["exit_distance"]))].append(event)
    order = [
        "approach_to_k3_spike_12_14",
        "k3_spike_15",
        "k2_to_k1_reset_16_18",
        "k1_plateau_with_k4_tail_19_21",
        "k2_k1_flip_22_23",
        "outer_k1_k2_flip_24_27",
        "outer_mixed_tail_28_30",
    ]
    rows = []
    profile_by_d = {int(r["exit_distance"]): r for r in profile}
    for zone in order:
        vals = groups.get(zone, [])
        if not vals:
            continue
        distances = sorted({int(v["exit_distance"]) for v in vals})
        k_counts = Counter(str(v["transition_k"]) for v in vals)
        top2 = k_counts.most_common(2)
        support = "supported" if len(vals) >= 1000 and len(distances) >= 1 else "low_support"
        signature = []
        for d in distances:
            p = profile_by_d[d]
            signature.append(f"{d}:{p['dominant_k']}/{p['second_k']}")
        rows.append(
            {
                "zone_candidate": zone,
                "distance_min": min(distances),
                "distance_max": max(distances),
                "distance_signature": " -> ".join(signature),
                "event_count": len(vals),
                "support_level": support,
                "dominant_k": top2[0][0] if top2 else "",
                "dominant_k_share": pct(top2[0][1], len(vals)) if top2 else "",
                "second_k": top2[1][0] if len(top2) > 1 else "",
                "second_k_share": pct(top2[1][1], len(vals)) if len(top2) > 1 else "",
                "top2_share": pct(sum(c for _, c in top2), len(vals)) if top2 else "",
                "distinct_k_count": len(k_counts),
                "k_entropy_bits": entropy(k_counts),
                "k_distribution": top_counts(k_counts, 14),
                "k1_share": pct(k_counts["1"], len(vals)),
                "k2_share": pct(k_counts["2"], len(vals)),
                "k3_share": pct(k_counts["3"], len(vals)),
                "k4_share": pct(k_counts["4"], len(vals)),
                "k_ge4_share": pct(sum(c for k, c in k_counts.items() if int(k) >= 4), len(vals)),
                "interpretation": "descriptive k-structure corridor zone; not causal threshold",
            }
        )
    return rows


def fonts():
    try:
        return ImageFont.truetype("arial.ttf", 24), ImageFont.truetype("arial.ttf", 12), ImageFont.truetype("arial.ttf", 10)
    except Exception:
        f = ImageFont.load_default()
        return f, f, f


def draw_heatmap(profile: list[dict[str, object]]) -> None:
    title, body, small = fonts()
    raw_ks = sorted({int(k) for row in profile for k in [part.split(":")[0] for part in str(row["k_distribution"]).split("; ")] if k})
    raw_ks = [k for k in raw_ks if k <= 13]
    rows_by_d = {int(r["exit_distance"]): r for r in profile}
    count_by = {}
    max_count = 1
    for row in profile:
        d = int(row["exit_distance"])
        c = Counter()
        for part in str(row["k_distribution"]).split("; "):
            if ":" in part:
                k, v = part.rsplit(":", 1)
                c[int(k)] = int(v)
        for k, v in c.items():
            count_by[(d, k)] = v
            max_count = max(max_count, v)
    cell_w, cell_h = 58, 30
    width = 180 + len(raw_ks) * cell_w
    height = 120 + (END_DISTANCE - START_DISTANCE + 1) * cell_h
    img = Image.new("RGB", (width, height), "#fafaf7")
    draw = ImageDraw.Draw(img)
    draw.text((30, 24), "k-structure corridor, exit_distance 12-30", fill="#222", font=title)
    x0, y0 = 145, 85
    for j, k in enumerate(raw_ks):
        draw.text((x0 + j * cell_w + 16, y0 - 22), str(k), fill="#222", font=small)
    for i, d in enumerate(range(START_DISTANCE, END_DISTANCE + 1)):
        y = y0 + i * cell_h
        label = f"{d}*" if d in REQUESTED else str(d)
        draw.text((35, y + 7), label, fill="#b84a4a" if d in REQUESTED else "#222", font=small)
        dom = str(rows_by_d[d]["dominant_k"])
        draw.text((75, y + 7), f"dom {dom}", fill="#555", font=small)
        for j, k in enumerate(raw_ks):
            val = count_by.get((d, k), 0)
            intensity = int(250 - 190 * math.sqrt(val / max_count)) if val else 250
            color = (intensity, int(250 - 110 * math.sqrt(val / max_count)) if val else 250, 235)
            x = x0 + j * cell_w
            draw.rectangle((x, y, x + cell_w - 2, y + cell_h - 2), fill=color, outline="#eee")
            if val:
                draw.text((x + 5, y + 7), str(val), fill="#111", font=small)
    draw.text((30, height - 22), "* requested landmark distances", fill="#555", font=small)
    img.save(OUT / "k_structure_corridor_heatmap.png")


def build_report(profile: list[dict[str, object]], zones: list[dict[str, object]]) -> None:
    by_d = {int(r["exit_distance"]): r for r in profile}
    lines = [
        "# k-Structure Corridor Report",
        "",
        "This is a finite observational corridor profile, not a mechanism.",
        "Exit distance is a coordinate, not a cause.",
        "Zone candidates are descriptive groupings, not causal thresholds.",
        "No proof, causality, counterexample, or global Collatz claim is made.",
        "",
        "## Scope",
        "",
        "- Distance window: exit_distance 12-30.",
        "- This is treated separately from the miss-front region at exit_distance 3-8.",
        "- Main object: k distribution along distance, not miss type.",
        "",
        "## Requested Landmark Context",
        "",
        "| distance | events | dominant k | second k | top2 share | k1 | k2 | k3 | k4 | k>=4 | entropy |",
        "|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for d in [15, 18, 23, 27]:
        r = by_d[d]
        lines.append(
            f"| {d} | {r['event_count']} | {r['dominant_k']} | {r['second_k']} | {r['top2_share']} | "
            f"{r['k1_share']} | {r['k2_share']} | {r['k3_share']} | {r['k4_share']} | {r['k_ge4_share']} | {r['k_entropy_bits']} |"
        )
    lines.extend(
        [
            "",
            "## Corridor Zone Candidates",
            "",
            "| zone | distance | events | signature | dominant/second | entropy | support |",
            "|---|---|---:|---|---|---:|---|",
        ]
    )
    for z in zones:
        lines.append(
            f"| {z['zone_candidate']} | {z['distance_min']}-{z['distance_max']} | {z['event_count']} | "
            f"{z['distance_signature']} | {z['dominant_k']}/{z['second_k']} | {z['k_entropy_bits']} | {z['support_level']} |"
        )
    lines.extend(
        [
            "",
            "## Reading",
            "",
            "- Distance 15 is the clearest local spike: k=3 is dominant and reaches 0.590798 share.",
            "- Distance 18 is not a k3 point; it is a reset-like k1-heavy point after the 16-17 transition.",
            "- Distances 22-23 show a k2/k1 flip: distance 22 is k2-heavy, distance 23 is k1-heavy.",
            "- Distances 26-27 show a similar outer flip: distance 26 is k2-heavy, distance 27 is k1-heavy.",
            "- The 12-30 corridor is not a single smooth gradient. It is better described as alternating local regimes.",
            "- The zone split is supported descriptively, but should not be treated as a mechanism or threshold model.",
            "",
            "## Output Files",
            "",
            "- `k_structure_corridor_12_30.csv`",
            "- `k_structure_corridor_zone_candidates.csv`",
            "- `k_structure_corridor_heatmap.png`",
        ]
    )
    (OUT / "k_structure_corridor_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    events = load_events()
    profile = profile_rows(events)
    zones = zone_rows(events, profile)
    write_csv(OUT / "k_structure_corridor_12_30.csv", profile)
    write_csv(OUT / "k_structure_corridor_zone_candidates.csv", zones)
    draw_heatmap(profile)
    build_report(profile, zones)
    print(f"events={len(events)} distances={len(profile)} zones={len(zones)}")


if __name__ == "__main__":
    main()
