# Skill spec

How skills in this repository are structured and written. The base format is
the open [Agent Skills specification](https://agentskills.io/specification);
this document adds the conventions the validator and catalog rely on.

## Layout

```
skills/<name>/
  SKILL.md                    required
  examples/sample-prompts.md  required
  samples/                    required for v1 skills: input-<x>.md and output-<x>.md
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
  tier: neutral                       # or buildr-connected
  stages: preconstruction, estimating # comma-separated, from the list below
  version: "1.0.0"                    # semver, quoted
  author: Buildr
---
```

The spec only allows string values under `metadata`, which is why `stages`
is a comma-separated string rather than a list.

Allowed `stages` values match the workflow taxonomy on buildr.com/library:
`business-development`, `preconstruction`, `estimating`, `workforce`,
`forecasting`, `operations`, `closeout`.

`tier: neutral` skills must not mention Buildr anywhere in the body. The
catalog adds the product tie-in; the skill stays usable by anyone.

## Body

Keep `SKILL.md` under 500 lines. Use these sections in this order, dropping
any that do not apply:

1. **Title and one-paragraph purpose.** What a human on a precon or project
   team would recognize as the job.
2. **Inputs.** What is required, what is optional, and what to do when
   something is missing. Ask once, plainly, then proceed or stop.
3. **Workflow.** Numbered steps. Read everything before summarizing
   anything. Lead outputs with the finding. Say where each fact came from.
4. **Boundaries.** What the skill will not do. Name the human gates.
5. **Files included with this skill.** One line per bundled file.
6. **Path resolution.** The standard paragraph: relative paths refer to the
   skill directory; never hard-code absolute paths.

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

`samples/` holds a synthetic input named `input-<something>.md` and the
output the skill should produce from it named `output-<something>.md`. These are shown on the catalog page and used as a manual eval.
Synthetic means invented: no real projects, owners, bids, or people. Keep
the input short enough to read in a minute and realistic enough that the
output exercises every section of the skill.

## Catalog

`tools/build_catalog.py` reads every skill's frontmatter, sample prompts, and
sample output into `catalog.json`. The buildr.com site fetches that file at
build time. Commit it with every change; CI checks that it is current.
