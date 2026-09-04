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
    check_fixtures.py       prove the verifier on known-good, wrong, shortcut, missing
    report.py               table of results across jobs
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
python3 evals/scripts/report.py
harbor view jobs -o evals/jobs   # trajectory viewer
```

Credentials are read from the environment or the local CLI logins; see the
header of `run.sh`. Nothing is printed.

## Writing a task

1. Copy `tasks/pay-app-review/harborview-app3` and fill in `Task.md` first.
2. Inputs must be new synthetic data. The shipped `samples/` inside a skill
   are visible to the agent and cannot be the eval input.
3. Verifier truth comes from a hidden fixture under `tests/fixtures/`, never
   from the memo's own claims.
4. Run `check_fixtures.py` until known-good passes and every wrong, shortcut,
   and missing case fails.
5. Run `nop` and `oracle` through Harbor before any model trial.
