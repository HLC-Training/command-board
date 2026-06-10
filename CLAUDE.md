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
- **Source files:** data/ folder (7 xlsx files)

---

## Monday Workflow — Trigger: "Build this week's board"

1. Confirm all 7 source files are present in data/
2. If any are missing — STOP and notify Jim. Do not proceed.
3. Read and process all 7 files
4. Generate board-data.json
5. Present build summary for Jim's review
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

Ignore `placeholder.txt` — it is not a source file.
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

1. Program = Craft, Repairs, or ILES → **Harry Hanson**
2. Gas Turbine → **Sherif Khalifa**
3. Steam Turbine → **Pablo Schibli**
4. Controls / GIC → **Mohammed Nizami**
5. Excitation / Generator → **Ben Smith**
6. Aeroderivative → **Greg Walker**
7. CTE → **Linda Nelson**
8. Unmatched → **FLAG TO JIM — never route silently**

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

- Use April data (most recent complete month) — NOT YTD
- All YTD actuals stored as decimals → multiply ×100
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

---

## board-data.json Field Reference

- `slide1.weeklyTotal` = total active students across all locations
- `slide1.internalStudents` = weeklyTotal minus oeStudents
- `slide1.oeStudents` = active OE students
- `slide1.internalCourses` = internal classes in session
- `slide1.oeCourses` = OE classes in session
- `slide1.locationBreakdown` = { HLC, BLC, KLC, Other } — must sum to weeklyTotal
- `slide3.learningCenters` = map markers — update BLC and KLC students here
- `slide3.totalStudents` = same as weeklyTotal

---

## Map Standards

- BLC Birr = lat 47.36, lon 8.04
  (Birr, Aargau, Switzerland — NOT Ireland, NOT UK)

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
C:\Users\210077026\Documents\GE Vernova\projects\command-board\build-notes.md
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

---

## Vault Integration

GE Vernova vault: `C:\Users\210077026\Documents\GE Vernova\`

Cowork handles vault file operations.
Claude Code handles GitHub repo commits only.
