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
| [rfp-intake](skills/rfp-intake) | Business development, Preconstruction | Neutral | Bid/no-bid intake review of an RFP, ITB, or RFQ: key dates, requirements to bid, scope, risk flags, and a go/no-go scorecard, every fact cited to the document. |

See [ROADMAP.md](ROADMAP.md) for what is coming next.

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
