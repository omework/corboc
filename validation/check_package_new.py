#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused CLI checks for package creation, name validation and no-overwrite behavior."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile
import tomllib


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corboc', type=Path, required=True)
    parser.add_argument('--keep', type=Path, default=Path('build/package-new-validation'))
    parser.add_argument('--skip-build', action='store_true', help='for targets without the native build driver')
    args = parser.parse_args()
    compiler = args.corboc.resolve()
    args.keep.mkdir(parents=True, exist_ok=True)
    rows = []
    with tempfile.TemporaryDirectory(prefix='corboc-new-') as temporary:
        root = Path(temporary)
        def run(*arguments):
            return subprocess.run([compiler, *arguments], cwd=root, capture_output=True, text=True, timeout=120)
        def record(name, condition):
            assert condition, name
            rows.append({'case': name, 'passed': True})
            print('PASS', name, flush=True)
        result = run('new', 'sample_db')
        project = root / 'sample_db'
        record('create', result.returncode == 0 and not result.stderr)
        record('scaffold', tomllib.loads((project / 'package.toml').read_text()) == {'package': {'name': 'sample_db'}}
               and (project / 'src/main.crb').read_text() == 'fn main() {\n}\n'
               and (project / '.gitignore').read_text().startswith('/build/\n')
               and (project / 'README.md').read_text().startswith('# sample_db\n')
               and not (project / '.git').exists())
        snapshot = {p.relative_to(project).as_posix(): p.read_bytes() for p in project.rglob('*') if p.is_file()}
        record('existing-package-refused', run('new', 'sample_db').returncode == 11
               and snapshot == {p.relative_to(project).as_posix(): p.read_bytes() for p in project.rglob('*') if p.is_file()})
        (root / 'occupied').write_text('keep me')
        record('existing-file-refused', run('new', 'occupied').returncode == 11 and (root / 'occupied').read_text() == 'keep me')
        (root / 'empty').mkdir()
        record('existing-empty-directory-refused', run('new', 'empty').returncode == 11 and not list((root / 'empty').iterdir()))
        if not args.skip_build:
            result = run('build', str(project))
            record('build-generated-package', result.returncode == 0)
            executable = project / 'build/sample_db'
            result = subprocess.run([executable], capture_output=True, timeout=10)
            record('run-generated-package', result.returncode == 0 and not result.stdout and not result.stderr)
        for label, arguments in [('missing-name', ('new',)), ('extra-argument', ('new', 'other', 'extra'))]:
            result = run(*arguments)
            record(label, result.returncode == 6 and 'usage: corboc new' in result.stderr)
        before = set(root.iterdir())
        for name in ['../escape', 'bad-name', '9name', 'std', 'runtime', 'x' * 256]:
            result = run('new', name)
            assert result.returncode == 6 and 'invalid package name' in result.stderr, (name, result)
        record('invalid-names-have-no-filesystem-effects', set(root.iterdir()) == before and not (root.parent / 'escape').exists())
    (args.keep / 'report.json').write_text(json.dumps({'checks': rows, 'build_exercised': not args.skip_build}, indent=2) + '\n')


if __name__ == '__main__':
    main()
