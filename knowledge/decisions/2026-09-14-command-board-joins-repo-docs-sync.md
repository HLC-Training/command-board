# command-board joins the repo_docs sync

**Date:** 2026-09-14
**Status:** active

## Decision

command-board vendors `sync-repo-docs.yml` and `scripts/sync_repo_docs.py`
byte-identical from samcos (the canonical source), making its `CLAUDE.md`,
`tasks/lessons.md`, and `knowledge/**` docs readable from chat via the
`repo_docs` table in SAM COS Supabase (`hucrkbomqsxpmokgypxg`).

## Context

command-board hosts the OFS Training Command Board build (build.py + index.html)
and carries real reasoning docs — two board-build learnings docs and the
Bowler-YTD decision among them — that chat sessions could not read. Four builds
queued against the repo in September 2026 were each being spec'd from one-line
decision summaries because the detailed learnings lived only in the repo. That
is precisely the gap the 2026-07-31 repo-docs-sync decision exists to close.

## Consequences

The participating-repo list is now: samcos, orion, orion-pll, hlc-scripts,
Plantcare, command-board. The vendoring rule carries over in full: any future
edit to the sync logic propagates to all participating repos by hand, now six.
