#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused installed-CLI checks: package verification and save/watch recovery."""
import argparse
import json
import os
from pathlib import Path
import queue
import subprocess
import tempfile
import threading
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler', required=True, type=Path)
    parser.add_argument('--out', type=Path, default=Path('build/check-validation/results.json'))
    args = parser.parse_args()
    compiler = args.compiler.resolve()
    results = []
    with tempfile.TemporaryDirectory(prefix='corboc-check-') as tmp:
        base = Path(tmp)
        package = base / 'project'
        (package / 'src/helper').mkdir(parents=True)
        manifest = package / 'package.toml'
        valid_manifest = '[package]\nname="project"\n'
        manifest.write_text(valid_manifest)
        main_file = package / 'src/main.crb'
        main_file.write_text('use project::helper::answer;\nfn main() { print(answer()); }\n')
        helper = package / 'src/helper/helper.crb'
        good = 'pub fn answer() -> i64 { 42 }\n'
        helper.write_text(good)
        # With no cc, linker or executable on PATH, successful checks still work.
        env = dict(os.environ, PATH=str(base / 'empty-path'))

        def check(name, arguments, expected=0, cwd=base):
            run = subprocess.run([str(compiler), *map(str, arguments)], cwd=cwd,
                                 env=env, capture_output=True, text=True, timeout=30)
            assert run.returncode == expected, (name, run.returncode, run.stdout[:400], run.stderr)
            assert '#include' not in run.stdout, (name, 'unexpected emitted C')
            results.append({'case': name, 'exit': run.returncode})
            print(name, 'passed', flush=True)
            return run

        check('current two-module package without C toolchain', ['check'], cwd=package)
        check('explicit package', ['check', package])
        alias = base / 'corboc-symlink'
        if os.name != 'nt':
            alias.symlink_to(compiler)
            run = subprocess.run([str(alias), 'check', str(package)], cwd=base,
                                 env=env, capture_output=True, text=True, timeout=30)
            assert run.returncode == 0, ('installed executable symlink', run.returncode, run.stderr)
            results.append({'case': 'installed executable symlink', 'exit': 0})
        assert not (package / 'build').exists()
        helper.write_text('pub fn answer() -> i64 { unknown }\n')
        check('semantic error in imported module', ['check', package], 8)
        helper.write_text('pub fn answer() -> i64 { let = }\n')
        check('syntax error in imported module', ['check', package], 7)
        helper.write_text(good)
        original = main_file.read_text()
        fixture = Path(__file__).resolve().parents[1] / 'validation/fixtures/mutex_rejections/destroy_owner.crb'
        main_file.write_text(fixture.read_text())
        check('owner destruction with live guard', ['check', package], 8)
        main_file.write_text(original)
        for options in [['check', '--bogus'], ['check', '--watch', '--watch'],
                        ['check', package, '--watch', 'extra']]:
            check('invalid CLI arguments', options, 6)
        check('missing package', ['check', base / 'missing'], 11)
        dependency = base / 'dependency'
        (dependency / 'src').mkdir(parents=True)
        (dependency / 'package.toml').write_text('[package]\nname="dependency"\n')
        (dependency / 'src/lib.crb').write_text('pub fn value() -> i64 { 17 }\n')
        manifest.write_text(valid_manifest + '\n[dependencies]\ndependency = { path = "../dependency" }\n')
        original_main = main_file.read_text()
        main_file.write_text('use dependency::value;\nfn main() { print(value()); }\n')
        check('path dependency resolution', ['check', package])
        main_file.write_text(original_main)
        manifest.write_text(valid_manifest)

        # One directly related regression: the shared package path still emits
        # and builds normally when invoked through build instead of check.
        if os.name != 'nt' and os.uname().sysname == 'Darwin' and os.uname().machine == 'arm64':
            binary = base / 'built-program'
            built = subprocess.run([str(compiler), 'build', str(package), '-o', str(binary)],
                                   cwd=base, capture_output=True, text=True, timeout=30)
            assert built.returncode == 0, ('normal build regression', built.returncode, built.stdout, built.stderr)
            ran = subprocess.run([str(binary)], capture_output=True, text=True, timeout=10)
            assert ran.returncode == 0 and ran.stdout.split() == ['42'], ran
            results.append({'case': 'shared compilation path still builds executable', 'exit': 0})

        # Read stderr asynchronously so assertions can time out without hanging.
        lines = queue.Queue()
        process = subprocess.Popen([str(compiler), 'check', '--watch', str(package)],
                                   cwd=base, env=env, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.PIPE, text=True, bufsize=1)
        def consume():
            for line in process.stderr:
                lines.put(line.strip())
        reader = threading.Thread(target=consume, daemon=True)
        reader.start()

        def wait_for(fragment, timeout=12):
            deadline = time.monotonic() + timeout
            seen = []
            while time.monotonic() < deadline:
                assert process.poll() is None, ('watch exited', process.returncode, seen)
                try:
                    line = lines.get(timeout=min(.2, max(.01, deadline-time.monotonic())))
                except queue.Empty:
                    continue
                seen.append(line)
                if fragment in line:
                    return
            raise AssertionError(('watch timed out', fragment, seen))

        try:
            wait_for('check passed')
            wait_for('watching sources')
            # Same-size replacement catches changes without relying on mtime/size.
            helper.write_text(good.replace('42', '43'))
            wait_for('check passed')
            helper.write_text('pub fn answer() -> i64 { missing }\n')
            wait_for('check failed')
            # Model editor save-by-rename and ensure error recovery.
            replacement = helper.with_suffix('.tmp')
            replacement.write_text(good)
            replacement.replace(helper)
            wait_for('check passed')
            extra = package / 'src/added.crb'
            extra.write_text('fn added() { let = }\n')
            wait_for('check failed')
            extra.unlink()
            wait_for('check passed')
            manifest.write_text('[package]\nname=\n')
            wait_for('check failed')
            manifest.write_text(valid_manifest)
            wait_for('check passed')
            # Generated/hidden files must not trigger the check loop.
            (package / 'build').mkdir()
            (package / 'build/ignored.crb').write_text('invalid')
            (package / '.ignored.crb').write_text('invalid')
            time.sleep(1.0)
            ignored = []
            while not lines.empty():
                ignored.append(lines.get_nowait())
            assert not any('checking package' in line for line in ignored), ignored
            assert process.poll() is None
            assert not list(package.glob('.corboc.*'))
            results.append({'case': 'watch saves, errors, recovery, atomic replacement, add/delete, manifest and ignored outputs', 'status': 'passed'})
            print('watch transitions passed', flush=True)
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            process.stderr.close()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2) + '\n')


if __name__ == '__main__':
    main()
