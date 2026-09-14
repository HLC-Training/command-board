# weeklyIncidents = 0 is a documented decision, not an oversight

**Date:** 2026-09-14
**Action item:** 554ceecf-09da-4d04-985f-0cd99f8b1893

`build.py`'s `weekly_incidents = 0` constant is intentional, not a stale
placeholder. There is no per-week incident count source — the Weekly Report
that once carried it is retired (see CLAUDE.md). The safety RAG's real signal
comes from KPI compliance (`liveStop` / `readAcross`, both computed fresh
from the Bowler Chart) and the cumulative `safetyLog`, not a weekly delta.

This means `calculate_safety_rag()`'s amber (1-2 incidents) and
incident-driven-red (3+) branches stay dead code under current inputs — that
is accepted, not a bug. If a future brief wants those branches live, the
honest fix is to derive `weekly_incidents` from `safetyLog` entries dated
within the board week (option (b) considered and deferred in the
2026-09-14 safety/staleness brief) — not to invent a new incident-count
source.

If a diagnostic flags `weekly_incidents = 0` again: check the comment at its
definition in `build.py` first. If it still cites this note, it is working
as designed.
