#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused package build defaults, manifest options and publication checks."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corboc', type=Path, required=True)
    parser.add_argument('--keep', type=Path, default=ROOT/'build/package-build/validation')
    args = parser.parse_args()
    compiler = args.corboc.resolve()
    work = args.keep.resolve()
    work.mkdir(parents=True, exist_ok=True)
    report = []

    def package(name, manifest, source='fn main(){print(42);}\n'):
        path = work/name
        (path/'src').mkdir(parents=True, exist_ok=True)
        (path/'package.toml').write_text(manifest)
        (path/'src/main.crb').write_text(source)
        return path

    def build(name, cwd, arguments, binary=None, expected=0, diagnostic=None):
        result = subprocess.run([compiler, 'build', *map(str, arguments)], cwd=cwd,
                                capture_output=True, text=True, timeout=120)
        passed = result.returncode == expected
        if diagnostic is not None:
            passed = passed and diagnostic in result.stderr
        row = {'name':name, 'status':result.returncode, 'stdout':result.stdout,
               'stderr':result.stderr, 'passed':passed}
        if expected == 0:
            passed = passed and binary.is_file()
            if binary.is_file():
                executed = subprocess.run([binary], capture_output=True, text=True, timeout=30)
                row['execution'] = {'status':executed.returncode, 'stdout':executed.stdout,
                                    'stderr':executed.stderr}
                passed = passed and executed.returncode == 0 and executed.stdout == '42\n' and not executed.stderr
        row['passed'] = bool(passed)
        report.append(row)
        print(('PASS' if passed else 'FAIL')+' '+name, flush=True)
        return passed

    default = package('default', '[package]\nname="demo"\n')
    build('package_name_default', default, [], default/'build/demo')
    build('existing_build_directory', default, [], default/'build/demo')
    configured = package('configured', '[package]\nname="demo"\n[bin] # Binary filename\nname="api-server"\n')
    build('configured_name', configured, [], configured/'build/api-server')
    build('cwd_output_override', configured, ['-o', 'override'], configured/'override')
    empty = package('empty_bin', '[bin]\n[package]\nname="fallback"\n')
    build('empty_bin_default', empty, [], empty/'build/fallback')
    external = package('package with spaces', '[package]\nname="external"\n')
    build('explicit_package_default', work, [external], external/'build/external')
    build('legacy_explicit_output', work, [external, '-o', 'legacy'], work/'legacy')

    dependency = package('numbers', '[package]\nname="numbers"\n[bin]\nname="unused-library-name"\n',
                         'pub fn answer()->i64{42}\n')
    dependencies = '[dependencies]\nnumbers={path="../numbers"}\n'
    binary = '[bin]\nname="from-dependency"\n'
    for name, sections in [('bin_before_dependencies', binary+dependencies),
                           ('bin_after_dependencies', dependencies+binary)]:
        app = package(name, '[package]\nname="app"\n'+sections,
                      'use app::helper::answer;fn main(){print(answer());}\n')
        (app/'src/helper').mkdir(exist_ok=True)
        (app/'src/helper/helper.crb').write_text('use numbers::answer as original;use std::num::min_i64;pub fn answer()->i64{min_i64(original(),50)}\n')
        build(name, app, [], app/'build/from-dependency')

    for name, extra in [('empty_name','name=""\n'),
                        ('name_is_path','name="../escape"\n'),
                        ('duplicate_name','name="first"\nname="second"\n'),
                        ('duplicate_bin','[bin]\n')]:
        invalid = package(name, '[package]\nname="invalid"\n[bin]\n'+extra)
        build(name, invalid, [], expected=12, diagnostic='invalid package manifest')
        assert not (work/'escape').exists()
    missing = work/'missing';missing.mkdir(exist_ok=True)
    build('missing_manifest', missing, [], expected=11, diagnostic='cannot read package binary settings')
    blocked = package('blocked', '[package]\nname="blocked"\n')
    (blocked/'build').write_text('keep me')
    build('build_directory_is_file', blocked, [], expected=11, diagnostic='cannot create build directory')
    assert (blocked/'build').read_text() == 'keep me'
    build('missing_output_argument', default, ['-o'], expected=6, diagnostic='usage: corboc build')
    previous = hashlib.sha256((default/'build/demo').read_bytes()).hexdigest()
    (default/'src/main.crb').write_text('fn main(\n')
    build('failed_build', default, [], expected=7, diagnostic='package compilation failed')
    retained = hashlib.sha256((default/'build/demo').read_bytes()).hexdigest() == previous
    cleaned = not list((default/'build').glob('.corboc.*'))
    report.append({'name':'failed_build_preserves_binary_and_cleans_workspace', 'passed':retained and cleaned})
    print(('PASS' if retained and cleaned else 'FAIL')+' failed_build_preserves_binary_and_cleans_workspace')
    (work/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    raise SystemExit(0 if all(row['passed'] for row in report) else 1)


if __name__ == '__main__':
    main()
