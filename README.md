# Buildr construction skills

Construction-specific skills for AI coding agents, written by the
[Buildr](https://buildr.com) team. Each skill is a folder with a `SKILL.md`
in the open [Agent Skills](https://agentskills.io) format, so it works in
Claude Code, Codex, Cursor, and any other agent that reads skills.

Browse the catalog with sample prompts and sample output at
[buildr.com/skills](https://buildr.com/skills).

## Install

Choose a folder install for the complete skill, or copy instructions with the
required resources as described below.

**Skills CLI** (any supported agent):

```bash
npx skills add buildrtech/skills --skill rfp-intake
# or everything
npx skills add buildrtech/skills --all
```

**Claude Code plugin marketplace:**

```
/plugin marketplace add buildrtech/skills
/plugin install all@buildr
```

**Paste into your agent instructions:** open any `skills/<name>/SKILL.md`,
copy everything below the frontmatter into your `CLAUDE.md` or `AGENTS.md`.
Copy the complete skill folder alongside those instructions, including its
references, scripts, assets, and templates, and identify its local path for the
agent. Pasting the body alone does not supply those files or install runtime
dependencies. For chat-only tools without file execution, provide the referenced
text and inputs as attachments; script or PDF workflows still require a runtime.

## Skills

| Skill | Stage | What it does |
|---|---|---|
| [bid-leveling](skills/bid-leveling) | Preconstruction, Estimating | Level sub bids on bid day. See every scope gap, accept or enter plugs, and find out who is really low once the scope matches. |
| [drawing-scope-extraction](skills/drawing-scope-extraction) | Preconstruction, Estimating | Turn drawing sheets into a cited scope list by CSI division, with exclusions, open questions, and review coverage. |
| [proposal-builder](skills/proposal-builder) | Business development, Estimating | Build polished construction proposal PDFs with pdfcn, sourced scope, pricing and qualifications. |
| [rfp-intake](skills/rfp-intake) | Business development, Preconstruction | Turn a solicitation and its addenda into a cited bid/no-bid review with current requirements, risks, and a conditional recommendation. |
| [workforce-planning](skills/workforce-planning) | Workforce, Operations | Prep the staffing meeting: who is overloaded, which jobs have empty seats, who rolls off when, and what changes if you win the pursuits you are chasing. |

The catalog contains five skills. See [ROADMAP.md](ROADMAP.md) for what is next.

## Requirements

Every shipped skill works with documents and data you provide. No Buildr account or connection is required. Check each skill for local tools and dependencies.

## What every skill ships with

- `SKILL.md`: the instructions, under 500 lines, with a `metadata` block that
  drives the catalog (human summary, tier, workflow stages, version).
- `examples/sample-prompts.md`: prompts that should and should not trigger it.
- `samples/`: a synthetic input and the output the skill is expected to
  produce, so you can judge it before installing.
- `references/` and `scripts/` when the skill needs them.

## Contributing

Pull requests are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) and
[docs/skill-spec.md](docs/skill-spec.md) first, then run:

```bash
pip install pyyaml
python3 tools/validate_skills.py
python3 tools/build_catalog.py
python3 tools/validate_marketplace.py
python3 -m unittest discover -s tools/tests -v
```

## Disclaimer

These skills prepare information for people who make construction
decisions. They are not legal, financial, safety, or engineering advice.
Review every output before you rely on it, and never let an agent make
recordability, wage, or contractual determinations on its own.

## License

MIT. See [LICENSE](LICENSE).
