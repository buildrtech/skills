#!/usr/bin/env python3
"""Run a task's verifier on the host against fixture outputs before any model trial.

For each fixture it builds a temporary workspace that mirrors /app (the
task's environment/input plus the fixture memo at output/review-memo.md),
runs rewardkit on the task's tests/ directory, and checks the reward
against the expectation.

Usage:
    python3 evals/scripts/check_fixtures.py evals/tasks/pay-app-review/harborview-app3

Requires uv (uses `uvx --from harbor-rewardkit==0.2.0`).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REWARDKIT = ["uvx", "--from", "harbor-rewardkit==0.2.0", "python", "-m", "rewardkit"]


def run_verifier(task: Path, memo: str | None) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp) / "app"
        shutil.copytree(task / "environment" / "input", ws / "input")
        (ws / "output").mkdir()
        if memo is not None:
            (ws / "output" / "review-memo.md").write_text(memo, encoding="utf-8")
        out = Path(tmp) / "reward.json"
        proc = subprocess.run(
            [*REWARDKIT, str(task / "tests"), "--workspace", str(ws), "--output", str(out)],
            capture_output=True,
            text=True,
        )
        if not out.is_file():
            print(proc.stdout)
            print(proc.stderr, file=sys.stderr)
            raise SystemExit(f"verifier wrote no reward for fixture; exit {proc.returncode}")
        return json.loads(out.read_text())


def fixtures(task: Path) -> dict[str, tuple[str | None, str]]:
    """name -> (memo text or None, expected: 'pass' | 'fail')."""
    good = (task / "solution" / "reference-memo.md").read_text(encoding="utf-8")
    shipped = (REPO / "skills" / "pay-app-review" / "samples" / "output-review-memo.md").read_text(encoding="utf-8")
    approving = good.replace(
        "**Status:** Recommend hold for review",
        "**Status:** No exceptions found in the checks run",
    ) + "\n\nBased on the above, payment is approved for $562,365.00.\n"
    arithmetic_only = good.split("## Findings the script cannot make")[0] + (
        "\n## Items on hold for a human decision\n\n| # | Item | Line / column | Amount in question | Source | What would clear it |\n|---|---|---|---|---|---|\n"
        "| 1 | Column D overstated | G703 line 04 | $3,500.00 | script | corrected D |\n"
        "\n## Sources\n\nThis memo prepares a review and is not an approval, certification, or rejection of payment, not legal advice, and not a wage determination.\n"
    )
    return {
        "known-good (reference memo)": (good, "pass"),
        "shortcut (shipped sample memo pasted)": (shipped, "fail"),
        "wrong (approves payment)": (approving, "fail"),
        "wrong (arithmetic only, no manual findings)": (arithmetic_only, "fail"),
        "missing (no memo written)": (None, "fail"),
    }


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    task = Path(argv[0]).resolve()
    failures = 0
    print(f"{'fixture':48} {'reward':>7} {'soft':>6} {'corr':>6} {'bound':>6} {'fmt':>6} {'grnd':>6}  expect")
    for name, (memo, expect) in fixtures(task).items():
        r = run_verifier(task, memo)
        got = "pass" if r.get("reward", 0) >= 1 else "fail"
        mark = "ok " if got == expect else "BAD"
        if got != expect:
            failures += 1
        print(
            f"{name:48} {r.get('reward', 0):7.2f} {r.get('soft_score', 0):6.2f} "
            f"{r.get('correctness', 0):6.2f} {r.get('boundaries', 0):6.2f} "
            f"{r.get('format', 0):6.2f} {r.get('grounding', 0):6.2f}  {expect:5} {mark}"
        )
    print("\nall fixtures behaved as expected" if not failures else f"\n{failures} fixture(s) misbehaved")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
