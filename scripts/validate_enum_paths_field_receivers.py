#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused enum qualification, field receivers and associated diagnostic checks."""
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--compiler', type=Path, required=True)
p.add_argument('--out', type=Path, default=ROOT / 'build/enum-paths-field-methods/evidence')
a = p.parse_args()
compiler, out = a.compiler.resolve(), a.out.resolve()
out.mkdir(parents=True, exist_ok=True)
results = []
for name, expected in [
    ('enum_paths', ['42', '7', '0', '42', '1', '9', '11', '0', '0']),
    ('field_receivers', ['40', '44', '42']),
    ('field_mutex', ['42']),
]:
    emitted = subprocess.run([compiler, '--emit-package-c', ROOT / 'validation/fixtures' / name,
                              '--stdlib-dir', ROOT / '.deps/corbo/stdlib/src'],
                             capture_output=True, text=True, timeout=120)
    assert emitted.returncode == 0, (name, emitted.returncode, emitted.stdout[:600], emitted.stderr)
    source, binary = out / (name + '.c'), out / name
    source.write_text(emitted.stdout)
    subprocess.run(['cc', '-pthread', '-O1', '-fsanitize=undefined', '-fno-sanitize-recover=all',
                    source, '-lm', '-o', binary], check=True)
    ran = subprocess.run([binary], capture_output=True, text=True, timeout=20)
    assert ran.returncode == 0 and ran.stdout.split() == expected and not ran.stderr, (name, ran)
    results.append({'case': name, 'status': 'fatal UBSan passed', 'output': expected})
    print(name, 'passed', flush=True)

mutex = 'use std::sync::asyn::Mutex; struct Data{value:i64} struct Holder{mutex:Mutex<Data>} '
cases = [
    ('sync await', 'async fn answer()->i64{42} fn main(){let value=answer().await;}',
     ['.await is only allowed inside an async function']),
    ('future question', 'enum Error{Failed} async fn answer()->Result<i64,Error>{Ok(42)} fn use_it()->Result<i64,Error>{let value=answer()?;Ok(value)} fn main(){}',
     ['? requires a Result or Option', 'await a Future']),
    ('missing member', mutex + 'impl Holder{fn new()->Holder{Holder{}}} fn main(){}',
     ["missing required field 'mutex' when constructing 'Holder'", 'required field declared here']),
    ('immutable receiver', 'struct Item{value:i64} impl Item{fn add(&mut self){(*self).value+=1;}} struct Holder{item:Item} fn main(){let h=Holder{item:Item{value:0}};h.item.add();}',
     ['cannot mutate an immutable binding']),
    ('borrow outlives owner', mutex + 'async fn bad(){let h=Holder{mutex:Mutex::new(Data{value:1})};let mut guard=h.mutex.lock().await;drop(h);let data=guard.get_mut();print((*data).value);} fn main(){}',
     ['rule violation:', 'borrow']),
]
for name, text, messages in cases:
    source = out / (name.replace(' ', '_') + '.crb')
    source.write_text(text)
    ran = subprocess.run([compiler, 'check', source], capture_output=True, text=True, timeout=60)
    assert ran.returncode == 8, (name, ran)
    for message in messages:
        assert message in ran.stderr, (name, message, ran.stderr)
    assert str(source) + ':' in ran.stderr and '^' in ran.stderr and not ran.stdout, (name, ran)
    results.append({'case': name, 'status': 'rejected', 'stderr': ran.stderr})
    print(name, 'rejected', flush=True)
(out / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
