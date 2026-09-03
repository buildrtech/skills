# Leveling model

Read this at phase 3. The leveling model turns evidence records into the
comparison rows that become GC scope line items in Buildr and the bidder
cells that become submission line items. Build it in full and run the gate
at the end before the dry run.

## Structure

```json
{
  "project_id": null,
  "package_id": null,
  "cost_code_id": null,
  "branch_id": null,
  "bidders_by_submission_id": {},
  "base_rows": [],
  "alternate_rows": [],
  "outside_scope_rows": [],
  "review_rows": [],
  "unit_price_rows": [],
  "plugs": [],
  "carry_proposal": []
}
```

The id fields are null until phase 5 fills them from reloaded Buildr
records. Before submissions exist, rows may reference evidence `key` values
for readability, but every executable mapping must be re-keyed by
`submission_id` before the first `vcsUpsertSubmissionLineItems` call.

## Rows

A row is one estimator comparison scope: a distinct piece of work that at
least one bidder prices, excludes, or qualifies separately, or that the GC's
scope sheet lists. Examples in a drywall package: metal stud framing, gypsum
board hang and finish, acoustic insulation, shaft wall, firestopping, lifts
and mobilization.

- Do not make one row per bidder PDF line. Do not make one row per trade.
- Do not collapse itemized scope into a generic row when the evidence or an
  open review question depends on the separate scopes.
- Merge rows only when no bidder prices or excludes them separately and the
  merged row still shows the same included/excluded signal.
- Rows come from `base_rows` only when the scope belongs to the package's
  base comparison. Site work, material-only quotes, options, and scope the
  GC will buy elsewhere go to `outside_scope_rows` or `alternate_rows`.

Each row:

```json
{
  "row_key": "insulation",
  "description": "Acoustic batt insulation in partitions",
  "cost_code_id": null,
  "quantity": 1,
  "uom": "ls",
  "record_id": null,
  "source": "GC scope sheet line 3; all three proposals name it",
  "bidder_mappings_by_submission_id": {
    "<SUBMISSION_ID>": {
      "status": "excluded",
      "amount_in_cents": null,
      "source": "meridian-interiors-proposal.pdf p. 2, 'insulation by others'"
    }
  }
}
```

`record_id` is filled from `vcsCreateLineItems` (or from an existing
compatible row found with `vcsListLineItems`) in phase 5.

## Inclusion status per cell

- `included`: the bidder prices the scope, either as a line (amount present)
  or inside a lump sum (amount null, status included).
- `excluded`: the bidder says the scope is not in the bid.
- `omitted`: the bidder never mentions a scope the comparison requires.
- `unknown`: the wording is ambiguous; carry the quote in `source` and add a
  review row.

Never put an amount on an `excluded` or `omitted` cell. Never change a
status to make a row complete.

## Lump-sum bidders

When a bidder gives only a total, keep the total on the submission and give
every base row a cell with a status and a null amount. Do not allocate the
total across rows, and do not create a single "lump sum" row to hold it.

## Plugs

A plug is an estimator allowance added to a bidder's base total so that a row
they excluded or omitted compares with bidders who included it. Each plug in
`plugs[]` records:

```json
{
  "row_key": "insulation",
  "submission_id": "<SUBMISSION_ID>",
  "amount_in_cents": 1400000,
  "source": "user message: 'use $14,000 for insulation if anyone excludes it'",
  "original_status": "excluded"
}
```

Acceptable sources: the user's stated allowance, a budget line the user
points to, a bid-analysis value the user supplies, a bidder clarification.
Another bidder's line price is not automatically a plug; if the user chooses
to reuse it, record that as the user's decision.

Without a source the row stays at its original status, no plug is recorded,
and the row is listed as an unresolved review item. Missing plugs are not
blockers: persist the source status, finish validation, show the matrix, and
ask for the amount afterward.

## Leveled totals

For each bidder: base total, plus plugs, equals leveled base. Keep base
totals, plugs, alternates, priced qualifications, and leveled totals as
separate figures; never fold an alternate or a qualification into the base.
Mark a leveled total as incomplete when any required row for that bidder is
excluded, omitted, or unknown without a plug.

## Carry proposal

`carry_proposal[]` lists, per row, the bidder whose line the estimate should
carry, with the reason ("low leveled bidder", "only bidder who priced the
row", "user named"). It is a proposal for phase 4; the user decides. Only
rows where the chosen bidder has an `included` cell with an amount can be
carried. A plug cannot be carried, since it is not a bidder's price.

## Gate before the dry run

All of these must hold, or fix the model first:

- Base rows are separate from outside-scope and optional scope.
- Every `alternate_lines` entry in the evidence appears in `alternate_rows`,
  flagged solicited or unsolicited.
- Every excluded or omitted required scope is represented as excluded,
  omitted, plug, or review, with the original status preserved.
- No bidder total stands in for itemized rows when the bid itemized them.
- Every row's bidder mapping will be keyed by `submission_id`; no mapping is
  keyed by company name, file name, or alias.
- Every amount in the model has a source in an evidence record or a
  user-stated allowance.
