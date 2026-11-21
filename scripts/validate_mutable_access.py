#!/usr/bin/env python3
"""Validate mutation permission, same-lock access and branch-lifetime boundaries."""

import argparse
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ACCEPTED = {
    'mutable_access/aliases': ['true', 'true'],
    'mutable_access/arguments': ['true'],
    'mutable_access/record_aliases': ['true'],
    'mutable_access/inactive_futures': ['true'],
    'mutable_access/three_threads': ['true'],
    'aliased_buffers': ['true'],
    'coverage_gaps/lock_drop_release': ['42'],
    'propagation_binding_cleanup': ['1', 'true'],
    'owned_fixed_fields': ['true', 'true'],
}
REJECTED = {
    'mutable_access/reject_different_locks': 5,
    'mutable_access/reject_unprotected': 5,
    'mutable_access/reject_before_all_joins': 5,
    'mutable_access/reject_future_race': 5,
    'mutable_access/reject_lifetime': 4,
    'mutable_access/reject_owner_drop': 5,
    'mutable_access/reject_early_exit': 8,
    'coverage_gaps/reject_double_reserve': 5,
    'coverage_gaps/reject_lock_after_use': 5,
    'reject_array_move_reuse': 6,
}


def main():
    """Run only the changed mechanisms and their directly related regressions."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corboc', default=str(ROOT / 'build/mutable-access/corboc'))
    parser.add_argument('--stdlib', default=str(ROOT.parent / 'corbo-lang/stdlib/src'))
    parser.add_argument('--cc', default='cc')
    parser.add_argument('--output', default=str(ROOT / 'build/mutable-access/validation'))
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for case in list(ACCEPTED) + list(REJECTED):
        emitted = subprocess.run(
            [str(Path(args.corboc).resolve()), '--emit-package-c',
             str(ROOT / 'validation/fixtures' / case), '--stdlib-dir',
             str(Path(args.stdlib).resolve())], capture_output=True, text=True, timeout=60,
        )
        if case in REJECTED:
            diagnostic = emitted.stdout.split()
            if emitted.returncode not in (8, 9) or not diagnostic or diagnostic[0] != str(REJECTED[case]):
                raise RuntimeError(f'{case}: unexpected verdict {emitted.returncode}: {emitted.stdout}')
            results.append({'case': case, 'status': 'rejected', 'rule': diagnostic[0]})
        else:
            if emitted.returncode:
                raise RuntimeError(f'{case}: compiler exit {emitted.returncode}: {emitted.stdout}')
            stem = case.replace('/', '-')
            source = output / f'{stem}.c'
            source.write_text(emitted.stdout)
            binary = output / stem
            subprocess.run(
                [args.cc, '-O1', '-pthread', '-fsanitize=undefined',
                 '-fno-sanitize-recover=all', str(source), '-lm', '-o', str(binary)], check=True,
            )
            with tempfile.TemporaryDirectory(prefix='corbo-mutable-') as directory:
                run = subprocess.run([str(binary)], cwd=directory, capture_output=True, text=True, timeout=20)
            if run.returncode or run.stdout.split() != ACCEPTED[case]:
                raise RuntimeError(f'{case}: exit {run.returncode}: {run.stdout}\n{run.stderr}')
            results.append({'case': case, 'status': 'executed, fatal UBSan', 'output': run.stdout.split()})
        print(case, results[-1]['status'], flush=True)
    (output / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
    print(f'{len(ACCEPTED)} executions, {len(REJECTED)} rejections')


if __name__ == '__main__':
    main()
