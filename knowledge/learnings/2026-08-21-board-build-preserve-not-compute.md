# Board build: preserve-not-compute traps and the Smartsheet row cap

**Date:** 2026-08-21
**Trigger:** Every PLL card's 30-day look-ahead read 0 classes / 0 students on
the Aug 24 board. Root cause: `build.py` preserved `lookAhead30` from the
prior `board-data.json` instead of computing it, and nothing ever reseeded
it — a stale zero block echoed forward week over week, silently, on a
leadership-facing read path.

**Fix shipped this session:** `lookAhead30` is now computed from source every
run (internal from the Enrollment Database Smartsheet, OE/SS from the two
demand xlsx), routed program-first per the 2026-08-21 brief, with unmatched
classes flagged to Jim. It is no longer in the preserved set. All Smartsheet
fetches now page explicitly and assert completeness against the sheet's
`total_row_count`.

---

## (a) Remaining preserve/staleness contracts, ranked by how silently they fail

The brief listed CapEx, Bowler KPIs, and safetyKPIs as "still preserved."
As of current `build.py` (post commits `ecb7664`…`0550c9a`) that is no longer
literally true — all three are computed — but each still has a **reseed
contract** that can go stale without any visible failure:

1. **Bowler KPIs + safetyKPIs — highest silent-failure risk.**
   Computed fresh each run from the Bowler Chart xlsx in `data/`, with a
   per-KPI month walk-back (a blank/NA target month falls back to the latest
   populated month). The walk-back is the trap: if the Bowler Chart upload is
   forgotten, the build reuses the old committed xlsx and still reports
   plausible numbers from whatever month was last populated — no flag says
   "this file hasn't changed in N weeks." Reseed contract: a fresh Bowler
   Chart upload to `data/` on main. **Doc drift makes this worse:** CLAUDE.md
   still says Bowler KPIs are "PRESERVED from the previous board-data.json,
   Jim maintains them manually" — that describes the pre-`0550c9a` code.
   CLAUDE.md needs updating to match the computed reality (separate brief;
   not changed during this session's build run).

2. **safetyLog — preserved wholesale, by design.**
   Carried forward from the existing `board-data.json`; `SAFETY_LOG_BASE` in
   `build.py` is only the fallback when no board exists. Reseed contract:
   incidents are added by hand to the current board (or to
   `SAFETY_LOG_BASE`). Failure mode: deleting or hand-stripping
   `board-data.json` silently loses the cumulative log — the fallback would
   resurrect an older base list without warning. Note the two lists have
   already diverged (CLAUDE.md's log ends at the Jun 18 Heat Stress advisory;
   `SAFETY_LOG_BASE` carries the Jul 17 No-Photo advisory instead), which is
   fine only as long as the live board's log remains the source of truth.

3. **weeklyIncidents — hard-coded 0.**
   `build.py` assumes 0 new incidents every week; the safety RAG's
   incident-count path can literally never fire from source data. Reseed
   contract: a human remembers to edit the build (or the JSON) the week an
   incident happens. Low probability, but it is the same shape of bug as the
   look-ahead zeros: a constant pretending to be a computation.

4. **CapEx — computed live, lowest risk.**
   Pulled from the CapEx Smartsheet each run (Year 2026, Order ≥ 3 items,
   Cancelled excluded, budget from the Order-1 summary row). Reseed contract
   is the Smartsheet itself, which Ops maintains; staleness there is visible
   to its owners in a way a preserved JSON block never was.

**The general rule this incident bought:** any "preserve from prior
board-data.json" path needs either a computation or a staleness check. A
preserved section with no reseed becomes a stale/zero block that nobody sees
until they read the card on the Clevertouch.

## (b) The Smartsheet 250-row cap, and where it can bite

Filtered Smartsheet reads through the MCP/chat tooling cap at 250 rows and
set a quiet `is_sampled: true`. The Aug 24 look-ahead window had 325
enrollment rows — a single-shot read dropped ~75 rows and undercounted the
later weeks. This is what forced the hot-patch to page in 3 date-bounded
chunks.

In `build.py` the exposure was different but real: the SDK's `get_sheet`
returned the whole sheet in one response, with **no assertion** that it had.
`fetch_sheet_table` now pages explicitly (500 rows/page — the 4,545-row
enrollment sheet reads in 10 pages) and hard-fails if the accumulated row
count doesn't equal the sheet's `total_row_count`. That covers all five
Smartsheet pulls (Enrollment, Action Plans, CapEx, both Xyleme trackers).
Anything *outside* build.py that reads Smartsheet with a filter — chat
hot-patches, ad-hoc verification queries — must still page and must compare
retrieved rows against `rows_in_filter`, never trust a single response.

## (c) Should Friday QC gate look-ahead against a hand-count?

A full hand-count every Friday is more manual work than the failure warrants
now that the number is computed, flagged, and printed. Recommended gate
instead, added to the Friday checklist:

1. The build summary now prints `Enrollment DB rows with Start Date in
   window: N (M Registered/In Progress)` plus per-PLL look-ahead lines.
   **If N is 0, or every PLL reads 0/0, stop — that is a broken build, not
   an empty pipeline.** (The board can legitimately have a light week; it
   cannot legitimately have zero forward classes across all seven PLLs.)
2. Resolve every `UNMATCHED INTERNAL (30-day look-ahead)` flag before
   promoting — routing fixes go in `build.py`, never one-off JSON edits.
3. Once a month, spot-check one PLL's look-ahead against the Enrollment DB
   filtered by Start Date (paged!) — a 5-minute sanity pull, not a full
   recount.

## Regression note for future comparisons

The 2026-08-21 chat hot-patch numbers (Sherif 13/131, Pablo 14/156,
Ben 15/171, Mohammed 19/173, Harry 13/202, Greg 14/125, Linda 0/0) were
produced with two rule deviations the computed build deliberately does not
replicate:

- **Cancelled OE/SS classes were counted** (10 classes / 65 students across
  Sherif, Pablo, Mohammed, Greg). The brief's counting rules exclude
  Cancelled.
- **Two Repairs-program classes were routed by technology/name** (Advanced
  Buckets → Pablo, MAGIC Inspection → Mohammed). The brief's rule 1 routes
  Program = Craft/Repairs/ILES to Harry, program-first.

With those two corrections applied to the same source data, the computed
build reconciles class-for-class (Harry 13/212 = the hot-patch's 202 plus
Advanced Buckets 8 + MAGIC 2; Greg 13/120 = 14/125 minus one cancelled
class). Do not tune the routing to reproduce the hot-patch constants.
