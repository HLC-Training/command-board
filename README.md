# command-board

OFS Training Delivery Command Board — GE Vernova, Houston Learning Center.

Live board: https://hlc-training.github.io/command-board/ (GitHub Pages, `main` branch)

## How the board gets built

`build.py` generates `board-data.json`, which `index.html` renders on the wall
display. The build pulls **five sheets live from the Smartsheet API** and reads
**three manually uploaded xlsx files** from `data/`:

| Source | How it arrives |
|---|---|
| Enrollment Database | Smartsheet API |
| OFS Training Action Plan Tracker | Smartsheet API |
| CapEx | Smartsheet API |
| Xyleme Modernization Tracker | Smartsheet API |
| Xyleme Exams Transfer Tracker | Smartsheet API |
| 2026 Bowler Chart | manual upload to `data/` |
| CM Customer Demand List (OE UDC) | manual upload to `data/` |
| Open Enrollment Class List (SS UDC) | manual upload to `data/` |

The build runs in GitHub Actions — no local Python needed.

## Friday workflow

1. **Upload the 3 files** (Bowler + 2 UDCs) to `data/` on `main` via the
   GitHub web UI. Old copies of the same files can be deleted; the build
   matches by name pattern, not exact filename.
2. **Run the build** — Actions → **Build Command Board** → *Run workflow* →
   enter `week_of` (the **Monday** of the target week, `YYYY-MM-DD`) → Run.
   The workflow pulls live Smartsheet data, reads `data/`, builds
   `board-data.json`, and commits it to the **`preview`** branch.
   Check the run log for the build summary (totals, RAGs, unmatched classes).
3. **Review the preview** — Settings → Pages → switch Branch to `preview`
   (takes ~30 s to redeploy), then check
   https://hlc-training.github.io/command-board/ on a big screen.
4. **Promote** — Actions → **Promote Preview to Main** → *Run workflow*.
   This merges `preview` into `main`.
5. **Switch Pages back** — Settings → Pages → Branch back to `main` (~30 s).

If the build summary flags `UNMATCHED` classes, fix the routing keywords in
`build.py` (on `preview`), re-run the build, then promote.

## Secrets (already configured)

- `SMARTSHEET_API_TOKEN` — Smartsheet API access for the five live sheets
- `COMMAND_BOARD_TOKEN` — fine-grained PAT for branch commits and merges

## Running locally (optional)

```
SMARTSHEET_API_TOKEN=... PYTHONUTF8=1 python build.py --week 2026-07-13
```

Requires `pip install smartsheet-python-sdk openpyxl` (both auto-install on
first run). See `CLAUDE.md` for counting rules, PLL routing, and RAG logic.
