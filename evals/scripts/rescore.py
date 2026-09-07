#!/usr/bin/env python3
"""Re-run the current verifier on each trial's saved /app/output artifact.

Use after tightening or loosening a task's verifier so every trial in
evals/jobs is scored the same way. Rewrites verifier/reward.json,
verifier/reward-details.json, and the rewards in result.json for trials
that have an artifacts/app directory; records `rescored_at` in result.json.

Usage:
    python3 evals/scripts/rescore.py [jobs-dir] [--task <substring>]
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REWARDKIT = ["uvx", "--from", "harbor-rewardkit==0.2.0", "python", "-m", "rewardkit"]


def reject_links(root: Path) -> None:
    """Artifacts are untrusted: do not copy or let verifiers follow symlinks."""
    if root.is_symlink():
        raise ValueError(f"symlink is not allowed: {root}")
    for current, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            path = Path(current) / name
            if path.is_symlink():
                raise ValueError(f"symlink is not allowed: {path}")


def atomic_json(path: Path, data: dict) -> None:
    """Keep the prior record intact until a complete replacement is ready."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def rescore(trial_dir: Path) -> dict | None:
    result_path = trial_dir / "result.json"
    art = trial_dir / "artifacts" / "app"
    if not result_path.is_file() or not art.is_dir():
        return None
    data = json.loads(result_path.read_text())
    task_path = Path(((data.get("config") or {}).get("task") or {}).get("path") or "")
    if not task_path.is_absolute():
        task_path = REPO / task_path
    if not (task_path / "tests").is_dir():
        return None
    reject_links(art)
    reject_links(task_path / "environment")
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp) / "app"
        ws.mkdir()
        for child in (task_path / "environment").iterdir():
            if child.name == "Dockerfile":
                continue
            if child.is_dir():
                shutil.copytree(child, ws / child.name, dirs_exist_ok=True)
            else:
                shutil.copy2(child, ws / child.name)
        shutil.copytree(art, ws, dirs_exist_ok=True)
        out = Path(tmp) / "reward.json"
        subprocess.run(
            [*REWARDKIT, str(task_path / "tests"), "--workspace", str(ws), "--output", str(out)],
            capture_output=True,
            text=True,
        )
        if not out.is_file():
            return None
        rewards = json.loads(out.read_text())
        vdir = trial_dir / "verifier"
        vdir.mkdir(exist_ok=True)
        shutil.copy2(out, vdir / "reward.json")
        details = Path(tmp) / "reward-details.json"
        if details.is_file():
            shutil.copy2(details, vdir / "reward-details.json")
    if not isinstance(data.get("verifier_result"), dict):
        data["verifier_result"] = {}
    data["verifier_result"]["rewards"] = rewards
    exc = data.get("exception_info") or {}
    if exc.get("exception_type") in ("RewardFileNotFoundError", "VerifierOutputParseError"):
        # The agent finished; only the verifier failed. Rescoring supersedes it.
        data["superseded_exception_info"] = exc
        data["exception_info"] = None
    data["rescored_at"] = datetime.now(timezone.utc).isoformat()
    atomic_json(result_path, data)
    return rewards


def main(argv: list[str]) -> int:
    task_filter = None
    if "--task" in argv:
        i = argv.index("--task")
        task_filter = argv[i + 1]
        argv = argv[:i] + argv[i + 2 :]
    jobs_dir = Path(argv[0]) if argv else REPO / "evals" / "jobs"
    n = 0
    for result in sorted(jobs_dir.glob("*/*/result.json")):
        job = result.parents[1].name
        if job.startswith("_") or (task_filter and task_filter not in job):
            continue
        rewards = rescore(result.parent)
        if rewards is None:
            continue
        n += 1
        print(f"{job.split('__', 1)[0]:34} {'__'.join(job.split('__')[1:3]):26} reward={rewards.get('reward', 0):.2f}")
    print(f"\nrescored {n} trial(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
