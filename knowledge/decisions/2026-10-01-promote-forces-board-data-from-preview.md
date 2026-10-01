# Promote forces board-data.json from preview; index.html is not forced

**Date:** 2026-10-01
**Repo:** command-board
**Status:** active

## Decision

`promote-to-main.yml` merges preview into main, then runs
`git checkout origin/preview -- board-data.json`, commits if anything changed,
and fails the job unless main's board-data.json blob equals preview's.
`index.html` is not forced. It flows main -> preview (decision
2026-09-14-preview-build-py-is-build-source), and forcing it from preview would
silently revert a main-side change made between build and promote. If the merge conflicts on board-data.json alone, preview's copy is taken; a conflict on any other file aborts the merge and fails the job.

## Why

A plain `git merge` can resolve a diverged generated file to the stale side
with no error. On 2026-09-14 that cost hours. The promote now runs unattended
on the Sunday cron, so a wrong merge has to fail the job rather than ship.

## Related

- Action item 48491cc8 named both files; index.html was dropped deliberately.
- The 2026-09-30 capacity UI was committed to preview's index.html, against the
  main -> preview direction, and would have been reverted by the next build.
  It was landed on main the same session.
