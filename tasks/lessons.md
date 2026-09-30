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
