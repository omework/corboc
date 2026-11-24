#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused omitted-bound slice reborrows, async File and unchanged protection checks."""
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--compiler', type=Path, required=True)
p.add_argument('--out', type=Path, default=ROOT / 'build/slice-reborrow/results.json')
a = p.parse_args()
compiler = a.compiler.resolve()
expected = {'forms': '2 11 1 20 0 20 0', 'async_file': '2 65 66 2'}
results = []
for fixture in sorted((ROOT / 'validation/fixtures/slice_reborrow').glob('*.crb')):
    name = fixture.stem
    package = a.out.resolve().parent / name
    (package / 'src').mkdir(parents=True, exist_ok=True)
    (package / 'package.toml').write_text('[package]\nname="slice_reborrow"\n')
    source = package / 'src/main.crb'
    source.write_text(fixture.read_text())
    if name in ('shared_mutation', 'overlapping'):
        checked = subprocess.run([compiler, 'check', source], capture_output=True, text=True, timeout=60)
        assert checked.returncode == 8 and 'error[N5]' in checked.stderr, (name, checked)
        results.append({'case': name, 'status': 'N5 refusal', 'diagnostic': checked.stderr})
    else:
        emit = subprocess.run([compiler, '--emit-package-c', package, '--stdlib-dir', ROOT / '.deps/corbo/stdlib/src'], capture_output=True, text=True, timeout=60)
        assert emit.returncode == 0, (name, emit.returncode, emit.stdout[-1500:], emit.stderr)
        c = package / 'main.c'
        c.write_text(emit.stdout)
        binary = package / 'main'
        built = subprocess.run(['cc', '-O1', '-pthread', '-fsanitize=undefined', '-fno-sanitize-recover=all', c, '-lm', '-o', binary], capture_output=True, text=True)
        assert built.returncode == 0, (name, built.stderr)
        run = subprocess.run([binary], capture_output=True, text=True, timeout=20)
        if name == 'out_of_bounds':
            assert run.returncode != 0 and 'borne de tranche' in run.stderr and 'runtime error:' not in run.stderr, (name, run)
            status = 'runtime bounds refusal'
        else:
            assert run.returncode == 0 and not run.stderr and run.stdout.split() == expected[name].split(), (name, run)
            status = 'passed, fatal UBSan'
            if name == 'async_file':
                Path('/tmp/corboc-slice-reborrow-file').unlink(missing_ok=True)
        results.append({'case': name, 'status': status, 'stdout': run.stdout, 'stderr': run.stderr})
    print(name, results[-1]['status'], flush=True)
a.out.parent.mkdir(parents=True, exist_ok=True)
a.out.write_text(json.dumps(results, indent=2) + '\n')
