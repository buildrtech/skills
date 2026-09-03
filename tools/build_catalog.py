#!/usr/bin/env python3
"""Generate catalog.json from skill frontmatter.

catalog.json is committed and consumed by the buildr.com /skills catalog at
build time. CI fails if it is out of date; run this script after editing any
SKILL.md.

Usage:
    python3 tools/build_catalog.py           # write catalog.json
    python3 tools/build_catalog.py --check   # exit 1 if catalog.json is stale
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

from skill_utils import collect_files, skill_roots, split_csv, split_frontmatter  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = REPO_ROOT / "catalog.json"
REPO_SLUG = "buildrtech/skills"
MARKETPLACE_PATH = REPO_ROOT / ".claude-plugin" / "marketplace.json"
CATALOG_VERSION = 2

# File contents are inlined so the catalog site can show every file in a
# skill without extra requests. Only text files under this size are inlined;
# larger or binary files keep their path and size with content set to null.
MAX_INLINE_BYTES = 256 * 1024
TEXT_SUFFIXES = {
    ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".csv",
    ".py", ".sh", ".js", ".mjs", ".ts", ".html", ".css",
}


def plugin_memberships() -> dict[str, list[str]]:
    """Map skill name -> plugin names that include it, from marketplace.json."""
    memberships: dict[str, list[str]] = {}
    if not MARKETPLACE_PATH.is_file():
        return memberships
    manifest = json.loads(MARKETPLACE_PATH.read_text(encoding="utf-8"))
    for plugin in manifest.get("plugins", []):
        for skill_path in plugin.get("skills", []):
            skill_name = Path(skill_path).name
            memberships.setdefault(skill_name, []).append(plugin["name"])
    return memberships


def read_optional(skill_root: Path, relative: str) -> str | None:
    path = skill_root / relative
    return path.read_text(encoding="utf-8") if path.is_file() else None


def file_entry(skill_root: Path, path: Path) -> dict:
    relative = path.relative_to(skill_root).as_posix()
    size = path.stat().st_size
    content = None
    if path.suffix.lower() in TEXT_SUFFIXES and size <= MAX_INLINE_BYTES:
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = None
    return {"path": relative, "bytes": size, "content": content}


def first_sample(skill_root: Path, files: list[str], prefix: str) -> str | None:
    """First markdown sample with the given prefix; other formats (JSON, HTML,
    CSV) are still browsable as files but are not rendered as prose."""
    for relative in files:
        if relative.startswith(f"samples/{prefix}") and relative.endswith(".md"):
            return read_optional(skill_root, relative)
    return None


def build_entry(skill_root: Path, plugins: dict[str, list[str]]) -> dict:
    content = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(content)
    metadata = frontmatter.get("metadata", {}) or {}
    name = frontmatter["name"]
    file_entries = [file_entry(skill_root, p) for p in collect_files(skill_root)]
    files = [entry["path"] for entry in file_entries]
    tier = metadata.get("tier", "neutral")
    first_plugin = (plugins.get(name) or ["all"])[0]

    return {
        "name": name,
        "description": frontmatter["description"],
        "license": frontmatter.get("license"),
        "tier": tier,
        "stages": split_csv(metadata.get("stages")),
        "version": metadata.get("version"),
        "author": metadata.get("author", "Buildr"),
        "path": f"skills/{name}",
        "files": file_entries,
        "plugins": plugins.get(name, []),
        "install": {
            "skills_cli": f"npx skills add {REPO_SLUG} --skill {name}",
            "claude_plugin": [
                f"/plugin marketplace add {REPO_SLUG}",
                f"/plugin install {first_plugin}@buildr",
            ],
            "paste": body.strip(),
        },
        "sample_prompts": read_optional(skill_root, "examples/sample-prompts.md"),
        "sample_input": first_sample(skill_root, files, "input-"),
        "sample_output": first_sample(skill_root, files, "output-"),
    }


def build_catalog() -> dict:
    plugins = plugin_memberships()
    entries = [build_entry(root, plugins) for root in skill_roots(REPO_ROOT)]
    return {
        "version": CATALOG_VERSION,
        "repo": REPO_SLUG,
        "skills": entries,
    }


def render(catalog: dict) -> str:
    return json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str]) -> int:
    catalog = render(build_catalog())
    if "--check" in argv:
        current = CATALOG_PATH.read_text(encoding="utf-8") if CATALOG_PATH.is_file() else ""
        if current != catalog:
            print("ERROR: catalog.json is out of date; run python3 tools/build_catalog.py")
            return 1
        print("ok   catalog.json is up to date")
        return 0
    CATALOG_PATH.write_text(catalog, encoding="utf-8")
    print(f"wrote {CATALOG_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
