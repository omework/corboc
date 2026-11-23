#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused declared dereferencing, A<T> payload borrows and guard integration."""
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--compiler', type=Path, required=True)
p.add_argument('--stdlib', type=Path, required=True)
p.add_argument('--case', action='append', help='Run only selected fixture names')
p.add_argument('--out', type=Path, default=ROOT / 'build/reference-methods/results.json')
a = p.parse_args()
compiler, stdlib = a.compiler.resolve(), a.stdlib.resolve()
expected = {'generic_receiver': '42', 'wrapper': '13 42 42', 'generic': '42 true', 'allocation': '42 7',
            'native': '42 2', 'once': '99 42 false 12', 'mutex_deref': '42 42 42'}
fixtures = ROOT / 'validation/fixtures/reference_methods'
work = a.out.resolve().parent
results = []
for source in sorted(fixtures.glob('*.crb')):
    name = source.stem
    if a.case and name not in a.case:
        continue
    package = work / name
    (package / 'src').mkdir(parents=True, exist_ok=True)
    (package / 'package.toml').write_text('[package]\nname="reference_methods"\n')
    (package / 'src/main.crb').write_text(source.read_text())
    emitted = subprocess.run([compiler, '--emit-package-c', package, '--stdlib-dir', stdlib], text=True, capture_output=True, timeout=60)
    assert 'corbo: ' not in emitted.stderr, (name, emitted.stderr)
    if name not in expected:
        assert emitted.returncode in (8, 9), (name, 'unexpected acceptance')
        results.append({'case': name, 'status': 'refused', 'exit': emitted.returncode, 'diagnostic': emitted.stdout + emitted.stderr})
    else:
        assert emitted.returncode == 0, (name, emitted)
        c = package / 'main.c'
        c.write_text(emitted.stdout)
        binary = package / 'main'
        subprocess.run(['cc', '-pthread', '-O1', '-fsanitize=undefined', '-fno-sanitize-recover=all', c, '-lm', '-o', binary], check=True, capture_output=True, text=True, timeout=90)
        run = subprocess.run([binary], text=True, capture_output=True, timeout=20)
        assert run.returncode == 0 and not run.stderr, (name, run)
        assert run.stdout.split() == expected[name].split(), (name, run.stdout)
        results.append({'case': name, 'status': 'passed, fatal UBSan', 'stdout': run.stdout})
    print(name, results[-1]['status'], flush=True)
a.out.parent.mkdir(parents=True, exist_ok=True)
a.out.write_text(json.dumps(results, indent=2) + '\n')
