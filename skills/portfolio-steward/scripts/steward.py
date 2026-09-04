#!/usr/bin/env python3
"""Create, inspect, and harvest project-steward child copies."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any
from uuid import uuid4


SCHEMA_VERSION = 1
DEFAULT_SKILLS_DIR = ".codex/skills"
DEFAULT_CONTROL_DIR = ".steward"
HEADING_RE = re.compile(r"^(#{2,3})\s+(.+?)\s*$")


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def toolkit_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_template() -> Path:
    return toolkit_root() / "skills/project-steward"


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def tree_hash(root: Path) -> str:
    digest = sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(relative + b"\0")
        digest.update(sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def headings(skill_dir: Path) -> list[dict[str, Any]]:
    skill = skill_dir / "SKILL.md"
    if not skill.is_file():
        raise ValueError(f"missing SKILL.md in {skill_dir}")
    result: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    for line in skill.read_text(encoding="utf-8").splitlines():
        match = HEADING_RE.match(line)
        if not match:
            continue
        title = match.group(2)
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "section"
        counts[slug] = counts.get(slug, 0) + 1
        result.append({"id": f"{slug}-{counts[slug]}", "level": len(match.group(1)), "title": title})
    return result


def git_revision(path: Path) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def child_paths(target: Path, lineage: dict[str, Any]) -> tuple[Path, Path, Path]:
    control = target / lineage["control_dir"]
    child = target / lineage["child_skill"]
    base = control / "base" / lineage["child_name"]
    return control, child, base


def load_lineage(target: Path, control_dir: str = DEFAULT_CONTROL_DIR) -> dict[str, Any]:
    lineage = read_json(target / control_dir / "lineage.json")
    required = {"schema_version", "control_dir", "child_name", "child_skill"}
    missing = required - lineage.keys()
    if missing:
        raise ValueError(f"lineage is missing: {', '.join(sorted(missing))}")
    return lineage


def command_init(args: argparse.Namespace) -> dict[str, Any]:
    target = Path(args.target).expanduser().resolve()
    template = Path(args.template).expanduser().resolve() if args.template else default_template()
    if not target.is_dir():
        raise ValueError(f"target repository does not exist: {target}")
    if not (template / "SKILL.md").is_file():
        raise ValueError(f"template is not a Skill directory: {template}")

    skills_dir = Path(args.skills_dir)
    control_dir = Path(args.control_dir)
    child = target / skills_dir / args.name
    control = target / control_dir
    lineage_path = control / "lineage.json"
    base = control / "base" / args.name
    manifest_path = control / "port-manifest.json"
    collisions = [path for path in (child, lineage_path, base, manifest_path) if path.exists()]
    if collisions:
        formatted = ", ".join(str(path) for path in collisions)
        raise ValueError(f"refusing to overwrite existing steward files: {formatted}")

    shutil.copytree(template, child)
    shutil.copytree(template, base)
    snapshot_hash = tree_hash(base)
    source_headings = headings(base)
    lineage = {
        "schema_version": SCHEMA_VERSION,
        "created_at": now(),
        "control_dir": control_dir.as_posix(),
        "child_name": args.name,
        "child_skill": child.relative_to(target).as_posix(),
        "upstream": {
            "skill": "skills/project-steward",
            "revision": git_revision(toolkit_root()),
            "snapshot_sha256": snapshot_hash,
        },
    }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "source_snapshot_sha256": snapshot_hash,
        "sections": [{**section, "disposition": "keep", "reason": ""} for section in source_headings],
    }
    write_json(lineage_path, lineage)
    write_json(manifest_path, manifest)
    return {
        "target": str(target),
        "child_skill": str(child),
        "base_snapshot": str(base),
        "lineage": str(lineage_path),
        "manifest": str(manifest_path),
        "source_snapshot_sha256": snapshot_hash,
    }


def status_report(target: Path, template: Path | None = None) -> dict[str, Any]:
    lineage = load_lineage(target)
    control, child, base = child_paths(target, lineage)
    manifest = read_json(control / "port-manifest.json")
    base_hash = tree_hash(base)
    child_hash = tree_hash(child)
    expected = {item["title"] for item in manifest.get("sections", []) if isinstance(item, dict)}
    current = {item["title"] for item in headings(child)}
    source = template or default_template()
    upstream_hash = tree_hash(source) if source.is_dir() else None
    return {
        "target": str(target),
        "child_skill": str(child),
        "base_hash": base_hash,
        "child_hash": child_hash,
        "child_modified": base_hash != child_hash,
        "upstream_hash": upstream_hash,
        "upstream_changed": upstream_hash is not None and upstream_hash != base_hash,
        "missing_source_sections": sorted(expected - current),
        "added_child_sections": sorted(current - expected),
        "evolution_count": len(list((control / "evolutions").glob("EV-*.json"))),
    }


def command_status(args: argparse.Namespace) -> dict[str, Any]:
    target = Path(args.target).expanduser().resolve()
    template = Path(args.template).expanduser().resolve() if args.template else None
    return status_report(target, template)


def command_evolve(args: argparse.Namespace) -> dict[str, Any]:
    target = Path(args.target).expanduser().resolve()
    lineage = load_lineage(target)
    control, _, base = child_paths(target, lineage)
    evolution_dir = control / "evolutions"
    evolution_id = args.id or f"EV-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid4().hex[:8]}"
    destination = evolution_dir / f"{evolution_id}.json"
    if destination.exists():
        raise ValueError(f"evolution already exists: {destination}")
    proposal = {
        "schema_version": SCHEMA_VERSION,
        "id": evolution_id,
        "created_at": now(),
        "child_name": lineage["child_name"],
        "base_snapshot_sha256": tree_hash(base),
        "scope": args.scope,
        "failure": args.failure,
        "root_cause": args.root_cause,
        "rule_change": args.rule_change,
        "evidence": args.evidence,
        "validation": args.validation,
        "privacy_review": args.privacy_review,
    }
    write_json(destination, proposal)
    return {"proposal": str(destination), "id": evolution_id, "scope": args.scope}


def resolve_registry_child(registry_path: Path, value: str) -> Path:
    candidate = Path(value).expanduser()
    return candidate.resolve() if candidate.is_absolute() else (registry_path.parent / candidate).resolve()


def harvest_registry(registry_path: Path) -> dict[str, Any]:
    registry = read_json(registry_path)
    children = registry.get("children")
    if not isinstance(children, list):
        raise ValueError("registry children must be an array")
    proposals: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for item in children:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str) or not isinstance(item.get("path"), str):
            errors.append({"child": str(item), "error": "child requires name and path strings"})
            continue
        child_root = resolve_registry_child(registry_path, item["path"])
        try:
            lineage = load_lineage(child_root)
            control, _, _ = child_paths(child_root, lineage)
            for proposal_path in sorted((control / "evolutions").glob("EV-*.json")):
                proposal = read_json(proposal_path)
                proposal["source"] = {"registry_name": item["name"], "path": str(child_root)}
                ready = proposal.get("scope") == "upstream_candidate" and proposal.get("privacy_review") == "passed"
                proposal["harvest_status"] = "ready_for_review" if ready else "recorded_not_ready"
                proposals.append(proposal)
        except ValueError as error:
            errors.append({"child": item["name"], "error": str(error)})

    groups: dict[str, list[str]] = {}
    for proposal in proposals:
        key = re.sub(r"\s+", " ", str(proposal.get("rule_change", "")).strip().lower())
        if key:
            groups.setdefault(key, []).append(str(proposal.get("id", "unknown")))
    duplicate_groups = [
        {"rule_change_key": key, "proposal_ids": ids}
        for key, ids in sorted(groups.items())
        if len(ids) > 1
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "registry": str(registry_path),
        "proposals": proposals,
        "errors": errors,
        "exact_duplicate_groups": duplicate_groups,
        "summary": {
            "children": len(children),
            "proposals": len(proposals),
            "ready_for_review": sum(item["harvest_status"] == "ready_for_review" for item in proposals),
            "errors": len(errors),
        },
    }


def command_harvest(args: argparse.Namespace) -> dict[str, Any]:
    registry = Path(args.registry).expanduser().resolve()
    report = harvest_registry(registry)
    if args.output:
        write_json(Path(args.output).expanduser().resolve(), report)
    return report


def print_result(value: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(value, indent=2, ensure_ascii=False))
        return
    for key, item in value.items():
        if isinstance(item, (dict, list)):
            print(f"{key}: {json.dumps(item, ensure_ascii=False)}")
        else:
            print(f"{key}: {item}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Copy the canonical steward into a repository")
    init.add_argument("target")
    init.add_argument("--name", default="project-steward")
    init.add_argument("--template", help="Override the canonical project-steward directory")
    init.add_argument("--skills-dir", default=DEFAULT_SKILLS_DIR)
    init.add_argument("--control-dir", default=DEFAULT_CONTROL_DIR)
    init.add_argument("--json", action="store_true")
    init.set_defaults(handler=command_init)

    status = sub.add_parser("status", help="Show child drift and future-sync readiness")
    status.add_argument("target")
    status.add_argument("--template", help="Override the canonical project-steward directory")
    status.add_argument("--json", action="store_true")
    status.set_defaults(handler=command_status)

    evolve = sub.add_parser("evolve", help="Record a child steward evolution proposal")
    evolve.add_argument("target")
    evolve.add_argument("--failure", required=True)
    evolve.add_argument("--root-cause", required=True)
    evolve.add_argument("--rule-change", required=True)
    evolve.add_argument("--evidence", action="append", default=[])
    evolve.add_argument("--validation", action="append", default=[])
    evolve.add_argument("--scope", choices=("local", "upstream_candidate"), default="local")
    evolve.add_argument("--privacy-review", choices=("pending", "passed"), default="pending")
    evolve.add_argument("--id")
    evolve.add_argument("--json", action="store_true")
    evolve.set_defaults(handler=command_evolve)

    harvest = sub.add_parser("harvest", help="Collect child evolution proposals from a registry")
    harvest.add_argument("registry")
    harvest.add_argument("--output", help="Write the durable harvest report JSON")
    harvest.add_argument("--json", action="store_true")
    harvest.set_defaults(handler=command_harvest)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = args.handler(args)
    except ValueError as error:
        parser.error(str(error))
    print_result(result, args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
