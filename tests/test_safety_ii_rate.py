"""
Safety RAG must be red while the Bowler I&I rate is above plan
(Jim, 2026-10-09 — replaces the weekly hand patch to safetyRag).

    python tests/test_safety_ii_rate.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build import bowler_month_rate, calculate_safety_rag  # noqa: E402

GREEN = {"value": 100, "rag": "green"}


def kpis(ii_value, ii_plan=0.0, month="Aug"):
    rag = "red" if ii_value is not None and ii_value > ii_plan else "green"
    return {"liveStop": GREEN, "readAcross": GREEN,
            "iiRate": {"value": ii_value, "plan": ii_plan, "month": month, "rag": rag}}


def test_ii_above_zero_forces_red_even_with_zero_incidents():
    rag, reason = calculate_safety_rag(0, "amber", kpis(0.95))
    assert rag == "red"
    assert "I&I rate 0.95 vs 0 plan (Aug)" in reason


def test_ii_zero_stays_green():
    assert calculate_safety_rag(0, "amber", kpis(0.0))[0] == "green"


def test_ii_missing_does_not_force_red():
    assert calculate_safety_rag(0, "amber", kpis(None))[0] == "green"


def test_rate_reader_keeps_raw_value_and_walks_back():
    month_cols = {7: 1, 8: 2, 9: 3}
    row = ["I&I Rate", 1.089, 0.95, None]
    assert bowler_month_rate(month_cols, row, 9) == (0.95, 8)   # not 95


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"{len(tests)} passed")
