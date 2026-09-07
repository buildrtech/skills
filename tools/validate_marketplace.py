#!/usr/bin/env python3
"""Check plugin membership against the installed skill tree."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def validate(manifest, names):
    errors = []
    groups = {}
    for plugin in manifest.get('plugins', []):
        name = plugin.get('name')
        if not isinstance(name, str) or not name.strip() or name in groups:
            errors.append('plugin names must be unique non-empty strings')
        members = plugin.get('skills', [])
        if not isinstance(members, list) or any(not isinstance(p, str) for p in members):
            errors.append(f'{name}: skills must be a list of paths')
            continue
        if len(members) != len(set(members)):
            errors.append(f'{name}: duplicate skill membership')
        expected_paths = {f'./skills/{n}' for n in names}
        for member in members:
            if member not in expected_paths:
                errors.append(f'{name}: unknown skill path {member}')
        groups[name] = set(members)
    expected = {f'./skills/{n}' for n in names}
    if groups.get('all') != expected:
        errors.append('all plugin must contain every existing skill exactly once')
    return errors


def main():
    manifest = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
    names = {p.parent.name for p in (ROOT / 'skills').glob('*/SKILL.md')}
    errors = validate(manifest, names)
    for error in errors:
        print(f'ERROR: {error}')
    if not errors:
        print('ok   marketplace membership')
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
