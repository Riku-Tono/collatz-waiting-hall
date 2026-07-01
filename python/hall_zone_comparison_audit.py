from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
DETAIL = OUT / "waiting_hall_interior_detail.csv"

MISS_TYPES = ["A", "B", "C1", "C2", "C3", "C_unassigned"]
BEHAVIORS = ["drift", "wait", "exit", "miss"]
ZONE_SPECS = {
    "miss_front_3_8": (3, 8),
    "k_structure_corridor_12_30": (12, 30),
}


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


def top_counts(counter: Counter[str], n: int = 12) -> str:
    return "; ".join(f"{k}:{v}" for k, v in counter.most_common(n))


def entropy(counter: Counter[str]) -> float:
    total = sum(counter.values())
    if not total:
        return 0.0
    return round(-sum((count / total) * math.log2(count / total) for count in counter.values()), 6)


def zone_for_distance(distance: int) -> str:
    for zone, (lo, hi) in ZONE_SPECS.items():
        if lo <= distance <= hi:
            return zone
    return ""


def load_events() -> list[dict[str, object]]:
    events = []
    for row in read_csv(DETAIL):
        distance = int(row["distance_from_exit"])
        zone = zone_for_distance(distance)
        if not zone:
            continue
        miss_type = row["miss_local_type"] if row["miss_local_type"] in MISS_TYPES else ""
        events.append(
            {
                "zone": zone,
                "exit_distance": distance,
                "transition_k": int(row["transition_k"]),
                "near_behavior": row["near_behavior"],
                "miss_event": int(row["miss_event"]),
                "miss_local_type": miss_type,
                "trajectory_behavior_class": row["trajectory_behavior_class"],
            }
        )
    return events


def distribution(counter: Counter[str]) -> dict[str, float]:
    total = sum(counter.values())
    keys = sorted(counter, key=lambda x: (int(x) if x.isdigit() else 999, x))
    return {key: pct(counter[key], total) for key in keys}


def l1_for_keys(a: dict[str, float], b: dict[str, float], keys: list[str]) -> float:
    return round(sum(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in keys), 6)


def aggregate_zone(events: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        groups[str(event["zone"])].append(event)
    rows = []
    for zone in ZONE_SPECS:
        vals = groups.get(zone, [])
        distances = [int(v["exit_distance"]) for v in vals]
        ks = [int(v["transition_k"]) for v in vals]
        k_counts = Counter(str(v["transition_k"]) for v in vals)
        miss_types = Counter(str(v["miss_local_type"]) for v in vals if str(v["miss_local_type"]))
        behaviors = Counter(str(v["near_behavior"]) for v in vals)
        miss_count = sum(int(v["miss_event"]) for v in vals)
        top2 = k_counts.most_common(2)
        row: dict[str, object] = {
            "zone": zone,
            "distance_min": min(distances) if distances else "",
            "distance_max": max(distances) if distances else "",
            "event_count": len(vals),
            "miss_count": miss_count,
            "miss_rate": pct(miss_count, len(vals)),
            "mean_transition_k": round(mean(ks), 6) if ks else "",
            "median_transition_k": median(ks) if ks else "",
            "dominant_k": top2[0][0] if top2 else "",
            "dominant_k_share": pct(top2[0][1], len(vals)) if top2 else "",
            "second_k": top2[1][0] if len(top2) > 1 else "",
            "second_k_share": pct(top2[1][1], len(vals)) if len(top2) > 1 else "",
            "k_entropy_bits": entropy(k_counts),
            "k_distribution": top_counts(k_counts, 99),
            "miss_type_distribution": top_counts(miss_types),
            "behavior_distribution": top_counts(behaviors),
            "trajectory_behavior_distribution": top_counts(Counter(str(v["trajectory_behavior_class"]) for v in vals)),
            "zone_reading": "miss-zone" if miss_count else "k-structure-zone",
        }
        for miss_type in MISS_TYPES:
            row[f"{miss_type}_count"] = miss_types[miss_type]
            row[f"{miss_type}_share_of_zone_events"] = pct(miss_types[miss_type], len(vals))
            row[f"{miss_type}_share_of_zone_misses"] = pct(miss_types[miss_type], miss_count)
        rows.append(row)
    return rows


def k_comparison(zone_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_zone = {str(r["zone"]): r for r in zone_rows}
    counters = {}
    shares = {}
    all_k = set()
    for zone, row in by_zone.items():
        c = Counter()
        for part in str(row["k_distribution"]).split("; "):
            if ":" in part:
                k, v = part.rsplit(":", 1)
                c[k] = int(v)
                all_k.add(k)
        counters[zone] = c
        shares[zone] = distribution(c)
    keys = sorted(all_k, key=lambda x: int(x))
    rows = []
    for k in keys:
        a = shares["miss_front_3_8"].get(k, 0.0)
        b = shares["k_structure_corridor_12_30"].get(k, 0.0)
        rows.append(
            {
                "transition_k": k,
                "miss_front_count": counters["miss_front_3_8"][k],
                "miss_front_share": a,
                "k_structure_count": counters["k_structure_corridor_12_30"][k],
                "k_structure_share": b,
                "share_difference_k_structure_minus_miss_front": round(b - a, 6),
                "abs_share_difference": round(abs(b - a), 6),
            }
        )
    rows.append(
        {
            "transition_k": "ALL_L1",
            "miss_front_count": sum(counters["miss_front_3_8"].values()),
            "miss_front_share": "",
            "k_structure_count": sum(counters["k_structure_corridor_12_30"].values()),
            "k_structure_share": "",
            "share_difference_k_structure_minus_miss_front": "",
            "abs_share_difference": l1_for_keys(shares["miss_front_3_8"], shares["k_structure_corridor_12_30"], keys),
        }
    )
    return rows


def miss_type_comparison(zone_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    by_zone = {str(r["zone"]): r for r in zone_rows}
    for miss_type in MISS_TYPES:
        mf_miss_share = float(by_zone["miss_front_3_8"][f"{miss_type}_share_of_zone_misses"])
        ks_miss_share = float(by_zone["k_structure_corridor_12_30"][f"{miss_type}_share_of_zone_misses"])
        rows.append(
            {
                "miss_local_type": miss_type,
                "miss_front_count": by_zone["miss_front_3_8"][f"{miss_type}_count"],
                "miss_front_share_of_misses": mf_miss_share,
                "miss_front_share_of_events": by_zone["miss_front_3_8"][f"{miss_type}_share_of_zone_events"],
                "k_structure_count": by_zone["k_structure_corridor_12_30"][f"{miss_type}_count"],
                "k_structure_share_of_misses": ks_miss_share,
                "k_structure_share_of_events": by_zone["k_structure_corridor_12_30"][f"{miss_type}_share_of_zone_events"],
                "share_difference_k_structure_minus_miss_front": round(ks_miss_share - mf_miss_share, 6),
            }
        )
    rows.append(
        {
            "miss_local_type": "ALL_MISS_RATE",
            "miss_front_count": by_zone["miss_front_3_8"]["miss_count"],
            "miss_front_share_of_misses": 1.0,
            "miss_front_share_of_events": by_zone["miss_front_3_8"]["miss_rate"],
            "k_structure_count": by_zone["k_structure_corridor_12_30"]["miss_count"],
            "k_structure_share_of_misses": "",
            "k_structure_share_of_events": by_zone["k_structure_corridor_12_30"]["miss_rate"],
            "share_difference_k_structure_minus_miss_front": "",
        }
    )
    return rows


def behavior_comparison(events: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        groups[str(event["zone"])].append(event)
    rows = []
    for behavior in BEHAVIORS:
        mf_count = sum(1 for v in groups["miss_front_3_8"] if v["near_behavior"] == behavior)
        ks_count = sum(1 for v in groups["k_structure_corridor_12_30"] if v["near_behavior"] == behavior)
        rows.append(
            {
                "near_behavior": behavior,
                "miss_front_count": mf_count,
                "miss_front_share": pct(mf_count, len(groups["miss_front_3_8"])),
                "k_structure_count": ks_count,
                "k_structure_share": pct(ks_count, len(groups["k_structure_corridor_12_30"])),
                "share_difference_k_structure_minus_miss_front": round(
                    pct(ks_count, len(groups["k_structure_corridor_12_30"])) - pct(mf_count, len(groups["miss_front_3_8"])),
                    6,
                ),
            }
        )
    return rows


def distance_profiles(events: list[dict[str, object]]) -> dict[int, Counter[str]]:
    profiles: dict[int, Counter[str]] = defaultdict(Counter)
    for event in events:
        profiles[int(event["exit_distance"])][str(event["transition_k"])] += 1
    return profiles


def similar_distance_pairs(events: list[dict[str, object]], top_n: int = 10) -> list[dict[str, object]]:
    profiles = distance_profiles(events)
    shares = {d: distribution(c) for d, c in profiles.items()}
    rows = []
    for d1 in range(3, 9):
        for d2 in range(12, 31):
            keys = sorted(set(shares[d1]) | set(shares[d2]), key=lambda x: int(x))
            score = l1_for_keys(shares[d1], shares[d2], keys)
            rows.append(
                {
                    "miss_front_distance": d1,
                    "k_structure_distance": d2,
                    "k_distribution_l1": score,
                    "miss_front_k_distribution": top_counts(profiles[d1]),
                    "k_structure_k_distribution": top_counts(profiles[d2]),
                    "reading": "lower score means more similar k distribution",
                }
            )
    return sorted(rows, key=lambda r: (float(r["k_distribution_l1"]), int(r["miss_front_distance"]), int(r["k_structure_distance"])))[:top_n]


def build_report(zone_rows, k_rows, miss_rows, behavior_rows, similar_rows) -> None:
    by_zone = {str(r["zone"]): r for r in zone_rows}
    l1_row = [r for r in k_rows if r["transition_k"] == "ALL_L1"][0]
    lines = [
        "# Hall Zone Comparison Report: miss-front 3-8 vs k-structure corridor 12-30",
        "",
        "This is a finite observational hall-zone comparison, not a mechanism.",
        "Exit distance is a coordinate, not a cause.",
        "Zone labels are descriptive groupings, not causal thresholds.",
        "No proof, causality, counterexample, or global Collatz claim is made.",
        "",
        "## Zone Summary",
        "",
        "| zone | distance | events | miss | miss_rate | dominant k | k distribution | behavior | reading |",
        "|---|---|---:|---:|---:|---|---|---|---|",
    ]
    for row in zone_rows:
        lines.append(
            f"| {row['zone']} | {row['distance_min']}-{row['distance_max']} | {row['event_count']} | {row['miss_count']} | "
            f"{row['miss_rate']} | {row['dominant_k']} | {row['k_distribution']} | {row['behavior_distribution']} | {row['zone_reading']} |"
        )
    lines.extend(
        [
            "",
            "## Direct Difference",
            "",
            f"- k-distribution L1 difference: {l1_row['abs_share_difference']}.",
            f"- miss-front miss_rate: {by_zone['miss_front_3_8']['miss_rate']}.",
            f"- k-structure corridor miss_rate: {by_zone['k_structure_corridor_12_30']['miss_rate']}.",
            "- Because the 12-30 zone has zero miss events here, it should be treated as a k-structure-zone, not a miss-zone.",
            "",
            "## Similar Distance Pairs",
            "",
            "| miss-front distance | corridor distance | k L1 |",
            "|---:|---:|---:|",
        ]
    )
    for row in similar_rows:
        lines.append(f"| {row['miss_front_distance']} | {row['k_structure_distance']} | {row['k_distribution_l1']} |")
    lines.extend(
        [
            "",
            "## Reading",
            "",
            "- The two regions are not the same phenomenon in this finite profile.",
            "- 3-8 combines nonzero miss events with a mostly k1/k2/k3 near-exit mix.",
            "- 12-30 has no miss events and instead shows alternating k-regimes, including k3 spike at 15 and k1/k2 flips around 22-23 and 26-27.",
            "- Some individual distances can look k-similar, but the zone-level miss and behavior profiles separate them.",
            "",
            "## Output Files",
            "",
            "- `hall_zone_comparison_3_8_vs_12_30.csv`",
            "- `hall_zone_k_distribution_comparison.csv`",
            "- `hall_zone_miss_type_comparison.csv`",
            "- `hall_zone_behavior_comparison.csv`",
        ]
    )
    (OUT / "hall_zone_comparison_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    events = load_events()
    zone_rows = aggregate_zone(events)
    k_rows = k_comparison(zone_rows)
    miss_rows = miss_type_comparison(zone_rows)
    behavior_rows = behavior_comparison(events)
    similar_rows = similar_distance_pairs(events)
    write_csv(OUT / "hall_zone_comparison_3_8_vs_12_30.csv", zone_rows + [{"zone": "similar_distance_pair", **r} for r in similar_rows])
    write_csv(OUT / "hall_zone_k_distribution_comparison.csv", k_rows)
    write_csv(OUT / "hall_zone_miss_type_comparison.csv", miss_rows)
    write_csv(OUT / "hall_zone_behavior_comparison.csv", behavior_rows)
    build_report(zone_rows, k_rows, miss_rows, behavior_rows, similar_rows)
    print(
        f"events={len(events)} miss_front={zone_rows[0]['event_count']} k_structure={zone_rows[1]['event_count']} "
        f"k_l1={[r for r in k_rows if r['transition_k'] == 'ALL_L1'][0]['abs_share_difference']}"
    )


if __name__ == "__main__":
    main()
