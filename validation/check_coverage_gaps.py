#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Replay reported documentation gaps and their directly affected rule boundaries."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    'reference_return': '42\n', 'scalar_contract': '42\n', 'branch_wrapper': '',
    'address_operand': '42\n', 'numeric_try_from': '255\n',
    'borrowed_text_len': '2\n', 'byte_content_eq': 'true\n',
    'exclusive_receiver': '43\n', 'buffered_custom_sink': '',
    'contract_output_inference': '42\n', 'contract_relay': '42\n',
    'borrow_chain': '42\n', 'contract_two_types': '20\n22\n',
    'branch_result': '42\n', 'buffered_count': '2\n',
    'numeric_bounds': '0\n255\nfalse\nfalse\n',
    'numeric_exact': 'true\ntrue\ntrue\ntrue\ntrue\n',
    'lock_drop_release': '42\n',
}
REJECT = {'reject_dangling': 4, 'reject_loan_write': 5,
          'reject_contract': 1, 'reject_address_escape': 4,
          'reject_double_reserve': 5, 'reject_lock_after_use': 5,
          'reject_shared_field_write': 5}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corboc', type=Path, required=True)
    parser.add_argument('--stdlib', type=Path, default=ROOT/'.deps/corbo/stdlib/src')
    parser.add_argument('--keep', type=Path, default=ROOT/'build/coverage-gaps')
    parser.add_argument('--only')
    parser.add_argument('--jobs', type=int, default=3)
    args = parser.parse_args()
    compiler = args.corboc.resolve()
    args.keep = args.keep.resolve(); args.keep.mkdir(parents=True, exist_ok=True)
    names = list(EXPECTED) + list(REJECT)
    if args.only:
        names = [name for name in names if name in args.only.split(',')]
        if not names: parser.error('unknown case')

    def run(name):
        output = args.keep/name; output.mkdir(exist_ok=True)
        result = subprocess.run([compiler, '--emit-package-c',
                                 ROOT/'validation/fixtures/coverage_gaps'/name,
                                 '--stdlib-dir', args.stdlib.resolve()],
                                capture_output=True, timeout=120)
        (output/'corboc.stderr').write_bytes(result.stderr)
        if name in REJECT:
            diagnostic = result.stdout.decode(errors='replace')
            passed = result.returncode == 8 and diagnostic.splitlines()[:1] == [str(REJECT[name])]
            (output/'corboc.stdout').write_text(diagnostic)
            return {'name': name, 'passed': passed, 'stage': 'rejection',
                    'status': result.returncode, 'diagnostic': diagnostic}
        if result.returncode:
            (output/'corboc.stdout').write_bytes(result.stdout)
            return {'name': name, 'passed': False, 'stage': 'corboc',
                    'status': result.returncode, 'diagnostic': (result.stdout+result.stderr).decode(errors='replace')[:800]}
        source = output/'program.c'; source.write_bytes(result.stdout)
        result = subprocess.run(['cc', '-std=c11', '-pthread', '-O1',
                                 '-fsanitize=undefined', '-fno-sanitize-recover=all',
                                 source, '-lm', '-o', output/'program'], capture_output=True, timeout=120)
        (output/'cc.stderr').write_bytes(result.stderr)
        if result.returncode:
            return {'name': name, 'passed': False, 'stage': 'C',
                    'diagnostic': result.stderr.decode(errors='replace')[:1500]}
        result = subprocess.run([output/'program'], cwd=output, capture_output=True, text=True, timeout=20)
        (output/'stdout').write_text(result.stdout); (output/'stderr').write_text(result.stderr)
        return {'name': name, 'passed': (result.returncode, result.stdout, result.stderr) == (0, EXPECTED[name], ''),
                'stage': 'execution', 'status': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        rows = list(pool.map(run, names))
    report = {'compiler': str(compiler), 'configuration': 'host, O1, fatal UBSan',
              'cases': rows, 'all_passed': all(row['passed'] for row in rows)}
    (args.keep/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    for row in rows:
        print(('PASS ' if row['passed'] else 'FAIL ')+row['name']+
              ('' if row['passed'] else ' '+json.dumps(row)))
    if not report['all_passed']: raise SystemExit(1)


if __name__ == '__main__':
    main()
