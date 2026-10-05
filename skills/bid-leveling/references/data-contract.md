# Data contract

`scripts/level.mjs` reads one JSON file with three top-level keys: `package`,
`bids`, and `openQuestions`. `samples/bid-data.json` is a full example.

Money is **integer cents** everywhere: `$842,500.00` is `84250000`, `$39.50`
is `3950`, and deducts are negative. `null` means the bid states no number. It
never means zero.

## `package`

| Field | Rule |
|---|---|
| `project`, `name` | Required. `name` is the package, e.g. `09A Metal framing and gypsum board`. |
| `asOf` | Required, `YYYY-MM-DD`. Usually the day you level. |
| `bidDue`, `sections` | Optional, shown in the brief. |
| `scopeSource` | Where the rows came from (`the 09A scope sheet`), or `null` when the rows are the union of what the bids mention. |
| `addenda` | `[{ number, date, summary }]`. Bids that don't acknowledge one are flagged. |
| `rows` | `[{ key, label, class }]`. One row per scope item. `key` is lowercase letters, digits, `-`, or `_`. |
| `alternates` | Alternates the package asked for: `[{ key, label, kind }]`, kind `add` or `deduct`. |
| `basis` | Items every bid should treat the same way: `[{ key, label }]`, usually `bond` and `tax`. |
| `governing` | `{ bidderKey: bidId }` for every bidder that sent more than one submission. The user decides; you record it. |

Row classes:

- `base`: scope the package needs from every bidder. Anything but `included`
  is a gap that needs a plug.
- `outside`: work that belongs to another package (ACT ceilings in a drywall
  bid). Never a gap. When a bid carries it with a price, the script suggests
  an adjustment to remove it.
- `review`: rows where whether the scope belongs in the package is the
  estimator's call. Shown and flagged, never a gap. Change the class to `base`
  once it's decided.

## `bids[]`

| Field | Rule |
|---|---|
| `id` | Required, unique, same key rules as rows. |
| `bidder` | Company name as printed. |
| `bidderKey` | Optional. Give two submissions from the same company the same `bidderKey`; `package.governing` then picks one. |
| `received` | `YYYY-MM-DD`. |
| `files` | The source documents as received. Every evidence entry names one of them. |
| `total`, `totalRef` | The stated base bid in cents and its evidence, or `null` when the bid states no total. |
| `addendaAcknowledged` | Addendum numbers the bid acknowledges, `[]` for none, or `null` when the bid doesn't say. |
| `scope` | `{ rowKey: { status, amount?, note?, ref } }` with an entry for **every** package row. |
| `alternates` | `{ alternateKey: { amount, printedLabel, ref } }` for requested alternates the bid prices. `amount` may be `null` when offered without a price. |
| `proposedAlternates` | `[{ label, kind, amount, ref }]` for alternates the bidder volunteered. Listed, never in totals. |
| `unitPrices` | `[{ description, unit, price, ref }]`. Listed, never multiplied into totals. |
| `basis` | `{ basisKey: { treatment, amount?, percent?, inTotal?, ref } }`. See below. |
| `qualifications` | `[{ text, ref }]` for conditions with no dollar figure: schedule, access, validity, drawing dates. |
| `questions` | `[{ text, ref? }]` for questions the script can't derive, such as a late revision. |
| `evidence` | `[{ ref, file, location, quote }]`. See [extracting bids](extracting-bids.md). |

Scope status:

| Status | Meaning |
|---|---|
| `included` | The bid says it is in. `amount` is the itemized price, or omitted when the bid doesn't itemize it. |
| `excluded` | The bid says it is out: "by others", "NIC", "excluded", a bid-form row with no price. Put the bid's words in `note`. |
| `omitted` | The bid doesn't mention it at all. The evidence says what was searched. |
| `unknown` | The bid mentions it, but the wording doesn't settle whether it's priced. Put the wording in `note`. |

Only `included` rows may carry an `amount`.

Basis treatment:

| Treatment | Use when | Fields |
|---|---|---|
| `included` | The bid says the price includes it. | `amount` and `inTotal: true` when a bid form itemizes it inside the total. |
| `excluded` | The bid says it's not included. | `percent` (e.g. `1.5`) or `amount` when the bid says what it would add. |
| `notStated` | The bid is silent. A missing basis key means the same. | none |

When the estimator carries an item, the script adds the bidder's stated amount,
or its stated percent of the base bid. With neither, the bid stays incomplete
until the estimator enters a figure.

## `openQuestions[]`

`[{ text, source }]`: decisions for the user, each naming the file it came from.

## Scenario

The tab saves the estimator's choices as a scenario. `--scenario` accepts
either the exported file (`{ "format": "bid-tab", "scenario": ... }`) or the
bare scenario:

```json
{
  "plugs": { "northgate:sheathing": { "amount": 4120000, "source": "...", "kind": "accepted" } },
  "adjustments": [{ "bid": "prairie", "amount": -4600000, "description": "...", "source": "..." }],
  "alternates": { "alt1_level5_corridors": true },
  "basis": { "bond": "carry" },
  "basisEntries": { "summit:bond": { "amount": 1200000, "source": "..." } },
  "governing": { "ridgeline": "ridgeline-rev" }
}
```

Plugs are keyed `bidId:rowKey` and must target a gap on a `base` row. Every
plug, adjustment, and basis entry needs a source. `kind` is `accepted` for a
suggestion the estimator accepted and `entered` for their own figure.
