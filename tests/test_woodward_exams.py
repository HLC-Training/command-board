"""
Woodward → Greg routing and exam-pipeline total rules (2026-10-29).

    python tests/test_woodward_exams.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import build  # noqa: E402
from build import route_customer, route_pll, route_lookahead_internal  # noqa: E402

W = "26-567 - OEC - Control System - Woodward (Aero) Operation, Maintenance & Troubleshooting"


def test_customer_woodward_beats_control_tech():
    assert route_customer("Control System", W) == ("greg", False)


def test_customer_plain_controls_still_mohammed():
    assert route_customer("Control System", "26-722 - OEC - Mark VIe Familiarization")[0] == "mohammed"


def test_internal_woodward_greg():
    assert route_pll("Woodward Governor Controls 26-1") == ("greg", False)


def test_lookahead_woodward_greg():
    assert route_lookahead_internal("Woodward Controls 26-1", "", "Controls") == ("greg", False)


def test_exam_buckets():
    b = build.EXAM_STATUS_BUCKETS
    assert b["on hold"] == "underReview"
    assert b["rework needed"] == "underReview"
    assert "n/a" not in b and "n/a" in build.EXAM_STATUS_EXCLUDED


if __name__ == "__main__":
    fails = 0
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            try:
                f(); print("PASS", n)
            except AssertionError as e:
                fails += 1; print("FAIL", n, e)
    sys.exit(1 if fails else 0)
