"""Run pytest only for test files included in the current pre-commit run."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _collect_test_targets(files: Iterable[str]) -> list[str]:
    targets: set[Path] = set()
    for file_path in files:
        path = Path(file_path)
        if not path.suffix == ".py":
            continue
        if "tests" not in path.parts:
            continue

        absolute = (REPO_ROOT / path).resolve()
        if REPO_ROOT in absolute.parents or absolute == REPO_ROOT:
            try:
                targets.add(absolute.relative_to(REPO_ROOT))
            except ValueError:
                continue
    return sorted(str(target).replace("\\", "/") for target in targets)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Run pytest for changed test files only"
    )
    parser.add_argument("files", nargs="*")
    args = parser.parse_args(argv)

    test_targets = _collect_test_targets(args.files)
    if not test_targets:
        print("No changed test files detected; skipping pytest run.")
        return 0

    env = os.environ.copy()
    backend_path = str(REPO_ROOT / "backend")
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        backend_path if not existing else os.pathsep.join([backend_path, existing])
    )

    cmd = [sys.executable, "-m", "pytest", *test_targets]
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=REPO_ROOT, env=env)
    if result.returncode == 5:
        print("Pytest returned exit code 5 (No tests collected). Treating as success.")
        return 0
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
