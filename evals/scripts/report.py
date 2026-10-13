#!/usr/bin/env python3
"""Summarize Harbor jobs under evals/jobs into one table.

Usage:
    python3 evals/scripts/report.py [jobs-dir] [--markdown] [--cells]

One row per trial (or per task x lane x condition cell with --cells): lane, condition, model, reward dimensions, whether the
agent read the target skill, cost, tokens, and wall time. Condition and lane
are parsed from the job name written by run.sh
(<task>__<lane>__<with-skills|baseline>__<stamp>).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DIMS = ("reward", "soft_score", "correctness", "boundaries", "format", "grounding")


def skill_used(trial_dir: Path, skill: str) -> str:
    """Did the agent load the skill? Reads the ATIF trajectory's tool calls."""
    traj = trial_dir / "agent" / "trajectory.json"
    if not traj.is_file():
        return "-"
    try:
        data = json.loads(traj.read_text(encoding="utf-8", errors="ignore"))
    except json.JSONDecodeError:
        return "?"
    needles = (f"{skill}/SKILL.md", f"skills/{skill}/")
    hit = False

    def walk(node):
        nonlocal hit
        if hit:
            return
        if isinstance(node, dict):
            for tc in node.get("tool_calls") or []:
                fn = tc.get("function_name") or tc.get("name") or ""
                args = json.dumps(tc.get("arguments") or tc)
                if fn == "Skill" and f'"{skill}"' in args:
                    hit = True
                if any(n in args for n in needles):
                    hit = True
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for x in node:
                walk(x)

    walk(data)
    return "yes" if hit else "no"


def rows(jobs_dir: Path) -> list[dict]:
    out = []
    for result in sorted(jobs_dir.glob("*/*/result.json")):
        if result.parents[1].name.startswith("_"):
            continue  # e.g. _superseded/: jobs scored by an older verifier
        data = json.loads(result.read_text())
        job = result.parents[1].name
        parts = job.split("__")
        task_name = parts[0] if len(parts) > 2 else "?"
        lane = parts[1] if len(parts) > 2 else data.get("agent_info", {}).get("name", "?")
        cond = parts[2] if len(parts) > 3 else "?"
        rewards = (data.get("verifier_result") or {}).get("rewards") or {}
        agent = data.get("agent_result") or {}
        skill = (data.get("config", {}).get("task", {}).get("path") or "").split("/")
        skill_name = skill[-2] if len(skill) >= 2 else ""
        exc = data.get("exception_info") or {}
        timing = data.get("agent_execution") or {}
        secs = None
        if timing.get("started_at") and timing.get("finished_at"):
            from datetime import datetime

            secs = (datetime.fromisoformat(timing["finished_at"]) - datetime.fromisoformat(timing["started_at"])).total_seconds()
        out.append(
            {
                "job": job,
                "task": task_name,
                "lane": lane,
                "cond": cond,
                "model": ((data.get("agent_info") or {}).get("model_info") or {}).get("name")
                or ((data.get("config") or {}).get("agent") or {}).get("model_name")
                or "",
                **{d: rewards.get(d) for d in DIMS},
                "skill_used": skill_used(result.parent, skill_name) if skill_name else "?",
                "cost_usd": agent.get("cost_usd"),
                "in_tok": agent.get("n_input_tokens"),
                "out_tok": agent.get("n_output_tokens"),
                "secs": secs,
                "error": exc.get("exception_type") or "",
            }
        )
    return out


def fmt(v) -> str:
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:.2f}"
    return str(v)


def aggregate(data: list[dict]) -> list[dict]:
    """One row per (task, lane, cond): mean of each dimension, n trials, mean cost."""
    from collections import defaultdict
    from statistics import mean, pstdev

    cells: dict[tuple, list[dict]] = defaultdict(list)
    for r in data:
        cells[(r["task"], r["lane"], r["cond"])].append(r)
    out = []
    for (task, lane, cond), rs in sorted(cells.items()):
        row = {"task": task, "lane": lane, "cond": cond, "model": rs[0]["model"], "n": len(rs)}
        for d in DIMS:
            vals = [r[d] for r in rs if r[d] is not None]
            row[d] = mean(vals) if vals else None
            row[d + "_sd"] = pstdev(vals) if len(vals) > 1 else None
        row["skill_used"] = f"{sum(1 for r in rs if r['skill_used'] == 'yes')}/{len(rs)}"
        costs = [r["cost_usd"] for r in rs if r["cost_usd"] is not None]
        row["cost_usd"] = mean(costs) if costs else None
        row["errors"] = sum(1 for r in rs if r["error"])
        out.append(row)
    return out


def main(argv: list[str]) -> int:
    md = "--markdown" in argv
    agg = "--cells" in argv
    argv = [a for a in argv if a not in ("--markdown", "--cells")]
    jobs_dir = Path(argv[0]) if argv else REPO / "evals" / "jobs"
    data = rows(jobs_dir)
    if not data:
        print(f"no results under {jobs_dir}")
        return 1
    cols = ["task", "lane", "cond", "model", *DIMS, "skill_used", "cost_usd", "in_tok", "out_tok", "secs", "error"]
    if agg:
        data = aggregate(data)
        cols = ["task", "lane", "cond", "model", "n", "reward", "reward_sd", "soft_score", "soft_score_sd", "correctness", "boundaries", "format", "grounding", "skill_used", "cost_usd", "errors"]
    if md:
        print("| " + " | ".join(cols) + " |")
        print("|" + "---|" * len(cols))
        for r in data:
            print("| " + " | ".join(fmt(r[c]) for c in cols) + " |")
    else:
        widths = {c: max(len(c), *(len(fmt(r[c])) for r in data)) for c in cols}
        print("  ".join(c.ljust(widths[c]) for c in cols))
        for r in data:
            print("  ".join(fmt(r[c]).ljust(widths[c]) for c in cols))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
