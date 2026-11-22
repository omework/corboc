#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused primitive-copy behavior and non-primitive/lifetime boundary checks."""
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler', type=Path, required=True)
    parser.add_argument('--stdlib', type=Path, default=ROOT / '.deps/corbo/stdlib/src')
    parser.add_argument('--out', type=Path, default=ROOT / 'build/implicit-primitives')
    args = parser.parse_args()
    compiler, stdlib, out = args.compiler.resolve(), args.stdlib.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    def emit(package):
        return subprocess.run([str(compiler), '--emit-package-c', str(package), '--stdlib-dir', str(stdlib)],
                              capture_output=True, text=True, timeout=90)
    results = []
    emitted = emit(ROOT / 'validation/fixtures/implicit_primitives')
    assert emitted.returncode == 0, (emitted.returncode, emitted.stdout[:500], emitted.stderr)
    source = out / 'primitives.c'
    source.write_text(emitted.stdout)
    binary = out / 'primitives'
    subprocess.run(['cc', '-pthread', '-O1', '-fsanitize=undefined', '-fno-sanitize-recover=all',
                    str(source), '-lm', '-o', str(binary)], check=True)
    ran = subprocess.run([str(binary)], capture_output=True, text=True, timeout=30)
    expected = ['true'] * 20 + ['20', '41', '41', '20', '20', '20', '20', '20', '3', '20', '99']
    assert ran.returncode == 0 and ran.stdout.split() == expected and not ran.stderr, (ran.returncode, ran.stdout, ran.stderr)
    results.append({'case': 'primitives, calls, branches, tuples, independent copies, borrows, async and owned cleanup',
                    'status': 'executed, fatal UBSan', 'stdout': ran.stdout.split()})
    print('primitive copy witness passed', flush=True)
    for source in sorted((ROOT / 'validation/fixtures/implicit_primitive_refusals').glob('*.crb')):
        package = out / source.stem
        (package / 'src').mkdir(parents=True, exist_ok=True)
        (package / 'package.toml').write_text('[package]\nname="copy_refusal"\n')
        (package / 'src/main.crb').write_text(source.read_text())
        refused = emit(package)
        assert refused.returncode in (8, 9), (source.name, refused.returncode, refused.stdout[:200])
        results.append({'case': source.stem, 'status': 'rejected', 'exit': refused.returncode,
                        'diagnostic': refused.stdout.strip()})
        print(source.stem, 'rejected', flush=True)
    (out / 'results.json').write_text(json.dumps(results, indent=2) + '\n')


if __name__ == '__main__':
    main()
