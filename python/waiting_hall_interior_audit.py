from __future__ import annotations

import csv
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "outputs"
PREEXIT_WORK = Path(r"C:\Users\yauki\Documents\Codex\2026-06-29\task-scale-recurrence-audit-of-merge\work")
PREEXIT_OUT = Path(r"C:\Users\yauki\Documents\Codex\2026-06-29\task-scale-recurrence-audit-of-merge\outputs")
MISS_STATE_OUT = Path(r"C:\Users\yauki\Documents\design\collatz\collatz_state\2026-06-30_collatz_state\csv")
NEWCHAT_OUT = Path(r"C:\Users\yauki\Documents\Codex\2026-06-29\new-chat-3\outputs")

sys.path.insert(0, str(PREEXIT_WORK))
import preexit_waiting_hall_audit as preexit  # noqa: E402


ZONE_ORDER = ["upper_hall", "mid_hall", "lower_hall", "exit_layer"]
EXIT_LAYER_WIDTH = 2


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    if not fields:
        fields = ["status"]
        rows = [{"status": "no_rows"}]
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def top_counts(counter: Counter[str], n: int = 8) -> str:
    return "; ".join(f"{k}:{v}" for k, v in counter.most_common(n))


def band_bounds(label: str) -> tuple[int, int]:
    lo, hi = label.split("-", 1)
    return int(lo), int(hi)


def hall_zone(remaining_k: int, band_lower: int, band_upper: int) -> tuple[str, int, float]:
    distance = remaining_k - band_lower
    width = max(1, band_upper - band_lower)
    ratio = distance / width
    if distance <= EXIT_LAYER_WIDTH:
        return "exit_layer", distance, ratio
    if ratio <= 1 / 3:
        return "lower_hall", distance, ratio
    if ratio <= 2 / 3:
        return "mid_hall", distance, ratio
    return "upper_hall", distance, ratio


def coarse_type(value: str) -> str:
    if value.startswith("A"):
        return "A"
    if value.startswith("B"):
        return "B"
    if value.startswith("C_unassigned"):
        return "C_unassigned"
    if value.startswith("C"):
        return "C"
    return value or "none"


def k_bucket(k: int) -> str:
    if k == 1:
        return "k1"
    if k == 2:
        return "k2"
    if k == 3:
        return "k3"
    if k <= 5:
        return "k4_5"
    return "k6plus"


def load_preexit_context() -> tuple[dict[tuple[str, str, str], dict[str, str]], dict[tuple[str, str, str], dict[str, str]]]:
    behavior = {
        (r["sample_id"], r["trajectory_id"], r["band_label"]): r
        for r in read_csv(PREEXIT_OUT / "preexit_step3_behavior_classes.csv")
    }
    waiting = {
        (r["sample_id"], r["trajectory_id"], r["band_label"]): r
        for r in read_csv(PREEXIT_OUT / "exit_waiting_behavior.csv")
    }
    return behavior, waiting


def load_miss_context() -> tuple[dict[tuple[str, str, str], dict[str, str]], dict[tuple[str, str, str], dict[str, str]]]:
    miss_events = {}
    for r in read_csv(MISS_STATE_OUT / "miss_transition_windows_detail.csv"):
        if r.get("delta") == "0":
            miss_events[(r["sample_id"], r["trajectory_id"], r["event_index"])] = r

    join = {}
    for r in read_csv(NEWCHAT_OUT / "miss_wait_event_join_detail.csv"):
        join[(r["sample_id"], r["trajectory_id"], r["miss_event_index"])] = r
    return miss_events, join


def classify_event(row: dict[str, object], behavior_class: str, is_miss: bool) -> str:
    if is_miss:
        return "miss"
    if row["band_after"] != row["band"]:
        return "exit"
    if row["position_label"] == "exit_layer":
        return "exit"
    if "drift_down" in behavior_class or "then_drop" in behavior_class:
        return "drift"
    return "wait"


def build_detail() -> list[dict[str, object]]:
    raw, _sample_meta = preexit.prepare_raw()
    behavior_map, waiting_map = load_preexit_context()
    miss_event_map, miss_join_map = load_miss_context()

    detail: list[dict[str, object]] = []
    for item in raw:
        sample_id = str(item["sample_id"])
        trajectory_id = str(item["trajectory_id"])
        band = str(item["band_label"])
        lower = int(item["band_lower_edge"])
        upper = int(item["band_upper_edge"])
        start = int(item["first_entry_index"])
        end = int(item["first_pass_index"])
        key = (sample_id, trajectory_id, band)
        behavior = behavior_map.get(key, {})
        waiting = waiting_map.get(key, {})
        events = [
            e
            for e in item["events"]
            if start <= int(e["position"]) <= end and str(e["from_band"]) == band
        ]
        prev_k = None
        for idx, event in enumerate(events):
            event_index = int(event["position"])
            r_before = int(event["remaining_K_before"])
            transition_k = int(event["transition_k"])
            zone, distance, ratio = hall_zone(r_before, lower, upper)
            if idx + 1 < len(events):
                next_event = events[idx + 1]
                next_zone, _next_distance, _next_ratio = hall_zone(int(next_event["remaining_K_before"]), lower, upper)
                next_destination = next_zone
            elif str(event["to_band"]) != band:
                next_destination = f"exit_to_{event['to_band']}"
            else:
                next_destination = "end_of_observed_window"
            k_move = "start"
            if prev_k is not None:
                if transition_k > prev_k:
                    k_move = "up"
                elif transition_k < prev_k:
                    k_move = "down"
                else:
                    k_move = "flat"
            prev_k = transition_k

            miss = miss_event_map.get((sample_id, trajectory_id, str(event_index)), {})
            join = miss_join_map.get((sample_id, trajectory_id, str(event_index)), {})
            row: dict[str, object] = {
                "sample_id": sample_id,
                "trajectory_id": trajectory_id,
                "event_index": event_index,
                "band": band,
                "remaining_K_before": r_before,
                "transition_k": transition_k,
                "position_label": zone,
                "distance_from_exit": distance,
                "distance_ratio_in_band": round(ratio, 6),
                "band_after": str(event["to_band"]),
                "remaining_K_after": int(event["remaining_K_after"]),
                "next_destination": next_destination,
                "near_behavior": "",
                "k_move_from_previous": k_move,
                "wait_length": waiting.get("wait_length", ""),
                "waiting_class": waiting.get("waiting_class", ""),
                "trajectory_behavior_class": behavior.get("behavior_class", ""),
                "miss_event": int(bool(miss)),
                "miss_local_type": miss.get("inherited_miss_local_type", join.get("miss_local_type", "")),
                "miss_local_type_coarse": coarse_type(miss.get("inherited_miss_local_type", join.get("miss_local_type", ""))),
                "candidate_overlap": miss.get("candidate_overlap", join.get("candidate_overlap_note", "")),
                "next_caught_exit_layer": miss.get("next_caught_exit_layer", join.get("next_caught_exit_layer", "")),
                "source_scope": "first_entry_to_first_pass_event_rows",
            }
            row["near_behavior"] = classify_event(row, str(row["trajectory_behavior_class"]), bool(miss))
            detail.append(row)
    return detail


def summarize_zone(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for r in rows:
        groups[str(r["position_label"])].append(r)
    summary = []
    for zone in ZONE_ORDER:
        vals = groups.get(zone, [])
        waits = [int(v["wait_length"]) for v in vals if str(v["wait_length"]) != ""]
        exits = [v for v in vals if str(v["near_behavior"]) == "exit"]
        miss = [v for v in vals if int(v["miss_event"])]
        summary.append(
            {
                "position_label": zone,
                "event_count": len(vals),
                "mean_wait": round(mean(waits), 3) if waits else "",
                "median_wait": median(waits) if waits else "",
                "k_distribution": top_counts(Counter(str(v["transition_k"]) for v in vals)),
                "k_bucket_distribution": top_counts(Counter(k_bucket(int(v["transition_k"])) for v in vals)),
                "k_up": sum(1 for v in vals if v["k_move_from_previous"] == "up"),
                "k_down": sum(1 for v in vals if v["k_move_from_previous"] == "down"),
                "k_flat": sum(1 for v in vals if v["k_move_from_previous"] == "flat"),
                "miss_event_count": len(miss),
                "miss_local_type_distribution": top_counts(Counter(str(v["miss_local_type"]) for v in miss if str(v["miss_local_type"]))),
                "trajectory_behavior_distribution": top_counts(Counter(str(v["trajectory_behavior_class"]) for v in vals)),
                "near_behavior_distribution": top_counts(Counter(str(v["near_behavior"]) for v in vals)),
                "next_destination_distribution": top_counts(Counter(str(v["next_destination"]) for v in vals)),
                "exit_event_share": round(len(exits) / len(vals), 6) if vals else "",
            }
        )
    return summary


def summarize_k(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for r in rows:
        grouped[(str(r["position_label"]), str(r["transition_k"]))].append(r)
    out = []
    for zone in ZONE_ORDER:
        for k in sorted({int(key[1]) for key in grouped if key[0] == zone}):
            vals = grouped[(zone, str(k))]
            out.append(
                {
                    "position_label": zone,
                    "transition_k": k,
                    "event_count": len(vals),
                    "near_behavior_distribution": top_counts(Counter(str(v["near_behavior"]) for v in vals)),
                    "miss_local_type_distribution": top_counts(Counter(str(v["miss_local_type"]) for v in vals if str(v["miss_local_type"]))),
                    "next_destination_distribution": top_counts(Counter(str(v["next_destination"]) for v in vals)),
                }
            )
    return out


def summarize_type(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    total_by_type = Counter(str(r["miss_local_type"]) for r in rows if str(r["miss_local_type"]))
    for (zone, miss_type), vals in sorted(
        defaultdict(list, {}).items()
    ):
        pass
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    grouped_coarse: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for r in rows:
        if str(r["miss_local_type"]):
            grouped[(str(r["position_label"]), str(r["miss_local_type"]))].append(r)
            grouped_coarse[(str(r["position_label"]), str(r["miss_local_type_coarse"]))].append(r)
    for zone in ZONE_ORDER:
        for miss_type in sorted({k[1] for k in grouped if k[0] == zone}):
            vals = grouped[(zone, miss_type)]
            out.append(
                {
                    "position_label": zone,
                    "type_level": "local",
                    "miss_local_type": miss_type,
                    "event_count": len(vals),
                    "share_within_type": round(len(vals) / total_by_type[miss_type], 6) if total_by_type[miss_type] else "",
                    "transition_k_distribution": top_counts(Counter(str(v["transition_k"]) for v in vals)),
                    "candidate_overlap_distribution": top_counts(Counter(str(v["candidate_overlap"]) for v in vals)),
                    "next_destination_distribution": top_counts(Counter(str(v["next_destination"]) for v in vals)),
                }
            )
        for miss_type in sorted({k[1] for k in grouped_coarse if k[0] == zone}):
            vals = grouped_coarse[(zone, miss_type)]
            total = sum(1 for r in rows if str(r["miss_local_type_coarse"]) == miss_type)
            out.append(
                {
                    "position_label": zone,
                    "type_level": "coarse",
                    "miss_local_type": miss_type,
                    "event_count": len(vals),
                    "share_within_type": round(len(vals) / total, 6) if total else "",
                    "transition_k_distribution": top_counts(Counter(str(v["transition_k"]) for v in vals)),
                    "candidate_overlap_distribution": top_counts(Counter(str(v["candidate_overlap"]) for v in vals)),
                    "next_destination_distribution": top_counts(Counter(str(v["next_destination"]) for v in vals)),
                }
            )
    return out


def fonts():
    try:
        return ImageFont.truetype("arial.ttf", 24), ImageFont.truetype("arial.ttf", 15), ImageFont.truetype("arial.ttf", 11)
    except Exception:
        f = ImageFont.load_default()
        return f, f, f


def draw_waiting_hall_map(rows: list[dict[str, object]], summary: list[dict[str, object]]) -> None:
    title, body, small = fonts()
    counts = {r["position_label"]: int(r["event_count"]) for r in summary}
    miss_counts = {z: sum(1 for r in rows if r["position_label"] == z and int(r["miss_event"])) for z in ZONE_ORDER}
    max_count = max(counts.values() or [1])
    img = Image.new("RGB", (1250, 720), "#f8f8f5")
    draw = ImageDraw.Draw(img)
    draw.text((40, 32), "Waiting Hall Interior Map", fill="#222", font=title)
    draw.text((40, 62), "Finite event map: position is distance from the lower-edge exit layer.", fill="#555", font=small)
    y0 = 135
    colors = {
        "upper_hall": "#7aa6c2",
        "mid_hall": "#d8b365",
        "lower_hall": "#80b1a2",
        "exit_layer": "#d96767",
    }
    for i, zone in enumerate(ZONE_ORDER):
        y = y0 + i * 130
        width = int(850 * counts.get(zone, 0) / max_count)
        draw.rounded_rectangle((210, y, 210 + width, y + 70), radius=8, fill=colors[zone], outline="#333")
        draw.text((40, y + 20), zone, fill="#222", font=body)
        draw.text((225, y + 18), f"events={counts.get(zone, 0)}  miss={miss_counts.get(zone, 0)}", fill="white", font=body)
        draw.text((225, y + 44), f"near: {next((s['near_behavior_distribution'] for s in summary if s['position_label'] == zone), '')[:90]}", fill="white", font=small)
    draw.text((975, 650), "exit direction", fill="#555", font=small)
    draw.line((1100, 150, 1100, 585), fill="#555", width=3)
    draw.polygon([(1100, 610), (1088, 585), (1112, 585)], fill="#555")
    img.save(OUT / "waiting_hall_interior_map.png")


def draw_flow_map(rows: list[dict[str, object]]) -> None:
    title, body, small = fonts()
    edges = Counter((str(r["position_label"]), str(r["next_destination"])) for r in rows)
    max_edge = max(edges.values() or [1])
    positions = {
        "upper_hall": (160, 110),
        "mid_hall": (160, 270),
        "lower_hall": (160, 430),
        "exit_layer": (160, 590),
        "exit_to_16-31": (850, 330),
        "exit_to_32-63": (850, 410),
        "exit_to_64-127": (850, 490),
        "end_of_observed_window": (850, 570),
    }
    img = Image.new("RGB", (1200, 760), "#f8f8f5")
    draw = ImageDraw.Draw(img)
    draw.text((40, 32), "Band Position Flow Map", fill="#222", font=title)
    draw.text((40, 62), "Aggregated next destination from each hall zone.", fill="#555", font=small)
    for (src, dst), count in sorted(edges.items(), key=lambda kv: kv[1]):
        if src not in positions:
            continue
        if dst not in positions:
            positions[dst] = (850, 150 + 55 * (len(positions) % 9))
        x1, y1 = positions[src]
        x2, y2 = positions[dst]
        w = 1 + int(7 * count / max_edge)
        draw.line((x1 + 150, y1 + 22, x2, y2 + 22), fill="#777", width=w)
    for node, (x, y) in positions.items():
        count = sum(v for (s, _d), v in edges.items() if s == node) or sum(v for (_s, d), v in edges.items() if d == node)
        draw.rounded_rectangle((x, y, x + 230, y + 48), radius=7, fill="#ffffff", outline="#333")
        draw.text((x + 10, y + 8), f"{node} ({count})", fill="#222", font=small)
    img.save(OUT / "band_position_flow_map.png")


def draw_k_heatmap(rows: list[dict[str, object]]) -> None:
    title, body, small = fonts()
    ks = sorted({int(r["transition_k"]) for r in rows})
    zones = ZONE_ORDER
    counts = Counter((str(r["position_label"]), int(r["transition_k"])) for r in rows)
    max_count = max(counts.values() or [1])
    cell_w, cell_h = 62, 64
    img = Image.new("RGB", (220 + cell_w * len(ks), 210 + cell_h * len(zones)), "#f8f8f5")
    draw = ImageDraw.Draw(img)
    draw.text((35, 30), "k by Hall Zone Heatmap", fill="#222", font=title)
    draw.text((35, 60), "Cell value is event count.", fill="#555", font=small)
    x0, y0 = 180, 125
    for j, k in enumerate(ks):
        draw.text((x0 + j * cell_w + 16, y0 - 25), str(k), fill="#222", font=small)
    for i, zone in enumerate(zones):
        draw.text((35, y0 + i * cell_h + 22), zone, fill="#222", font=small)
        for j, k in enumerate(ks):
            c = counts[(zone, k)]
            intensity = int(245 - 185 * math.sqrt(c / max_count)) if c else 245
            color = (intensity, int(250 - 120 * math.sqrt(c / max_count)) if c else 250, 235)
            x = x0 + j * cell_w
            y = y0 + i * cell_h
            draw.rectangle((x, y, x + cell_w - 3, y + cell_h - 3), fill=color, outline="#ddd")
            if c:
                draw.text((x + 14, y + 22), str(c), fill="#111", font=small)
    img.save(OUT / "k_by_hall_zone_heatmap.png")


def build_report(rows: list[dict[str, object]], zone_summary: list[dict[str, object]]) -> None:
    upper = [r for r in rows if r["position_label"] == "upper_hall" and r["k_move_from_previous"] in {"up", "down", "flat"}]
    lower = [r for r in rows if r["position_label"] == "lower_hall" and r["k_move_from_previous"] in {"up", "down", "flat"}]
    mid_wait = [r for r in rows if r["position_label"] == "mid_hall" and str(r["trajectory_behavior_class"]) == "mid_band_wait_then_drop"]
    drift_starts = {}
    for r in rows:
        key = (r["sample_id"], r["trajectory_id"], r["band"])
        if str(r["trajectory_behavior_class"]) == "drift_down" and key not in drift_starts:
            drift_starts[key] = r["position_label"]
    miss_rows = [r for r in rows if int(r["miss_event"])]
    miss_zone = Counter(str(r["position_label"]) for r in miss_rows)
    coarse = Counter((str(r["miss_local_type_coarse"]), str(r["position_label"])) for r in miss_rows)

    lines = [
        "# Waiting Hall Interior Report",
        "",
        "This is a finite-sample observational map. It does not claim a mechanism, proof, or global Collatz result.",
        "",
        "## Scope",
        "",
        "- Object: band-internal event rows from first entry to first pass.",
        "- Position: `remaining_K_before - band_lower_edge` is treated as distance from the exit.",
        "- `exit_layer`: distance 0-2, matching the previous exit-layer audit width.",
        "- `lower_hall / mid_hall / upper_hall`: the non-exit part of the band split by within-band distance ratio.",
        "- No new miss type is created. Existing `A/B/C1/C2/C3/C_unassigned` labels are reused as-is.",
        "",
        "## Zone Summary",
        "",
        "| zone | events | mean wait | median wait | k movement | near behavior | miss types |",
        "|---|---:|---:|---:|---|---|---|",
    ]
    for s in zone_summary:
        lines.append(
            f"| {s['position_label']} | {s['event_count']} | {s['mean_wait']} | {s['median_wait']} | "
            f"up:{s['k_up']} down:{s['k_down']} flat:{s['k_flat']} | {s['near_behavior_distribution']} | {s['miss_local_type_distribution']} |"
        )

    def move_dist(vals: list[dict[str, object]]) -> str:
        return top_counts(Counter(str(v["k_move_from_previous"]) for v in vals))

    lines.extend(
        [
            "",
            "## Requested Comparisons",
            "",
            f"- upper_hall k movement: {move_dist(upper)}",
            f"- lower_hall k movement: {move_dist(lower)}",
            f"- `mid_band_wait_then_drop` has {len(mid_wait)} mid_hall events. By zone: {top_counts(Counter(str(r['position_label']) for r in rows if str(r['trajectory_behavior_class']) == 'mid_band_wait_then_drop'))}",
            f"- First observed zone for `drift_down` trajectories: {top_counts(Counter(str(v) for v in drift_starts.values()))}",
            f"- Miss event zone distribution: {top_counts(miss_zone)}",
            f"- A/B/C/C_unassigned coarse type x zone: {top_counts(coarse, 20)}",
            "",
            "## Reading",
            "",
            "Inside the hall, events are distributed across lower/mid/upper positions as well as the exit layer. `near_behavior` is an observational label derived from position plus existing behavior/miss joins; it is not a new type.",
            "",
            "`drift_down` is kept as a candidate-overlap context item, consistent with the previous audit. It is not promoted to a direct event-level causal relation.",
            "",
            "## Outputs",
            "",
            "- `waiting_hall_interior_detail.csv`",
            "- `waiting_hall_zone_summary.csv`",
            "- `waiting_hall_k_summary.csv`",
            "- `waiting_hall_type_distribution.csv`",
            "- `waiting_hall_interior_map.png`",
            "- `band_position_flow_map.png`",
            "- `k_by_hall_zone_heatmap.png`",
        ]
    )
    (OUT / "waiting_hall_interior_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    detail = build_detail()
    zone_summary = summarize_zone(detail)
    k_summary = summarize_k(detail)
    type_summary = summarize_type(detail)

    write_csv(OUT / "waiting_hall_interior_detail.csv", detail)
    write_csv(OUT / "waiting_hall_zone_summary.csv", zone_summary)
    write_csv(OUT / "waiting_hall_k_summary.csv", k_summary)
    write_csv(OUT / "waiting_hall_type_distribution.csv", type_summary)
    draw_waiting_hall_map(detail, zone_summary)
    draw_flow_map(detail)
    draw_k_heatmap(detail)
    build_report(detail, zone_summary)
    print(f"events={len(detail)} zones={len(zone_summary)} k_rows={len(k_summary)} type_rows={len(type_summary)}")


if __name__ == "__main__":
    main()
