# Source files are chosen newest-by-filename-date; ambiguity fails the build

**Date:** 2026-09-30
**Status:** active

## Decision

For each file-based source (CM Customer Demand List, ClassList, Bowler
Chart), build.py parses the date stamp in every matching filename in `data/`
and uses the newest. If any candidate's date cannot be parsed, or two
candidates share the newest date, the build fails and lists the candidates.
File modification time is never used. The build summary opens with a
SOURCES block, and warns when a chosen file is older than
SOURCE_MAX_AGE_DAYS (10 days for the customer files, 35 for the Bowler
Chart).

## Context

On 2026-09-30 a build matched 9/11 customer files while 9/24 files sat in
the same folder, with no signal in the build summary (bug 5fc3cd0d). A
wrong-but-plausible board is the failure this repo keeps paying for: see
the 2026-08-21 lookAhead30 learning and the 2026-09-08 Bowler YTD learning.

## Consequences

- Old uploads can stay in `data/`; they no longer affect the build.
- An upload without a date in its filename now stops the build. That is
  deliberate. Rename the file or remove the older one.
- A forgotten weekly upload now shows as STALE instead of passing silently.
