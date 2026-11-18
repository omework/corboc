#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused executable and ownership regressions for general callable lowering."""
import argparse
import json
from pathlib import Path
import platform
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ACCEPTED = {
    'modes': '42\n10\n20\n2\n42\n42\n',
    'mutable': '2\n7\n5\n6\n',
    'borrow': '11\n12\n12\n',
    'cleanup': '9\n90\n9\n',
    'shared_capture': '7\n7\n',
    'pipeline_interop': '42\n1\n120\n7\n',
}
REJECTED = {
    'captured_target_mutation': 'fn main() { let mut n: i64 = 7; let view = &n; let c = || { *view }; n = 8; print(c()); }',
    'moved_capture': '''fn main() { let number: i64 = 7; let c = move || { number }; print(number); print(c()); }''',
    'signature': '''fn apply(f: fn(bool) -> i64) -> i64 { f(true) }
fn main() { let c = |x: i64| { x }; print(apply(c)); }''',
    'moved_callable': '''fn apply(f: fn(i64) -> i64) -> i64 { f(1) }
fn main() { let c = |x: i64| { x }; print(apply(c)); print(c(2)); }''',
    'shared_mutation': '''fn apply(f: &fn() -> i64) -> i64 { f() }
fn main() { let mut n: i64 = 0; let mut c = move || { n += 1; n }; print(apply(&c)); }''',
    'missing_move': '''struct R { value: i64 }
fn main() { let r = R { value: 7 }; let c = || { let view = &r; (*view).value }; print(c()); }''',
    'dangling_capture': '''fn main() {
    let c = { let n: i64 = 7; let view = &n; || { *view } };
    print(c());
}''',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corboc', type=Path, required=True)
    parser.add_argument('--keep', type=Path, required=True)
    parser.add_argument('--cc', default='cc')
    args = parser.parse_args()
    compiler = args.corboc.resolve()
    keep = args.keep.resolve()
    keep.mkdir(parents=True, exist_ok=True)
    evidence = []

    def emit(name, source):
        path = keep / (name + '.crb')
        path.write_text(source)
        return subprocess.run([compiler, '--emit-c', path], capture_output=True, timeout=120)

    for name, expected in ACCEPTED.items():
        fixture = ROOT / 'validation/fixtures/callables' / name
        if (fixture / 'package.toml').exists():
            result = subprocess.run([compiler, '--emit-package-c', fixture, '--stdlib-dir',
                                     ROOT / '.deps/corbo/stdlib/src'], capture_output=True, timeout=120)
        else:
            source = fixture.with_suffix('.crb').read_text()
            result = emit(name, source)
        assert result.returncode == 0 and result.stdout.startswith(b'/'), (
            name, result.returncode, result.stdout[:400], result.stderr)
        c = keep / (name + '.c')
        c.write_bytes(result.stdout)
        binary = keep / name
        subprocess.run([*shlex.split(args.cc), '-std=c11', '-pthread', '-O1',
                        '-fsanitize=undefined', '-fno-sanitize-recover=all',
                        c, '-lm', '-o', binary], check=True, timeout=120)
        run = subprocess.run([binary], capture_output=True, text=True, timeout=15)
        assert (run.returncode, run.stdout, run.stderr) == (0, expected, ''), (name, run)
        evidence.append({'name': name, 'accepted': True, 'stdout': run.stdout})
        print('executed:', name, flush=True)

    for name, source in REJECTED.items():
        result = emit(name, source)
        assert result.returncode == 8, (name, result.returncode, result.stdout[:400], result.stderr)
        evidence.append({'name': name, 'accepted': False, 'status': result.returncode,
                         'diagnostic': result.stdout.decode()})
        print('refused:', name, flush=True)

    report = {'platform': platform.platform(), 'compiler': str(compiler),
              'cflags': '-O1 -fsanitize=undefined -fno-sanitize-recover=all',
              'cases': evidence, 'scope': 'general callables; no broad corpus or platform campaign'}
    (keep / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Completed:', len(ACCEPTED), 'executions and', len(REJECTED), 'rejections')


if __name__ == '__main__':
    main()
