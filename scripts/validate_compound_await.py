#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused compound await propagation and explicit slice argument diagnostics."""
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--compiler', type=Path, required=True)
p.add_argument('--out', type=Path, default=ROOT / 'build/compound-await/results.json')
p.add_argument('--case', action='append')
a = p.parse_args()
compiler = a.compiler.resolve()
results = []
for name, expected in {'file': '2', 'suspension': '1 42 42 1 40 7', 'missing_shared': None, 'missing_mutable': None}.items():
    if a.case and name not in a.case:
        continue
    package = a.out.resolve().parent / name
    (package / 'src').mkdir(parents=True, exist_ok=True)
    (package / 'package.toml').write_text('[package]\nname="compound_await"\n')
    source = package / 'src/main.crb'
    source.write_text((ROOT / 'validation/fixtures/compound_await' / (name + '.crb')).read_text())
    if expected is None:
        checked = subprocess.run([compiler, 'check', source], capture_output=True, text=True, timeout=60)
        assert checked.returncode == 8, (name, checked.returncode, checked.stderr)
        mode = 'mutable' if name == 'missing_mutable' else 'shared'
        for text in [f'explicit {mode} borrow', 'expected: &mut [u8]' if mode == 'mutable' else 'expected: &[u8]', 'actual: unborrowed slice expression', 'help:', '&mut buffer[..]' if mode == 'mutable' else '&data[..]']:
            assert text in checked.stderr, (name, text, checked.stderr)
        assert 'E0009' not in checked.stderr
        spelling = 'buffer[..]' if mode == 'mutable' else 'data[..]'
        content = source.read_text()
        offset = content.index(spelling)
        line = content[:offset].count('\n') + 1
        column = offset - content.rfind('\n', 0, offset)
        assert f'{source}:{line}:{column}:' in checked.stderr, checked.stderr
        results.append({'case': name, 'status': 'precise N1 refusal', 'diagnostic': checked.stderr})
    else:
        emitted = subprocess.run([compiler, '--emit-package-c', package, '--stdlib-dir', ROOT / '.deps/corbo/stdlib/src'], capture_output=True, text=True, timeout=60)
        assert emitted.returncode == 0, (name, emitted.returncode, emitted.stderr, emitted.stdout[-1500:])
        c = package / 'main.c'
        c.write_text(emitted.stdout)
        binary = package / 'main'
        built = subprocess.run(['cc', '-O1', '-pthread', '-fsanitize=undefined', '-fno-sanitize-recover=all', c, '-lm', '-o', binary], capture_output=True, text=True)
        assert built.returncode == 0, (name, built.stderr)
        run = subprocess.run([binary], capture_output=True, text=True, timeout=20)
        assert run.returncode == 0 and not run.stderr and run.stdout.split() == expected.split(), (name, run)
        if name == 'file':
            Path('/tmp/corboc-compound-await-file').unlink(missing_ok=True)
        results.append({'case': name, 'status': 'passed, fatal UBSan', 'stdout': run.stdout})
    print(name, results[-1]['status'], flush=True)
a.out.parent.mkdir(parents=True, exist_ok=True)
a.out.write_text(json.dumps(results, indent=2) + '\n')
