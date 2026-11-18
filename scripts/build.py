#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Build/install corboc with pinned sources and optionally verify self-hosting."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess

from corbo_sources import ROOT, lock, prepare


def run(command, **kwargs):
    print("+", shlex.join(map(str, command)), flush=True)
    return subprocess.run(list(map(str, command)), check=True, timeout=600, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", default=os.environ.get("CORBOC_SEED", "corboc"))
    parser.add_argument("--prefix", type=Path, default=ROOT / "build/install")
    parser.add_argument("--from-repo", type=Path)
    parser.add_argument("--cc", default=os.environ.get("CC", "cc"))
    parser.add_argument("--cflags", default="-O1")
    parser.add_argument("--verify-self", action="store_true")
    args = parser.parse_args()
    seed = shutil.which(args.seed)
    if seed is None:
        raise SystemExit("An existing self-hosted seed supporting the current grammar is required (--seed).")
    seed = Path(seed).resolve()
    source = prepare(args.from_repo)
    data = lock()
    run(["python3", ROOT / "scripts/runtime_sources.py", "--check"])
    prefix = args.prefix.resolve()
    build = ROOT / "build/bootstrap"
    build.mkdir(parents=True, exist_ok=True)
    (prefix / "bin").mkdir(parents=True, exist_ok=True)
    shared = prefix / "share/corbo"
    shared.mkdir(parents=True, exist_ok=True)
    stdlib = shared / "stdlib/src"
    # This is an owned install artifact, replaced to avoid obsolete STD modules.
    if stdlib.exists():
        shutil.rmtree(stdlib)
    shutil.copytree(source / data["stdlib"], stdlib)
    shutil.copy2(ROOT / "corbo.lock", shared / "corbo.lock")
    (prefix / "include").mkdir(exist_ok=True)
    shutil.copy2(source / data["runtime"] / "corbo_runtime.h", prefix / "include/corbo_runtime.h")
    cc = shlex.split(args.cc)
    flags = shlex.split(args.cflags)

    def emit(compiler, output):
        with output.open("wb") as stream:
            run([compiler, "--emit-package-c", ROOT, "--stdlib-dir", stdlib], stdout=stream)

    def compile_c(path, binary):
        run([*cc, "-std=c11", "-pthread", *flags, path, "-lm", "-o", binary])

    first_c = build / "stage1.c"
    binary = prefix / "bin/corboc"
    emit(seed, first_c)
    compile_c(first_c, binary)
    report = {"corbo_revision": data["rev"], "seed": str(seed), "compiler": str(binary),
              "c_sha256": hashlib.sha256(first_c.read_bytes()).hexdigest(), "self_verified": False}
    if args.verify_self:
        second_c = build / "stage2.c"
        emit(binary, second_c)
        if first_c.read_bytes() != second_c.read_bytes():
            raise RuntimeError("Rebuilt compiler emitted different compiler C; retained both stages")
        second = prefix / "bin/corboc-stage2"
        compile_c(second_c, second)
        third_c = build / "stage3.c"
        emit(second, third_c)
        if second_c.read_bytes() != third_c.read_bytes():
            raise RuntimeError("Compiler C differs across reconstructed generations")
        # Exercise the normal command with automatic installed-STD discovery.
        cli = prefix / "bin/corboc-cli"
        run([second, "build", ROOT, "-o", cli])
        package = build / "smoke"
        (package / "src/math").mkdir(parents=True, exist_ok=True)
        (package / "package.toml").write_text('[package]\nname="smoke"\n')
        (package / "src/math/math.crb").write_text('pub fn answer()->i64{42}\n')
        (package / "src/main.crb").write_text('use smoke::math::answer; fn main(){print(answer());}\n')
        program = build / "smoke-program"
        run([cli, "build", package, "-o", program])
        result = run([program], capture_output=True, text=True)
        if (result.stdout, result.stderr) != ("42\n", ""):
            raise RuntimeError(f"Unexpected smoke result: {result}")
        report.update(self_verified=True, normal_build=str(cli), module_smoke="42")
    (build / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
