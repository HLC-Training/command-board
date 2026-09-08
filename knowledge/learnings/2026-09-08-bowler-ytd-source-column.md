# Bowler YTD came from a month-mean, not the sheet's YTD column

**Date:** 2026-09-08
**Trigger:** Action item `b334e632` flagged the Bowler month walk-back as a
"computed-but-wrong" defect family. Investigating it surfaced a second, more
concrete bug: `process_bowler()`'s YTD figure was the arithmetic mean of the
populated monthly Act values (Jan through the target month), not the sheet's
own owner-maintained "YTD Actual" column. The two diverge — the sheet's
figure is weighted and some months are N/A, a mean can't reproduce that. On
the 2026-09-07 build all three cards shipped wrong YTDs (PTSI 82 vs true 83,
Timecard 79 vs true 72, FLIQ 20 vs true 29) and were hand-patched at QC. This
was the third consecutive build patched for a Bowler figure.

A second defect rode along: PTSI has a named exception in CLAUDE.md — when
its target-month Act is N/A, the board must show the YTD figure in both
slots labeled "YTD," never walk back to a prior month. The generic
month-walk-back (correct for Timecard/FLIQ) doesn't know about per-KPI
exceptions, so the 09-07 build showed "Jun 81" for PTSI — the disallowed
fallback.

**Fix shipped this session:**

- `process_bowler()` now reads YTD directly from `parse_bowler_value(py_row[6])`
  — the py-row (same row that carries the KPI name) at column index 6, which
  is the sheet's "YTD Actual" header column. Confirmed against the committed
  `2026 Bowler Chart - OFS Training.xlsx`: PTSI py-row index 6 = 0.83,
  Timecard = 0.72, FLIQ = 0.29 — matching the QC-corrected values exactly.
- Added a PTSI-only branch: if the target month's Act cell is None/NA
  *before any walk-back*, `monthLabel="YTD"`, `monthValue=ytdValue`,
  `monthRag=ytdRag`, and the walk-back is skipped entirely for that KPI.
  Timecard and FLIQ are untouched — their walk-back was already correct
  (both landed on Jul on the committed sheet, which is right).
- New `find_kpi_rowset()` returns the full `{"py","plan","act"}` set per KPI
  (the existing `find_kpi_act_row()` stayed, since `process_safety_kpis()`
  still only needs the Act row and has no YTD slot).
- Six fixtures in `tests/test_bowler_ytd.py`: YTD-from-source against the
  real committed sheet, a behavioral proof that mutating only the YTD cell
  (leaving months untouched) moves the output — a mean of unchanged months
  provably can't do that — the PTSI N/A→YTD path, the PTSI normal-month
  path, Timecard/FLIQ walk-back staying untouched, and the overall Bowler
  RAG reason still citing a month (not "YTD") for the two KPIs that still
  walk back.
- Corrected CLAUDE.md's Bowler KPI Rules section, which still described YTD
  as a month-mean.

**The general rule this incident bought:** when a source sheet has an
authored aggregate column (like a YTD total a human maintains), read it —
don't re-derive the aggregate from the components and hope they match. A
computed value can still be *wrong*, not just stale; "computed from source"
is not the same claim as "computed correctly from source." And a named
per-KPI exception (PTSI's N/A rule) can't live inside a generic walk-back —
it needs its own branch, checked before the generic path runs, or the
walk-back will silently swallow it.

## Scope note

The month walk-back itself (`bowler_month_value()`) was explicitly out of
scope for this fix — it is correct, and Timecard/FLIQ's landing on Jul on
the committed sheet proves it. Only PTSI's N/A path was wrong, and only
because it has an exception the generic walk-back has no way to know about.
The staleness-flag gap this action item was originally opened for (a
forgotten weekly Bowler upload reads as valid instead of stale) is still
open and separate — see action item `b334e632`'s remaining scope.
