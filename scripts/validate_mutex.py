#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused public mutex API, ownership and shared-task regression checks."""
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    """Compile three positive programs with fatal UBSan and ten refusal fixtures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler', type=Path, required=True)
    parser.add_argument('--stdlib', type=Path, default=ROOT / '.deps/corbo/stdlib/src')
    parser.add_argument('--out', type=Path, default=ROOT / 'build/mutex-validation')
    args = parser.parse_args()
    compiler = args.compiler.resolve()
    stdlib = args.stdlib.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    results = []
    positives = [('mutex_api', ['42', '42']), ('mutex_threads', ['3', '4']),
                 ('mutex_aggregate', ['41', '99', '99', '41'])]
    for name, expected in positives:
        emitted = subprocess.run([str(compiler), '--emit-package-c',
                                  str(ROOT / 'validation/fixtures' / name),
                                  '--stdlib-dir', str(stdlib)], capture_output=True, text=True, timeout=60)
        assert emitted.returncode == 0, (name, emitted.returncode, emitted.stdout[:500], emitted.stderr)
        source = out / (name + '.c')
        source.write_text(emitted.stdout)
        binary = out / name
        subprocess.run(['cc', '-O1', '-pthread', '-fsanitize=undefined', '-fno-sanitize-recover=all',
                        str(source), '-lm', '-o', str(binary)], check=True)
        run = subprocess.run([str(binary)], capture_output=True, text=True, timeout=20)
        assert run.returncode == 0 and run.stdout.split() == expected and not run.stderr, (name, run)
        results.append({'case': name, 'status': 'executed, fatal UBSan', 'stdout': run.stdout.split()})
        print(name, 'passed', flush=True)
    for source in sorted((ROOT / 'validation/fixtures/mutex_rejections').glob('*.crb')):
        package = out / ('reject-' + source.stem)
        (package / 'src').mkdir(parents=True, exist_ok=True)
        (package / 'package.toml').write_text('[package]\nname="mutex_rejection"\n')
        (package / 'src/main.crb').write_text(source.read_text())
        run = subprocess.run([str(compiler), '--emit-package-c', str(package), '--stdlib-dir', str(stdlib)],
                             capture_output=True, text=True, timeout=30)
        expected_exit = 9 if source.stem == 'checked_interior_mutation' else 13 if source.stem == 'raw_helper' else 8
        assert run.returncode == expected_exit, (source.name, run.returncode, run.stdout[:300])
        results.append({'case': source.stem, 'status': 'rejected', 'exit': run.returncode,
                        'diagnostic': run.stdout.strip()})
        print(source.stem, 'rejected', flush=True)
    (out / 'results.json').write_text(json.dumps(results, indent=2) + '\n')


if __name__ == '__main__':
    main()
