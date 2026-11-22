#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused enum-pattern, equality and copy integration checks; no broad corpus run."""
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler', type=Path, required=True)
    parser.add_argument('--stdlib', type=Path, default=ROOT / '.deps/corbo/stdlib/src')
    parser.add_argument('--language', type=Path, default=ROOT.parent / 'corbo-lang')
    parser.add_argument('--out', type=Path, default=ROOT / 'build/enums')
    args = parser.parse_args()
    compiler, stdlib, out = args.compiler.resolve(), args.stdlib.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    def emit(package):
        return subprocess.run([str(compiler), '--emit-package-c', str(package), '--stdlib-dir', str(stdlib)],
                              capture_output=True, text=True, timeout=90)

    cases = [
        ('enum_values', ROOT / 'validation/fixtures/enum_values',
         ['true', 'false', '12', '7', '12', '7', 'true', 'true', 'true', 'true', '2',
          'true', '1', '1', '1', 'true', 'true', '9', '8', 'true', '42']),
        ('enum_equality', ROOT / 'validation/fixtures/enum_equality',
         ['true', '3', 'true', 'false', 'true', 'true', 'true', 'true', 'true', 'true', 'true', 'true']),
        ('enum_ownership', ROOT / 'validation/fixtures/enum_ownership',
         ['7', '7', '9', '101', '101', '102', '2', '103', '103', '104', '105']),
        ('readme_enums', args.language.resolve() / 'examples/features/enums', ['true', '42', '42']),
    ]
    results = []
    for name, package, expected in cases:
        emitted = emit(package)
        assert emitted.returncode == 0, (name, emitted.returncode, emitted.stdout[:500], emitted.stderr)
        source, binary = out / (name + '.c'), out / name
        source.write_text(emitted.stdout)
        subprocess.run(['cc', '-pthread', '-O1', '-fsanitize=undefined', '-fno-sanitize-recover=all',
                        str(source), '-lm', '-o', str(binary)], check=True)
        ran = subprocess.run([str(binary)], capture_output=True, text=True, timeout=30)
        assert ran.returncode == 0 and ran.stdout.split() == expected and not ran.stderr, (name, ran.returncode, ran.stdout, ran.stderr)
        results.append({'case': name, 'status': 'executed with fatal UBSan', 'stdout': ran.stdout.split()})
        print(name, 'passed', flush=True)

    for source in sorted((ROOT / 'validation/fixtures/enum_refusals').glob('*.crb')):
        package = out / ('reject_' + source.stem)
        (package / 'src').mkdir(parents=True, exist_ok=True)
        (package / 'package.toml').write_text('[package]\nname="enum_refusal"\n')
        (package / 'src/main.crb').write_text(source.read_text())
        rejected = emit(package)
        assert rejected.returncode in (8, 9), (source.name, rejected.returncode, rejected.stdout[:100], rejected.stderr)
        results.append({'case': source.stem, 'status': 'rejected', 'exit': rejected.returncode,
                        'diagnostic': rejected.stdout.strip()})
        print(source.stem, 'rejected', flush=True)
    (out / 'results.json').write_text(json.dumps(results, indent=2) + '\n')


if __name__ == '__main__':
    main()
