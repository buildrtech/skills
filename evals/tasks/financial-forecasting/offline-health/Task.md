# Offline financial forecast evidence

This is an explicitly synthetic fixture replay, not a Harbor task or MCP API
emulator. There was no financial-forecasting task/verifier at baseline 9a62032.
Run `python3 -m unittest discover -s evals/tasks/financial-forecasting/offline-health -v`.
The test invokes the actual bundled CLI and checks independent arithmetic,
missing inputs, undefined denominators, provenance ids, uncapped completion,
and the existing Harbor Street sample arithmetic. It scores no headings.

## Fresh paired evaluation

Completed one baseline and one revised run using `paired-prompt.md`, with
hidden `paired-rubric.md`: 8/8 each. See
`../../../reviews/financial-forecasting/REPORT.md` for provider/settings,
trace evidence and unscored grounding caveats. Only the chosen skill and prompt
were exposed; no live connector or writes. Equivalent formatting is accepted.

Historical margin-bridge and near-miss estimate-email cases were not fresh-run.
The deterministic historical/denominator checks do not prove trigger behavior.
