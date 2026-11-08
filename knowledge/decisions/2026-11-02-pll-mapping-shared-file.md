# PLL routing rules live in data/pll-mapping.json, shared with NPS Mk II

Date: 2026-11-02. Status: active. Action item 55b71b85 (command-board), spawned from 98a22c9b (nps-mk2). Jim, chat with Sam.

## Decision

Every rule that assigns a class to a Product Line Leader moves out of build.py into `data/pll-mapping.json`. build.py loads the file at startup and fails fast if it is missing or references an unknown PLL. The file is the single source of truth for routing on the Command Board and for NPS Mk II, which fetches it from main at run time and snapshots it beside each month's data.

The file carries three kinds of content: the board rules extracted from build.py unchanged (internal program rules in evaluation order, customer technology rules, named overrides, vendor-led keywords, excluded programs); the UDC Technology vocabulary with Jim's 2026-11-02 ownership answers, which the board ignores; and a per-dashboard `show_in` flag, because Non-Technical is shown as its own line in Mk II and excluded on the board.

## Branch rule

The file lives under `data/` so that, once promoted to main, an edit made on main through the web UI reaches preview on the next build's sync step, the same way weekly uploads do. The first commit lands on preview together with the build.py change that reads it, so file and reader arrive together.

## Why

Two dashboards attributing the same class to different PLLs is the failure this prevents. A rule in Python can only be shared by copying it, and a copy drifts. A JSON file can be read by both and edited once.

## Verified

Routing output over the live Enrollment Database was captured before the refactor and diffed after it: zero differences. Per-rule tests in tests/test_pll_mapping.py.

## Schema as built (Jim's ruling, 2026-11-02)

The first brief's schema could not hold all the routing, because `route_pll` carries inline rules (CTE, craft, Mark VIe) and the look-ahead router has its own. Nothing stays inline. `internal_rules` replaces `internal_program_rules`: one ordered list mirroring `route_pll`, whose file order is the evaluation order (the Woodward `named_overrides` ref sits between craft and Mark VIe, where the code checks it). `lookahead_rules` is the equivalent ordered list for `route_lookahead_internal`, with `lookahead_technology_rules` and `excluded_programs` referenced from it. `vendor_led_keywords` is checked first in `route_pll`, in code. The Mk II keys (`udc_technology`, `location_rules`) are not read by build.py. `LOCATION_MAP` and `classify_location` stay in build.py: they classify delivery location, not PLL.

## Known divergence from Jim's 2026-11-02 ruling

Jim ruled Craft goes to Harry regardless of location. `route_customer` has no Craft or Harry rule, and Harry and Linda are documented as never receiving customer rows, so a customer row with Technology Craft is flagged UNMATCHED. Confirmed as a bug and deliberately not fixed in this refactor. Tracked as action item cb5bf727, its own commit after this one.
