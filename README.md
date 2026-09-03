# Buildr construction skills

Construction-specific skills for AI coding agents, written by the
[Buildr](https://buildr.com) team. Each skill is a folder with a `SKILL.md`
in the open [Agent Skills](https://agentskills.io) format, so it works in
Claude Code, Codex, Cursor, and any other agent that reads skills.

Browse the catalog with sample prompts and sample output at
[buildr.com/skills](https://buildr.com/skills).

## Install

Pick whichever fits your setup. All three install the same files.

**Skills CLI** (any supported agent):

```bash
npx skills add buildrtech/skills --skill rfp-intake
# or everything
npx skills add buildrtech/skills --all
```

**Claude Code plugin marketplace:**

```
/plugin marketplace add buildrtech/skills
/plugin install precon@buildr
```

**Paste into your agent instructions:** open any `skills/<name>/SKILL.md`,
copy everything below the frontmatter into your `CLAUDE.md` or `AGENTS.md`.
Skills that ship `references/` or `scripts/` work best installed as folders,
but the body alone is enough for most of them.

## Skills

| Skill | Stage | Tier | What it does |
|---|---|---|---|
| [rfp-intake](skills/rfp-intake) | Business development, Preconstruction | Neutral | Run a bid/no-bid intake review on an RFP or bid invitation. |
| [bid-leveling](skills/bid-leveling) | Preconstruction, Estimating | Neutral | Level subcontractor bids for one trade package into a bid tab or bid comparison matrix. |
| [drawing-scope-extraction](skills/drawing-scope-extraction) | Preconstruction, Estimating | Neutral | Extract a scope of work from a construction drawing set, grouped by CSI division, with every item cited to a sheet, detail, or note. |
| [precon-pdf-templates](skills/precon-pdf-templates) | Business development, Preconstruction, Estimating | Neutral | Produce polished PDFs for general contractor and preconstruction workflows from bundled HTML templates and themes. |
| [rfi-drafter](skills/rfi-drafter) | Operations, Preconstruction | Neutral | Draft a Request for Information (RFI) for a general contractor from a described drawing or specification conflict, citing the sheets, details, and spec paragraphs the user provides, proposing a resolution when the documents support one, and producing an RFI log row. |
| [pay-app-review](skills/pay-app-review) | Operations, Forecasting | Neutral | Check a contractor's or subcontractor's progress payment application (AIA G702/G703-style application and continuation sheet, or any schedule-of-values billing) for math, continuity, retainage, change order, and stored materials problems, then prepare a review memo with a hold/release list for a human decision. |
| [construction-connectors](skills/construction-connectors) | Operations, Preconstruction, Estimating | Neutral | Work safely and accurately over construction software MCP servers and connectors (project management, cost, drawings, takeoff, BIM). |
| [bid-leveling-buildr](skills/bid-leveling-buildr) | Preconstruction, Estimating | Buildr-connected | Level subcontractor bids and persist the result into Buildr through the Buildr MCP server, including the bid package, bidders, submissions, GC scope line items, submission pricing, alternates, and carry selections on a reviewable change-request branch. |
| [workforce-planning](skills/workforce-planning) | Workforce, Forecasting | Buildr-connected | Analyze and plan construction workforce staffing over Buildr workforce data through the Buildr MCP server. |
| [financial-forecasting](skills/financial-forecasting) | Forecasting, Operations | Buildr-connected | Analyze Buildr financial forecasts through the Buildr MCP server. |

All ten v1 skills have shipped. See [ROADMAP.md](ROADMAP.md) for what is next.

## Tiers

- **Neutral** skills work with whatever documents and data you hand the
  agent. They never require a Buildr account and never mention Buildr.
- **Buildr-connected** skills read and write Buildr data through the Buildr
  MCP server. They are marked in the catalog and in each skill's
  `metadata.tier`.

## What every skill ships with

- `SKILL.md`: the instructions, under 500 lines, with a `metadata` block that
  drives the catalog (tier, workflow stages, version).
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
```

## Disclaimer

These skills prepare information for people who make construction
decisions. They are not legal, financial, safety, or engineering advice.
Review every output before you rely on it, and never let an agent make
recordability, wage, or contractual determinations on its own.

## License

MIT. See [LICENSE](LICENSE).
