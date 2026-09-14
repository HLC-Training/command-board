# The build workflow's "sync from main" step reverted a preview-only build.py fix

**Date:** 2026-09-14
**Trigger:** Action item `45c5f5aa`. While verifying the 2026-09-14
safety/staleness brief, `tests/test_bowler_ytd.py` failed 5/6 on HEAD. The
2026-09-08 Bowler YTD fix (commit `7bd439a`, decision `2a6b41e7`, learnings
`2026-09-08-bowler-ytd-source-column.md`) was gone from main, preview, AND
`feature/board-upgrade` — `process_bowler()` was back to
`sum(ytd_vals) / len(ytd_vals)`. The live wall board had been showing
month-mean YTDs again since the 2026-09-13 promote.

**Root cause — the pipeline, not the code:** `build-board.yml` checked out
`preview` and then ran `git checkout origin/main -- data/ build.py index.html`.
The 7bd439a fix had been committed only to `preview` (correct per the
workflow — that is where builds run). On 2026-09-11 the Friday build ran
before the fix had been promoted, so the sync step silently replaced
preview's fixed build.py with main's pre-fix copy, the build committed on
top of that, and the 2026-09-13 promote carried the broken build.py to main.
Nothing in the run log said a source file had been reverted. The decision
was correct throughout; only the code regressed against it.

**Fix shipped this session (feature/board-upgrade):**

- Re-implemented the YTD source-column read + PTSI N/A→YTD branch +
  `find_kpi_rowset()` on top of the `606044c` staleness-flag change (the
  two coexist: the PTSI YTD branch `continue`s before the walk-back and its
  staleness flag; Timecard/FLIQ keep both). The mean block is deleted.
- `build-board.yml` no longer syncs build.py from main — only `data/` and
  `index.html`. **The build now uses preview's build.py.** A build.py fix
  must be on `preview` to take effect in a build; it reaches main via
  Promote Preview to Main like everything else. CLAUDE.md records this.
- `tests/test_bowler_ytd.py` now reads a FROZEN copy of the 2026-09-08
  Bowler sheet (`tests/fixtures/2026-09-08 Bowler Chart - OFS Training.xlsx`,
  git `51a4ca3`) instead of the live `data/` copy. Reason: Jim's 2026-09-11
  upload populated Aug for Timecard/FLIQ, so tests 5 and 6 (which assert the
  Aug-N/A→Jul walk-back) had a second, unrelated way to fail — the fixture
  under them changed. No assertions were touched; 6/6 pass on the frozen
  fixture, and the YTD gate (83/72/29) also holds on the live sheet.

**Two rules this incident bought:**

1. A CI step that copies a source file from another branch is a silent
   revert mechanism for every fix that has not yet crossed that branch.
   Sync *inputs* (data uploads, a template), never *code*. If code must be
   shared, merge it — a merge conflicts loudly; a checkout does not.
2. A test that reads a file the weekly workflow replaces is not a
   regression test — it is a test of whatever was uploaded last. Pin a
   frozen fixture for behavioral assertions; keep the live-file check as a
   separate, clearly-labeled smoke check if one is wanted.

**Not fixed by this session:** the preview/main `board-data.json` at the
time of writing was built with the mean calc. It must not be promoted; a
correct board comes only from a build run after this fix is on `preview`.
