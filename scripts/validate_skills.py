#!/usr/bin/env python3
"""Validate the small, portable contract used by this skill collection."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
SHARED = SKILLS / "_shared" / "references"
REQUIRED_SHARED = {
    "architecture.md",
    "clean-architecture-and-boundaries.md",
    "equivalence-and-benchmarking.md",
    "ffi-integration-patterns.md",
    "functional-programming-principles.md",
    "guardrails.md",
    "oop-principles.md",
    "rust-idioms-and-safety.md",
    "security-and-privacy-guardrails.md",
    "solid-principles.md",
}


def error(message: str) -> None:
    print(f"ERROR: {message}")


def main() -> int:
    failures = 0
    missing_shared = sorted(REQUIRED_SHARED - {path.name for path in SHARED.glob("*.md")})
    for name in missing_shared:
        error(f"missing shared reference: skills/_shared/references/{name}")
        failures += 1

    plugins = [path for path in SKILLS.iterdir() if path.is_dir() and path.name != "_shared"]
    if not plugins:
        error("no host-language plugins found under skills/")
        failures += 1

    for plugin in sorted(plugins):
        skill = plugin / "SKILL.md"
        agent = plugin / "agents" / "openai.yaml"
        guardrails = plugin / "references" / "guardrails.md"
        for path in (skill, agent, guardrails):
            if not path.is_file():
                error(f"{plugin.relative_to(ROOT)} is missing {path.relative_to(plugin)}")
                failures += 1
        if skill.is_file():
            content = skill.read_text(encoding="utf-8")
            if not content.startswith("---\n") or "\nname:" not in content or "\ndescription:" not in content:
                error(f"{skill.relative_to(ROOT)} needs YAML front matter with name and description")
                failures += 1

    if failures:
        return 1
    print(f"Validated {len(plugins)} plugin(s) and {len(REQUIRED_SHARED)} shared references.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
