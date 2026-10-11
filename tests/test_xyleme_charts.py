"""
Xyleme half-donut chart tests (Jim, 2026-10-09).

The three charts mirror the D&D Projects Dashboard widgets. Totals checked
against the live dashboard on 2026-10-09: pipeline 352, exams 326,
modernization 91. Run from the repo root:

    python tests/test_xyleme_charts.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build import XYLEME_CHARTS, xyleme_chart_slices  # noqa: E402

CHART = {c["key"]: c for c in XYLEME_CHARTS}


def test_summary_report_reads_one_row_by_column():
    titles = ["Sheet Name", "Published & Approved", "Published without SME Approval",
              "Published Requiring Updates", "In Review by SME(s)", "WIP",
              "In Backlog", "Material not Received"]
    rows = [("Content Transfer Tracker", 49, 7, 3, 7, 8, 41, 237)]
    slices, extras = xyleme_chart_slices(CHART["pipeline"], titles, rows)
    assert [s["count"] for s in slices] == [49, 7, 3, 7, 8, 41, 237]
    assert sum(s["count"] for s in slices) == 352
    assert extras == {}


def test_status_report_skips_blank_statuses():
    # The modernization report has 411 rows; only the 91 with a Status count.
    titles = ["Primary", "Status"]
    rows = [("parent", None), ("m1", "Completed"), ("m2", "Not Received"),
            ("m3", ""), ("m4", "Completed")]
    slices, _ = xyleme_chart_slices(CHART["modernization"], titles, rows)
    got = {s["label"]: s["count"] for s in slices}
    assert got["Completed"] == 2 and got["Not Received"] == 1
    assert sum(got.values()) == 3


def test_slice_order_matches_dashboard():
    titles = ["Primary", "Status"]
    slices, _ = xyleme_chart_slices(CHART["exams"], titles, [])
    assert [s["label"] for s in slices] == [lb for lb, _ in CHART["exams"]["slices"]]


def test_rework_needed_is_counted():
    # The old exams pipeline had no bucket for Rework Needed (24 exams lost).
    titles = ["Primary", "Status"]
    rows = [("e1", "Rework Needed"), ("e2", "Rework Needed")]
    slices, _ = xyleme_chart_slices(CHART["exams"], titles, rows)
    assert {s["label"]: s["count"] for s in slices}["Rework Needed"] == 2


def test_unknown_status_is_shown_and_reported():
    titles = ["Primary", "Status"]
    rows = [("e1", "On Hold")]
    slices, extras = xyleme_chart_slices(CHART["exams"], titles, rows)
    assert extras == {"On Hold": 1}
    assert slices[-1]["label"] == "On Hold" and slices[-1]["count"] == 1


def test_no_two_slices_share_a_color_within_a_chart():
    for c in XYLEME_CHARTS:
        colors = [col.lower() for _, col in c["slices"]]
        assert len(colors) == len(set(colors)), c["title"]


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"{len(tests)} passed")
