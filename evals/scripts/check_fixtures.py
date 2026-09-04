#!/usr/bin/env python3
"""Run a task's verifier on the host against fixture cases before any model trial.

Each case under ``tests/fixtures/cases/<name>/`` describes one workspace the
verifier must score in a known way:

    expect          "pass" or "fail" (pass means reward == 1)
    files           optional; lines of "<src relative to repo>\\t<dest relative to /app>"
    workspace/      optional; files overlaid onto /app

The workspace starts as the task's ``environment/`` directory minus the
Dockerfile, which mirrors what the image copies into /app (for example
``environment/input`` becomes ``/app/input``). A case with neither ``files``
nor ``workspace`` is the "agent wrote nothing" case.

Usage:
    python3 evals/scripts/check_fixtures.py evals/tasks/<skill>/<case> [...]

Requires uv (uses ``uvx --from harbor-rewardkit==0.2.0``).
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


def build_workspace(task: Path, case: Path, ws: Path) -> None:
    env = task / "environment"
    for child in env.iterdir():
        if child.name == "Dockerfile":
            continue
        if child.is_dir():
            shutil.copytree(child, ws / child.name, dirs_exist_ok=True)
        else:
            shutil.copy2(child, ws / child.name)
    (ws / "output").mkdir(exist_ok=True)
    overlay = case / "workspace"
    if overlay.is_dir():
        shutil.copytree(overlay, ws, dirs_exist_ok=True)
    mapping = case / "files"
    if mapping.is_file():
        for line in mapping.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            src, dest = line.split("\t")
            target = ws / dest
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / src, target)


def run_verifier(task: Path, case: Path) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp) / "app"
        ws.mkdir()
        build_workspace(task, case, ws)
        out = Path(tmp) / "reward.json"
        proc = subprocess.run(
            [*REWARDKIT, str(task / "tests"), "--workspace", str(ws), "--output", str(out)],
            capture_output=True,
            text=True,
        )
        if not out.is_file():
            print(proc.stdout)
            print(proc.stderr, file=sys.stderr)
            raise SystemExit(f"verifier wrote no reward for case {case.name}; exit {proc.returncode}")
        return json.loads(out.read_text())


def check_task(task: Path) -> int:
    cases_dir = task / "tests" / "fixtures" / "cases"
    cases = sorted(p for p in cases_dir.iterdir() if p.is_dir()) if cases_dir.is_dir() else []
    if not cases:
        print(f"{task}: no fixture cases under tests/fixtures/cases")
        return 1
    failures = 0
    dims: list[str] = []
    results = []
    for case in cases:
        expect = (case / "expect").read_text().strip()
        r = run_verifier(task, case)
        got = "pass" if r.get("reward", 0) >= 1 else "fail"
        if got != expect:
            failures += 1
        results.append((case.name, expect, got, r))
        for k in r:
            if k not in dims:
                dims.append(k)
    dims = ["reward", "soft_score"] + [d for d in dims if d not in ("reward", "soft_score")]
    print(f"\n{task.relative_to(REPO)}")
    print(f"{'case':40} " + " ".join(f"{d[:8]:>8}" for d in dims) + "  expect")
    for name, expect, got, r in results:
        mark = "ok " if got == expect else "BAD"
        print(f"{name:40} " + " ".join(f"{r.get(d, 0):8.2f}" for d in dims) + f"  {expect:5} {mark}")
    return failures


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    total = 0
    for arg in argv:
        total += check_task(Path(arg).resolve())
    print("\nall fixtures behaved as expected" if not total else f"\n{total} fixture(s) misbehaved")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
