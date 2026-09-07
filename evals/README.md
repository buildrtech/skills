# Skill evals

Harbor tasks that score the skills in `skills/` when run by real agents.
Design notes are in `docs/evals-proposal.md`. This directory is not part of
the catalog; `tools/build_catalog.py` only reads `skills/`.

## Layout

```
evals/
  tasks/<skill>/<case>/     one Harbor task per case
    Task.md                 human-reviewed spec and hidden truth (never in the image)
    task.toml               Harbor config
    instruction.md          exact agent input
    environment/            Dockerfile and agent-visible input files
    tests/                  rewardkit verifier: test.sh, reward.toml, one dir per dimension
    solution/               oracle path and the known-good reference output
  scripts/
    run.sh                  run one task in one lane and condition
    check_fixtures.py       prove the verifier on the cases under tests/fixtures/cases
    report.py               table of results across jobs (--cells for per-cell means)
  jobs/                     run output (gitignored)
```

## Lanes and conditions

| Lane | Harbor agent | Skill delivery |
|---|---|---|
| `claude-code` | built in | `--skills ./skills` copied into Claude's skills dir |
| `codex` | built in | `--skills ./skills` copied into `~/.agents/skills` |
| `oracle` | built in | runs `solution/solve.sh`; proves the reference scores 1 |
| `nop` | built in | does nothing; proves an empty workspace scores 0 |

Every task runs in two conditions: `with-skills` (all nine skills injected,
mirroring the marketplace `all` plugin) and `baseline` (no skills). The
difference is the skill's lift.

## Run

```bash
uv tool install harbor            # 0.20.0 or later
python3 evals/scripts/check_fixtures.py evals/tasks/pay-app-review/harborview-app3
evals/scripts/run.sh nop with-skills
evals/scripts/run.sh oracle with-skills
evals/scripts/run.sh claude-code with-skills
evals/scripts/run.sh claude-code baseline
evals/scripts/run.sh codex with-skills
evals/scripts/run.sh codex baseline
ATTEMPTS=3 evals/scripts/run.sh claude-code with-skills   # variance: 3 trials in one job
python3 evals/scripts/report.py            # one row per trial
python3 evals/scripts/report.py --cells    # mean and sd per task x lane x condition
harbor view jobs -o evals/jobs   # trajectory viewer
```

`CONCURRENCY` defaults to 1; increase it only within an agreed evaluation budget.
`ATTEMPTS` defaults to 1. Extra Harbor arguments follow `--`, with or without
an explicit task path. Wrapper diagnostics omit arguments because they can
contain credentials. API keys take precedence over inherited force-login flags.

Credentials are read from the environment or the local CLI logins; see the
header of `run.sh`. Nothing is printed.

## Writing a task

1. Copy `tasks/pay-app-review/harborview-app3` and fill in `Task.md` first.
2. Inputs must be new synthetic data. The shipped `samples/` inside a skill
   are visible to the agent and cannot be the eval input.
3. Verifier truth comes from a hidden fixture under `tests/fixtures/`, never
   from the memo's own claims.
4. Add cases under `tests/fixtures/cases/<name>/` (an `expect` file saying
   pass or fail, plus a `workspace/` overlay or a `files` mapping of
   repo-relative sources to /app paths). Every task needs at least
   `known-good`, `shortcut-shipped-sample`, one `wrong-*`, and `missing`.
   Run `check_fixtures.py` until every case behaves.
5. Run `nop` and `oracle` through Harbor before any model trial.

## Reviewing revisions

Keep the six existing task families and their hidden fixtures. Compare revisions
against a preserved Git baseline with unfamiliar inputs; see
[the authoring spec](../docs/skill-spec.md#verification). Existing samples are
smoke tests, not proof of skill lift. A fresh-thread result is not a ChatGPT.com
or Claude.ai UI test. Synthetic MCP replay is not live integration proof.

Rescoring rejects symlink artifacts before invoking a verifier, and replaces the
trial result atomically after serialization. Run shared regression checks with
`python3 -m unittest discover -s tools/tests -v`.
