# Leveling model

How `scripts/level_bids.py` turns extractions and estimator decisions into
leveled totals. Read this at step 3 of the workflow, when classifying rows,
and again at step 5 when reviewing the flags.

## The arithmetic

```
leveled total = stated base bid + sum of plugs + sum of adjustments
```

That is all the script computes. Alternates, unit prices, and priced
qualifications are listed beside the totals but never added to them. A
bidder with no stated total has no leveled total. A bidder with any base
row that is not included and not plugged has an **incomplete** leveled
total, and the headline "lowest complete leveled total" ignores it.

## Row classes

Every scope row carries a `row_class`. It defaults to `base`. The class is
set per row, and the first bidder to name a `scope_key` fixes the class for
everyone; a later extraction that classifies the same key differently is
flagged and overridden.

| Class | Use it for | How the script treats it |
|---|---|---|
| `base` | Scope the package requires from every bidder: the GC's scope sheet, the spec sections in the package, and whatever the bids themselves show the trade normally carries (lifts, cleanup, layout). | Printed in the Base scope matrix. Any status other than `included` is a gap. Gaps without a plug make the leveled total incomplete. Plugs apply only here. |
| `outside_scope` | Work a bidder priced inside its total that belongs to a different package: ACT ceilings inside a drywall bid, site concrete inside a foundations bid. | Printed in its own section, never a gap, plugs ignored. Remove the amount with a sourced adjustment on that bidder if the bid itemizes it; if it does not, ask the bidder for the breakout and add a review item. |
| `supplier_or_installer` | Rows that exist only because the package mixes furnish-only quotes with furnish-and-install quotes; see below. | Printed in its own section, never a gap, plugs ignored. |
| `review` | Rows where whether the scope belongs in the package at all is a human decision: an addendum item the GC has not confirmed, a scope split between two packages, a line the estimator wants to see side by side without counting it yet. | Printed in its own section, never a gap, plugs ignored. Promote the row to `base` in the extractions once the decision is made. |

Choose `base` unless there is a stated reason not to. The point of the
other classes is to keep a row visible without letting it move a total.

## Gap signals

A gap is a `base` row whose status for a bidder is anything but
`included`. The extraction records four kinds:

| Status | Signal in the bid | What to do |
|---|---|---|
| `excluded` | "Excluded", "NIC", "not in contract", "by others", "by GC", "by owner", a named item in an exclusions list, a bid form row with no amount and a "by others" note. | Plug it or leave it unresolved. Quote the exclusion in `note`. |
| `omitted` | The bid never mentions the scope, in either direction. Common in email quotes and one-paragraph proposals. | Plug it or leave it unresolved, and add a review item asking the bidder to confirm. Silence is not inclusion. |
| `unknown` | The bid mentions the scope but the wording does not settle whether it is priced ("as required", "per plans" where the plans are ambiguous, a scope named in the body but absent from the itemized form). | Usually leave unresolved and ask the bidder. Plug only if the estimator explicitly decides to. |
| `not_addressed` | Not a status you write; the script assigns it when a base row exists for other bidders but this bidder's extraction has no entry for it. | A flag is raised. Re-read the bid and record the row as included, excluded, omitted, or unknown. |

Other signals the script raises as leveling flags, printed under Review
items:

- **Itemized lines do not sum to the total.** When every included base row
  for a bidder has an amount, the script adds them (plus priced
  qualifications marked `in_total`) and compares to the stated total. A
  mismatch usually means a missing line, an outside-scope item, or a bid
  form arithmetic error. Ask the bidder which number governs.
- **Same bidder in two extractions.** Only the first is used. Merge a
  revised bid into one extraction rather than submitting both.
- **Different trade scopes.** The extractions name different `trade_scope`
  strings. Confirm they belong in one package.
- **No stated total.** The bidder's `total_bid_amount_in_cents` is null.
- **Plug ignored.** The plug targets a non-base row, or a row the bidder
  already includes.
- **Duplicate row in one extraction.** The first entry is kept.

## Plugs

A plug is an amount the estimator adds to one bidder's total so that a gap
in that bid is carried on the same basis as the other bids. Plugs are
recorded in the decisions file, never in the extraction, and never chosen
by the agent.

Rules the script enforces:

- A plug names a `bidder_name` that matches an extraction exactly and a
  `scope_key` that exists in the rows.
- `amount_in_cents` is a non-null integer.
- `source` is non-empty: who decided the amount and where it came from.
  "Estimator (M. Reyes, 8/24) carried Prairie's itemized sheathing line,
  bid form row 6" is a source. "Plug" is not.
- Plugs apply only to `base` rows with a status other than `included`. A
  plug on any other row is ignored and flagged.

Rules the estimator holds to, which the script cannot check:

- A plug is the estimator's judgment about what the missing scope would
  cost this bidder to add, not a market price. Common sources, in the order
  most teams prefer them: another bidder's itemized line for the same
  scope, the GC's own estimate line for that scope, a quote from the trade
  that will actually do it, a historical cost the estimator can name.
- The same gap across two bidders can carry the same plug or different
  plugs; either is fine if each is sourced.
- A plug taken from another bidder's itemized line is a leveling
  convenience, not a statement that the bidder would charge that. Say so
  in the source.
- A gap the estimator does not want to plug yet stays unresolved. An
  incomplete leveled total is an honest result. Do not plug at zero to make
  a total complete.
- Plugs never come from the agent's general knowledge, from averaging bids,
  or from a cost database the user did not name. If the user asks for a
  plug without giving a number, ask for the number and its source.

## Adjustments

An adjustment is a signed amount applied to one bidder's total for a reason
other than a base-row gap. Typical uses:

- Removing work the bidder priced that is outside the package
  (`-4600000` to strip ACT ceilings from a drywall bid).
- Putting bids on a common basis for a priced qualification once the
  estimator decides what that basis is (adding a bond to a bidder that
  excluded it, using the bidder's own stated percentage or amount).
- Correcting a stated arithmetic error the bidder has confirmed in writing.

An adjustment needs `bidder_name`, a non-null signed `amount_in_cents`, a
`description`, and a `source`. Adjustments are not tied to a scope key and
do not resolve gaps; a gap is resolved only by a plug.

## Supplier and installer splits

Some packages draw both furnish-only quotes (a supplier pricing material,
no labor) and furnish-and-install quotes. They cannot be compared until one
side is completed.

- If the package is meant to be furnish-and-install, treat a supplier-only
  quote as a bidder whose labor rows are `excluded`, and plug the labor
  with a sourced amount (an installer's labor-only quote, the GC's
  self-perform takeoff). The leveled total then means "this material plus
  that labor".
- If the package is meant to be split, level suppliers against suppliers
  and installers against installers in two separate runs, and use the
  `supplier_or_installer` class only for rows that appear on one side and
  not the other, so they stay visible without counting as gaps.
- Always say in the output which of these the comparison assumes. A
  supplier's number beside an installer's number with no plug is not a
  comparison.

## Priced qualifications

Bonds, sales and use tax, escalation, delivery, overtime and shift premiums,
permits, and retainage terms are listed in their own table and are never
applied by the script. Leveling them is a two-step decision for the
estimator:

1. Decide the common basis: does every bid carry the bond, or none? Is tax
   in or out? Is escalation a real exposure given the award date?
2. Record the change as an adjustment for each bidder that is off that
   basis, using the bidder's own stated amount or percentage as the source.

Until step 2 is recorded, the table is the answer and the leveled totals do
not include those items.

## How the decisions file overrides

The decisions file is the only input that can change a leveled total beyond
the stated base bid. Its shape:

```json
{
  "plugs": [
    {"bidder_name": "...", "scope_key": "...", "amount_in_cents": 4120000, "source": "..."}
  ],
  "adjustments": [
    {"bidder_name": "...", "amount_in_cents": -4600000, "description": "...", "source": "..."}
  ]
}
```

- Pass it as one of the positional arguments; the script recognizes it by
  the `plugs` or `adjustments` key. More than one decisions file is allowed
  and they are concatenated.
- The decisions file never changes an extraction. Statuses, amounts, and
  evidence stay as extracted; the plug is displayed next to the gap
  ("Excluded; plug $41,200") so the reader sees both.
- If a decision references a bidder or scope key that does not exist, the
  script stops with an error rather than silently dropping it.
- Decisions are dated judgments. When a bidder answers a question and
  includes the scope, update the extraction and remove the plug; do not
  leave a plug on an included row (the script would ignore it and flag it).

`samples/input-estimator-decisions.json` is a worked example against the
three sample extractions.
