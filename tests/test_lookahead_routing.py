"""
Per-rule fixture tests for the 30-day look-ahead routing (2026-08-21 brief).

One assertion per routing rule — an aggregate "routing works" test would pass
a partial implementation. Run from the repo root:

    python tests/test_lookahead_routing.py

No network access needed — everything runs against in-memory fixtures.
"""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build import (  # noqa: E402
    CUSTOMER_TECH_RULES,
    compute_lookahead_customer,
    compute_lookahead_internal,
    route_customer,
    route_lookahead_internal,
)

WINDOW_START = date(2026, 8, 24)
WINDOW_END   = date(2026, 9, 22)   # start + 29 days, inclusive

ENR_HEADERS = ["Course Name", "Program", "Technology", "Start Date",
               "Finish Date", "Location", "Course Status",
               "Student Status"]


def enr_row(course, start, status="Registered", program="", tech=""):
    return (course, program, tech, start, "", "Houston Learning Center",
            "", status)


CUST_HEADERS = ["Course Title", "Technology", "Contractual # of Students",
                "Unique Identifier", "Class Name", "Delivery Start Date",
                "Class Status"]


def cust_row(title, tech, students, uid, name, start, status="Confirmed"):
    return (title, tech, students, uid, name, start, status)


def test_a_craft_gas_turbine_is_harry_not_sherif():
    """(a) Program-first: Program=Craft + Technology=Gas Turbine → Harry."""
    pll, flagged = route_lookahead_internal(
        "HA Combustion Training 26-5", "Craft", "Gas Turbine")
    assert (pll, flagged) == ("harry", False), (pll, flagged)
    # Repairs is program-first too — even when Technology says Steam Turbine.
    pll, flagged = route_lookahead_internal(
        "Advanced Buckets 26-1", "Repairs", "Steam Turbine")
    assert (pll, flagged) == ("harry", False), (pll, flagged)


def test_b_leadership_is_excluded_not_routed():
    """(b) A Leadership class is EXCLUDED — no PLL, no flag, even Craft."""
    pll, flagged = route_lookahead_internal(
        "Craft Leadership Program 26-4", "Craft", "Non-Technical")
    assert (pll, flagged) == ("__excluded__", False), (pll, flagged)
    # And end-to-end: it contributes to no card and raises no flag.
    per_pll, flags, _ = compute_lookahead_internal(
        ENR_HEADERS,
        [enr_row("Craft Leadership Program 26-4", "2026-09-01",
                 program="Craft", tech="Non-Technical")],
        WINDOW_START, WINDOW_END)
    assert all(v == {"classes": 0, "students": 0} for v in per_pll.values()), per_pll
    assert flags == [], flags


def test_b2_cte_precedes_craft():
    """CTE wins over Craft: 'Craft Entry Level CTE Program' is Linda's."""
    pll, flagged = route_lookahead_internal(
        "Craft Entry Level CTE Program 26-1", "Craft",
        "CTE / Workforce Readiness")
    assert (pll, flagged) == ("linda", False), (pll, flagged)


def test_c_oe_generator_lands_on_ben():
    """(c) An OE class with Technology=Generator routes to Ben Smith."""
    pll, flagged = route_customer("Generator")
    assert (pll, flagged) == ("ben", False), (pll, flagged)
    per_pll, flags = compute_lookahead_customer(
        [("OE", CUST_HEADERS,
          [cust_row("EX2100e Regulator", "Generator", 12, "GEN-1",
                    "Generator Maintenance 26-9", "2026-09-10")])],
        WINDOW_START, WINDOW_END)
    assert per_pll["ben"] == {"classes": 1, "students": 12}, per_pll["ben"]
    assert flags == [], flags


def test_d_harry_and_linda_take_zero_customer_rows():
    """(d) No customer technology can ever route to Harry or Linda."""
    rule_plls = {pll for pll, _ in CUSTOMER_TECH_RULES}
    assert "harry" not in rule_plls and "linda" not in rule_plls, rule_plls
    for tech in ("Gas Turbine", "Steam Turbine", "Controls", "Generator",
                 "Aeroderivative", "Balance of Plant", "General", "HRSG",
                 "Combined Cycle", "Simulator", "Craft", "CTE"):
        pll, _ = route_customer(tech)
        assert pll not in ("harry", "linda"), (tech, pll)


def test_e_unmatched_internal_flags_instead_of_vanishing():
    """(e) An internal class matching no rule raises a flag — never silent."""
    pll, flagged = route_lookahead_internal(
        "Underwater Basket Weaving 26-1", "Mystery Program", "Unknown Tech")
    assert (pll, flagged) == (None, True), (pll, flagged)
    per_pll, flags, _ = compute_lookahead_internal(
        ENR_HEADERS,
        [enr_row("Underwater Basket Weaving 26-1", "2026-09-01",
                 program="Mystery Program", tech="Unknown Tech")],
        WINDOW_START, WINDOW_END)
    assert all(v == {"classes": 0, "students": 0} for v in per_pll.values()), per_pll
    assert len(flags) == 1 and "UNMATCHED INTERNAL" in flags[0], flags


def test_e2_blank_program_falls_back_to_name_router():
    """Blank Program/Technology falls back to the weekly name router."""
    pll, flagged = route_lookahead_internal(
        "Gas Turbine Fundamentals 26-8", "", "")
    assert (pll, flagged) == ("sherif", False), (pll, flagged)


def test_f_oe_dedupe_across_files_by_identity():
    """A class listed in both demand files counts once (identity = UID + name)."""
    row = cust_row("GT Ops", "Gas Turbine", 10, "UID-7",
                   "GT Operations 26-3", "2026-09-01")
    per_pll, flags = compute_lookahead_customer(
        [("OE", CUST_HEADERS, [row]), ("SS", CUST_HEADERS, [row])],
        WINDOW_START, WINDOW_END)
    assert per_pll["sherif"] == {"classes": 1, "students": 10}, per_pll["sherif"]
    assert flags == [], flags


def test_f2_cancelled_and_zero_student_customer_classes_excluded():
    """Cancelled OE classes and classes with no students never count."""
    per_pll, flags = compute_lookahead_customer(
        [("SS", CUST_HEADERS, [
            cust_row("GT Maint", "Gas Turbine", 12, "C-1",
                     "GT Maintenance 26-4", "2026-09-01", status="Cancelled"),
            cust_row("GT Maint", "Gas Turbine", 0, "C-2",
                     "GT Maintenance 26-5", "2026-09-01", status="Tentative"),
        ])],
        WINDOW_START, WINDOW_END)
    assert per_pll["sherif"] == {"classes": 0, "students": 0}, per_pll["sherif"]
    assert flags == [], flags


def test_g_window_bounds_inclusive_and_status_filter():
    """Start Date on both window edges counts; excluded statuses do not."""
    rows = [
        enr_row("Gas Turbine Fundamentals 26-8", WINDOW_START.isoformat()),
        enr_row("Gas Turbine Fundamentals 26-8", WINDOW_END.isoformat()),
        enr_row("Gas Turbine Fundamentals 26-8", "2026-09-23"),          # +30d: out
        enr_row("Gas Turbine Fundamentals 26-8", "2026-09-01", "Withdrawal"),
        enr_row("Gas Turbine Fundamentals 26-8", "2026-09-01", "Waitlisted"),
        enr_row("Gas Turbine Fundamentals 26-8", "2026-09-01", "No Show"),
        enr_row("Gas Turbine Fundamentals 26-8", "2026-09-01", "Cancelled"),
        enr_row("Gas Turbine Fundamentals 26-8", "2026-09-01", "Late Withdrawal"),
        enr_row("Gas Turbine Fundamentals 26-8", "2026-09-01", ""),      # no student
        enr_row("Gas Turbine Fundamentals 26-8", "2026-09-01", "In Progress"),
    ]
    per_pll, flags, stats = compute_lookahead_internal(
        ENR_HEADERS, rows, WINDOW_START, WINDOW_END)
    # 1 class, 3 active students (2 edge Registered + 1 In Progress)
    assert per_pll["sherif"] == {"classes": 1, "students": 3}, per_pll["sherif"]
    assert stats["rows_in_window"] == 9, stats   # all but the +30d row
    assert flags == [], flags


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
