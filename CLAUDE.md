# CLAUDE.md — OFS Command Board
## GE Vernova | Houston Learning Center

This file governs all Claude Code sessions in this repo.
Read it fully before taking any action.

---

## Repo and Live URL

- **Repo:** HLC-Training/command-board (GitHub Pages, root/main)
- **Live:** https://hlc-training.github.io/command-board/
- **Template:** index.html — do not restructure. Content changes (like the
  slide-1 Xyleme card) happen only when Jim explicitly briefs them.
- **Data file:** board-data.json — built weekly on the `preview` branch
- **Build tool:** build.py — the ONLY way board-data.json gets built
- **Source files:** 5 Smartsheet sheets (live API) + 3 xlsx files in data/

---

## Friday Workflow — GitHub Actions (no local build needed)

1. Jim uploads 3 files to data/ on `main` via GitHub web UI
   (Bowler + 2 UDCs — see Required Sources below)
2. Jim triggers **Build Command Board** workflow with `week_of`
   (the Monday, YYYY-MM-DD) → builds board-data.json on `preview`
3. Jim reviews: Settings → Pages → branch `preview` → check live URL
4. Jim triggers **Promote Preview to Main** → board goes live
5. Jim switches Pages branch back to `main`

Resolve every UNMATCHED flag in the build summary (workflow run log)
before promoting — routing fixes go in build.py, never one-off JSON edits.

A local build still works when needed:

   ```
   SMARTSHEET_API_TOKEN=... PYTHONUTF8=1 python build.py --week YYYY-MM-DD
   ```

   (`PYTHONUTF8=1` is required or the script crashes on box-drawing
   characters. Never hand-build board-data.json — hand-built boards have
   produced missing `totalClasses`, a malformed Week at a Glance entry,
   wrong slide 3 data, and inflated student counts.)

   `--week`/`WEEK_OF` tolerates a pasted `week_of: YYYY-MM-DD` label,
   surrounding quotes/whitespace (`sanitize_week_override()` strips them
   before parsing) — a bare `week_of: 2026-07-20` crashed run #1 on
   2026-07-17. Anything else invalid after cleanup fails fast with the
   expected format.

---

## Required Sources

**Live from the Smartsheet API** (SMARTSHEET_API_TOKEN; sheet IDs in build.py):

| Sheet | Feeds |
|------|-------|
| Enrollment Database | Slides 1–3 student/class counts, PLL cards |
| OFS Training Action Plan Tracker | Action Plans RAG + panel |
| CapEx | CapEx RAG + panel |
| Xyleme Modernization Tracker | Xyleme card (modules ring + recently published) |
| Xyleme Exams Transfer Tracker | Xyleme card (exams pipeline) |

**Manual xlsx uploads to data/** — confirm all 3 before building.
File names include date stamps that change weekly — match by pattern:

| File | Pattern to match |
|------|-----------------|
| CM Customer Demand List | contains `CMCustomerDemandList` or `CM Customer` |
| Open Enrollment Class List | contains `ClassList` |
| 2026 Bowler Chart | contains `Bowler Chart` |

Ignore any placeholder `.txt` file (`placeholder.txt`, `placehilder.txt`, …) — not a source file.
Weekly uploads often carry `(N)` suffixes — the patterns above still match.
If any of the 3 patterns go unmatched — STOP and notify Jim.
The Weekly Report is retired — do not reference or request it.

---

## Build Summary (present before committing)

- Total students and classes
- PLL assignments and student counts
- Any flagged or unmatched classes
- Safety RAG status and reason
- Bowler KPI status and reason

---

## PLL Mapping Rules — CRITICAL

Apply in this exact order:

### Internal Training — program-first:

1. **Vendor-led / non-technical** (Achieving Customer Success,
   Field Engineer - Onboarding, Train the Trainer, Project Management,
   Leadership) → **totals only, no PLL, never flagged**
2. **CTE / Workforce Readiness → Linda Nelson** — this check MUST precede
   the Craft rule ("Craft Entry Level CTE Program" is Linda's, not Harry's)
3. Program = Craft, Repairs, ILES, or Stator → **Harry Hanson**
4. Gas Turbine (incl. 7FA/9FA/7HA/9HA, Live Outage TTT) → **Sherif Khalifa**
5. Steam Turbine (incl. blading) → **Pablo Schibli**
6. Controls / GIC (incl. COMET Commissioning) → **Mohammed Nizami**
7. Excitation / Generator (incl. EX2100) → **Ben Smith**
8. Aeroderivative (incl. LM2500/LM6000/LMS100, AET MI) → **Greg Walker**
9. Unmatched → **FLAG TO JIM — never route silently**

This order is implemented in build.py (`route_pll`, `INTERNAL_RULES`,
`VENDOR_LED_KEYWORDS`). New routing decisions go there as keywords —
never as one-off JSON edits.

### Customer Training — technology only:

- Gas Turbine, Balance of Plant, General → **Sherif Khalifa**
- Steam Turbine, Combined Cycle, HRSG → **Pablo Schibli**
- Controls / GIC, Simulator → **Mohammed Nizami**
- Excitation / Generator → **Ben Smith**
- Aeroderivative → **Greg Walker**

### Hard Rules:

- Harry Hanson and Linda Nelson: **zero customer rows**
- OE/SS classes go under the correct PLL by technology
- Never create a separate OE/SS block
- No class appears under two PLLs
- Steam Power Documentation = Steam Turbine → Pablo Schibli
- Vendor-led classes count in weekly totals but are **never attributed
  to any PLL card** (they appear as ℹ️ VENDOR-LED in the build summary)

### PLL Order in JSON and on Slide 2:

Sherif → Pablo → Ben Smith → Mohammed → Harry → Greg → Linda Nelson → Week at a Glance

- Always use full names: "Linda Nelson" not "Linda"

---

## Slide 2 Layout — 8 Cards Only

1. Sherif Khalifa — Gas Turbine
2. Pablo Schibli — Steam Turbine
3. Ben Smith — Excitation/Generator
4. Mohammed Nizami — Controls/GIC
5. Harry Hanson — Craft/Repairs/ILES
6. Greg Walker — Aeroderivative
7. Linda Nelson — CTE/Workforce Readiness
8. Week at a Glance

---

## Bowler KPI Rules

- **Bowler KPIs, the Bowler RAG, and safetyKPIs (liveStop/readAcross) are
  derived fresh from the Bowler Chart every build** (as of the Jul 2026
  hardening — no longer preserved from the previous board-data.json).
  `load_bowler_sheet()` reads the sheet's true header row (JAN…DEC, with
  1Q/2Q/3Q/4Q columns skipped) and each KPI's 3-row PY/Plan/Act block.
- **Month auto-selection:** target month = build month minus 1 (most
  recent complete month), via `bowler_target_month(date.today())`. If the
  target month's Act cell is empty/NA, `bowler_month_value()` walks
  backward to the most recent populated month and reports that month as
  `monthLabel`.
- **Value normalization:** `parse_bowler_value()` strips stray characters
  (`%`, `*`, etc.) then treats a result `<= 1.5` as a decimal fraction
  (×100) — the sheet mixes decimals (0.91), bare percentages (84.6), and
  dirty strings (`'*58%'`, `'90%%'`).
- **YTD value** = mean of populated Act values from Jan through the target
  month (not the walked-back month — YTD always spans the full year so far).
- Thresholds (`BOWLER_CONFIG` in build.py):
  - Post-Training Skill Improvement (PTSI): Green ≥70%, Red <63%
  - Timecard On-Time Delivery: Green ≥92%, Red <82%
  - FLIQ (Fully Loaded & Qualified Instructors): REVERSE metric (lower is
    better), Green <15%, Amber ≥15%, **no red** — health-monitoring only

---

## Safety RAG Logic

- **Green:** 0 incidents AND all KPIs in spec
- **Amber:** 1–2 minor incidents AND all KPIs in spec
- **Red Path A:** Any KPI out of spec — `liveStop` or `readAcross` red
  (<90% vs the 90% plan) overrides the zero-incident green, per
  `calculate_safety_rag()` in build.py
- **Red Path B:** 3+ incidents AND all KPIs in spec

`liveStop` (Live Save Rule Compliance %) and `readAcross` (Read Across
Closing Rate) are extracted from the Bowler Chart with the same
month-auto-select + NA-walk-back logic as the Bowler KPIs above
(`process_safety_kpis()`) — no longer preserved from the previous board.
Both are green ≥90%, red <90%, no amber zone.

### Cumulative Safety Log — carry forward always (newest first):

- **Jul 17, 2026:** 📵 No-Photo Policy — Training Bays — advisory (unauthorized
  social media post from the training bays)
- **Apr 3, 2026:** Lube oil spill during maintenance exercise — contained, cleaned, no injury
- **Mar 14, 2026:** Slip on wet floor near lab entrance — no injury, area secured

(Retired 2026-07-17: Jun 18 Heat Stress Awareness advisory — season passed.)

build.py carries `safetyLog` forward from the existing board-data.json
automatically — new incidents are added there (or to `SAFETY_LOG_BASE`
in build.py, which must be kept in sync so a from-scratch rebuild matches
production), never dropped.

---

## Slide 1 RAG Strip Order (locked)

Bowler → Safety → Action Plans → CapEx

---

## Location Rules

Source data uses these exact strings — match accordingly:

| Source string | Board category |
|---------------|---------------|
| `Houston Learning Center` | HLC |
| `Birr Learning Center` | BLC |
| `Houston Learning Center / Birr Learning Center` | HLC only (no split) |
| `Houston Learning Center/Birr Learning Center` | HLC only (no split) |
| `Kuwait` (any form) | KLC |
| Anything else | Other/Distance Learning |

---

## Student and Class Counting — CRITICAL

**Count all classes IN SESSION during the week — not just classes that start that week.**

A class is in session if: `Start Date <= week end date` AND `Finish Date >= week start date`

**Active student statuses to COUNT:** Registered, In Progress, Completed, Auditor

**Statuses to EXCLUDE:** Cancelled, No Show, Withdrawal, Waitlisted, Did Not Finish, Did Not Pass

Never use start-date-only logic. Multi-week classes already in progress must be included.

**Lesson (Jul 6, 2026):** a hand-built board reported 423 students because it
counted 33 Withdrawal + 3 Did Not Finish rows; the correct total per these
rules was 387. If a target number doesn't match build.py output, check the
status filter before assuming the build is wrong.

---

## board-data.json Field Reference

Buckets are determined by SOURCE FILE: Internal ← Enrollment Database,
OE ← CMCustomerDemandList, SS ← ClassList. OE + SS = "customer".

- `slide1.weeklyTotal` = total active students (Internal + OE + SS)
- `slide1.internalStudents` = active Enrollment Database students
- `slide1.oeStudents` = active customer students (OE + SS combined)
- `slide1.internalCourses` = internal classes in session
- `slide1.oeCourses` = customer classes in session (OE + SS)
- `slide1.locationBreakdown` = { HLC, BLC, KLC, Other } — must sum to weeklyTotal
- `slide2.plls[]` = the 7 PLL cards **in PLL order**, each requiring
  `totalClasses` (int, internal + customer), `totalStudents`,
  `internalStudents`, `oeStudents`, `oeClasses`, `courses[]`,
  `oeCourses[]`, `lookAhead30` — index.html renders `undefined` if any
  are missing
- `slide2.plls[]` **must end with the sentinel `{"name": "__WAG__"}`** —
  index.html builds the Week at a Glance card itself from slide1 +
  safetyLog and skips the sentinel. Never embed a real Week at a Glance
  object in the array.
- `slide3.pins` = **INTERNAL student country of ORIGIN** (Enrollment
  Database `Student Country` column) — NOT class delivery location.
  Typically ~38 countries.
- `slide3.learningCenters` = HLC/BLC/KLC map markers (internal students)
- `slide3.totalStudents` = **internalStudents** (slide 3 is internal-only;
  build.py validation enforces this — it is NOT weeklyTotal)
- `slide4.weekDelivery` = customer (OE + SS) training by DELIVERY country

---

## Carried-Forward Sections — verify each build

build.py preserves these from the existing board-data.json instead of
recomputing:

- **safetyLog** — cumulative, carried forward always (see Safety RAG Logic)
- **Per-PLL lookAhead30** (currently all zeros — the Jul 6 hand-built
  board dropped them; needs manual re-entry if Jim wants them back;
  flagged in the build summary under "VERIFY MANUALLY")

Bowler KPIs, Bowler RAG, and safetyKPIs (liveStop/readAcross) are NO
LONGER carried forward as of the Jul 2026 hardening — see Bowler KPI
Rules. CapEx is also NOT carried forward — it is computed live from the
CapEx Smartsheet (Year 2026, Order ≥ 3 line items, Cancelled excluded;
budget totals from the Order-1 summary row).

Because preservation reads the CURRENT board-data.json, never delete or
hand-strip that file — a bad board propagates into the next build.

---

## Map Standards

- BLC Birr = lat 47.36, lon 8.04
  (Birr, Aargau, Switzerland — NOT Ireland, NOT UK)
- Country pins come from `COUNTRY_INFO` / `COUNTRY_ALIASES` in build.py —
  if a pin lands at (0,0), add the missing country or alias there

---

## Commit Format

Weekly board data is committed by the **Build Command Board** workflow to
the `preview` branch and reaches `main` via **Promote Preview to Main** —
never push board-data.json straight to `main`.

For a local build committed manually (rare):

```
git add board-data.json
git commit -m "Week of [DATE] — [N] students, [N] classes"
git push origin preview
```

---

## After Committing — Tell Jim:

- Week date range confirmed
- Total students and classes
- Any unmatched classes flagged
- Safety RAG status and reason
- Bowler RAG status and reason

Then produce this Cowork archive prompt:

```
Append the following to
C:\Users\210077026\Documents\SAM-COS-Vault\Work\projects\command-board\build-notes.md
Do not modify existing content.

## [DATE] — Week of [DATE RANGE]
Students: [N] | Classes: [N]
Safety: [RAG] | Bowler: [RAG]
Flags: [any issues]
Commit: [commit hash]
```

---

## File Protection

- **index.html** — do not touch during a build run; structural changes
  only on Jim's explicit brief (last change: Xyleme card, Jul 2026)
- **CLAUDE.md** — Do not modify during a build run
- **board-data.json** — The only file written during a build
- **build.py** — routing/logic fixes are allowed but go in a SEPARATE
  commit from the weekly board-data.json commit
- **main branch** — weekly data reaches it only via Promote Preview to Main

---

## Vault Integration

GE Vernova vault: `C:\Users\210077026\Documents\SAM-COS-Vault\`
(build notes live under `Work\projects\command-board\build-notes.md`)

The vault is on a different machine/profile — Cowork handles vault file
operations. Claude Code handles GitHub repo commits only, and produces
the Cowork archive prompt after each build.
