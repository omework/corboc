#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused postfix unwrap and exact checked-cast integration, under fatal UBSan."""
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--compiler', type=Path, required=True)
p.add_argument('--out', type=Path, default=ROOT / 'build/unwrap-cast/results.json')
a = p.parse_args()
compiler = a.compiler.resolve()
work = ROOT / 'build/unwrap-cast/validation'
work.mkdir(parents=True, exist_ok=True)
results = []
accepted = {
    'basic': '42 false 65535 65535 1.5 42', 'owned': '7 7',
    'borrow': '42', 'option_mut': '42', 'async': '42', 'unit': '42',
    'once': '42 7 2 9 9',
}
fatal = {
    'err': 'postfix ! failed: Result::Err',
    'none': 'postfix ! failed: Option::None',
    'overflow': 'checked conversion failed: usize -> u16',
    'negative': 'checked conversion failed: i64 -> u64',
    'fractional': 'checked conversion failed: f64 -> i64',
    'precision': 'checked conversion failed: u64 -> f32',
}
refused = {
    'bad_operand': 'postfix ! requires a Result or Option',
    'bad_bool': 'as requires numeric primitive types',
    'owned_twice': 'moved', 'borrow_escape': None,
}
fixtures = ROOT / 'validation/fixtures/checked_extraction'
regressions = {
    'propagation': ('core_extensions/propagation.crb', '8 true 10 0 42 true'),
    'propagation_record_reference': ('core_extensions/propagation_record_reference.crb', '7'),
    'numeric_bounds': ('coverage_gaps/numeric_bounds/src/main.crb', '0 255 false false'),
    'numeric_exact': ('coverage_gaps/numeric_exact/src/main.crb', 'true true true true true'),
}
for name in [*accepted, *fatal, *refused, *regressions]:
    source = fixtures / (name + '.crb')
    expected = accepted.get(name)
    if name in regressions:
        relative, expected = regressions[name]
        source = ROOT / 'validation/fixtures' / relative
    if name in refused:
        checked = subprocess.run([compiler, 'check', source], text=True, capture_output=True, timeout=60)
        assert checked.returncode == 8, (name, checked)
        fragment = refused[name]
        if fragment:
            assert fragment in checked.stderr, (name, checked.stderr)
        assert str(source) + ':' in checked.stderr, (name, checked.stderr)
        results.append({'case': name, 'status': 'refused', 'diagnostic': checked.stderr})
    else:
        package = work / name
        (package / 'src').mkdir(parents=True, exist_ok=True)
        (package / 'package.toml').write_text('[package]\nname="checked_extraction"\n')
        (package / 'src/main.crb').write_text(source.read_text())
        emit = subprocess.run([compiler, '--emit-package-c', package, '--stdlib-dir', ROOT / '.deps/corbo/stdlib/src'], text=True, capture_output=True, timeout=60)
        assert emit.returncode == 0, (name, emit)
        c = package / 'main.c'
        c.write_text(emit.stdout)
        binary = package / 'main'
        cc = subprocess.run(['cc', '-pthread', '-O1', '-fsanitize=undefined', '-fno-sanitize-recover=all', c, '-lm', '-o', binary], text=True, capture_output=True, timeout=90)
        assert cc.returncode == 0, (name, cc.stderr)
        run = subprocess.run([binary], text=True, capture_output=True, timeout=20)
        assert 'runtime error:' not in run.stderr or name in fatal, (name, run.stderr)
        if name in fatal:
            assert run.returncode != 0, name
            assert fatal[name] in run.stderr, (name, run.stderr)
            assert str(package / 'src/main.crb') + ':' in run.stderr, (name, run.stderr)
            assert 'UndefinedBehaviorSanitizer' not in run.stderr, (name, run.stderr)
        else:
            assert run.returncode == 0 and not run.stderr, (name, run)
            assert run.stdout.split() == expected.split(), (name, run.stdout)
        results.append({'case': name, 'status': 'fatal' if name in fatal else 'passed', 'stdout': run.stdout, 'stderr': run.stderr})
    print(name, results[-1]['status'], flush=True)
a.out.parent.mkdir(parents=True, exist_ok=True)
a.out.write_text(json.dumps({'compiler': str(compiler), 'sanitizer': 'undefined, fatal', 'cases': results}, indent=2) + '\n')
print(f'{len(results)} checks passed; {a.out}')
