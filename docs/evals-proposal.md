# Proposal: an eval suite for the Buildr skills on Harbor

Status: draft for discussion, September 2026. Nothing here is built yet.

## What I looked at

- This repo: nine v1 skills. Every skill ships `examples/sample-prompts.md`
  (trigger and non-trigger prompts) and a `samples/` pair (synthetic input,
  expected output). Four skills ship deterministic scripts
  (`check_pay_app.py`, `level_bids.py`, `scope_list.py`, the template
  `render.mjs` files). Two skills need the Buildr MCP server, which exposes
  only `search` and `execute` code-mode tools.
- Harbor 0.22.0 (`harbor-framework/harbor`). A task is `instruction.md`,
  `task.toml`, `environment/Dockerfile`, `tests/test.sh`, optional
  `solution/solve.sh`. The verifier writes `/logs/verifier/reward.json`.
  Relevant built-ins:
  - Native skill injection: `harbor run --skills ./skills` uploads skill
    folders into the container; the `claude-code` and `codex` agents copy
    them into their skills directories. `environment.skills_dir` does the
    same from the image.
  - Rewardkit (`harbor-rewardkit`): programmatic criteria in Python plus
    LLM or agent judges in TOML, nested into named reward dimensions.
  - `[[environment.mcp_servers]]` registers MCP servers with compatible
    agents, so mock Buildr and mock Procore servers are first class.
  - Simulated user over the ACP bridge (`--user-agent`), target support is
    `claude-code` and `gemini-cli` today.
  - `oracle` runs `solution/solve.sh`; `nop` does nothing. Both are for
    testing verifiers before spending model calls.
  - ATIF trajectories from every built-in agent, so trigger detection can
    read a normalized trajectory instead of vendor logs.
- LangChain `eval-engineering` skill (`langchain-ai/langchain-skills`). It is
  a methodology, not a runner: a human-reviewed `Task.md` beside each Harbor
  task, verifiers built from independent evidence with judges only for
  semantics, a fixed set of verifier fixtures (known-good, alternative valid,
  realistic wrong, shortcut, collateral change, corrupt evidence),
  calibration by reading full trajectories, and a repo-local "World
  Knowledge" skill that accumulates project facts across tasks. Their blog on
  evaluating skills reports 82 percent completion with a skill versus 9
  without on a constrained Claude Code task, and recommends paired
  with-skill and without-skill runs.
- OpenAI Codex team guidance for testing skills: four prompt buckets
  (explicit, implicit, contextual, negative control), trigger rate as a
  metric, JSONL trace checks plus a rubric grader.
- NVIDIA SkillEvaluator / ACES paper: built on Harbor, runs paired
  with-skill and baseline trials and reports "skill lift"; supports Claude
  Code, Codex, OpenCode, and Terminus-2. Worth a look as prior art; it does
  not know construction, so our verifiers still have to be ours.
- How the two chat surfaces consume skills:
  - Claude.ai: custom skills are uploaded as a zip and run inside the
    code-execution sandbox. The API equivalent is the Messages API with the
    `code_execution_20250825` tool and `container.skills` pointing at a skill
    uploaded through `/v1/skills`; inputs go through the Files API and
    produced files come back as file ids. That is a faithful proxy.
  - ChatGPT.com: skills come from the Skills picker, invoked by `@name` or
    implicitly from the description. There is no documented API that runs a
    ChatGPT skill. The closest proxies are the Responses API with the skill
    body as instructions plus the code interpreter tool, or Codex CLI, which
    natively loads `SKILL.md` from `~/.agents/skills`.

## One finding that shapes the design

The skills ship their own expected outputs. A with-skill agent has
`samples/output-review-memo.md` on disk and can copy it. Evaluating on the
shipped samples measures copying, not the skill. The eval inputs therefore
have to be new synthetic cases that live only in the task's hidden verifier
data, and the shipped samples become the oracle smoke test and nothing more.
This also argues for keeping `evals/` outside `skills/`, which the catalog
builder already ignores.

## Agent matrix

Four lanes, each run twice per task: with the skill and without it. The
difference is the skill's lift, which is the number we actually care about.

| Lane | Harbor agent | Skill delivery | Stands in for |
|---|---|---|---|
| Claude Code | `claude-code` (built in) | `--skills ./skills` | Claude Code users |
| Codex CLI | `codex` (built in) | `--skills ./skills` into `~/.agents/skills` | Codex users, nearest scriptable proxy for ChatGPT skill semantics |
| Claude chat | custom `BaseAgent` calling the Messages API with code execution and `container.skills` | skill uploaded once via `/v1/skills`, inputs via Files API | Claude.ai |
| ChatGPT chat | custom `BaseAgent` calling the Responses API with code interpreter | skill body as instructions, references attached as files | ChatGPT.com |

The two chat agents run on the host, not in the container. After the API
conversation ends they write the final assistant message to
`/app/response.md` and any produced files to `/app/output/` in the Harbor
container, then the normal verifier runs. They record token counts and cost
into `AgentContext` and write an ATIF trajectory so the results viewer and
trigger checks work the same way in all four lanes.

Neither chat lane is the real product. Browser automation of Claude.ai or
ChatGPT.com would be brittle and outside their terms, so I am not proposing
it. Instead, a short manual checklist on the real surfaces runs once per
release, using the same hidden cases, and the result is recorded next to the
automated run.

## Task families

Every task follows the eval-engineering layout: `Task.md` (human-reviewed
spec, never copied into the image), `task.toml`, `instruction.md`,
`environment/`, `tests/`, and `solution/solve.sh` where a script can produce
the reference answer.

### A. Outcome tasks, one to three per skill

The instruction is a realistic prompt with input files staged at
`/app/input/`. The verifier recomputes truth from the hidden fixture, never
from the agent's own claims.

| Skill | Hidden fixture | Deterministic checks | Judge checks |
|---|---|---|---|
| pay-app-review | new G702/G703 pair with planted errors | every planted finding appears with the right line, column, and amount; status is hold; cover-sheet math recomputed; memo never says approved | memo sections follow the template; each amount names its source |
| bid-leveling | three new sub bids | leveled totals equal `level_bids.py` on the same extraction; every gap and plug named | scope classification is defensible |
| drawing-scope-extraction | sheet index plus candidates | every scope item cites a sheet or detail that exists in the index; CSI division assignments valid; coverage ledger complete | no invented scope |
| rfp-intake | new solicitation | key dates, bond and insurance thresholds, and required forms match the fixture, each with a page or section citation; scorecard present; contains the not-legal-advice line | risks are grounded |
| rfi-drafter | new conflict description | cites only sheets and spec paragraphs supplied; RFI log row present | proposed resolution is supported or explicitly withheld |
| precon-pdf-templates | budget JSON | data validates against the shipped schema; `render.mjs` output exists and is non-empty; PDF or HTML present | design review notes applied |
| construction-connectors | mock Procore-style MCP server (FastMCP) with a mutation log | plan-and-log produced; mutation log is empty unless the prompt granted approval; every record id cited exists in the mock | plan is safe and sequenced |
| workforce-planning | mock Buildr MCP server with seeded people, assignments, and demand | utilization and bench numbers recomputed from the seed; no `execute` write calls | report follows the template |
| financial-forecasting | mock Buildr MCP server with seeded forecasts and actuals | over and under billing recomputed from the seed; closed-period actuals untouched | narrative matches the numbers |

The shipped `samples/` become `solution/solve.sh` inputs for the oracle run
and a smoke test, not scored cases.

### B. Trigger tasks

All nine skills installed together, as the marketplace `all` plugin does.
Prompts come from each skill's `examples/sample-prompts.md` and are labeled
by the four buckets: explicit, implicit, contextual, negative control. The
verifier reads the ATIF trajectory and records which `SKILL.md` was read.
Metrics are trigger precision and recall per skill and per lane. This is
only automatable in the two CLI lanes and, partially, in the Claude chat
lane (code-execution logs show skill file reads). ChatGPT.com trigger
behavior stays on the manual checklist.

### C. Grounding and boundary tasks

Adversarial variants of the outcome tasks:

- required input missing: the skill should ask once and stop, not invent a
  sample;
- contract terms missing: run the checks that are possible and say which
  were skipped;
- "approve this pay app": produce the review, never approve;
- prompt injection inside an attached document: instructions in the
  document must be treated as data;
- a fabricated-number check: every dollar amount, date, and sheet id in the
  output must appear in the input set or be arithmetic on it.

These use negated judge criteria and deterministic provenance checks, and
they are the tasks where a skill-versus-baseline difference is most likely
to matter for a construction user.

### D. Multi-turn, later

Harbor's simulated user over the ACP bridge lets a second agent play the
estimator who answers the one clarifying question. Target support is Claude
Code only today, so this is a phase 4 item for the ask-once-then-proceed
behavior.

## Verifier design

Rewardkit, with one directory per dimension:

```
tests/
  test.sh                      # uvx --with harbor-rewardkit rewardkit /tests
  reward.toml                  # reward = all-pass(correctness, boundaries); soft_score = weighted mean
  correctness/checks.py        # recompute from hidden fixture
  grounding/checks.py          # provenance of every number and citation
  grounding/judge.toml         # bounded semantic questions only
  boundaries/judge.toml        # negated criteria: never approves, never invents
  format/checks.py             # template sections present
```

Rules carried over from eval-engineering:

- `reward` is the strict all-pass score; `soft_score` exists for diagnosis.
- Judge model pinned in `task.toml` under `[verifier.env]`, credentials from
  the host, never in source.
- Before any model trial, every verifier is run against six fixtures:
  known-good, alternative valid, realistic wrong, shortcut (the shipped
  sample output pasted verbatim), collateral change (a mutation on the mock
  MCP), and corrupt evidence. The last must produce an infrastructure error,
  not a zero.
- Non-agent failures (build, timeout, judge error, credential) are never
  scored.

## Repo layout

```
evals/
  README.md                    # how to run, cost expectations
  harbor_agents/
    claude_chat.py             # Messages API + code execution + container.skills
    chatgpt_chat.py            # Responses API + code interpreter
    common.py                  # write response.md and output/ into the env, ATIF
  fixtures/
    mcp/buildr_mock/           # FastMCP server: search, execute, seeded data, mutation log
    mcp/procore_mock/
    base.Dockerfile            # python 3.12, node, uv, poppler; used by every task
  tasks/<skill>/<case-id>/     # Harbor tasks (Task.md, task.toml, instruction.md, environment/, tests/, solution/)
  configs/
    claude-code.json, codex.json, claude-chat.json, chatgpt-chat.json
    baseline-*.json            # same tasks, no --skills
  scripts/
    report.py                  # reward.json across lanes -> markdown table, skill lift
    check_fixtures.py          # runs the six verifier fixtures per task
  jobs/                        # gitignored run output
.claude/skills/buildr-skills-world/SKILL.md   # World Knowledge skill per eval-engineering
```

Skills are injected at run time from the working tree with
`--skills ./skills`, so a PR that edits a skill is evaluated as edited, and
tasks never vendor a copy.

## Phasing

| Phase | Scope | Exit criterion |
|---|---|---|
| 0 | Install Harbor, base image, one pay-app-review task end to end with `nop`, `oracle`, `claude-code`, `codex`; six verifier fixtures pass | First real trajectory read in full and classified |
| 1 | Outcome tasks for the seven neutral skills, both CLI lanes, with and without skill; `report.py`; nightly job on Modal or Daytona | Skill lift table per skill |
| 2 | `claude_chat` and `chatgpt_chat` agents; rerun phase 1 tasks | Four-lane table; manual checklist written and run once |
| 3 | Trigger suite, mock Buildr and Procore MCP servers, grounding and boundary tasks | Trigger precision and recall per skill; connected skills scored |
| 4 | Simulated-user tasks; PR gate that runs a one-trial subset when `skills/**` changes | Regressions surface on the PR |

Rough size of a full run and what it costs:

| Item | Estimate |
|---|---|
| Tasks | 9 skills x about 3 cases, plus trigger and boundary sets, about 45 |
| Trials per full run | 45 tasks x 4 lanes x 2 conditions x 3 attempts, about 1,080 |
| Cost per full run | roughly $300 to $1,200 depending on models and judge |
| Nightly subset | 1 attempt, CLI lanes only, roughly a tenth of that |

## Decisions I need from you

1. Chat surfaces: accept the API proxies plus a manual release checklist,
   or is a real-surface run required for launch claims?
2. Models per lane for the first table, and the judge. My default is Claude
   Sonnet 5 and the current GPT-5 series for agents, Claude Sonnet 5 as the
   pinned judge, with one cross-vendor judge run to check for bias.
3. Where evals live: this repo under `evals/` (my recommendation, the
   catalog ignores it) or a private repo, given that hidden fixtures and
   `Task.md` would be public here.
4. Whether to trial NVIDIA SkillEvaluator in phase 0 alongside the
   hand-rolled tasks, or skip it.
5. Budget for the nightly job and whether it runs on a cloud sandbox
   provider or a self-hosted Docker runner.

## Sources

- Harbor docs: https://www.harborframework.com/docs, tasks, agents,
  rewardkit, simulated user, `examples/tasks/hello-skills`
- LangChain eval-engineering skill:
  https://github.com/langchain-ai/langchain-skills/tree/main/config/skills/eval-engineering
- LangChain, Evaluating Skills: https://www.langchain.com/blog/evaluating-skills
- OpenAI, Testing Agent Skills Systematically with Evals:
  https://developers.openai.com/blog/eval-skills
- NVIDIA SkillEvaluator: https://github.com/NVIDIA/SkillEvaluator and
  https://arxiv.org/html/2608.20614
- Claude skills API: https://platform.claude.com/docs/en/build-with-claude/skills-guide
- Claude.ai skills: https://support.claude.com/en/articles/12512180-use-skills-in-claude
- ChatGPT and Codex skills: https://learn.chatgpt.com/docs/build-skills
