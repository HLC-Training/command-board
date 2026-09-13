## Bowler YTD came from a month-mean, not the sheet's YTD column
A "computed from source" KPI can still be computed wrong. process_bowler
averaged the monthly Act values to fake a YTD instead of reading the sheet's
owner-maintained YTD Actual column (py-row, index 6). It drifted every week and
got hand-patched at QC three builds running. Lesson: when a source has an
authored aggregate column, read it — don't re-derive the aggregate from the
components and hope they match. And a named per-KPI exception (PTSI's N/A → YTD
rule) can't live inside a generic walk-back; it needs its own branch.
