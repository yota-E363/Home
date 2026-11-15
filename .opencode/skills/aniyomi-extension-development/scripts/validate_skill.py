#!/usr/bin/env python3
"""Small offline package check for the Aniyomi extension skill."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "SKILL.md",
    "README.md",
    "references/architecture.md",
    "references/call-flow-and-identity.md",
    "references/network-and-parsing.md",
    "references/kotlin-patterns.md",
    "references/validation.md",
    "references/compatibility.md",
    "references/presentation-and-webview.md",
    "references/saradahentai-case-study.md",
    "examples/current-source.kt",
    "examples/fixture_test.py",
    "examples/posts.fixture.json",
]


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    if missing:
        print("missing:", ", ".join(missing))
        return 1
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    required_terms = ["KeiSource", "AnimeHttpSource", "Fetch.XHR", "unclassified", "lintRelease"]
    absent = [term for term in required_terms if term not in skill and term not in (ROOT / "references/network-and-parsing.md").read_text(encoding="utf-8")]
    if absent:
        print("missing concepts:", ", ".join(absent))
        return 1
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "-v", "examples/fixture_test.py"],
        cwd=ROOT,
        text=True,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
