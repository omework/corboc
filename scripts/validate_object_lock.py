#!/usr/bin/env python3
"""Validate only object-lock inheritance, checked re-entry and direct regressions."""

import argparse
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ACCEPTED = {
    'helpers': ['true', 'true'],
    'unmarked': ['true'],
    'generic': ['true'],
    'module': ['true'],
    'through_result': ['42'],
    'three_threads': ['true'],
}
REJECTED = {
    'reject_direct': 5,
    'reject_indirect': 5,
    'reject_recursion': 5,
    'reject_alias': 5,
    'reject_possible_alias': 5,
    'reject_function_helper': 5,
    'reject_generic_reentry': 5,
    'reject_marker_on_method': 1,
    'reject_duplicate': 1,
    'reject_enum': 1,
}


def main():
    """Run bounded semantic and syntax checks without a broad legacy campaign."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corboc', default=str(ROOT / 'build/object-lock/corboc'))
    parser.add_argument('--stdlib', default=str(ROOT / '.deps/corbo/stdlib/src'))
    parser.add_argument('--output', default=str(ROOT / 'build/object-lock/validation'))
    args = parser.parse_args()
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for name in list(ACCEPTED) + list(REJECTED):
        emitted = subprocess.run(
            [str(Path(args.corboc).resolve()), '--emit-package-c',
             str(ROOT / 'validation/fixtures/object_lock' / name),
             '--stdlib-dir', str(Path(args.stdlib).resolve())], capture_output=True, text=True, timeout=60,
        )
        if name in REJECTED:
            assert emitted.returncode == 8 and emitted.stdout.split()[0] == str(REJECTED[name]), (name, emitted.returncode, emitted.stdout[:160])
            result = {'case': name, 'status': 'rejected', 'rule': REJECTED[name]}
        else:
            assert emitted.returncode == 0, (name, emitted.returncode, emitted.stdout[:160])
            source = out / f'{name}.c'
            source.write_text(emitted.stdout)
            binary = out / name
            subprocess.run(['cc', '-O1', '-pthread', '-fsanitize=undefined', '-fno-sanitize-recover=all', str(source), '-lm', '-o', str(binary)], check=True)
            with tempfile.TemporaryDirectory(prefix='corbo-object-lock-') as directory:
                run = subprocess.run([str(binary)], cwd=directory, capture_output=True, text=True, timeout=20)
            assert run.returncode == 0 and run.stdout.split() == ACCEPTED[name], (name, run.returncode, run.stdout, run.stderr)
            result = {'case': name, 'status': 'executed, fatal UBSan', 'output': run.stdout.split()}
        results.append(result)
        print(name, result['status'], flush=True)
    (out / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
    print(f'{len(ACCEPTED)} executions, {len(REJECTED)} rejections')


if __name__ == '__main__':
    main()
