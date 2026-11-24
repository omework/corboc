#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused static byte-order API and pre-import target.endian selection."""
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--compiler', type=Path, required=True)
p.add_argument('--stdlib', type=Path, required=True)
p.add_argument('--out', type=Path, default=ROOT / 'build/binary-orders/results.json')
a = p.parse_args()
compiler, stdlib = a.compiler.resolve(), a.stdlib.resolve()
work = a.out.resolve().parent
results = []
source = (ROOT / 'validation/fixtures/binary_orders/main.crb').read_text()
selection = '''#(if: target.endian == "little")
fn chosen() -> i64 { 1 }
#(endif)
#(if: target.endian == "big")
use nonexistent::excluded;
fn chosen() -> i64 { 2 }
#(endif)
fn main() { print(chosen()); }
'''
for name, text in [('api', source), ('selection', selection)]:
    package = work / name
    (package / 'src').mkdir(parents=True, exist_ok=True)
    (package / 'src/main.crb').write_text(text)
    (package / 'package.toml').write_text('[package]\nname="binary_orders"\n')
    emitted = subprocess.run([compiler, '--emit-package-c', package, '--stdlib-dir', stdlib], capture_output=True, text=True, timeout=60)
    assert emitted.returncode == 0, (name, emitted.returncode, emitted.stdout[-1500:], emitted.stderr)
    c = package / 'main.c'
    c.write_text(emitted.stdout)
    binary = package / 'main'
    built = subprocess.run(['cc', '-O1', '-pthread', '-fsanitize=undefined', '-fno-sanitize-recover=all', c, '-lm', '-o', binary], capture_output=True, text=True)
    assert built.returncode == 0, (name, built.stderr)
    run = subprocess.run([binary], capture_output=True, text=True, timeout=20)
    expected = ['true'] * 35 if name == 'api' else ['1']
    assert run.returncode == 0 and not run.stderr and run.stdout.split() == expected, (name, run)
    results.append({'case': name, 'status': 'passed, fatal UBSan', 'stdout': run.stdout})
    print(name, results[-1]['status'], flush=True)
a.out.parent.mkdir(parents=True, exist_ok=True)
a.out.write_text(json.dumps(results, indent=2) + '\n')
