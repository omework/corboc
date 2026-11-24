#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Execute the generic-guard tuple-array loop and its explicit-ref variant."""
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--compiler', type=Path, required=True)
p.add_argument('--out', type=Path, default=ROOT / 'build/wal-guard-loop/results.json')
a = p.parse_args()
compiler = a.compiler.resolve()
source = (ROOT / 'validation/fixtures/wal_file/guard_loop.crb').read_text()
cases = {
    'dereference': source,
    'explicit-reference': source.replace('for slot in &mut (*guard).buffer {',
        'let mut value = guard.mut_ref();\n    for slot in &mut value.buffer {'),
}
results = []
for name, text in cases.items():
    package = a.out.resolve().parent / name
    (package / 'src').mkdir(parents=True, exist_ok=True)
    (package / 'src/main.crb').write_text(text)
    (package / 'package.toml').write_text('[package]\nname="wal_guard_loop"\n')
    emit = subprocess.run([compiler, '--emit-package-c', package, '--stdlib-dir', ROOT / '.deps/corbo/stdlib/src'], capture_output=True, text=True, timeout=60)
    assert emit.returncode == 0, (name, emit.returncode, emit.stdout[-1500:], emit.stderr)
    c = package / 'main.c'
    c.write_text(emit.stdout)
    binary = package / 'main'
    built = subprocess.run(['cc', '-O1', '-pthread', '-fsanitize=undefined', '-fno-sanitize-recover=all', c, '-lm', '-o', binary], capture_output=True, text=True)
    assert built.returncode == 0, (name, built.stderr)
    run = subprocess.run([binary], capture_output=True, text=True, timeout=20)
    assert run.returncode == 0 and not run.stderr and run.stdout.split() == ['3', '7', '0', '2'], (name, run)
    results.append({'case': name, 'status': 'passed, fatal UBSan', 'stdout': run.stdout})
    print(name, 'passed', flush=True)
a.out.parent.mkdir(parents=True, exist_ok=True)
a.out.write_text(json.dumps(results, indent=2) + '\n')
