#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Selected-file diagnostics, import context and watch recovery."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from validate_file_watch import Watch

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--compiler', type=Path, required=True)
parser.add_argument('--out', type=Path, default=Path('build/check-focus/results.json'))
args = parser.parse_args()
results = []
with tempfile.TemporaryDirectory(prefix='corboc-check-focus-') as temporary:
    base = Path(temporary).resolve()
    prefix = base / 'install'
    (prefix / 'bin').mkdir(parents=True)
    compiler = prefix / 'bin/corboc'
    shutil.copy2(args.compiler.resolve(), compiler)
    (prefix / 'share/corbo/stdlib/src').mkdir(parents=True)
    project = base / 'project'
    for directory in ['target', 'helper', 'unrelated', 'service/child', 'other']:
        (project / 'src' / directory).mkdir(parents=True)
    (project / 'package.toml').write_text('[package]\nname="project"\n')
    main = project / 'src/main.crb'
    main.write_text('fn main(){let =;}\n')
    unrelated = project / 'src/unrelated/unrelated.crb'
    unrelated.write_text('pub fn wrong(){let =;}\n')
    selected = project / 'src/target/target.crb'
    helper = project / 'src/helper/helper.crb'
    helper.write_text('pub fn answer()->i64{42}\n')
    good = 'use project::helper::answer;\npub fn value()->i64{answer()}\n'
    selected.write_text('pub fn value()->i64{missing_selected}\n')
    env = dict(os.environ, PATH=str(base / 'empty-path'))

    def check(name, target, expect=0, contains=None):
        ran = subprocess.run([compiler, 'check', target], cwd=base, env=env,
                             capture_output=True, text=True, timeout=30)
        text = ran.stdout + ran.stderr
        assert ran.returncode == expect, (name, ran.returncode, text)
        if contains: assert contains in text, (name, text)
        if target == selected:
            assert str(main) + ':' not in text and str(unrelated) + ':' not in text, (name, text)
        results.append({'case': name, 'exit': ran.returncode})
        print(name, 'passed', flush=True)

    check('selected semantic error precedes unrelated syntax errors', selected, 8, 'missing_selected')
    selected.write_text('pub fn value(){let =;}\n')
    check('selected syntax error retains its file location', selected, 7, str(selected) + ':1:')
    selected.write_text(good)
    check('valid module ignores unrelated main and module errors', selected)
    helper.write_text('pub fn answer()->i64{missing_dependency}\n')
    check('required dependency remains checked', selected, 8, str(helper) + ':1:')
    helper.write_text('pub fn answer()->i64{42}\n')
    companion = selected.with_name('companion.crb')
    companion.write_text('fn companion()->i64{7}\n')
    selected.write_text('pub fn value()->i64{companion()}\n')
    check('module companions remain visible', selected)
    selected.write_text(good)
    check('directory check still reports package errors', project, 7)

    # Aliases retain namespace identity, including qualified children.
    service = project / 'src/service/service.crb'
    service.write_text('pub fn answer()->i64{42}\n')
    child = project / 'src/service/child/child.crb'
    child.write_text('pub fn answer()->i64{42}\n')
    other = project / 'src/other/other.crb'
    other.write_text('pub fn answer()->i64{1}\n')
    selected.write_text('use project::service as svc;\npub fn value()->i64{svc::child::answer()}\n')
    check('module alias preserves qualified descendants', selected)
    selected.write_text('use project::{service as svc, other};\npub fn value()->i64{svc::answer()+other::answer()}\n')
    # The root module is an import context for this grouped namespace.
    main.write_text('fn main(){}\n')
    check('grouped namespace aliases preserve all members', selected)

    # An unselected target branch must not pull in its broken import.
    selected.write_text('''#(if: target.os == "unsupported-test-os")
use project::unrelated::wrong;
#(endif)
pub fn value()->i64{42}
''')
    check('excluded target import does not select unrelated source', selected)

    selected.write_text(good)
    main.write_text('fn main(){let =;}\n')
    watch = Watch(compiler, selected, env, base)
    try:
        watch.wait('check passed'); watch.wait('watching sources')
        selected.write_text('pub fn value()->i64{missing_selected}\n')
        watch.wait(str(selected) + ':'); watch.wait('check failed')
        helper.write_text('pub fn answer()->i64{42}\n// dependency save\n')
        watch.wait(str(selected) + ':'); watch.wait('check failed')
        selected.write_text(good)
        watch.wait('check passed')
        helper.write_text('pub fn answer()->i64{missing_dependency}\n')
        watch.wait(str(helper) + ':'); watch.wait('check failed')
        helper.write_text('pub fn answer()->i64{42}\n')
        watch.wait('check passed')
        results.append({'case': 'watch preserves target, imports and recovery', 'status': 'passed'})
        print('watch preserves target, imports and recovery passed', flush=True)
    finally:
        watch.close()
args.out.parent.mkdir(parents=True, exist_ok=True)
args.out.write_text(json.dumps(results, indent=2) + '\n')
