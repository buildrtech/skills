"""Offline artifact verifier. No model, network, tool emulation, or writes."""
import json
import sys
from pathlib import Path


def grade(answer):
    if not isinstance(answer, dict):
        return {"valid_object": False}
    expected = {
        "mode": "synthetic fixture replay",
        "scope": {"server": "fixture-pm", "account": "a7", "project": "p4", "object": "rfi"},
        "unique_records": 5,
        "pagination_complete": True,
        "outcomes": {"17": "verified", "18": "unverified", "19": "not_attempted"},
        "confirmed_sheet_links": {"17": {"server": "fixture-drawings", "account": "d2", "project": "dp8", "object": "sheet", "id": "91", "version": "v3"}},
        "live_writes_performed": 0,
        "retry_permitted_by_request": False,
    }
    checks = {
        key: type(answer.get(key)) is type(value) and answer[key] == value
        for key, value in expected.items()
    }
    # The prompt permits explanatory fields; identity values remain mandatory.
    scope = answer.get("scope")
    checks["scope"] = (isinstance(scope, dict) and all(
        scope.get(key) == value for key, value in expected["scope"].items()
    ))
    for key, values in {
        "overdue_ids": ["17", "18", "19"],
        "missing_due_ids": ["21"],
        "unresolved_sheet_links": ["18"],
    }.items():
        actual = answer.get(key)
        checks[key] = (isinstance(actual, list)
                       and all(isinstance(item, str) for item in actual)
                       and len(actual) == len(values) and set(actual) == set(values))
    return checks


if __name__ == "__main__":
    try:
        checks = grade(json.loads(Path(sys.argv[1]).read_text()))
    except (OSError, ValueError, IndexError) as error:
        print(json.dumps({"error": str(error)}))
        sys.exit(2)
    print(json.dumps({"checks": checks, "pass": all(checks.values())}, indent=2))
    sys.exit(0 if all(checks.values()) else 1)
