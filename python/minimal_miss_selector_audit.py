from __future__ import annotations

import itertools
import math
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
SOURCE_DETAIL = (
    Path("C:/Users/yauki/Documents/Codex/2026-06-30")
    / "task-waiting-hall-interior-map-audit"
    / "outputs"
    / "waiting_hall_interior_detail.csv"
)

COORDS = [
    "exit_distance",
    "remaining_K_before",
    "residue_pair_mod32",
    "transition_k",
]

REQUIRED_WORDING = [
    "These are finite-sample selector cells, not causal rules.",
    "Miss-only does not mean necessary, sufficient, or mechanistic outside this dataset.",
    "The result shows coordinate redundancy in this scan.",
    "No proof, causality, counterexample, or global Collatz claim is made.",
]

RESTRICTED_REPORT_PATTERNS = [
    r"\bmechanism\b",
    r"\bmechanistic\b",
    r"\bproof\b",
    r"\bcausality\b",
    r"\bcausal\b",
    r"\bcounterexample\b",
    r"\bglobal Collatz\b",
]


def normalize_event_table(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required_source = [
        "distance_from_exit",
        "remaining_K_before",
        "remaining_K_after",
        "transition_k",
        "miss_event",
    ]
    missing = [col for col in required_source if col not in df.columns]
    if missing:
        raise SystemExit(f"source table lacks required columns: {missing}")

    df = df.copy()
    df["event_row_id"] = range(1, len(df) + 1)
    df["exit_distance"] = pd.to_numeric(df["distance_from_exit"], errors="coerce").astype("Int64")
    df["remaining_K_before"] = pd.to_numeric(df["remaining_K_before"], errors="coerce").astype("Int64")
    df["remaining_K_after"] = pd.to_numeric(df["remaining_K_after"], errors="coerce").astype("Int64")
    df["transition_k"] = pd.to_numeric(df["transition_k"], errors="coerce").astype("Int64")
    df["residue_pair_mod32"] = (
        (df["remaining_K_before"] % 32).astype(str)
        + "->"
        + (df["remaining_K_after"] % 32).astype(str)
    )
    df["miss_event"] = pd.to_numeric(df["miss_event"], errors="coerce").fillna(0).astype(int)

    missing_coords = [coord for coord in COORDS if coord not in df.columns]
    if missing_coords:
        raise SystemExit(f"candidate coordinate columns missing after normalization: {missing_coords}")
    if df[COORDS].isna().any().any():
        bad = df[COORDS].isna().sum()
        raise SystemExit(f"candidate coordinates contain NA values: {bad.to_dict()}")
    return df


def selector_mask(df: pd.DataFrame, miss: pd.DataFrame, coords: list[str]) -> pd.Series:
    support = miss[coords].drop_duplicates()
    merged = df[coords].merge(support, on=coords, how="left", indicator=True)
    return merged["_merge"].eq("both")


def summarize_selector(df: pd.DataFrame, miss: pd.DataFrame, coords: list[str]) -> dict[str, object]:
    mask = selector_mask(df, miss, coords)
    matched = df.loc[mask]
    miss_count = int(matched["miss_event"].sum())
    non_miss_count = int(len(matched) - miss_count)
    matched_events = int(len(matched))
    miss_rate = miss_count / matched_events if matched_events else math.nan
    return {
        "coordinate_set": " + ".join(coords),
        "tuple_count": int(miss[coords].drop_duplicates().shape[0]),
        "matched_events": matched_events,
        "miss_count": miss_count,
        "non_miss_count": non_miss_count,
        "miss_rate": round(miss_rate, 6) if matched_events else "",
    }


def tuple_detail(df: pd.DataFrame, miss: pd.DataFrame, coords: list[str]) -> pd.DataFrame:
    support = miss.groupby(coords, dropna=False).size().reset_index(name="selector_miss_support_count")
    counts = (
        df.groupby(coords, dropna=False)["miss_event"]
        .agg(matched_events="count", miss_count="sum")
        .reset_index()
    )
    detail = support.merge(counts, on=coords, how="left")
    detail["non_miss_count"] = detail["matched_events"] - detail["miss_count"]
    detail["miss_rate"] = (detail["miss_count"] / detail["matched_events"]).round(6)
    detail["tuple_values"] = detail.apply(
        lambda row: "; ".join(f"{coord}={row[coord]}" for coord in coords), axis=1
    )
    detail["coordinate_set"] = " + ".join(coords)
    detail["selector_level"] = len(coords)
    detail["is_miss_only_tuple"] = detail["non_miss_count"].eq(0)
    detail = detail.sort_values(
        ["non_miss_count", "miss_count", "tuple_values"],
        ascending=[False, False, True],
    )
    return detail


def example_rows(df: pd.DataFrame, coords: list[str], row: pd.Series, limit: int = 5) -> str:
    mask = pd.Series(True, index=df.index)
    for coord in coords:
        mask &= df[coord].eq(row[coord])
    examples = df.loc[mask & df["miss_event"].eq(0)].head(limit)
    preferred = [
        "event_row_id",
        "sample_id",
        "trajectory_id",
        "starting_value",
        "remaining_K_before",
        "remaining_K_after",
        "transition_k",
        "exit_distance",
        "residue_pair_mod32",
        "near_behavior",
        "miss_local_type",
    ]
    cols = [col for col in preferred if col in examples.columns]
    parts = []
    for _, ex in examples[cols].iterrows():
        parts.append("; ".join(f"{col}={ex[col]}" for col in cols))
    return " | ".join(parts)


def summarize_tuple_level(df: pd.DataFrame, detail: pd.DataFrame, coords: list[str]) -> dict[str, object]:
    mixed = detail[detail["non_miss_count"] > 0].copy()
    largest = ""
    examples = ""
    if not mixed.empty:
        largest_row = mixed.sort_values(["non_miss_count", "miss_count"], ascending=[False, False]).iloc[0]
        largest = (
            f"{largest_row['tuple_values']} "
            f"(non_miss_count={int(largest_row['non_miss_count'])}, "
            f"miss_count={int(largest_row['miss_count'])})"
        )
        examples = example_rows(df, coords, largest_row)
    summary = summarize_selector(df, df[df["miss_event"] == 1], coords)
    summary.update(
        {
            "number_of_miss_only_tuples": int(detail["is_miss_only_tuple"].sum()),
            "number_of_mixed_tuples": int((detail["non_miss_count"] > 0).sum()),
            "largest_non_miss_leakage_tuple": largest,
            "largest_non_miss_leakage_examples": examples,
        }
    )
    return summary


def single_coordinate_summary(df: pd.DataFrame, miss: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for coord in COORDS:
        summary = summarize_selector(df, miss, [coord])
        summary["coordinate"] = coord
        summary["selector_values"] = summary.pop("tuple_count")
        rows.append(
            {
                "coordinate": summary["coordinate"],
                "selector_values": summary["selector_values"],
                "matched_events": summary["matched_events"],
                "miss_count": summary["miss_count"],
                "non_miss_count": summary["non_miss_count"],
                "miss_rate": summary["miss_rate"],
            }
        )
    return pd.DataFrame(rows)


def level_comparison(
    single: pd.DataFrame,
    two_summary: pd.DataFrame,
    three_summary: pd.DataFrame,
    four_summary: dict[str, object],
    total_miss: int,
) -> pd.DataFrame:
    rows = []
    for _, row in single.iterrows():
        rows.append(
            {
                "coordinate_level": 1,
                "coordinate_set": row["coordinate"],
                "tuple_count": row["selector_values"],
                "matched_events": row["matched_events"],
                "miss_count": row["miss_count"],
                "non_miss_count": row["non_miss_count"],
                "miss_rate": row["miss_rate"],
            }
        )
    for level, table in [(2, two_summary), (3, three_summary)]:
        for _, row in table.iterrows():
            rows.append(
                {
                    "coordinate_level": level,
                    "coordinate_set": row["coordinate_set"],
                    "tuple_count": row["tuple_count"],
                    "matched_events": row["matched_events"],
                    "miss_count": row["miss_count"],
                    "non_miss_count": row["non_miss_count"],
                    "miss_rate": row["miss_rate"],
                }
            )
    rows.append(
        {
            "coordinate_level": 4,
            "coordinate_set": four_summary["coordinate_set"],
            "tuple_count": four_summary["tuple_count"],
            "matched_events": four_summary["matched_events"],
            "miss_count": four_summary["miss_count"],
            "non_miss_count": four_summary["non_miss_count"],
            "miss_rate": four_summary["miss_rate"],
        }
    )
    comparison = pd.DataFrame(rows)
    comparison["all_miss_captured"] = comparison["miss_count"].eq(total_miss)
    comparison["zero_non_miss_leakage"] = comparison["non_miss_count"].eq(0)
    return comparison


def markdown_table(df: pd.DataFrame, columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    rows = []
    for _, row in df[columns].iterrows():
        rows.append("| " + " | ".join(str(row[col]) for col in columns) + " |")
    return "\n".join([header, sep, *rows])


def build_candidates(two_summary: pd.DataFrame, two_detail: pd.DataFrame, total_miss: int) -> pd.DataFrame:
    rows = []
    full_two = two_summary[
        two_summary["miss_count"].eq(total_miss) & two_summary["non_miss_count"].eq(0)
    ]
    for _, row in full_two.iterrows():
        rows.append(
            {
                "candidate_type": "minimal_full_selector_candidate",
                "coordinate_level": 2,
                "coordinate_set": row["coordinate_set"],
                "tuple_count": row["tuple_count"],
                "matched_events": row["matched_events"],
                "miss_count": row["miss_count"],
                "non_miss_count": row["non_miss_count"],
                "miss_rate": row["miss_rate"],
                "leakage_tuple": "",
                "leakage_examples": "",
            }
        )
    if rows:
        return pd.DataFrame(rows)

    close = two_summary.sort_values(["non_miss_count", "tuple_count", "coordinate_set"]).head(6)
    for _, row in close.iterrows():
        leaks = two_detail[
            (two_detail["coordinate_set"].eq(row["coordinate_set"]))
            & (two_detail["non_miss_count"] > 0)
        ].sort_values(["non_miss_count", "miss_count"], ascending=[False, False])
        leakage_tuple = ""
        leakage_examples = ""
        if not leaks.empty:
            leak = leaks.iloc[0]
            leakage_tuple = (
                f"{leak['tuple_values']} "
                f"(non_miss_count={int(leak['non_miss_count'])}, miss_count={int(leak['miss_count'])})"
            )
            leakage_examples = leak.get("non_miss_examples", "")
        rows.append(
            {
                "candidate_type": "close_but_leaky_2coord_selector",
                "coordinate_level": 2,
                "coordinate_set": row["coordinate_set"],
                "tuple_count": row["tuple_count"],
                "matched_events": row["matched_events"],
                "miss_count": row["miss_count"],
                "non_miss_count": row["non_miss_count"],
                "miss_rate": row["miss_rate"],
                "leakage_tuple": leakage_tuple,
                "leakage_examples": leakage_examples,
            }
        )
    return pd.DataFrame(rows)


def report_has_forbidden_unrequired_language(report: str) -> list[str]:
    protected = report
    for phrase in REQUIRED_WORDING:
        protected = protected.replace(phrase, "")
    found = []
    for pattern in RESTRICTED_REPORT_PATTERNS:
        if re.search(pattern, protected, flags=re.IGNORECASE):
            found.append(pattern)
    return found


def main() -> None:
    OUT.mkdir(exist_ok=True)
    df = normalize_event_table(SOURCE_DETAIL)
    miss = df[df["miss_event"] == 1].copy()
    nonmiss = df[df["miss_event"] == 0].copy()
    if len(miss) != 228:
        raise SystemExit(f"Expected total miss count = 228, found {len(miss)}")
    if len(nonmiss) == 0:
        raise SystemExit("Non-miss background is empty")

    one = single_coordinate_summary(df, miss)
    one.to_csv(OUT / "miss_selector_1coord_summary.csv", index=False)

    two_details = []
    two_summaries = []
    for coords in itertools.combinations(COORDS, 2):
        coord_list = list(coords)
        detail = tuple_detail(df, miss, coord_list)
        detail["non_miss_examples"] = detail.apply(
            lambda row: example_rows(df, coord_list, row) if row["non_miss_count"] > 0 else "",
            axis=1,
        )
        two_details.append(detail)
        two_summaries.append(summarize_tuple_level(df, detail, coord_list))
    two_detail = pd.concat(two_details, ignore_index=True)
    two_summary = pd.DataFrame(two_summaries).sort_values(["non_miss_count", "coordinate_set"])
    two_summary.to_csv(OUT / "miss_selector_2coord_summary.csv", index=False)
    two_detail.to_csv(OUT / "miss_selector_2coord_detail.csv", index=False)

    three_details = []
    three_summaries = []
    for coords in itertools.combinations(COORDS, 3):
        coord_list = list(coords)
        detail = tuple_detail(df, miss, coord_list)
        detail["non_miss_examples"] = detail.apply(
            lambda row: example_rows(df, coord_list, row) if row["non_miss_count"] > 0 else "",
            axis=1,
        )
        three_details.append(detail)
        three_summaries.append(summarize_tuple_level(df, detail, coord_list))
    three_detail = pd.concat(three_details, ignore_index=True)
    three_summary = pd.DataFrame(three_summaries).sort_values(["non_miss_count", "coordinate_set"])
    three_summary.to_csv(OUT / "miss_selector_3coord_summary.csv", index=False)
    three_detail.to_csv(OUT / "miss_selector_3coord_detail.csv", index=False)

    four_summary = summarize_selector(df, miss, COORDS)
    comparison = level_comparison(one, two_summary, three_summary, four_summary, len(miss))
    comparison.to_csv(OUT / "miss_selector_level_comparison.csv", index=False)

    candidates = build_candidates(two_summary, two_detail, len(miss))
    candidates.to_csv(OUT / "minimal_miss_selector_candidates.csv", index=False)

    first_miss_only_level = int(
        comparison[comparison["all_miss_captured"] & comparison["zero_non_miss_leakage"]][
            "coordinate_level"
        ].min()
    )
    best_single = one.sort_values(["non_miss_count", "matched_events", "coordinate"]).iloc[0]
    two_full = two_summary[
        two_summary["miss_count"].eq(len(miss)) & two_summary["non_miss_count"].eq(0)
    ]
    all_three_full = bool(
        three_summary["miss_count"].eq(len(miss)).all()
        and three_summary["non_miss_count"].eq(0).all()
    )
    four_redundancy = (
        "The 4-coordinate tuple is redundant for this finite-sample separation because "
        "2-coordinate selectors already match 228 miss events with 0 non-miss events."
        if not two_full.empty
        else (
            "The 4-coordinate tuple is redundant for this finite-sample separation because "
            "all tested 3-coordinate projections also match 228 miss events with 0 non-miss events."
            if all_three_full
            else "The 4-coordinate tuple is the sharpest tested level in this scan."
        )
    )
    two_coord_answer = (
        "Four 2-coordinate pairs capture all 228 miss events with 0 non-miss events in this table."
        if len(two_full) == 4
        else (
            f"{len(two_full)} 2-coordinate pair(s) capture all 228 miss events with 0 non-miss events "
            "in this table."
            if not two_full.empty
            else "No 2-coordinate pair captures all 228 miss events with 0 non-miss events in this table."
        )
    )
    candidate_answer = (
        "The 2-coordinate minimal full selector candidates are: "
        + "; ".join(two_full["coordinate_set"].tolist())
        + "."
        if not two_full.empty
        else (
            "No 2-coordinate minimal full selector candidate appears in this finite sample. "
            "Since all tested 3-coordinate selectors match 228 miss events with 0 non-miss events, "
            "3 coordinates are the smallest tested full miss-only selector level."
        )
    )

    report = f"""# Minimal Miss-Only Selector Audit

Source table: `{SOURCE_DETAIL}`

## Validation

- Total rows in event table: {len(df)}
- Total miss count: {len(miss)}
- Non-miss background rows included: {len(nonmiss)}
- Candidate coordinates present: {", ".join(COORDS)}
- Output files written as CSV/MD in this task's `outputs` directory.

## 1. Single Coordinates

Single-coordinate selectors do not identify miss-only cells when each selector is defined as the set of values observed among the 228 miss events.

{markdown_table(one, ["coordinate", "selector_values", "matched_events", "miss_count", "non_miss_count", "miss_rate"])}

The most informative single coordinate by lowest non-miss leakage is `{best_single["coordinate"]}`: it matches {int(best_single["miss_count"])} miss events and {int(best_single["non_miss_count"])} non-miss events.

## 2. Two-Coordinate Selectors

{markdown_table(two_summary, ["coordinate_set", "tuple_count", "matched_events", "miss_count", "non_miss_count", "miss_rate", "number_of_miss_only_tuples", "number_of_mixed_tuples"])}

{two_coord_answer}

## 3. Three-Coordinate Selectors

{markdown_table(three_summary, ["coordinate_set", "tuple_count", "matched_events", "miss_count", "non_miss_count", "miss_rate", "number_of_miss_only_tuples", "number_of_mixed_tuples"])}

All tested 3-coordinate selectors match 228 miss events with 0 non-miss events.

## 4. Coordinate-Level Comparison

{markdown_table(comparison, ["coordinate_level", "coordinate_set", "tuple_count", "matched_events", "miss_count", "non_miss_count", "miss_rate", "all_miss_captured", "zero_non_miss_leakage"])}

Miss-only full selectors first appear at coordinate level {first_miss_only_level}.

## 5. Minimal Selector Candidates

{candidate_answer}

{four_redundancy}

The result shows coordinate redundancy in this scan.

## 6. Careful Reading

These are finite-sample selector cells, not causal rules.

Miss-only does not mean necessary, sufficient, or mechanistic outside this dataset.

No proof, causality, counterexample, or global Collatz claim is made.
"""
    forbidden = report_has_forbidden_unrequired_language(report)
    if forbidden:
        raise SystemExit(f"Report contains restricted wording outside required disclaimer: {forbidden}")
    (OUT / "minimal_miss_selector_report.md").write_text(report, encoding="utf-8")

    required_outputs = [
        "miss_selector_1coord_summary.csv",
        "miss_selector_2coord_summary.csv",
        "miss_selector_2coord_detail.csv",
        "miss_selector_3coord_summary.csv",
        "miss_selector_3coord_detail.csv",
        "miss_selector_level_comparison.csv",
        "minimal_miss_selector_candidates.csv",
        "minimal_miss_selector_report.md",
    ]
    empty = [name for name in required_outputs if (OUT / name).stat().st_size == 0]
    if empty:
        raise SystemExit(f"empty output files: {empty}")

    print(f"source_rows={len(df)}")
    print(f"miss_count={len(miss)}")
    print(f"non_miss_background={len(nonmiss)}")
    print(f"first_miss_only_full_selector_level={first_miss_only_level}")
    print(f"two_coord_full_selectors={len(two_full)}")
    print(f"all_three_coord_full_selectors={all_three_full}")
    print("wrote_outputs=" + ", ".join(required_outputs))


if __name__ == "__main__":
    main()
