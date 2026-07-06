# CLAUDE.md — OFS Command Board
## GE Vernova | Houston Learning Center

This file governs all Claude Code sessions in this repo.
Read it fully before taking any action.

---

## Repo and Live URL

- **Repo:** HLC-Training/command-board (GitHub Pages, root/main)
- **Live:** https://hlc-training.github.io/command-board/
- **Template:** index.html — NEVER MODIFY THIS FILE
- **Data file:** board-data.json — updated every Monday
- **Build tool:** build.py — the ONLY way board-data.json gets built
- **Source files:** data/ folder (7 xlsx files)

---

## Monday Workflow — Trigger: "Build this week's board"

1. **`git pull` first** — Jim uploads weekly data files (and sometimes edits)
   via GitHub web, so the local clone may be far behind origin
2. Confirm all 7 source files are present in data/
3. If any are missing — STOP and notify Jim. Do not proceed.
4. Run the canonical build tool:

   ```
   PYTHONUTF8=1 python build.py --week YYYY-MM-DD
   ```

   (Monday of the target week. Python 3.12 lives at
   `C:\Users\Jim\AppData\Local\Programs\Python\Python312\python.exe` —
   not on PATH. `PYTHONUTF8=1` is required or the script crashes on
   box-drawing characters.)

   Never hand-build board-data.json — hand-built boards have produced
   missing `totalClasses`, a malformed Week at a Glance entry, wrong
   slide 3 data, and inflated student counts (counted Withdrawals).
5. Present the build summary for Jim's review — resolve every
   UNMATCHED flag before committing (routing fixes go in build.py)
6. Wait for approval ("approved" or "commit it")
7. Commit board-data.json to repo root
8. Report completion and produce Cowork archive prompt

---

## Required Source Files (data/ folder)

Confirm all 7 are present before building.
File names include date stamps that change weekly — match by pattern:

| File | Pattern to match |
|------|-----------------|
| Enrollment Database | contains `Enrollment Database` |
| CM Customer Demand List | contains `CMCustomerDemandList` or `CM Customer` |
| Open Enrollment Class List | contains `ClassList` |
| 2026 Bowler Chart | contains `Bowler Chart` |
| OFS Training Action Plan Tracker | contains `Action Plan Tracker` |
| CapEx | contains `Capex` or `CapEx` |
| Weekly Report | contains `Weekly Report` |

Ignore any placeholder `.txt` file (`placeholder.txt`, `placehilder.txt`, …) — not a source file.
Weekly uploads often carry `(N)` suffixes (e.g. `Enrollment Database (5).xlsx`) — the patterns above still match.
If any of the 7 patterns go unmatched — STOP and notify Jim.

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
   Field Engineer - Onboarding, Train the Trainer) → **totals only, no PLL**
2. **CTE / Workforce Readiness → Linda Nelson** — this check MUST precede
   the Craft rule ("Craft Entry Level CTE Program" is Linda's, not Harry's)
3. Program = Craft, Repairs, or ILES → **Harry Hanson**
4. Gas Turbine (incl. 7FA/9FA/7HA/9HA, Live Outage TTT) → **Sherif Khalifa**
5. Steam Turbine (incl. blading) → **Pablo Schibli**
6. Controls / GIC → **Mohammed Nizami**
7. Excitation / Generator (incl. EX2100) → **Ben Smith**
8. Aeroderivative (incl. LM2500/LM6000/LMS100) → **Greg Walker**
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

- **Bowler KPIs and the Bowler RAG are PRESERVED from the previous
  board-data.json**, not parsed from the Bowler Chart — Jim maintains
  them manually (the xlsx parse is unreliable and is only a fallback
  when no existing board exists). Confirm the carried-forward values
  with Jim each build.
- Current status (as of Jul 6, 2026): **AMBER — Timecard YTD 72% vs 92% plan**
- Thresholds (for when values are updated):
  - All actuals stored as decimals → multiply ×100
  - Instructor Utilization: REVERSE metric — lower is better
  - Post-Training Skill Improvement: Green ≥70%, Red <63%
  - Timecard OTD: Green ≥92%, Red <82%

---

## Safety RAG Logic

- **Green:** 0 incidents AND all KPIs in spec
- **Yellow:** 1–2 minor incidents AND all KPIs in spec
- **Red Path A:** Any KPI out of spec
- **Red Path B:** 3+ incidents AND all KPIs in spec

### Cumulative Safety Log — carry forward always:

- **Mar 14, 2026:** Slip on wet floor near lab entrance — no injury, area secured
- **Apr 3, 2026:** Lube oil spill during maintenance exercise — contained, cleaned, no injury
- **Jun 18, 2026:** 🌡️ Heat Stress Awareness advisory — hydration, vehicle,
  and Bldg 1 Bay precautions; EHS distributing cooling towels & electrolytes

build.py carries `safetyLog` forward from the existing board-data.json
automatically — new incidents are added there (or to `SAFETY_LOG_BASE`
in build.py), never dropped.

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
recomputing (no reliable weekly source). The build summary flags them
under "VERIFY MANUALLY":

- **CapEx** ($6.07M / 26 projects as of Jul 6, 2026 — Capex.xlsx has no
  clean summary source)
- **Bowler KPIs + Bowler RAG** (see Bowler KPI Rules)
- **safetyKPIs** and **safetyLog**
- **Per-PLL lookAhead30** (currently all zeros — the Jul 6 hand-built
  board dropped them; needs manual re-entry if Jim wants them back)

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

After Jim approves:

```
git add board-data.json
git commit -m "Week of [DATE] — [N] students, [N] classes"
git push origin main
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

- **index.html** — NEVER TOUCH. Ever.
- **CLAUDE.md** — Do not modify during a build run
- **board-data.json** — The only file written during a build
- **build.py** — routing/logic fixes are allowed but go in a SEPARATE
  commit from the weekly board-data.json commit

---

## Vault Integration

GE Vernova vault: `C:\Users\210077026\Documents\SAM-COS-Vault\`
(build notes live under `Work\projects\command-board\build-notes.md`)

The vault is on a different machine/profile — Cowork handles vault file
operations. Claude Code handles GitHub repo commits only, and produces
the Cowork archive prompt after each build.
