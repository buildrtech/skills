# Review memo template

Use this default layout at step 10; equivalent headings are acceptable. Lead with the status. Paste the script's two
tables unchanged. Every amount in the memo cites where it came from: the
application (file or page and line and column), the contract terms the
reviewer supplied, or the script's arithmetic on those. The memo prepares a
decision; it never makes one.

Status wording, pick one:

- **Recommend hold for review.** At least one error-severity finding, or a
  required document is missing.
- **No exceptions found in the checks run.** Zero errors; warnings, if any,
  are listed with what was confirmed. Say which checks were skipped for lack
  of terms or a prior period.
- **Review incomplete.** A required input was missing or unreadable and the
  user chose to proceed anyway. Say which checks did not run.

```
# Pay app review: <project>, Application No. <n>, period ending <date>

**Status:** Recommend hold for review | No exceptions found in the checks run | Review incomplete
**In one line:** <the finding that most changes what happens next, with its amount>

## Summary

Three to six sentences. What was submitted (Line 8 as submitted and what it
is for), what the review covered (which documents, which period compared,
which contract terms), the count of errors and warnings, and the two or
three findings that drive the status. Say plainly that this memo is not an
approval, certification, or rejection.

## Contract terms used

| Term | Value | Source |
|---|---|---|
| Original contract sum | | contract, page |
| Approved change orders | | change order log, entries listed |
| Retainage on completed work | | contract clause |
| Retainage on stored materials | | contract clause |
| Retainage reduction milestone | reached / not reached / none | contract clause, and the measure |
| Stored materials rules | | contract clause |
| Lien waiver requirement | | contract clause |
| Certified payroll requirement | required / not required | contract clause |
| Cumulative prior certificates | amount, through date | certificate history |

## Script findings

Command run (relative to the skill directory), then both tables the script
printed, unchanged.

## Findings the script cannot make

One bullet per finding, each citing line and column or cover-sheet line and
the document it came from:

- Change order reconciliation: each approved change order and where it does
  and does not appear (Line 2, summary box, G703 line).
- Continuity notes: version of the prior schedule used, renumbered or split
  lines, Line 7 versus the certified amount.
- Stored materials backup: per flagged line, what the contract requires and
  what is in the package.
- Questions for the field: per percent-jump, over-100-percent, or
  100-percent line, the question to ask, not a conclusion.
- Anything derived, unreadable, or assumed during extraction.

## Items on hold for a human decision

| # | Item | Line / column | Amount in question | Source | What would clear it |
|---|---|---|---|---|---|

Amount in question is the amount the finding puts in doubt, cited to the
application, not a proposed deduction. Do not total this column and do not
present a "corrected amount due"; the script's recomputed Line 8 is shown
for comparison only and does not incorporate corrections to the schedule.

## Items ready

Lines and cover-sheet fields that passed every check that ran, so the
reviewer knows what is not in question. Name the checks that ran on them.

## Documents

| Document | Required by | Status | Note |
|---|---|---|---|

Status is present, missing, not required, or open. Do not judge sufficiency.

## Next steps

Only what the user would do next: questions to send the contractor, what a
corrected resubmission needs to contain, who decides the hold items. Offer
follow-on work (question list, corrected schedule, tracking entries) only
if asked, and never change a record or send anything without approval.

## Sources

Which files or pages each set of facts came from, which checks were skipped
and why, and the sentence: this memo prepares a review and is not an
approval, certification, or rejection of payment, not legal advice, and not a
wage determination.
```
