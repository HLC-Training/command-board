"""
Per-KPI fixture tests for the Bowler YTD fix (2026-09-08 brief).

process_bowler() previously computed YTD as the mean of populated monthly
Act values. That drifts from the sheet's own owner-maintained "YTD Actual"
column (py-row, index 6) and shipped wrong three builds running. This file
proves YTD now reads that column, and that PTSI's N/A-month exception
(show YTD in both slots, never walk back) is wired correctly while
Timecard/FLIQ keep the standard walk-back.

Run from the repo root:

    python tests/test_bowler_ytd.py

No network access needed. Tests 1, 5, and 6 read the committed
"data/2026 Bowler Chart - OFS Training.xlsx" directly (target_month is
hardcoded to August=8 rather than derived from date.today(), so the
assertions stay deterministic regardless of when this runs). The rest use
small in-memory rowset fixtures.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build import (  # noqa: E402
    find_file,
    load_bowler_sheet,
    process_bowler,
)

BOWLER_XLSX = find_file(["bowler chart"])
TARGET_MONTH = 8  # August — the target month for the 2026-09-08 committed sheet

# ── synthetic fixtures for isolated per-rule tests ─────────────────────────
# Simple one-column-per-month layout (real sheet skips 1Q/2Q/3Q/4Q columns,
# but process_bowler only consumes month_cols as a mapping — that layout
# quirk belongs to load_bowler_sheet, not this function).
MONTH_COLS = {m: 7 + m for m in range(1, 13)}  # JAN at col 8 ... DEC at col 19


def py_row(ytd_raw):
    """py-row fixture: only index 6 (YTD Actual) matters to process_bowler."""
    return tuple([None] * 6 + [ytd_raw])


def act_row(**by_month_abbr_lower):
    """
    act-row fixture: build a row long enough to hold every month column,
    filling from month-number kwargs, e.g. act_row(jun=0.81, aug=None).
    """
    abbr_to_num = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                   "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
    row = [None] * 20
    for k, v in by_month_abbr_lower.items():
        row[MONTH_COLS[abbr_to_num[k]]] = v
    return tuple(row)


def kpi_rows_fixture(ptsi_ytd=0.83, ptsi_act=None,
                      timecard_ytd=0.72, timecard_act=None,
                      instutil_ytd=0.29, instutil_act=None):
    return {
        "post-training skill improvement": {
            "py": py_row(ptsi_ytd),
            "act": ptsi_act if ptsi_act is not None else act_row(),
        },
        "timecard otd": {
            "py": py_row(timecard_ytd),
            "act": timecard_act if timecard_act is not None else act_row(),
        },
        "fully loaded and qualified instructors": {
            "py": py_row(instutil_ytd),
            "act": instutil_act if instutil_act is not None else act_row(),
        },
    }


# ── 1. YTD from source, not mean (real committed sheet) ────────────────────

def test_1_ytd_from_source_matches_committed_sheet():
    """YTD reads index 6 of the py-row — asserted against the real xlsx."""
    assert BOWLER_XLSX is not None, "data/2026 Bowler Chart - OFS Training.xlsx not found"
    month_cols, kpi_rows = load_bowler_sheet(BOWLER_XLSX)
    kpis, _, _ = process_bowler(month_cols, kpi_rows, TARGET_MONTH)
    assert kpis["ptsi"]["ytdValue"] == 83, kpis["ptsi"]["ytdValue"]
    assert kpis["timecard"]["ytdValue"] == 72, kpis["timecard"]["ytdValue"]
    assert kpis["instUtil"]["ytdValue"] == 29, kpis["instUtil"]["ytdValue"]


# ── 2. behavioral proof: YTD tracks the source column, not the months ──────

def test_2_ytd_moves_with_source_column_not_with_months():
    """
    Change ONLY the Timecard YTD Actual cell (py-row index 6) to 0.50 and
    leave every monthly Act value untouched (populated, non-trivial values —
    no mean of them lands on 50). If ytdValue still moves to 50, the read
    path is the source column, not a re-derived mean.
    """
    rows = kpi_rows_fixture(
        timecard_ytd=0.50,
        timecard_act=act_row(jan=0.83, feb=0.60, apr=0.72, may=0.85,
                              jun=0.89, jul=0.91),  # mean of these != 50
    )
    kpis, _, _ = process_bowler(MONTH_COLS, rows, TARGET_MONTH)
    assert kpis["timecard"]["ytdValue"] == 50, kpis["timecard"]["ytdValue"]


# ── 3. PTSI N/A → YTD in both slots, never a prior-month walk-back ─────────

def test_3_ptsi_na_target_month_shows_ytd_not_prior_month():
    """
    PTSI's target-month (Aug) Act is N/A; June is populated at 0.81 (81%).
    The disallowed old behavior was to walk back and show "Jun 81". The
    fixed behavior must show monthLabel "YTD" with monthValue == ytdValue.
    """
    rows = kpi_rows_fixture(
        ptsi_ytd=0.83,
        ptsi_act=act_row(mar=0.83, jun=0.81, aug=None),
    )
    kpis, _, _ = process_bowler(MONTH_COLS, rows, TARGET_MONTH)
    ptsi = kpis["ptsi"]
    assert ptsi["monthLabel"] == "YTD", ptsi["monthLabel"]
    assert ptsi["monthValue"] == ptsi["ytdValue"], (ptsi["monthValue"], ptsi["ytdValue"])
    assert ptsi["monthValue"] != 81, ptsi["monthValue"]  # 81 = disallowed Jun walk-back


# ── 4. PTSI populated target month still shows the month, not YTD ──────────

def test_4_ptsi_populated_target_month_shows_month_not_ytd():
    """Task 2 must not break the normal path when PTSI's target month has data."""
    rows = kpi_rows_fixture(
        ptsi_ytd=0.83,
        ptsi_act=act_row(jun=0.81, aug=0.75),
    )
    kpis, _, _ = process_bowler(MONTH_COLS, rows, TARGET_MONTH)
    ptsi = kpis["ptsi"]
    assert ptsi["monthLabel"] == "Aug", ptsi["monthLabel"]
    assert ptsi["monthValue"] == 75, ptsi["monthValue"]


# ── 5. Timecard / FLIQ walk-back stays untouched (real committed sheet) ────

def test_5_timecard_and_fliq_walkback_unchanged():
    """
    Both KPIs are N/A for Aug (the target month) on the committed sheet and
    must walk back to Jul, unaffected by the PTSI-only branch.
    """
    month_cols, kpi_rows = load_bowler_sheet(BOWLER_XLSX)
    kpis, _, _ = process_bowler(month_cols, kpi_rows, TARGET_MONTH)
    assert kpis["timecard"]["monthLabel"] == "Jul", kpis["timecard"]["monthLabel"]
    assert kpis["timecard"]["monthValue"] == 89, kpis["timecard"]["monthValue"]
    assert kpis["instUtil"]["monthLabel"] == "Jul", kpis["instUtil"]["monthLabel"]
    assert kpis["instUtil"]["monthValue"] == 21, kpis["instUtil"]["monthValue"]


# ── 6. Overall RAG still cites a month, not "YTD" ───────────────────────────

def test_6_overall_rag_reason_cites_a_month_not_ytd():
    month_cols, kpi_rows = load_bowler_sheet(BOWLER_XLSX)
    kpis, overall, reason = process_bowler(month_cols, kpi_rows, TARGET_MONTH)
    assert overall == "amber", overall
    assert "YTD" not in reason, reason
    assert "Jul" in reason, reason


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {name}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
