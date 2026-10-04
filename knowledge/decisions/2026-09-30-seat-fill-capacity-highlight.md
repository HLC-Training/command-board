# Seat fill is highlighted by capacity state, computed every build

**Date:** 2026-09-30
**Status:** active

## Decision

The Command Board highlights seat fill amber with a FULL marker at capacity
and GE Vernova Alert orange (#EC642B) with an OVER marker over capacity. The
state is computed every build from current source data and is never
preserved. Classes with no capacity value get no highlight and are counted
as unknown in the build summary.

## Context

The September 2026 Glint survey's loudest team-wide theme was quality being
traded for volume, with class sizes named specifically. Every class already
has a max capacity and the board already showed seat fill, so the response
was a highlight on the existing display rather than a new card.

## Consequences

- Capacity is the current max in the source, which may be a raised cap. A
  class full at a raised cap shows FULL, not OVER.
- Phase 2 (action item 73b6812d) adds a flag for classes above their
  original/ideal capacity once that table exists.
