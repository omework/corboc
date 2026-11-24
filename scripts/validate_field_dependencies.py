#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused sibling-field dependencies and overlapping mutable-borrow checks."""
import argparse
import json
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--compiler', type=Path, required=True)
p.add_argument('--out', type=Path, default=ROOT/'build/field-dependencies/results.json')
p.add_argument('--case', action='append')
a = p.parse_args()
compiler = a.compiler.resolve()
expected = {'async_file':'2', 'async_siblings':'42 42', 'sync_siblings':'42 42', 'successive_mut':'3', 'disjoint_mut_fields':'1 2'}
results = []
for source in sorted((ROOT/'validation/fixtures/field_dependencies').glob('*.crb')):
    name = source.stem
    if a.case and name not in a.case:
        continue
    work = a.out.resolve().parent/name
    (work/'src').mkdir(parents=True,exist_ok=True)
    (work/'package.toml').write_text('[package]\nname="field_dependencies"\n')
    (work/'src/main.crb').write_text(source.read_text())
    emit = subprocess.run([compiler,'--emit-package-c',work,'--stdlib-dir',ROOT/'.deps/corbo/stdlib/src'],capture_output=True,text=True,timeout=60)
    assert 'corbo: ' not in emit.stderr, (name,emit.returncode,emit.stderr,emit.stdout[-1500:] if emit.returncode else "unexpected acceptance")
    if name in expected:
        assert emit.returncode==0, (name,emit.returncode,emit.stderr,emit.stdout[-1500:] if emit.returncode else "unexpected acceptance")
        c=work/'main.c';c.write_text(emit.stdout);binary=work/'main'
        built=subprocess.run(['cc','-pthread','-O1','-fsanitize=undefined','-fno-sanitize-recover=all',c,'-lm','-o',binary],capture_output=True,text=True)
        assert built.returncode==0,(name,built.stderr)
        run=subprocess.run([binary],capture_output=True,text=True,timeout=20)
        assert run.returncode==0 and not run.stderr and run.stdout.split()==expected[name].split(),(name,run)
        results.append({'case':name,'status':'passed, fatal UBSan','stdout':run.stdout})
        if name == 'async_file':
            Path('/tmp/corboc-field-dependency-wal').unlink(missing_ok=True)
    else:
        assert emit.returncode==8,(name,emit.returncode,emit.stderr,emit.stdout[-1500:] if emit.returncode else "unexpected acceptance")
        results.append({'case':name,'status':'rule refusal','diagnostic':emit.stdout})
    print(name,results[-1]['status'],flush=True)
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(results,indent=2)+'\n')
