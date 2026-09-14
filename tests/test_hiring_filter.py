"""
Per-status and dedupe tests for the slide-2 Open Positions card
(hiring-box brief, 2026-09-14).

filter_hiring_rows() is the pure (no network, no QR) filter/dedupe step
behind process_hiring(). These tests prove, one assertion per Current Step
value, that each open step is INCLUDED and each closed step is EXCLUDED,
that Order 1.0 / 3.0 rows never surface, that duplicate requisitions
collapse by take-max, and that the QR helper encodes the exact URL.

Run from the repo root:

    python tests/test_hiring_filter.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import build  # noqa: E402
from build import (  # noqa: E402
    HIRING_CLOSED_STEPS,
    HIRING_OPEN_STEPS,
    filter_hiring_rows,
    qr_data_uri,
)

HEADERS = ["Order", "Product Line", "Job Title", "Hiring Manager",
           "Candidate Name", "Country", "Current Step", "Budget Year",
           "Start Date", "Quantity Approved", "Quantity posted",
           "Quantity filled", "Backfill / Incremental", "Business Driver",
           "Payroll", "Cost Type", "Requisition Number", "Link", "Modified"]


def row(order, pl="Gas Turbine", title="Gas Turbine Instructor",
        country="Remote", step="posted", posted=1.0, filled=None,
        req=None, link=None, candidate=None):
    r = [None] * len(HEADERS)
    r[0], r[1], r[2], r[4], r[5], r[6] = order, pl, title, candidate, country, step
    r[10], r[11], r[16], r[17] = posted, filled, req, link
    return tuple(r)


passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}  {detail}")


print("\n── Per-status: each OPEN step is included ──")
for step in sorted(HIRING_OPEN_STEPS):
    pos, st = filter_hiring_rows(HEADERS, [row(2.0, step=step, title=f"T-{step}")])
    check(f"step '{step}' → included", len(pos) == 1 and pos[0]["step"] == step,
          f"got {pos}")

print("\n── Per-status: each CLOSED step is excluded ──")
for step in sorted(HIRING_CLOSED_STEPS):
    pos, st = filter_hiring_rows(HEADERS, [row(2.0, step=step, title=f"T-{step}")])
    check(f"step '{step}' → excluded", len(pos) == 0 and st["excluded_by_step"].get(step) == 1,
          f"got {pos} stats={st['excluded_by_step']}")

print("\n── Step matching is case/whitespace-insensitive ──")
pos, _ = filter_hiring_rows(HEADERS, [row(2.0, step="  Interviews ")])
check("'  Interviews ' → included as 'interviews'", len(pos) == 1 and pos[0]["step"] == "interviews")
pos, _ = filter_hiring_rows(HEADERS, [row(2.0, step="HIRED")])
check("'HIRED' → excluded", len(pos) == 0)

print("\n── Unknown step is hidden and flagged, never routed silently ──")
pos, st = filter_hiring_rows(HEADERS, [row(2.0, step="on hold")])
check("'on hold' → excluded + flagged", len(pos) == 0 and len(st["unknown_step"]) == 1)

print("\n── Blank step follows HIRING_INCLUDE_BLANK_STEP and is flagged ──")
orig = build.HIRING_INCLUDE_BLANK_STEP
build.HIRING_INCLUDE_BLANK_STEP = True
pos, st = filter_hiring_rows(HEADERS, [row(2.0, step=None, link="http://x")])
check("blank step (include=True) → shown as 'not set' + flagged",
      len(pos) == 1 and pos[0]["step"] == "not set" and len(st["blank_step"]) == 1)
build.HIRING_INCLUDE_BLANK_STEP = False
pos, st = filter_hiring_rows(HEADERS, [row(2.0, step=None, link="http://x")])
check("blank step (include=False) → hidden + flagged",
      len(pos) == 0 and len(st["blank_step"]) == 1)
build.HIRING_INCLUDE_BLANK_STEP = orig

print("\n── Order filter: 1.0 summary and 3.0 candidate rows never surface ──")
rows = [
    row(1.0, title=None, step=None, posted=2.0),                     # summary
    row(2.0, step="interviews"),                                      # requisition
    row(3.0, step="interviews", candidate="A Person", posted=None),   # candidate (open step!)
    row(3.0, step="declined", candidate="B Person", posted=None),     # candidate
]
pos, st = filter_hiring_rows(HEADERS, rows)
check("only the Order-2.0 row survives", len(pos) == 1 and st["order_2_rows"] == 1,
      f"got {len(pos)} order2={st['order_2_rows']}")
check("3.0 candidate with an open step is NOT shown", all(p["jobTitle"] for p in pos) and len(pos) == 1)

print("\n── Dedupe on (Job Title, Product Line, Country): take-max, first link wins ──")
rows = [
    row(2.0, pl="Generator", title="Instructor", country="Remote", step="interviews", posted=1.0),
    row(2.0, pl="Generator", title="Instructor", country="Remote", step="interviews", posted=1.0),
    row(2.0, pl="Gas Turbine", title="Gas Turbine Instructor", country="Remote",
        step="interviews", posted=1.0, req="26-2478", link="https://example.com/gt"),
    row(2.0, pl="Gas Turbine", title="Gas Turbine Instructor", country="Remote",
        step="interviews", posted=1.0),
    row(2.0, pl="Steam Turbine", title="Instructor", country="Remote", step="posted"),  # same title, other PL
]
pos, st = filter_hiring_rows(HEADERS, rows)
check("pre-dedupe = 5, post-dedupe = 3", st["pre_dedupe"] == 5 and st["post_dedupe"] == 3,
      f"pre={st['pre_dedupe']} post={st['post_dedupe']}")
gen = [p for p in pos if p["productLine"] == "Generator"]
gt = [p for p in pos if p["productLine"] == "Gas Turbine"]
check("Generator/Instructor collapsed to one", len(gen) == 1)
check("GT Instructor collapsed to one", len(gt) == 1)
check("take-max: posted stays 1 (not summed to 2)", gen[0]["posted"] == 1 and gt[0]["posted"] == 1,
      f"gen={gen[0]['posted']} gt={gt[0]['posted']}")
check("link survives the collapse (non-empty wins)", gt[0]["link"] == "https://example.com/gt"
      and gt[0]["reqNumber"] == "26-2478")
check("same title under a different Product Line is NOT merged",
      any(p["productLine"] == "Steam Turbine" for p in pos))

print("\n── Link → QR: null without a link; QR encodes the exact URL ──")
pos, _ = filter_hiring_rows(HEADERS, [row(2.0, link=None)])
check("no Link → link is None", pos[0]["link"] is None)
url = "https://www.fieldcore.com/careers/jobs/?p=job%2FoceeAfwY&__jvst=Job+Board&__jvsd=Email&nl=1"
uri = qr_data_uri(url)
check("qr_data_uri returns a PNG data URI", uri.startswith("data:image/png;base64,"))
try:
    import base64
    from io import BytesIO
    import zxingcpp
    from PIL import Image
    img = Image.open(BytesIO(base64.b64decode(uri.split(",", 1)[1])))
    decoded = [r.text for r in zxingcpp.read_barcodes(img)]
    check("decoded QR == source URL", decoded == [url], f"decoded={decoded}")
except ImportError:
    print("  SKIP  decode (pip install zxing-cpp to enable)")

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
