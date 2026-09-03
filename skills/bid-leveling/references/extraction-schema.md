# Extraction schema

The JSON shape `scripts/level_bids.py` consumes. One file per bidder is the
normal case. The script also accepts an array of extractions, or an object
with a `submissions` array, and tells the files apart by their top-level
keys: an object with `bidder_name` is an extraction; an object with `plugs`
or `adjustments` is a decisions file (see `references/leveling-model.md`).

The script validates every file before it prints anything. If validation
fails it exits with status 2 and lists each problem. Fix the extraction;
do not work around it.

## General rules

- **Cents.** Every money field ends in `_in_cents` and is an integer or
  `null`. `$842,500.00` is `84250000`. `$4.10` per SF is `410`. Never a
  float, never a string, never a rounded dollar figure. Deducts are
  negative integers (`-950000`).
- **`null` means the bid does not state a number.** It never means zero.
  A bidder that includes framing without itemizing it gets
  `"amount_in_cents": null` on that row.
- **Every fact cites evidence.** Each scope row, exclusion, alternate, unit
  price, and priced qualification carries an `evidence_ref` that matches a
  `ref` in the `evidence` array. The script rejects an `evidence_ref` that
  does not resolve. Evidence quotes are copied from the bid, not
  paraphrased.
- **Never invent.** No bidder that did not bid, no amount the bid does not
  state, no scope row the bid or the package scope list does not name. A
  bid that is silent on a scope gets `omitted`, not `included`.
- **Keys line up across bidders.** `scope_key` and `alternate_key` are the
  join keys. Use the same key for the same scope in every extraction
  (`sound_batt` in all three, not `sound_batt`, `insulation`, and
  `batts`). Lowercase, digits, and underscores.

## Top-level fields

All thirteen keys are required. List-valued keys must be lists; use `[]`
when empty, never `null`.

| Field | Type | Meaning |
|---|---|---|
| `bidder_name` | non-empty string | The bidder as named on the bid. This is the join key for plugs and adjustments, so spell it identically in the decisions file. |
| `source_files` | list of strings | File names of the documents the extraction came from, as received (`northgate-proposal.pdf`). Shown in the Summary table. |
| `document_role` | string | What kind of document it is: `bid_proposal`, `bid_form`, `email`, `quote`, or similar. Informational. |
| `trade_scope` | string | The package as the bid describes it, ideally with spec sections. Used as the comparison heading; the script flags extractions whose trade scopes differ. |
| `total_bid_amount_in_cents` | integer or null | The bidder's stated base bid. `null` if the bid does not state one; the script then reports no leveled total for that bidder. |
| `scopes_of_work` | list of scope rows | Scope the bidder includes. |
| `excluded_scopes` | list of scope rows | Scope the bidder excludes, is silent on, or is unclear about. |
| `alternate_lines` | list of alternates | Add, deduct, or replace alternates the bidder priced. |
| `unit_price_lines` | list of unit prices | Unit prices the bidder offered. |
| `priced_qualifications` | list | Money-bearing conditions that are not scope: bonds, taxes, escalation, delivery, overtime, permits. |
| `review_items` | list | Things a human must resolve before the comparison is trusted. |
| `qualifications` | list | Non-priced conditions and assumptions the bidder states. |
| `evidence` | list of evidence entries | The quotes every `evidence_ref` points to. |

## Scope rows (`scopes_of_work` and `excluded_scopes`)

Both lists hold the same object shape. Which list a row sits in decides
which `status` values are allowed.

| Field | Required | Rule |
|---|---|---|
| `scope_key` | yes | Join key across bidders. |
| `scope` | recommended | Human label for the row. The first bidder's label is the one printed; keep labels consistent. Falls back to `scope_key`. |
| `status` | yes in `excluded_scopes`; defaults to `included` in `scopes_of_work` | In `scopes_of_work` the only allowed value is `included`. In `excluded_scopes` it must be `excluded`, `omitted`, or `unknown`. |
| `row_class` | no, defaults to `base` | One of `base`, `outside_scope`, `supplier_or_installer`, `review`. See `references/leveling-model.md`. |
| `amount_in_cents` | no | The itemized amount if the bid gives one for this row; otherwise `null`. Included amounts are displayed, never spread or totaled across bidders. |
| `note` | no | Short explanation, usually the bid's own words: `"Firestopping NIC"`. Printed in the gaps table. |
| `evidence_ref` | recommended | Ref into `evidence`. |

Status meanings:

- `included`: the bid says it is in. A row is not `included` because the
  package requires it; it is `included` because the bid says so.
- `excluded`: the bid says it is out. Signals: "excluded", "NIC", "not in
  contract", "by others", "not included", "by GC", "by owner", a scope row
  on a bid form with no amount and a note like "By others", or an
  exclusions list that names it.
- `omitted`: the bid never mentions it, in either direction. The evidence
  entry for an omission points at the whole document and says what is
  missing (`"No mention of in-wall blocking; no attachment."`).
- `unknown`: the bid mentions it but the wording does not settle whether it
  is priced ("firestopping as required", "insulation per plans" when the
  plans show two kinds). Record the ambiguous quote and add a review item.

A base row that a bidder's extraction does not mention at all is printed as
`Not addressed` and flagged. Do not leave base rows out of an extraction;
put them in `excluded_scopes` with the right status.

## Alternates (`alternate_lines`)

| Field | Required | Rule |
|---|---|---|
| `alternate_key` | yes | Join key across bidders (`alt_1_level5_corridors`). Bidder-proposed alternates get a key prefixed with the bidder (`summit_lift_deduct`) so they do not collide. |
| `label` | recommended | Printed label; the first bidder's label wins. |
| `kind` | yes | `add`, `deduct`, or `replace`. |
| `solicited` | yes | `true` if the bid documents asked for it, `false` if the bidder volunteered it. |
| `amount_in_cents` | yes (may be null) | Signed: deducts are negative. `null` when the bidder offers the alternate but states no price. |
| `evidence_ref` | recommended | Ref into `evidence`. |

An alternate is a priced change to the scope of work that the owner or GC
can accept or reject: a different finish level, a material substitution, a
scope the bidder offers to take on or drop. Alternates are listed and
compared but never applied to leveled totals.

**These are not alternates:** delivery charges, escalation clauses, overtime
or shift premiums, sales or use tax, permit fees, bond premiums, retainage
terms, payment-timing discounts. They are conditions on the price, not
changes to the scope, and they belong in `priced_qualifications`.

## Unit prices (`unit_price_lines`)

| Field | Required | Rule |
|---|---|---|
| `description` | recommended | What the unit price covers. |
| `unit` | recommended | `LF`, `SF`, `EA`, `CY`, `HR`. |
| `unit_price_in_cents` | yes (may be null) | Integer cents per unit. |
| `quantity` | no | Only if the bid states a quantity; otherwise `null`. Never estimate one. |
| `evidence_ref` | recommended | Ref into `evidence`. |

Unit prices are shown for comparison and never multiplied into totals.

## Priced qualifications (`priced_qualifications`)

| Field | Required | Rule |
|---|---|---|
| `description` | recommended | The condition in the bid's words: `"Performance and payment bond, if required, add 1.5% of contract value"`. |
| `amount_in_cents` | yes (may be null) | The dollar figure if the bid states one. Percentages stay in the description and the amount is `null`; do not compute the dollars. |
| `in_total` | no, boolean | `true` when the bid says the amount is already inside the base bid (a bond line on a bid form that the total includes). Omit or `false` otherwise. |
| `evidence_ref` | recommended | Ref into `evidence`. |

Entries with `in_total: true` and a stated amount are added to the itemized
lines when the script checks whether a bid's line items sum to its total.
Nothing else about them is applied.

## Review items and qualifications

Both lists accept objects or plain strings. Objects use `description` (for
`review_items`) or `text` (for `qualifications`) plus an optional
`evidence_ref`, which is printed after the text in parentheses.

- `review_items`: anything that must be settled by a person before the
  comparison is relied on. A total on the cover email that differs from the
  bid form. A quote dated before the last addendum. A bid with no signed
  proposal. An ambiguous scope line marked `unknown`.
- `qualifications`: conditions and assumptions with no direct dollar
  figure. "One mobilization per floor." "Tax included, bond not included."
  "Per drawings dated 7/15." Payment, schedule, and access assumptions go
  here too.

## Evidence (`evidence`)

| Field | Rule |
|---|---|
| `ref` | Short unique tag, conventionally bidder initials plus a number: `NG-1`, `SI-4`, `PW-6`. |
| `source_file` | One of the names in `source_files`. |
| `location` | Where in that file: `page 2, Exclusions`; `sheet Bid Form, row 10`; `email body, paragraph 3`. |
| `quote` | The text as it appears in the bid. Trim for length but do not reword. For an omission, describe what was searched and not found. |

One evidence entry can support several rows. Prefer more, shorter entries
over one entry that quotes a whole page; the reviewer should be able to
find the quote in seconds.

## Minimal example

```json
{
  "bidder_name": "Example Drywall Co.",
  "source_files": ["example-proposal.pdf"],
  "document_role": "bid_proposal",
  "trade_scope": "Division 09 metal framing and gypsum board (09 22 16, 09 21 16)",
  "total_bid_amount_in_cents": 84250000,
  "scopes_of_work": [
    {"scope_key": "metal_stud_framing", "scope": "Non-structural metal stud framing (09 22 16)", "status": "included", "amount_in_cents": null, "evidence_ref": "EX-1"}
  ],
  "excluded_scopes": [
    {"scope_key": "firestopping", "scope": "Firestopping at rated penetrations by this trade", "status": "excluded", "note": "\"Firestopping NIC\"", "evidence_ref": "EX-2"}
  ],
  "alternate_lines": [
    {"alternate_key": "alt_1_level5_corridors", "label": "Alternate 1: Level 5 finish at all corridors", "kind": "add", "solicited": true, "amount_in_cents": 1840000, "evidence_ref": "EX-3"}
  ],
  "unit_price_lines": [],
  "priced_qualifications": [
    {"description": "Performance and payment bond, if required, add 1.5% of contract value", "amount_in_cents": null, "evidence_ref": "EX-4"}
  ],
  "review_items": [],
  "qualifications": [
    {"text": "Sales tax on materials included.", "evidence_ref": "EX-4"}
  ],
  "evidence": [
    {"ref": "EX-1", "source_file": "example-proposal.pdf", "location": "page 1, Scope of Work", "quote": "Furnish and install non-structural metal framing."},
    {"ref": "EX-2", "source_file": "example-proposal.pdf", "location": "page 2, Exclusions", "quote": "Firestopping NIC."},
    {"ref": "EX-3", "source_file": "example-proposal.pdf", "location": "page 2, Alternates", "quote": "Alternate No. 1, Level 5 finish at all corridors: ADD $18,400.00."},
    {"ref": "EX-4", "source_file": "example-proposal.pdf", "location": "page 2, Terms", "quote": "Sales tax included. Performance and payment bond if required add 1.5%."}
  ]
}
```

The three files in `samples/` (`input-extraction-northgate.json`,
`input-extraction-summit.json`, `input-extraction-prairie.json`) are full
worked examples covering a PDF proposal, an email quote, and a spreadsheet
bid form.
