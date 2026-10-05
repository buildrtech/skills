# Extracting bids

How to turn the bids as received into `bid-data.json`. The goal is a record a
reviewer can check in seconds: every status and amount points at a short quote
from the bid.

## Rows

- Start from the scope sheet: one row per line item, in its order, with the
  package's own wording. Add a row only when a bid prices or excludes scope the
  sheet doesn't name, and choose its class (`base`, `outside`, or `review`).
- Use one key per scope across every bid. Two bids calling it "sound batts" and
  "insulation" share a single `sound_batts` row.
- Requested alternates come from the package and addenda, not from what
  bidders happened to price.

## Reading each bid

| Source | How to read it |
|---|---|
| PDF proposal | Extract the text (`pdftotext -layout`) or render the pages. Read scope, exclusions, clarifications, alternates, unit prices, and terms. Exclusions often sit on page 2 or in small print. |
| Bid form spreadsheet | Open each sheet. Row numbers are your evidence locations. A row with "By others" or a blank price is an exclusion, not an included $0. Add up the lines yourself; the script also checks. |
| Email quote | The body is the bid. Check for attachments. One paragraph usually leaves most rows `omitted`. |
| Lump sum ("$781,000, thx") | Rows the email names are `included`. "Per plans and specs" makes the remaining rows `unknown`, not `included`. A row not mentioned at all is `omitted`. |
| Revision | A separate submission with the same `bidderKey`. Ask which governs and record the answer in `package.governing`. A revision after bid time also goes in `openQuestions`. |

## Status signals

- `excluded`: "excluded", "NIC", "not in contract", "by others", "by GC",
  "by owner", a named item in an exclusions list, a bid-form row with no price.
- `omitted`: not mentioned anywhere. Before recording it, search the whole bid,
  including attachments, for the scope and its synonyms.
- `unknown`: "as required", "per plans" where the plans show options, a scope
  named in the letter but missing from the bid form, a reference to an
  addendum the bid otherwise ignores.
- `included`: the bid says so. Being required by the package doesn't make a
  row included.

## Money

- Cents, integers, signed. Copy amounts from the bid; never round or convert a
  percentage to dollars yourself.
- Bonds, taxes, escalation, delivery, overtime, and permits are conditions, not
  scope and not alternates. Bond and tax go under `basis`. The rest go in
  `qualifications`, quoting any percentage or amount.
- An alternate is a priced change in scope the GC can accept or reject. Match a
  bidder's alternate to a package alternate by scope, not by its number; when
  the scope differs, it belongs in `proposedAlternates`.
- Unit prices are recorded with their unit and never multiplied out.

## Supplier and installer quotes

If the package mixes furnish-only quotes with furnish-and-install quotes, say
which basis the tab assumes. For a furnish-and-install package, record the
supplier's labor rows as `excluded` so the estimator plugs them. To level
suppliers against suppliers instead, use a separate data file.

## Evidence

- `ref` is short and unique within the bid: bidder initials plus a number
  (`NG-4`, `PW-11`).
- `location` lets someone find it fast: `page 2, Exclusions`,
  `sheet Bid Form, row 6`, `email body, paragraph 2`.
- `quote` is copied, trimmed for length, never reworded. For an omission,
  say what was searched and not found.
- Prefer several short quotes over one long one. One quote can support several
  rows.

## Questions

The script writes questions for each bidder from the gaps, missing addenda,
basis items, unpriced alternates, and lines that don't add up. Add to a bid's
`questions` only what it can't derive: a late revision, a drawing date older
than the last addendum, a mismatch between a cover email and its attachment.
Decisions for the estimator go in `openQuestions`.
