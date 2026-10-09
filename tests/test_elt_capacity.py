"""
ELT ideal-capacity and Mark VIe routing tests (Jim, 2026-10-09).

Ideal class sizes from the 2026-10-08 staff meeting: GT 18, ST 18,
Controls 16, Excitation 12, Generator 12, Craft entry level 20. Aero has
no ELT. ALTs, CTE and Generator Repairs Accelerated keep the Enrollment
Database capacity. Run from the repo root:

    python tests/test_elt_capacity.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build import capacity_state, ideal_capacity, route_pll  # noqa: E402


def ideal_for(name):
    pll, flagged = route_pll(name)
    assert not flagged, f"{name} unexpectedly unmatched"
    return pll, ideal_capacity(name, pll)


def test_gt_elt_is_18():
    assert ideal_for("Entry Level Gas Turbine 26-2") == ("sherif", 18)
    assert ideal_for("Gas Turbine - Entry Level - Accelerated 26-1") == ("sherif", 18)


def test_st_elt_is_18():
    assert ideal_for("Entry Level Steam Turbine 26-2") == ("pablo", 18)


def test_mkvie_routes_to_mohammed_at_16():
    assert ideal_for("Entry Level GT MkVIe 26-2") == ("mohammed", 16)


def test_excitation_and_gen_are_12():
    assert ideal_for("Entry Level Electrical Excitation 26-2") == ("ben", 12)
    assert ideal_for("Generator Specialist Training 26-2") == ("ben", 12)


def test_craft_entry_level_is_20():
    assert ideal_for("Craft Entry Level GT Accelerated 26-8") == ("harry", 20)


def test_generator_repairs_accelerated_keeps_db_capacity():
    assert ideal_for("Entry Level Generator Repairs Accelerated 26-2") == ("harry", None)


def test_cte_keeps_db_capacity():
    assert ideal_for("Craft Entry Level CTE Program") == ("linda", None)
    assert ideal_for("CTE - Mechanic Assistant Fundamentals 26-1") == ("linda", None)


def test_alt_keeps_db_capacity():
    assert ideal_for("Advanced Gas Turbine Maintenance")[1] is None


def test_over_ideal_flags_over_even_when_db_says_full():
    # 24 enrolled against a 24-seat room used to read FULL; against GT's
    # ideal of 18 it must read OVER.
    _, ideal = ideal_for("Entry Level Gas Turbine 26-2")
    assert capacity_state(24, 24) == "at"
    assert capacity_state(24, ideal) == "over"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"{len(tests)} passed")
