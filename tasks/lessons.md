## Bowler YTD came from a month-mean, not the sheet's YTD column
A "computed from source" KPI can still be computed wrong. process_bowler
averaged the monthly Act values to fake a YTD instead of reading the sheet's
owner-maintained YTD Actual column (py-row, index 6). It drifted every week and
got hand-patched at QC three builds running. Lesson: when a source has an
authored aggregate column, read it — don't re-derive the aggregate from the
components and hope they match. And a named per-KPI exception (PTSI's N/A → YTD
rule) can't live inside a generic walk-back; it needs its own branch.

## Recoloring the seat-fill bar collides with the legend and the existing amber
The seat-fill bar already encodes fill % (green ≥80, amber 50-79, cyan over,
red <50) with a legend at the foot of slide 2. Painting FULL amber and OVER
orange onto the bar made a 100% bar look identical to a 60% bar and left the
"cyan = over-enrolled" legend wrong. Rendered at 1920x1080 it was obvious;
the DOM check alone would have passed. Lesson: put a new state on its own
element (the FULL/OVER tag), not on a channel the display already uses, and
look at a real render before calling a highlight done.

## data/ piles up on preview, not main, and the old matcher took the first file it saw
The build workflow runs `git checkout origin/main -- data/` on preview. That adds
new uploads but never removes files Jim deleted from main, so preview's data/
accumulated every weekly upload while main stayed clean. `find_file` returned the
first `iterdir()` hit (arbitrary order), so from Aug 3 to Sep 27 nearly every
promoted board used at least one stale customer file. Nothing in the summary
showed it. Lesson: a "latest" selection must be explicit and shown in the build
summary; and when a brief says where a problem lives, check the branch the
workflow actually reads (preview), not just the one people edit (main).

## 2026-10-01 — index.html changes go to main, even mid-feature
build-board.yml stages main's index.html onto preview every build. A UI change
committed only to preview (the 9/30 capacity tags) is reverted by the next
build with no error. Land index.html changes on main; land build.py changes on
preview. Check `git diff origin/main origin/preview -- index.html` before any
build. It should be empty.
