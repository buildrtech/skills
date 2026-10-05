# Data contract

`scripts/intake.mjs` reads two JSON files: the extraction
(`intake-data.json`, one per opportunity) and the company profile
(`company-profile.json`, reused across runs). `samples/` has a full example of
each.

Money is **integer cents**: `$18,200,000` is `1820000000`. Dates are
`YYYY-MM-DD`, and times are 24-hour `HH:MM` with the time zone the document
states (`CT`).

A **cite** is `{ "doc": "itb", "page": 3, "section": "§3" }`. `doc` must be a
supplied document, and `page` must be within its page count.

## Extraction: `intake-data.json`

| Field | Rule |
|---|---|
| `opportunity` | `name`, `owner`, and `asOf` are required. Optional `number`, `location`, `sector`, `deliveryMethod`, `contract`, and `estimatedValue` (cents), each with a matching `…Cite`. |
| `documents` | `[{ id, title, short?, supplied, pages?, note? }]`. Supplied documents need `pages`. Referenced but missing documents have `supplied: false`. |
| `scope` | `{ text, cite }`: the work in a few sentences. |
| `dates` | `[{ key, label, date, time?, tz?, mandatory?, cite, was? }]`. `bid_due` is required, and `questions_due` is used for the owner questions. `was` holds the superseded `{ date, time?, cite }` when an addendum moved it. |
| `changes` | `[{ item, now, was?, cite, wasCite? }]`: every change made by an addendum. Omit `was` for new requirements. |
| `bonds` | `{ text, performancePercent, cite }`. A performance bond turns on the bonding gate. |
| `insurance` | `[{ key, label, required, cite }]`. `key` matches `profile.insurance`. |
| `licenses` | `[{ key, label, when, cite }]`, where `when` is `bid`, `award`, or `contract`. `key` matches `profile.licenses`. |
| `terms` | `[{ key, label, cite }]`: notable contract terms. A `key` that matches `profile.disqualifyingTerms` fails the gate. |
| `requirements` | `[{ category, text, mandatory?, cite }]`: submission logistics, forms, post-bid deadlines, wage rules, prequalification. `mandatory: true` means the solicitation says a miss is grounds for rejection. |
| `risks` | `[{ title, says, consequence, offset?, cite }]`. |
| `criteria` | `[{ key, score, reason, cite?, profileField? }]`, one per company criterion. `score` is an integer from 0 to 5, or `null` when unknown. A score needs a `cite` or the `profileField` it rests on. |
| `ownerQuestions` | `[{ text, cite }]`: questions to send before the questions deadline. |
| `teamQuestions` | `[{ text }]`: anything the team must answer that the script can't derive. |

Stable keys to reuse across opportunities, so they match the profile:

- **Insurance:** `cgl_occurrence`, `cgl_aggregate`, `auto`, `umbrella`,
  `employers_liability`, `pollution`, `professional`.
- **Licenses:** a jurisdiction and class, e.g. `city-cedar-hollow-class-a`.

## Company profile: `company-profile.json`

| Field | Rule |
|---|---|
| `company` | Required. |
| `asOf` | When the profile was last confirmed. |
| `licenses` | `[{ key, label }]` held. Omit the field when unknown; an empty list means none held. |
| `bonding` | `{ singleLimit, aggregateLimit, currentBonded }`, in cents. |
| `insurance` | `{ key: limitInCents }` for coverages carried. |
| `minDaysToBid` | Days the team needs from intake to bid day. |
| `disqualifyingTerms` | `[{ key, label }]` the company won't accept. |
| `sectors`, `sizeRange`, `selfPerform`, `pastClients` | Context for scoring. Criteria cite these as a `profileField`. |
| `criteria` | `[{ key, label, weight }]`. Omit it to use the defaults below. |
| `thresholds` | `{ go, noGo, maxUnknownWeight }`. Defaults are 65, 45, and 25 (percent of the weight). |

Default criteria and weights: owner and relationship 10; delivery method and
contract 10; schedule and site constraints 15; scope and sector fit 20; size
fit 10; competition 10; risk allocation 15; team and capacity 10.

Scoring guide, for every criterion: 5 is a clear strength, 3 is neutral, 1 is
a serious problem, and 0 means it should be a gate.
