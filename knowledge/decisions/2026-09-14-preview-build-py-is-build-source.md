# The board build runs preview's build.py — the workflow no longer syncs build.py from main

**Date:** 2026-09-14
**Status:** active

## Decision

`.github/workflows/build-board.yml` syncs only `data/` and `index.html`
from `main` onto `preview` before building. `build.py` is not synced: the
build uses whatever build.py is on `preview`. A build.py fix must
therefore land on `preview` to take effect in a build, and reaches `main`
through Promote Preview to Main like the weekly board data.

## Context

The sync step used to run `git checkout origin/main -- data/ build.py
index.html`. That is a silent revert for any build.py change that lives on
preview but has not yet been promoted. On 2026-09-11 it overwrote the
2026-09-08 Bowler YTD source-column fix (commit `7bd439a`, decision
`2a6b41e7`) with main's pre-fix copy; the resulting build was promoted on
2026-09-13 and the live wall board showed mean-of-months YTDs again. The
decision was never wrong — the pipeline erased the code that implemented
it. Full write-up:
`knowledge/learnings/2026-09-14-workflow-build-py-sync-regression.md`.

## Consequences

- Data inputs (`data/` uploads, `index.html` template) still flow
  main → preview automatically; build logic does not.
- build.py fixes are committed to `preview` (or merged there from a
  feature branch) before the next Friday build. They keep going in a
  separate commit from the weekly board-data.json commit.
- If `main` ever carries a build.py change that `preview` lacks, it must be
  merged into preview deliberately — a merge conflicts loudly, a checkout
  does not.
- CLAUDE.md records the rule under the Friday Workflow and File Protection
  sections.
