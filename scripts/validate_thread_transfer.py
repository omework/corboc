#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Exercise thread-transfer composition and ordinary same-thread moves only."""

import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ACCEPTED = {
    'local_moves': ['42'],
    'local_closure': ['42'],
    'fresh_worker': ['true'],
    'default_worker': ['true'],
    'async_local_cleanup': ['42', 'true'],
}


def main():
    """Emit bounded fixtures and execute accepted paths with fatal UBSan."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corboc', default=str(ROOT / 'build/thread-transfer/corboc'))
    args = parser.parse_args()
    compiler = str(Path(args.corboc).resolve())
    output = ROOT / 'build/thread-transfer/validation'
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for package in sorted((ROOT / 'validation/fixtures/thread_transfer').iterdir()):
        emitted = subprocess.run(
            [compiler, '--emit-package-c', str(package),
             '--stdlib-dir', str(ROOT / '.deps/corbo/stdlib/src')],
            capture_output=True, text=True, timeout=60,
        )
        name = package.name
        if name.startswith('reject_'):
            expected = 1 if name in ('reject_placement', 'reject_duplicate') else 8
            assert emitted.returncode == 8 and emitted.stdout.split()[0] == str(expected), (
                name, emitted.returncode, emitted.stdout[:160], emitted.stderr[:160],
            )
            result = {'case': name, 'status': 'rejected', 'rule': expected}
        else:
            assert emitted.returncode == 0, (name, emitted.returncode, emitted.stdout[:160])
            source = output / f'{name}.c'
            source.write_text(emitted.stdout)
            binary = output / name
            subprocess.run(
                ['cc', '-O1', '-pthread', '-fsanitize=undefined',
                 '-fno-sanitize-recover=all', str(source), '-lm', '-o', str(binary)],
                check=True,
            )
            executed = subprocess.run([str(binary)], capture_output=True, text=True, timeout=20)
            assert executed.returncode == 0 and executed.stdout.split() == ACCEPTED[name], (
                name, executed.returncode, executed.stdout, executed.stderr,
            )
            result = {'case': name, 'status': 'executed, fatal UBSan', 'output': executed.stdout.split()}
        results.append(result)
        print(name, result['status'], flush=True)
    (output / 'results.json').write_text(json.dumps(results, indent=2) + '\n')


if __name__ == '__main__':
    main()
