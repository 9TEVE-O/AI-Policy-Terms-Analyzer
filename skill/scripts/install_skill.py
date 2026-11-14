#!/usr/bin/env python3
"""Preview or safely copy the existing skill to a standard local agent path."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

SKILL_NAME = "analyzing-policy-and-terms"
AGENTS = {"codex": ".agents/skills", "claude": ".claude/skills"}


def install(*, agent: str, scope: str, project_root: str | None, execute: bool) -> Path:
    source = Path(__file__).resolve().parents[1]
    if not (source / "SKILL.md").is_file():
        raise ValueError("Source skill missing SKILL.md")
    if scope == "project":
        if not project_root:
            raise ValueError("--project-root is required for project installs")
        root = Path(project_root).expanduser().resolve()
        if not root.is_dir():
            raise ValueError("Project root does not exist")
        target = root / AGENTS[agent] / SKILL_NAME
    else:
        target = Path.home() / AGENTS[agent] / SKILL_NAME
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Refusing to overwrite an existing skill: {target}")
    # copytree lists the source after parents are created. A destination inside
    # this tree would be copied into itself until the path or disk is exhausted.
    if target.resolve().is_relative_to(source):
        raise ValueError(f"Refusing to install the skill inside its own source tree: {target}")
    if execute:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target, symlinks=False)
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description="Local skill install; preview by default")
    parser.add_argument("--agent", required=True, choices=sorted(AGENTS))
    parser.add_argument("--scope", default="project", choices=["project", "user"])
    parser.add_argument("--project-root")
    parser.add_argument("--install", action="store_true", help="Explicitly create target")
    args = parser.parse_args(argv)
    try:
        target = install(agent=args.agent, scope=args.scope, project_root=args.project_root,
                         execute=args.install)
    except (OSError, ValueError, FileExistsError) as error:
        print(f"policy-skill: {error}", file=sys.stderr)
        return 2
    print(f"{'INSTALLED' if args.install else 'PREVIEW'}: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
