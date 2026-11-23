#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Check diagnostic recovery on save; optionally observe an unchanged user file."""
import argparse
import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def wait_for(process, log, message):
    """A diagnostic must arrive while watch remains alive, without runtime aborts."""
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        output = log.read_text()
        assert process.poll() is None, ('watch exited', output)
        assert 'corbo: ' not in output, output
        if message in output:
            return output
        time.sleep(0.1)
    raise AssertionError(('watch diagnostic timeout', log.read_text()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler', type=Path, required=True)
    parser.add_argument('--observed-file', type=Path)
    parser.add_argument('--out', type=Path, default=ROOT / 'build/dereference-crash/watch')
    args = parser.parse_args()
    compiler, work = args.compiler.resolve(), args.out.resolve()
    (work / 'src').mkdir(parents=True, exist_ok=True)
    (work / 'package.toml').write_text('[package]\nname="watch_crash"\n')
    source = work / 'src/main.crb'
    source.write_text((ROOT / 'validation/fixtures/reference_methods/unresolved_method.crb').read_text())
    log = work / 'watch.log'
    with log.open('w') as stream:
        process = subprocess.Popen([compiler, 'check', source, '--watch'], stdout=stream, stderr=subprocess.STDOUT)
        try:
            wait_for(process, log, 'check failed')
            source.write_text('fn main() { print(42); }\n')
            wait_for(process, log, 'check passed')
        finally:
            process.terminate()
            process.wait(timeout=5)
    results = {'failure_to_success': 'passed; watcher remained alive'}

    # Read-only observation: never save or fix the developer's actual source.
    if args.observed_file:
        observed = args.observed_file.resolve()
        original = observed.read_bytes()
        log = work / 'observed-watch.log'
        with log.open('w') as stream:
            process = subprocess.Popen([compiler, 'check', observed, '--watch'], stdout=stream, stderr=subprocess.STDOUT)
            try:
                wait_for(process, log, 'check failed')
            finally:
                process.terminate()
                process.wait(timeout=5)
        assert observed.read_bytes() == original, 'observed source changed during the check'
        results['observed_file'] = 'normal diagnostic; watcher remained alive; source unchanged'
    (work / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
    print('Watch recovery passed', flush=True)


if __name__ == '__main__':
    main()
