# Open Positions card: QR codes are generated at build time; duplicate requisitions collapse by take-max

**Date:** 2026-09-14
**Status:** active
**Action item:** 41c5735e-5154-486c-bf83-46666457c6dc

## Decision

1. **QR codes are rendered in build.py, not in the browser.** For every
   Open Positions row with an application `Link`, `qr_data_uri()` renders
   a PNG with the `qrcode[pil]` library and stores it in board-data.json
   as a `data:image/png;base64,…` string on the row's `qr` field. Rows
   without a Link get `qr: null`. index.html only does `<img src="…">`.
2. **Duplicate requisitions collapse by take-max.** Rows with the same
   (Job Title, Product Line, Country) are one position; `posted` and
   `filled` take the maximum across the duplicates, and the first
   non-empty Link / Requisition Number wins.

## Context

The board is a fixed kiosk display on wall screens across training centers,
some on locked-down networks. The alternative — a JS QR library loaded from
a CDN and rendered at page load — adds a runtime dependency, a network call
the screens may not be able to make, and a second place (after build.py)
where board content is computed. Build-time generation keeps index.html's
dependency surface flat (it still loads only d3/topojson for the maps) and
makes the JSON self-contained: what the build summary shows is exactly what
the wall renders. Cost: `qrcode[pil]` joins requirements.txt and the
workflow's install step, and board-data.json grows by ~3 KB per linked row.

Dedupe: the sheet's duplicate rows each describe the *same* seat ("1
posted" twice for one Generator Instructor req). Summing would report "2
posted" for a single opening — a phantom double-posting on a public wall.
Take-max can under-report only if a duplicate pair genuinely represents two
seats with different counts, which the sheet does not do today; if it ever
does, the rows should get distinct Requisition Numbers and the key can be
widened.

## Consequences

- A build.py change is needed to alter what a QR encodes; nothing in
  index.html knows about URLs.
- The build summary prints every collapsed pair (`ℹ️ duplicate requisition
  collapsed (take-max)`) so a real second seat mis-entered as a duplicate
  is visible on Friday, not silently halved.
- `tests/test_hiring_filter.py` pins both rules (per-step include/exclude,
  Order gating, take-max, link survival, QR decode == source URL).
- Learnings: `knowledge/learnings/2026-09-14-hiring-sheet-order-column-row-types.md`.
