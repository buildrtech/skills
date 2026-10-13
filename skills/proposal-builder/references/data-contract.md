# Data contract

`proposal.json` drives both the PDF (`render.tsx`) and the compliance check
(`scripts/check.mjs`). Both run the same validator, `proposal-core.mjs`, and
refuse to run on a problem. `samples/proposal.json` is a full example.

Money is **integer cents**. Dates are `YYYY-MM-DD`. A **source reference** is
`{ "id": "rfp", "page": 4, "section": "§4" }`. `id` must be in `sources`, and
`page` must be within that source's page count when one is given.

## `meta`

| Field | Rule |
|---|---|
| `project`, `client`, `proposer`, `reference` | Required text. |
| `date` | The draft date. Staleness is measured from it. |
| `status` | `DRAFT` (source lines print in the PDF) or `FOR REVIEW` (source lines hidden). |
| `currency` | An ISO code with two decimal places. Others are rejected rather than rounded. |
| `kicker`, `summary` | Cover eyebrow and lead. |
| `freshnessMonths` | How old a library entry or prior proposal can be before it's flagged. Default 12. |

## `sources`

`[{ id, kind, title, short?, date, pages? }]`

| `kind` | What | `date` means |
|---|---|---|
| `rfp` | The RFP and addenda | Issue date |
| `library` | A file in `company-library/` | When it was last verified |
| `prior` | A prior proposal | When it was written |
| `user` | Something the user said or sent for this proposal | When they said it |

## `rfp`

| Field | Rule |
|---|---|
| `title`, `number` | The RFP as named on its cover. |
| `requirements` | `[{ id, kind, text, points?, source }]`, where `kind` is `submittal`, `criterion`, `question`, or `format`. List every one the RFP states. |
| `forms` | `[{ id, name, included, section?, source }]`. `included: true` needs the `section` it sits in. |
| `pageLimit` | `{ max, excludes, source }`. `excludes` lists section kinds or ids the RFP leaves out of the count. The cover never counts. |

## `facts`

`[{ key, label, value, asOf, source }]`: values that can differ between sources
(EMR by year, a project's value, a completion date). Record one per source
that states it. Items that use a fact list its `key` in `facts`, and must
cite the source of the value they use.

## `sections`

In the RFP's required order. Each section starts on a new page.

| Field | Rule |
|---|---|
| `id`, `title` | Unique id. The title must appear on the page, because the check finds sections by their titles. |
| `kind` | `letter`, `narrative`, `projects`, `team`, `schedule`, `fee`, `forms`, `matrix`, or `appendix`. |
| `tab` | The RFP's label for it, e.g. `Tab B`. |
| `lead` | Optional one or two lines under the title. |
| `answers` | Requirement ids this section answers. |
| `items` | `[{ text, source, alsoFrom?, title?, group?, fields?, facts?, confirmed? }]`. Required except for `fee`, `forms`, and `matrix`. |

How each kind renders:

- `projects` and `team`: cards with a `title` and `fields` (short label/value
  text). Long values span the full width.
- `narrative` and `schedule`: numbered lists, grouped under consecutive `group`
  headings.
- `letter`: paragraphs, with an unsigned signature line.
- `forms`: a checklist of `rfp.forms`.
- `matrix`: the compliance matrix as an appendix.

`confirmed: true` marks a claim from a prior proposal that the user has
confirmed is still true.

## `fee`

- `{ "status": "unpriced", "note": "what is missing" }` when the fee isn't
  known. Never use zeros.
- `{ "status": "priced", "lines": [...], "totalCents": n }`, where each line
  is `{ id, label, basis, cents | percent, of?, option?, note?, source }`.
  - `basis` is `lump` (positive cents) or `percent` (with `of`, e.g. "the Cost
    of the Work").
  - `totalCents` must equal the lump-sum lines that aren't options.
  - Percentages are never added to the total.

## `questions`

`[{ text }]`: decisions or material the user must supply. They go in the
compliance check, not the PDF.
