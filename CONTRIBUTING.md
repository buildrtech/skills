# Contributing

Buildr writes and reviews every skill in this repository. Community pull
requests are welcome and go through the same review.

## Before you open a PR

1. Check [ROADMAP.md](ROADMAP.md) and open issues so you are not duplicating
   a skill in progress. If you want to build a roadmap skill, comment on the
   issue first so we can hand you what we already have.
2. Read [docs/skill-spec.md](docs/skill-spec.md). It covers the required
   files, frontmatter, and writing conventions.
3. Build the skill from a real workflow you run. Skills that are only a
   description of what a workflow should be, with no tested inputs and
   outputs, are declined.

## What a PR needs

- The skill folder under `skills/<name>/` with `SKILL.md`,
  `examples/sample-prompts.md`, and a `samples/` pair (synthetic input and
  expected output). Synthetic means invented. Never include a real
  solicitation, contract, bid, drawing, or customer data.
- `python3 tools/validate_skills.py` and `python3 tools/validate_marketplace.py` pass.
- Run targeted script tests and relevant existing verifier fixture checks.
  Preserve the previous revision and record a bounded fresh-context comparison
  with unfamiliar synthetic inputs; follow the verification section of the spec.
- `python3 tools/build_catalog.py` has been run and `catalog.json` is
  committed.
- If the skill belongs in a plugin group, add it to
  `.claude-plugin/marketplace.json`.
- A short PR description: who the skill is for, the workflow it replaces,
  and how you tested it (which agent, which model, what you fed it).

## Review checklist

Reviewers check for:

- **Grounding.** Every fact the skill produces must trace back to an input.
  Skills that let the agent fill gaps with plausible numbers or dates are sent
  back.
- **Boundaries.** The skill says what it will not do. Anything touching wage
  determinations, OSHA recordability, contract interpretation, or pricing
  needs an explicit human gate.
- **Neutral tier hygiene.** Neutral skills do not mention Buildr. The
  validator enforces this.
- **Portability.** No absolute paths, no assumptions about a specific
  sandbox, no dependencies that are not named in the skill.
- **Size.** `SKILL.md` stays under 500 lines. Detail goes in `references/`.
- **Licensing.** Only content you have the right to license under MIT.
  Vendored third-party skills are not accepted; link to them instead.

## Versioning

Bump `metadata.version` in `SKILL.md` on any change to behavior. Patch for
wording, minor for new capability, major for a change that alters outputs
existing users depend on. Bump `metadata.version` in
`.claude-plugin/marketplace.json` when any skill changes.
