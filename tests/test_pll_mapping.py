"""
Per-rule fixture tests for data/pll-mapping.json and the routers that read it
(2026-11-02 brief, action item 55b71b85).

One test per rule element, named for the rule, so a change to one rule fails
one test. test_every_rule_has_a_fixture fails when a rule is added to the file
without a fixture here. Run from the repo root:

    python tests/test_pll_mapping.py

No network access needed — everything runs against in-memory fixtures.
"""

import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import build  # noqa: E402
from build import (  # noqa: E402
    load_pll_mapping,
    process_enrollment,
    route_customer,
    route_lookahead_internal,
    route_pll,
)

MAPPING = json.loads(
    (Path(__file__).resolve().parent.parent / "data" / "pll-mapping.json")
    .read_text(encoding="utf-8"))
PLL_IDS = {p["id"] for p in MAPPING["plls"]}

# Fixture counts the file must match (see test_every_rule_has_a_fixture).
N_INTERNAL_RULES = 11
N_CUSTOMER_RULES = 5
N_NAMED_OVERRIDES = 1
N_LOOKAHEAD_RULES = 6
N_LOOKAHEAD_TECH_RULES = 7


def weekly(name):
    return route_pll(name)[0]


def lookahead(name, program="", tech=""):
    return route_lookahead_internal(name, program, tech)[0]


class InternalRules(unittest.TestCase):
    """internal_rules, in file order (build.py route_pll)."""

    def test_internal_00_cte_keywords_route_linda(self):
        self.assertEqual(weekly("Workforce Development Intro"), "linda")

    def test_internal_00_cte_before_craft_routes_linda(self):
        self.assertEqual(weekly("Craft Entry Level CTE Program"), "linda")

    def test_internal_00_cte_rule_precedes_craft_rule_in_file(self):
        rules = MAPPING["internal_rules"]
        cte = next(i for i, r in enumerate(rules) if r.get("source") == "build.py:595")
        craft = next(i for i, r in enumerate(rules) if r.get("source") == "build.py:600")
        self.assertLess(cte, craft)

    def test_internal_01_craft_routes_harry(self):
        self.assertEqual(weekly("Craft Safety Basics"), "harry")

    def test_internal_02_named_override_woodward_beats_controls(self):
        self.assertEqual(weekly("Woodward Governor Controls"), "greg")

    def test_internal_03_mkvi_beats_gt_keyword(self):
        self.assertEqual(weekly("Entry Level GT MkVIe"), "mohammed")

    def test_internal_04_harry_group_routes_harry(self):
        self.assertEqual(weekly("Stator Rewind Workshop"), "harry")

    def test_internal_05_sherif_group_routes_sherif(self):
        self.assertEqual(weekly("7FA Combustion Inspection"), "sherif")

    def test_internal_06_pablo_group_routes_pablo(self):
        self.assertEqual(weekly("HRSG Operations"), "pablo")

    def test_internal_07_mohammed_group_routes_mohammed(self):
        self.assertEqual(weekly("Fieldbus Networks"), "mohammed")

    def test_internal_08_ben_group_routes_ben(self):
        self.assertEqual(weekly("Retaining Ring Inspection"), "ben")

    def test_internal_09_greg_group_routes_greg(self):
        self.assertEqual(weekly("LM6000 Overview"), "greg")

    def test_internal_10_linda_group_routes_linda(self):
        self.assertEqual(weekly("Achieving Customer Excellence"), "linda")


class CustomerRules(unittest.TestCase):
    """customer_technology_rules and named_overrides (route_customer)."""

    def test_customer_00_greg_aeroderivative(self):
        self.assertEqual(route_customer("Aeroderivative", "Course X")[0], "greg")

    def test_customer_01_ben_excitation(self):
        self.assertEqual(route_customer("Excitation", "Course X")[0], "ben")

    def test_customer_02_mohammed_controls(self):
        self.assertEqual(route_customer("Controls", "Course X")[0], "mohammed")

    def test_customer_03_pablo_steam_turbine(self):
        self.assertEqual(route_customer("Steam Turbine", "Course X")[0], "pablo")

    def test_customer_04_sherif_gas_turbine(self):
        self.assertEqual(route_customer("Gas Turbine", "Course X")[0], "sherif")

    def test_customer_class_name_fallback_when_technology_blank(self):
        self.assertEqual(route_customer("", "Boiler Basics")[0], "pablo")

    def test_customer_named_override_woodward_beats_technology(self):
        self.assertEqual(route_customer("Control System", "Woodward Governor")[0], "greg")


class NamedOverrides(unittest.TestCase):
    def test_override_00_woodward_routes_greg_weekly_and_lookahead(self):
        self.assertEqual(weekly("Woodward Governor"), "greg")
        self.assertEqual(lookahead("Woodward Governor", "", "Controls"), "greg")


class VendorExcludedUnmatched(unittest.TestCase):
    HEADERS = ["Course Name", "Start Date", "Finish Date", "Location",
               "Student Status", "Student Country"]
    WEEK = (date(2026, 11, 2), date(2026, 11, 6))

    def enr(self, *names):
        rows = [(n, date(2026, 11, 2), date(2026, 11, 6),
                 "Houston Learning Center", "Registered", "United States")
                for n in names]
        return process_enrollment(self.HEADERS, rows, *self.WEEK)

    def test_vendor_led_has_no_pll_and_is_still_counted(self):
        self.assertEqual(route_pll("Train the Trainer"), ("__vendor__", False))
        r = self.enr("Train the Trainer")
        self.assertEqual(r["total_internal"], 1)
        self.assertEqual(r["internal_courses"], 1)
        self.assertEqual(sum(len(v) for v in r["pll_classes"].values()), 0)
        self.assertEqual(r["flags"], [])

    def test_excluded_programs_leadership_in_name(self):
        self.assertEqual(lookahead("Craft Leadership Program"), "__excluded__")

    def test_excluded_programs_project_management_in_program_column(self):
        self.assertEqual(lookahead("Course X", "Project Management", ""),
                         "__excluded__")

    def test_excluded_programs_leadership_in_technology_column(self):
        self.assertEqual(lookahead("Course X", "", "Leadership"), "__excluded__")

    def test_unmatched_fires_the_flag(self):
        self.assertEqual(route_pll("Basket Weaving 101"), (None, True))
        r = self.enr("Basket Weaving 101")
        self.assertEqual(len(r["flags"]), 1)
        self.assertIn("UNMATCHED INTERNAL", r["flags"][0])

    def test_unmatched_customer_fires_the_flag(self):
        self.assertEqual(route_customer("Underwater Welding", "Basket Weaving"),
                         (None, True))


class LookaheadRules(unittest.TestCase):
    """lookahead_rules in file order, then lookahead_technology_rules."""

    def test_lookahead_01_cte_in_name_routes_linda(self):
        self.assertEqual(lookahead("Craft Entry Level CTE Program"), "linda")

    def test_lookahead_02_cte_in_program_column_routes_linda(self):
        self.assertEqual(lookahead("Course X", "CTE", ""), "linda")

    def test_lookahead_03_craft_program_routes_harry(self):
        self.assertEqual(lookahead("Course X", "Craft", ""), "harry")

    def test_lookahead_04_named_override_beats_technology(self):
        self.assertEqual(lookahead("Woodward Governor", "", "Controls"), "greg")

    def test_lookahead_05_unmatched_flags(self):
        self.assertEqual(route_lookahead_internal("Basket Weaving", "", ""),
                         (None, True))

    def test_lookahead_05_vendor_led_fallback_is_excluded(self):
        self.assertEqual(lookahead("Train the Trainer"), "__excluded__")

    def test_lookahead_tech_00_gas_turbine_sherif(self):
        self.assertEqual(lookahead("Course X", "", "Gas Turbine"), "sherif")

    def test_lookahead_tech_01_steam_turbine_pablo(self):
        self.assertEqual(lookahead("Course X", "", "Steam Turbine"), "pablo")

    def test_lookahead_tech_02_controls_mohammed(self):
        self.assertEqual(lookahead("Course X", "", "Controls"), "mohammed")

    def test_lookahead_tech_03_excitation_ben(self):
        self.assertEqual(lookahead("Course X", "", "Excitation"), "ben")

    def test_lookahead_tech_04_aeroderivative_greg(self):
        self.assertEqual(lookahead("Course X", "", "Aeroderivative"), "greg")

    def test_lookahead_tech_05_workforce_technology_linda(self):
        self.assertEqual(lookahead("Course X", "", "Workforce"), "linda")

    def test_lookahead_tech_06_stator_harry(self):
        self.assertEqual(lookahead("Course X", "", "Stator"), "harry")


class Schema(unittest.TestCase):
    def test_every_rule_has_a_fixture(self):
        self.assertEqual(len(MAPPING["internal_rules"]), N_INTERNAL_RULES)
        self.assertEqual(len(MAPPING["customer_technology_rules"]), N_CUSTOMER_RULES)
        self.assertEqual(len(MAPPING["named_overrides"]), N_NAMED_OVERRIDES)
        self.assertEqual(len(MAPPING["lookahead_rules"]), N_LOOKAHEAD_RULES)
        self.assertEqual(len(MAPPING["lookahead_technology_rules"]["rules"]),
                         N_LOOKAHEAD_TECH_RULES)

    def test_every_referenced_pll_exists(self):
        refs = [r["pll"] for r in MAPPING["internal_rules"] if "ref" not in r]
        refs += [r["pll"] for r in MAPPING["customer_technology_rules"]]
        refs += [r["pll"] for r in MAPPING["named_overrides"]]
        refs += [r["pll"] for r in MAPPING["lookahead_technology_rules"]["rules"]]
        refs += [r["pll"] for r in MAPPING["lookahead_rules"] if "ref" not in r]
        refs += [v["pll"] for k, v in MAPPING["udc_technology"].items()
                 if not k.startswith("_") and v["pll"] is not None]
        self.assertTrue(refs)
        self.assertEqual({r for r in refs if r not in PLL_IDS}, set())

    def test_udc_technology_entries_have_pll_line_show_in(self):
        entries = {k: v for k, v in MAPPING["udc_technology"].items()
                   if not k.startswith("_")}
        self.assertEqual(len(entries), 19)
        for name, e in entries.items():
            for key in ("pll", "line", "show_in"):
                self.assertIn(key, e, f"{name} missing {key}")
            self.assertIsInstance(e["show_in"], list)

    def test_non_technical_is_nps_only_with_no_pll(self):
        e = MAPPING["udc_technology"]["Non-Technical"]
        self.assertEqual(e["show_in"], ["nps"])
        self.assertIsNone(e["pll"])

    def test_les_routes_harry_and_live_outage_routes_sherif(self):
        self.assertEqual(MAPPING["udc_technology"]["LES"]["pll"], "harry")
        self.assertEqual(MAPPING["udc_technology"]["Live Outage"]["pll"], "sherif")

    def test_board_pll_names_and_order_come_from_file(self):
        self.assertEqual(build.PLL_ORDER,
                         ["sherif", "pablo", "ben", "mohammed", "harry", "greg", "linda"])
        self.assertEqual(build.PLL_NAMES["harry"], "Harry Hanson")


class FailFast(unittest.TestCase):
    def test_missing_file_exits_naming_the_file(self):
        with self.assertRaises(SystemExit) as cm:
            load_pll_mapping(Path(tempfile.gettempdir()) / "no-such-dir" / "pll-mapping.json")
        self.assertEqual(cm.exception.code, 1)

    def test_unknown_pll_id_exits(self):
        bad = json.loads(json.dumps(MAPPING))
        bad["customer_technology_rules"][0]["pll"] = "nobody"
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "pll-mapping.json"
            p.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(SystemExit) as cm:
                load_pll_mapping(p)
        self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
