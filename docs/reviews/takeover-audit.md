# Skills architecture audit — 2026-09-07

Baseline: `9a62032a237cd7588f6f6c687021acc076cd6fb7` (`evals/harbor-phase-0`).
Both full T3 histories and the takeover handoff were read before revision.
Old files remain retrievable with `git show 9a62032:<path>`; an execution copy
is at `/tmp/skills-takeover-baseline-9a62032` for paired local evaluation.

## Contract and findings

Exactly nine skills remain: seven neutral, two connected (financial-forecasting
and workforce-planning). Connected bid leveling stays removed. Catalog v2 and
all three installation choices remain; instruction paste alone cannot deliver
required references, assets, or scripts.

The existing folders provide useful domain rules, samples, and deterministic
scripts. Shared guidance currently over-prescribes heading order, calls samples
manual evals without distinguishing leakage, and lacks an explicit behavior
comparison requirement. Validation checks frontmatter and size but not the
promised sample pair; CI only checks manifest paths exist, not complete coverage.
These are shared changes justified by source inspection.

Six Harbor outcome tasks already exist. Historical results are evidence, not a
current rerun: pay-app 4/4 per skill lane; RFI, bid, drawing 3/3; PDF Claude 3/3,
Codex 0/3; RFP Claude 2/3, Codex 0/3. PDF renderer/theme and RFP recommendation
completeness warrant targeted investigation. Heading or template adherence must
be scored separately from correctness unless the user explicitly requires that
contract. Verifier changes require a valid rejected example and a retained
substantive negative control.

Bid identity and printed-alternate reconciliation are priority script defects.
Connected workflows need honest fixture replay and missing-connection behavior;
no synthetic result establishes live MCP compatibility or authorizes writes.

## Review method and ownership

Coordinator owns README, CONTRIBUTING, docs, tools, manifests, catalog and shared
eval integration. Each of nine child threads owns only `skills/<name>/` and
`evals/tasks/<name>/` plus `evals/reviews/<name>/`. Workers do not commit.
Each reads all its resources and prior task evidence, improves actual files,
runs meaningful scripts/tests, and records old-versus-new evidence and limits.
Heavy model evaluations require coordinator scheduling; no broad matrix.
Fresh behavior evaluations use unfamiliar synthetic input with hidden expected
results, independent context and a bounded paired comparison. Samples remain
smoke tests. No production writes, pushes, merges, global skill edits or marketing
snapshot edits occur in this worktree.

## Authoring sources

- https://agentskills.io/specification
- https://agentskills.io/skill-creation/best-practices
- https://agentskills.io/skill-creation/evaluating-skills
- Local writing-great-skills and BB skill-creator guidance

Apply coherent scope, discriminating descriptions, conditional reference reads,
checkable completion, and tested scripts where fragile arithmetic or rendering
requires determinism. Keep precise domain constraints; prune repeated generic
instructions. Record observations before optimizing prompts or graders.

## Shared revisions and evidence

- Required `metadata.summary` separates a human outcome sentence (200 characters
  maximum) from agent trigger `description`; catalog v2 emits `summary` without
  a fallback. This follows root's browser finding that trigger prose obscures
  outcomes. All nine owners author their own sentence.
- Folder/paste installation copy now describes missing resources and execution
  dependencies honestly. Authoring guidance uses completion contracts and
  conditional resource pointers rather than prescribed headings.
- Validator now checks input/output sample presence in the appropriate format;
  marketplace validation checks known paths, duplicates, and complete `all`
  membership. Catalog does not invent an `all` install command for an unlisted
  skill. CI runs these checks plus shared unit tests.
- Verified five shared PR findings against the actual code: optional `--` was
  consumed as a task path; forwarded args were logged; inherited force-auth
  flags overrode API-key intent; artifact copy followed links; trial JSON was
  overwritten in place. Fixed parsing/logging/auth precedence, reject artifact
  symlinks before verification (preserving them would permit verifier reads),
  and atomically replace completed JSON. Runner concurrency defaults to one.
- Ten local shared tests pass with PyYAML in an isolated temporary venv. The
  runner tests use a recording executable to inspect the process boundary;
  these tests prove wrapper arguments/environment, not Harbor integration.
  Atomic-write failure and directory/file/dangling symlink cases use real files.
- Fresh behavior schedule: exactly one baseline and one revised run per skill,
  sequential per pair, at most two evaluator threads active. No broad matrix or
  chat-surface claims. Skill review workers are the nine direct child threads;
  independent evaluator threads are their children.

## Skill worker registry

All nine direct children use project `proj_sxhtrh8yts`, environment
`env_9qgefd7zm7`, parent `thr_hpvpiweaze`.

| Skill | Child thread |
|---|---|
| bid-leveling | `thr_kefaywjbew` |
| construction-connectors | `thr_r2pnqxusb4` |
| drawing-scope-extraction | `thr_hxa96szkr5` |
| financial-forecasting | `thr_qat4v7xjpq` |
| pay-app-review | `thr_enucp8t8e3` |
| precon-pdf-templates | `thr_mtamhw7f8u` |
| rfi-drafter | `thr_tvachgvz9u` |
| rfp-intake | `thr_4wnqeue5ke` |
| workforce-planning | `thr_gm9p2zc9t4` |

## Reproducing preserved baseline files

The Git object is the durable baseline; `/tmp` execution copies may expire.
To reconstruct an isolated copy without changing this checkout:

```sh
baseline_dir=$(mktemp -d /tmp/skills-baseline-9a62032.XXXXXX)
git archive 9a62032 skills evals | tar -x -C "$baseline_dir"
```

Pass that root to replay tools that accept a baseline override. Reports retain
original commands and hashes so a reconstruction can be checked before use.
Full fresh-thread transcripts live at the thread-storage paths recorded in
per-skill reports; bounded task inputs, artifacts and grading evidence are in
`evals/reviews/`. Historical/fresh scores describe the verifier revision used
and are not interchangeable.
