#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Resolve and verify the exact shared-source revision in corbo.lock."""

import argparse
from pathlib import Path
import re
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def git(*args, cwd=None, capture=False):
    return subprocess.run(
        ["git", *map(str, args)], cwd=cwd, check=True, text=True,
        stdout=subprocess.PIPE if capture else None, timeout=180,
    ).stdout


def lock():
    data = tomllib.loads((ROOT / "corbo.lock").read_text())["corbo"]
    if not re.fullmatch(r"[0-9a-f]{40}", data["rev"]):
        raise ValueError("corbo.lock must contain a full immutable commit ID")
    for name in ("stdlib", "runtime", "grammar", "rules", "validation_guidelines"):
        path = Path(data[name])
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"Invalid source path in corbo.lock: {name}")
    return data


def source_root(path=None):
    data = lock()
    source = Path(path).resolve() if path else ROOT / ".deps/corbo"
    if not source.is_dir():
        raise RuntimeError("Pinned sources missing; run python3 scripts/corbo_sources.py")
    revision = git("rev-parse", "HEAD", cwd=source, capture=True).strip()
    if revision != data["rev"]:
        raise RuntimeError(f"Corbo revision mismatch: expected {data['rev']}, found {revision}")
    # Documentation/build artifacts may change without affecting compiler inputs.
    # Runtime code, STD code and normative inputs must still match the lock.
    inputs = [data["stdlib"], data["runtime"], data["grammar"], data["rules"],
              data["validation_guidelines"], ":(exclude)runtime/*.md"]
    changes = git("status", "--porcelain", "--untracked-files=all", "--", *inputs,
                  cwd=source, capture=True)
    if changes.strip():
        raise RuntimeError("Pinned Corbo inputs have local changes:\n" + changes)
    for name in ("stdlib", "runtime", "grammar", "rules", "validation_guidelines"):
        if not (source / data[name]).exists():
            raise RuntimeError(f"Missing pinned source: {data[name]}")
    return source


def prepare(from_repo=None):
    data = lock()
    destination = ROOT / ".deps/corbo"
    if destination.exists():
        return source_root(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    remote = str(Path(from_repo).resolve()) if from_repo else data["git"]
    git("clone", "--no-hardlinks", "--no-checkout", remote, destination)
    git("remote", "set-url", "origin", data["git"], cwd=destination)
    available = subprocess.run(
        ["git", "cat-file", "-e", data["rev"] + "^{commit}"],
        cwd=destination, capture_output=True, timeout=30,
    )
    if available.returncode:
        git("fetch", "--depth=1", "origin", data["rev"], cwd=destination)
    git("checkout", "--detach", data["rev"], cwd=destination)
    return source_root(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-repo", type=Path, help="Use a local Git object source; the lock still applies")
    parser.add_argument("--check", action="store_true", help="Verify the existing cache without fetching")
    args = parser.parse_args()
    print(source_root() if args.check else prepare(args.from_repo))


if __name__ == "__main__":
    main()
