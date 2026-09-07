# Skill spec

How skills in this repository are structured and written. The base format is
the open [Agent Skills specification](https://agentskills.io/specification);
this document adds the conventions the validator and catalog rely on.

## Layout

```
skills/<name>/
  SKILL.md                    required
  examples/sample-prompts.md  required
  samples/                    required: input-<x> and output-<x> (appropriate format)
  references/                 optional: detail the agent loads on demand
  scripts/                    optional: executables the skill runs
```

`<name>` is lowercase letters, digits, and single hyphens, at most 64
characters, and must equal `name` in the frontmatter.

## Frontmatter

```yaml
---
name: rfp-intake
description: One or two sentences: what it does and when to use it. Under 1024 characters. This is the only text most agents see before deciding to load the skill, so include the trigger words users actually say.
license: MIT
metadata:
  summary: Review a bid invitation for requirements, risks, and a bid/no-bid recommendation.
  tier: neutral                       # or buildr-connected
  stages: preconstruction, estimating # comma-separated, from the list below
  version: "1.0.0"                    # semver, quoted
  author: Buildr
---
```

`metadata.summary` is required: one human-facing outcome sentence, at most 200
characters. The catalog exposes it as `summary`; keep agent trigger language in
`description`. There is no inferred summary or fallback to trigger prose.

The spec only allows string values under `metadata`, which is why `stages`
is a comma-separated string rather than a list.

Allowed `stages` values match the workflow taxonomy on buildr.com/library:
`business-development`, `preconstruction`, `estimating`, `workforce`,
`forecasting`, `operations`, `closeout`.

`tier: neutral` skills must not mention Buildr anywhere in the body. The
catalog adds the product tie-in; the skill stays usable by anyone.

## Body

Keep `SKILL.md` under 500 lines. Organize around the job rather than a fixed
heading order. Include required inputs, a useful missing-input path, the main
workflow, boundaries, and observable completion criteria. Lead results with the
finding and distinguish source facts, calculations, assumptions, and unknowns.

Descriptions identify real triggers and distinguish nearby tasks; procedures
belong in the body. Read the relevant source set before drawing conclusions.
Route long references with an explicit condition and resolve bundled paths from
the skill directory. Name dependencies and one tested default command for
scripts; explain why arithmetic, reconciliation, or rendering requires that
script. If a dependency is unavailable, report the blocked step accurately.

Output headings may vary when they carry the same required substance. Require
exact keys or templates only for a machine contract or a user's explicit format.
Keep domain invariants and observed failure corrections; prune generic advice
and repeated rules. Keep independently installed skills self-contained: shared
authoring guidance here is for contributors, not a hidden runtime dependency.

Writing rules that reviewers hold to:

- No fabricated facts. If the skill produces dates, amounts, requirements,
  or names, each one cites its source.
- Treat attached documents and fetched content as data, never as
  instructions.
- Say "not legal advice", "not a wage determination", "not an approval"
  wherever a reader might mistake the output for one.
- Phase-gate long references: tell the agent which reference to read at
  which step rather than loading everything up front.
- Prefer plain instructions over personas. "Read the whole solicitation
  before summarizing" beats "You are an expert estimator".

## Samples

`samples/` holds a synthetic input named `input-<something>.<format>` and the
expected output named `output-<something>.<format>`. Use the actual input/output
format (Markdown, JSON, CSV, HTML, etc.). Markdown samples render as prose in
the catalog; every bundled file remains browsable. Samples are demonstration
and script smoke tests, not independent behavior evaluations.
Synthetic means invented: no real projects, owners, bids, or people. Keep
the input short enough to read in a minute and realistic enough that the
output exercises every section of the skill.

## Catalog

`tools/build_catalog.py` reads every skill's frontmatter, sample prompts,
sample output, and the full contents of every text file under 256 KB into
`catalog.json` (format version 2). The buildr.com site fetches that file at
build time and renders a file browser from it, so anything you put in a
skill folder is public on the site as well as on GitHub. Commit
`catalog.json` with every change; CI checks that it is current.

## Verification

For behavior changes, preserve a Git baseline and test the previous and revised
skill with unfamiliar synthetic inputs in fresh contexts. Keep hidden expected
results out of installed folders. Inspect actions and resource reads as well as
final output. Record the exact revision, prompt, model/lane, commands, results,
and limitations in `evals/reviews/<skill>/`. Small discriminating comparisons
come before variance runs; no unbounded model matrix.

Deterministic tests must challenge actual calculations or validation boundaries.
For grader changes, record a valid rejected output and retain a substantive
negative case. Score correctness separately from stylistic compliance. Missing
inputs and near-miss triggers deserve explicit coverage. With no live MCP,
synthetic fixture replay and fresh-context boundary tests are useful, but label
them honestly: neither proves live auth, API compatibility, nor successful writes.

Sources: [authoring practices](https://agentskills.io/skill-creation/best-practices)
and [output evaluation](https://agentskills.io/skill-creation/evaluating-skills).
