#!/usr/bin/env python3
"""Validate every skill under skills/, or the skill directories passed as arguments.

Usage:
    python3 tools/validate_skills.py            # all skills
    python3 tools/validate_skills.py skills/rfp-intake
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

from skill_utils import skill_roots, validate_skill_tree  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent


def display(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def main(argv: list[str]) -> int:
    roots = [Path(a).resolve() for a in argv] if argv else skill_roots(REPO_ROOT)
    if not roots:
        print("ERROR: no skills found under skills/")
        return 1

    failed = 0
    for root in roots:
        errors = validate_skill_tree(root)
        if errors:
            failed += 1
            print(f"FAIL {display(root)}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"ok   {display(root)}")

    if failed:
        print(f"\n{failed} of {len(roots)} skills failed validation")
        return 1
    print(f"\nall {len(roots)} skills valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
