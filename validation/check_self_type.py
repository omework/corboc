#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused Self alias checks and native executions; no ownership rule changes."""
import argparse
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--compiler', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
compiler = args.compiler.resolve()
out = args.out.resolve()
out.mkdir(parents=True, exist_ok=True)
accepted = {
    'receiver': ('struct Point { x: i64 } impl Point { fn new(x:i64)->Self { Self{x:x} } fn zero()->Self { Self::new(0) } fn value(self:Self)->i64 { self.x } } fn main(){ let p=Point::zero(); print(p.value()); }', '0\n'),
    'generic': ('#(type:T) struct Boxed<T>{value:T} impl Boxed<T>{ fn new(value:T)->Self{Self{value:value}} fn wrap(value:T)->Self{Self::new(value)} fn get(&self)->T{(*self).value} } fn main(){let b=Boxed::wrap(42);print(b.get());}', '42\n'),
    'reference': ('struct Point{x:i64} impl Point{ fn equal(&self,other:&Self)->bool{(*self).x==(*other).x} } fn main(){let a=Point{x:4};let b=Point{x:4};print(a.equal(&b));}', 'true\n'),
}
for name, (source, expected) in accepted.items():
    package = out / name
    (package / 'src').mkdir(parents=True, exist_ok=True)
    (package / 'package.toml').write_text('[package]\nname="self_probe"\n')
    (package / 'src/main.crb').write_text(source + '\n')
    binary = package / 'probe'
    built = subprocess.run([compiler, 'build', package, '-o', binary], capture_output=True, text=True, timeout=120)
    assert built.returncode == 0, (name, built.stdout, built.stderr)
    ran = subprocess.run([binary], capture_output=True, text=True, timeout=30)
    assert (ran.returncode, ran.stdout) == (0, expected), (name, ran)
    print(name, 'passed', flush=True)
# Module resolution must leave Self for impl-scoped normalization.
package = out / 'module'
(package / 'src/model').mkdir(parents=True, exist_ok=True)
(package / 'package.toml').write_text('[package]\nname="self_probe"\n')
(package / 'src/model/model.crb').write_text('pub struct Point{x:i64} impl Point{pub fn new()->Self{Self{x:7}} pub fn value(&self)->i64{(*self).x}}\n')
(package / 'src/main.crb').write_text('use self_probe::model::Point; fn main(){let p=Point::new();print(p.value());}\n')
binary = package / 'probe'
subprocess.run([compiler, 'build', package, '-o', binary], check=True, capture_output=True, text=True, timeout=120)
assert subprocess.check_output([binary], text=True) == '7\n'
print('module passed', flush=True)
for name, source, code in [
    ('outside', 'fn main(){let x:Self=1;}', 'E0111'),
    ('extra', '#(type:T) struct Boxed<T>{value:T} impl Boxed<T>{fn new(value:T)->Self<T>{Self{value:value}}} fn main(){}', 'E0112'),
]:
    path = out / (name + '.crb')
    path.write_text(source + '\n')
    checked = subprocess.run([compiler, 'check', path], capture_output=True, text=True, timeout=120)
    assert checked.returncode != 0 and code in checked.stderr + checked.stdout, (name, checked)
    print(name, 'rejected with', code, flush=True)
