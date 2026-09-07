"""Shared validation and parsing for skills in this repository.

Adapted from the skill-creator validator used by Buildr's Kit agent, trimmed to
the open Agent Skills format plus the catalog metadata this repo requires.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

REQUIRED_FRONTMATTER_FIELDS = ("name", "description")
REQUIRED_METADATA_FIELDS = ("tier", "stages", "version", "summary")
REQUIRED_FILES = (
    Path("SKILL.md"),
    Path("examples") / "sample-prompts.md",
)
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_SKILL_MD_LINES = 500

TIERS = ("neutral", "buildr-connected")

# Mirrors STAGES in the buildr.com marketing site (src/lib/library.ts) so the
# /skills catalog and the /library section share one workflow taxonomy.
STAGES = (
    "business-development",
    "preconstruction",
    "estimating",
    "workforce",
    "forecasting",
    "operations",
    "closeout",
)

EXCLUDED_DIR_NAMES = {"__pycache__", "node_modules"}
EXCLUDED_FILE_NAMES = {".DS_Store"}
EXCLUDED_SUFFIXES = {".pyc"}
FORBIDDEN_PATH_PREFIXES = (
    "/global-skills/",
    "/user-skills/",
    "/account-skills/",
    "/workspace/",
)
MAX_ENTRY_SIZE_BYTES = 1 * 1024 * 1024
MAX_TOTAL_SIZE_BYTES = 5 * 1024 * 1024

FRONTMATTER_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL)


class MissingFrontmatterError(ValueError):
    pass


def split_frontmatter(content: str) -> tuple[Any, str]:
    """Return (parsed frontmatter, markdown body)."""
    match = FRONTMATTER_RE.match(content)
    if not match:
        raise MissingFrontmatterError
    body = content[match.end():]
    return yaml.safe_load(match.group(1)), body


def split_csv(value: Any) -> list[str]:
    if not isinstance(value, str):
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def _is_excluded_file(relative_path: Path) -> bool:
    return (
        relative_path.name in EXCLUDED_FILE_NAMES
        or relative_path.suffix in EXCLUDED_SUFFIXES
        or any(part in EXCLUDED_DIR_NAMES for part in relative_path.parts[:-1])
    )


def collect_files(skill_root: Path) -> list[Path]:
    files: list[Path] = []
    for current_root, dirnames, filenames in os.walk(skill_root, topdown=True, followlinks=False):
        current_path = Path(current_root)
        dirnames[:] = [
            d for d in dirnames
            if not (current_path / d).is_symlink() and d not in EXCLUDED_DIR_NAMES
        ]
        for filename in filenames:
            file_path = current_path / filename
            if file_path.is_symlink():
                continue
            relative_path = file_path.relative_to(skill_root)
            if _is_excluded_file(relative_path):
                continue
            files.append(file_path)
    return sorted(files, key=lambda p: p.relative_to(skill_root).as_posix())


def _validate_frontmatter(skill_root: Path, frontmatter: Any, body: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(frontmatter, dict):
        return ["SKILL.md frontmatter must be a YAML mapping"]

    for field in REQUIRED_FRONTMATTER_FIELDS:
        value = frontmatter.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"SKILL.md frontmatter must include a non-empty {field}")

    name = frontmatter.get("name")
    if isinstance(name, str):
        if not NAME_PATTERN.match(name):
            errors.append(f"name '{name}' must be lowercase letters, digits, and single hyphens")
        if len(name) > MAX_NAME_LENGTH:
            errors.append(f"name '{name}' exceeds {MAX_NAME_LENGTH} characters")
        if name != skill_root.name:
            errors.append(f"name '{name}' must match the directory name '{skill_root.name}'")

    description = frontmatter.get("description")
    if isinstance(description, str) and len(description) > MAX_DESCRIPTION_LENGTH:
        errors.append(f"description exceeds {MAX_DESCRIPTION_LENGTH} characters")

    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("SKILL.md frontmatter must include a metadata mapping")
        return errors

    for field in REQUIRED_METADATA_FIELDS:
        value = metadata.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"metadata.{field} must be a non-empty string")

    for key, value in metadata.items():
        if not isinstance(value, str):
            errors.append(f"metadata.{key} must be a string (the Agent Skills spec only allows string values)")

    summary = metadata.get("summary")
    if isinstance(summary, str) and len(summary) > 200:
        errors.append("metadata.summary exceeds 200 characters")

    tier = metadata.get("tier")
    if isinstance(tier, str) and tier not in TIERS:
        errors.append(f"metadata.tier must be one of {', '.join(TIERS)}")

    stages = split_csv(metadata.get("stages"))
    if isinstance(metadata.get("stages"), str) and not stages:
        errors.append("metadata.stages must list at least one workflow stage")
    for stage in stages:
        if stage not in STAGES:
            errors.append(f"metadata.stages contains unknown stage '{stage}' (allowed: {', '.join(STAGES)})")

    version = metadata.get("version")
    if isinstance(version, str) and not re.match(r"^\d+\.\d+\.\d+$", version):
        errors.append(f"metadata.version '{version}' must be semver (x.y.z)")

    if tier == "neutral" and re.search(r"\bbuildr\b", body, re.IGNORECASE):
        errors.append(
            "neutral-tier skills must not mention Buildr in the SKILL.md body; "
            "product tie-ins belong in the catalog, or set metadata.tier to buildr-connected"
        )

    return errors


def validate_skill_tree(skill_root: Path) -> list[str]:
    errors: list[str] = []

    if not skill_root.is_dir():
        return [f"skill root is not a directory: {skill_root}"]

    for required_file in REQUIRED_FILES:
        required_path = skill_root / required_file
        if required_path.is_symlink():
            errors.append(f"required path must not be a symlink: {required_file.as_posix()}")
        elif not required_path.is_file():
            errors.append(f"missing required file: {required_file.as_posix()}")

    skill_md_path = skill_root / "SKILL.md"
    if skill_md_path.is_file() and not skill_md_path.is_symlink():
        content = skill_md_path.read_text(encoding="utf-8")
        try:
            frontmatter, body = split_frontmatter(content)
        except MissingFrontmatterError:
            errors.append("SKILL.md must have YAML frontmatter with opening and closing --- delimiters")
        except yaml.YAMLError as error:
            errors.append(f"SKILL.md frontmatter is invalid YAML: {error}")
        else:
            errors.extend(_validate_frontmatter(skill_root, frontmatter, body))

        for prefix in FORBIDDEN_PATH_PREFIXES:
            if prefix in content:
                errors.append(
                    f"SKILL.md must use paths relative to the skill directory, not {prefix}..."
                )
        if content.count("\n") > MAX_SKILL_MD_LINES:
            errors.append(f"SKILL.md exceeds {MAX_SKILL_MD_LINES} lines; move detail into references/")

    for current_root, dirnames, filenames in os.walk(skill_root, topdown=True, followlinks=False):
        current_path = Path(current_root)
        for dirname in list(dirnames):
            directory_path = current_path / dirname
            if directory_path.is_symlink():
                errors.append(f"symlink directories are not allowed: {directory_path.relative_to(skill_root).as_posix()}")
            if dirname in EXCLUDED_DIR_NAMES:
                dirnames.remove(dirname)
        for filename in filenames:
            file_path = current_path / filename
            relative_path = file_path.relative_to(skill_root)
            if file_path.is_symlink():
                errors.append(f"symlink files are not allowed: {relative_path.as_posix()}")
            elif not file_path.is_file():
                errors.append(f"all entries must be regular files: {relative_path.as_posix()}")
            elif _is_excluded_file(relative_path):
                errors.append(f"remove generated or OS file from the skill: {relative_path.as_posix()}")

    samples = skill_root / "samples"
    for prefix in ("input-", "output-"):
        if not samples.is_dir() or not any(
            p.is_file() and not p.is_symlink() and p.name.startswith(prefix)
            for p in samples.iterdir()
        ):
            errors.append(f"missing synthetic sample: samples/{prefix}<name>.<format>")

    total_size = 0
    for file_path in collect_files(skill_root):
        size = file_path.stat().st_size
        if size > MAX_ENTRY_SIZE_BYTES:
            errors.append(f"'{file_path.relative_to(skill_root).as_posix()}' exceeds {MAX_ENTRY_SIZE_BYTES} bytes")
        total_size += size
    if total_size > MAX_TOTAL_SIZE_BYTES:
        errors.append(f"skill exceeds total size of {MAX_TOTAL_SIZE_BYTES} bytes")

    return sorted(set(errors))


def skill_roots(repo_root: Path) -> list[Path]:
    skills_dir = repo_root / "skills"
    if not skills_dir.is_dir():
        return []
    return sorted(p for p in skills_dir.iterdir() if p.is_dir() and not p.name.startswith("."))
