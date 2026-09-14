# The Training Master Hiring Sheet is not a flat list — `Order` encodes row type

**Date:** 2026-09-14
**Action item:** 41c5735e-5154-486c-bf83-46666457c6dc
**Sheet:** Training Master Hiring Sheet, Smartsheet ID `8760722187046788`

The hiring sheet that feeds the slide-2 Open Positions card looks like a
table of jobs but is really three interleaved row types, distinguished by
the numeric `Order` column (and mirrored by the API's parent/child depth):

| Order | Depth | What the row is | Key columns populated | Shown? |
|-------|-------|-----------------|-----------------------|--------|
| 1.0 | 0 | Product-line summary | Product Line, Hiring Manager, Quantity Approved/posted/filled | No |
| 2.0 | 1 | A requisition (an open seat) | Job Title, Country, Current Step, Quantity posted/filled, sometimes Requisition Number + Link | **Yes** |
| 3.0 | 2 | A candidate in a requisition's pipeline | Candidate Name, Current Step (their status) | No |

Three traps this creates, all hit on the first read:

1. **Candidate rows carry open-looking steps.** An Order-3.0 row with
   `Current Step = interviews` is a *person* being interviewed, not a seat.
   Filtering on step alone (without `Order == 2.0`) would have shown four
   phantom "Customer Instructor" positions from one Steam Turbine req's
   pipeline. `filter_hiring_rows()` gates on Order first, step second.
2. **Quantity Approved lives on the 1.0 row** and is per product line, not
   per role. It is never displayed (Jim's call — posted/filled instead).
3. **Requisitions are duplicated verbatim.** As of 2026-09-14 three pairs
   (Steam Turbine Customer Instructor, Generator Instructor, Gas Turbine
   Instructor) are exact duplicates on (Job Title, Product Line, Country),
   each saying "1 posted" for the same seat. Dedupe collapses them by
   TAKE-MAX, never sum; the first non-empty Link / Requisition Number wins
   (the GT Instructor pair has the link on only one row). 11 Order-2.0 rows
   → 8 positions.

Also observed: one requisition (Gas & Steam Turbine Controls Instructor,
req 26-2604) has a live Link but a **blank** Current Step and blank
Country. Blank is neither an open nor a closed step; the build shows it as
"not set" and prints a ⚠️ so the sheet owner fills it in
(`HIRING_INCLUDE_BLANK_STEP` in build.py flips that). Any *other*
unrecognised step value is hidden and flagged — never routed silently,
same rule as PLL routing.

The brief estimated "~9 requisitions, ~4 with links"; the real count is
8 / 4 because there are three duplicate pairs, not two. The count is never
hardcoded — read the build summary's `Hiring:` block each Friday.
