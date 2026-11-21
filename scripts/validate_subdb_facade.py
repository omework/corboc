#!/usr/bin/env python3
"""Run only the compiler regressions introduced by the SubDB facade integration."""

import argparse
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ACCEPTED = {
    'contract_method': ['42', '1'],
    'owned_fixed_fields': ['true', 'true'],
    'disjoint_buffers': ['true'],
    'aliased_buffers': ['true'],
    'propagation_binding_cleanup': ['1', 'true'],
}
REJECTED = [
    'reject_contract_method',
    'reject_array_move_reuse',
]


def main():
    """Compile the focused accepted/rejected fixtures and retain their observations."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corboc', default=str(ROOT / 'build/subdb/bin/corboc'))
    parser.add_argument('--stdlib', default=str(ROOT.parent / 'corbo-lang/stdlib/src'))
    parser.add_argument('--cc', default='cc')
    parser.add_argument('--output', default=str(ROOT / 'build/subdb/facade-validation'))
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    observations = []

    for case in list(ACCEPTED) + REJECTED:
        emitted = subprocess.run(
            [str(Path(args.corboc).resolve()), '--emit-package-c',
             str(ROOT / 'validation/fixtures' / case), '--stdlib-dir',
             str(Path(args.stdlib).resolve())],
            capture_output=True, text=True,
        )
        if case in REJECTED:
            if emitted.returncode not in (8, 9):
                raise RuntimeError(f'{case}: expected rejection, got {emitted.returncode}')
            observations.append({'case': case, 'status': 'rejected', 'exit': emitted.returncode})
            continue
        if emitted.returncode:
            raise RuntimeError(f'{case}: compiler exit {emitted.returncode}\n{emitted.stdout}')

        source = output / f'{case}.c'
        source.write_text(emitted.stdout)
        binary = output / case
        subprocess.run(
            [args.cc, '-O1', '-fsanitize=undefined', '-fno-sanitize-recover=all',
             str(source), '-o', str(binary)], check=True,
        )
        with tempfile.TemporaryDirectory(prefix='corboc-subdb-') as directory:
            executed = subprocess.run([str(binary)], cwd=directory, capture_output=True, text=True)
        if executed.returncode or executed.stdout.split() != ACCEPTED[case]:
            raise RuntimeError(f'{case}: exit {executed.returncode}\n{executed.stdout}\n{executed.stderr}')
        observations.append({
            'case': case, 'status': 'executed, fatal UBSan', 'output': executed.stdout.split(),
        })

    text = json.dumps(observations, indent=2) + '\n'
    (output / 'results.json').write_text(text)
    print(text, end='')


if __name__ == '__main__':
    main()
