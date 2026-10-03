# Proposal data

Use `samples/input-proposal.json` for the exact JSON shape. Required text fields:
`project`, `client`, `contractor`, `date`, `reference`, `summary`, `currency`.
`status` is `DRAFT` or `FOR REVIEW`; currency is a three-letter ISO code.
Use this template for currencies with two decimal minor units. For currencies
with different precision, adapt both the contract and formatter before rendering.

`scope`, `approach`, `team`, `schedule`, `exclusions`, `questions` are nonempty
arrays of `{text, source}`. Cite supplied documents by filename and page/row.
For an unknown, say what is unknown; `source` identifies the missing source or
the user decision needed. A source field is a trace, not proof: verify its claim.
The executive summary must be supportable by the source inventory too.

`pricing` is an array of `{id, label, kind, cents, source}`. IDs are unique.
`kind` is `base` or `option`. Signed integer cents preserve credits and decimals.
`baseTotalCents` must equal the sum of base rows; options are excluded. The
validator rejects unsafe numbers, duplicate IDs and unreconciled totals. It
does not verify tax treatment or source authenticity. No tax is inferred.

When pricing is not supplied, build an explicitly unpriced draft by adapting
the workspace template; do not populate its required pricing array with zeros.
Keep limitations and terms from the supplied offer, and flag conflicting terms
for human review rather than choosing the most convenient interpretation.
