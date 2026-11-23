#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused nominal receiver checks: structs/enums, moves and borrow permissions."""
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--compiler', type=Path, required=True)
p.add_argument('--out', type=Path, default=ROOT / 'build/enum-methods/evidence')
a = p.parse_args()
compiler, out = a.compiler.resolve(), a.out.resolve()
out.mkdir(parents=True, exist_ok=True)
results = []


def emit(package):
    return subprocess.run([compiler, '--emit-package-c', package, '--stdlib-dir',
                           ROOT / '.deps/corbo/stdlib/src'], capture_output=True,
                          text=True, timeout=120)


accepted = emit(ROOT / 'validation/fixtures/enum_methods')
assert accepted.returncode == 0, (accepted.returncode, accepted.stdout[:500], accepted.stderr)
c = out / 'methods.c'
c.write_text(accepted.stdout)
binary = out / 'methods'
subprocess.run(['cc', '-pthread', '-O1', '-fsanitize=undefined',
                '-fno-sanitize-recover=all', c, '-lm', '-o', binary], check=True)
ran = subprocess.run([binary], text=True, capture_output=True, timeout=20)
expected = ['true', '42', '42', 'true', '7', '12', '101', '101', '42', '43', '42']
assert ran.returncode == 0 and ran.stdout.split() == expected and not ran.stderr, (ran.returncode, ran.stdout, ran.stderr)
results.append({'case': 'nominal receivers and cleanup', 'status': 'fatal UBSan passed', 'output': expected})
print('nominal receivers and cleanup passed', flush=True)

base = '''enum Counter { Value(i64), Empty }
impl Counter {
    fn update(&mut self) {
        match &mut *self { Counter.Value(n) => { *n = 12; }, Counter.Empty => {} }
    }
}
'''
refusals = {
    'immutable receiver': (base + 'fn main(){let c=Counter.Value(1);c.update();}', 5),
    'shared reference receiver': (base + 'fn main(){let c=Counter.Value(1);let r=&c;r.update();}', 5),
    'moved receiver': ('''struct Data { value:i64 }
enum Owner { Item(Data), Empty }
impl Owner { fn finish(self:Owner)->i64{42} }
fn main(){let o=Owner.Item(Data{value:1});print(o.finish());print(o.finish());}''', 6),
    'reference after drop': ('''enum Counter { Value(i64) }
impl Counter { fn read(&self)->i64{42} }
fn main(){let c=Counter.Value(1);let r=&c;drop(c);print(r.read());}''', 5),
}
for name, (source, rule) in refusals.items():
    package = out / name.replace(' ', '_')
    (package / 'src').mkdir(parents=True, exist_ok=True)
    (package / 'package.toml').write_text('[package]\nname="enum_refusal"\n')
    (package / 'src/main.crb').write_text(source)
    rejected = emit(package)
    assert rejected.returncode == 8 and rejected.stdout.split()[0] == str(rule), (name, rejected.returncode, rejected.stdout[:500], rejected.stderr)
    results.append({'case': name, 'status': 'rejected', 'rule': rule})
    print(name, 'rejected', flush=True)
(out / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
