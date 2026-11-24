#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused definition-local method, signature and receiver validation."""
import argparse, json, subprocess, tempfile
from pathlib import Path
POSITIVE = '''
struct Counter {
    value: i64;
    pub const STEP: i64 = 2;
    pub fn new(value: i64) Counter { Counter { value: value } }
    pub fn add(self: &mut Counter, amount: i64) { self.value += amount; }
    pub fn noop(self: &Counter) () {}
    pub fn pair(self: &Counter) (i64, bool) { (self.value, true) }
    pub fn finish(self: Counter) i64 { self.value }
}
enum Outcome {
    Data(i64);
    End;
    pub fn is_end(&self) bool {
        match self { Outcome::Data(value) => { false }, Outcome::End => { true }, }
    }
}
fn apply(function: fn(i64) i64, value: i64) i64 { function(value) }
fn main() {
    let mut counter = Counter::new(20);
    counter.add(Counter::STEP);
    counter.noop();
    let (number, flag) = counter.pair();
    print(number); print(flag);
    let state = Outcome::End;
    print(state.is_end());
    let data = Outcome::Data(9);
    print(data.is_end());
    print(apply(|value: i64| i64 { value * 2 }, 7));
    print(counter.finish());
}
'''
GENERIC = '''
#(type: T)
struct Inner<T> {
    value: T;
    pub fn new(value: T) Inner<T> { Inner { value: value } }
}
#(type: T)
struct Container<T> {
    value: T;
    pub fn new(value: T) Container<T> { Container { value: value } }
    pub fn doubled(self: &Container<i64>) i64 { self.value * 2 }
    pub fn increment(self: &mut Container<i64>) { self.value += 1; }
    pub fn finish(self: Container<i64>) i64 { self.value }
    pub fn negate(self: &Container<bool>) bool { !self.value }
    pub fn inner_double(self: &Container<Inner<i64>>) i64 { self.value.value * 2 }
}
fn main() {
    let mut number = Container::new(20);
    number.increment();
    print(number.doubled());
    print(number.finish());
    let flag = Container::new(false);
    print(flag.negate());
    let nested = Container::new(Inner::new(3));
    print(nested.inner_double());
}
'''
CASES = [('inline_methods', POSITIVE, '22\ntrue\ntrue\nfalse\n14\n22\n'), ('constrained_receivers', GENERIC, '42\n21\ntrue\n6\n')]
NEGATIVE = [('unavailable_specialization', GENERIC[:GENERIC.index('fn main()')] + 'fn main() { let value = Container::new(true); print(value.doubled()); }'), ('shared_receiver_mutation', 'struct Point { value: i64; fn bad(self: &Point) { self.value = 2; } } fn main() { let p = Point { value: 1 }; p.bad(); }'), ('wrong_receiver_owner', 'struct Other { value: i64; } struct Point { value: i64; fn bad(self: &Other) i64 { self.value } } fn main() { let p = Point { value: 1 }; print(p.bad()); }'), ('consumed_receiver', 'struct Point { value: i64; fn finish(self: Point) i64 { self.value } } fn main() { let p = Point { value: 1 }; print(p.finish()); print(p.value); }')]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--compiler', required=True)
    p.add_argument('--stdlib', required=True)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    compiler = str(Path(a.compiler).resolve())
    std = str(Path(a.stdlib).resolve())
    results = []
    with tempfile.TemporaryDirectory(prefix='corbo-definition-methods-') as t:
        root = Path(t)
        for name, source, expected in CASES:
            package = root / name
            (package / 'src').mkdir(parents=True)
            (package / 'package.toml').write_text('[package]\nname = "demo"\n')
            (package / 'src/main.crb').write_text(source)
            proc = subprocess.run([compiler, '--emit-package-c', str(package), '--stdlib-dir', std], capture_output=True, timeout=180)
            if proc.returncode:
                raise RuntimeError(name + ': ' + str(proc.returncode) + ' ' + proc.stderr.decode())
            c = package / 'main.c'
            c.write_bytes(proc.stdout)
            exe = package / 'demo'
            subprocess.run(['cc', '-std=c11', '-pthread', '-O1', '-fsanitize=undefined', '-fno-sanitize-recover=all', str(c), '-lm', '-o', str(exe)], check=True, capture_output=True, timeout=120)
            run = subprocess.run([str(exe)], capture_output=True, text=True, timeout=15)
            if run.returncode or run.stdout != expected:
                raise RuntimeError(name + ': ' + repr(run.stdout) + ' ' + run.stderr)
            results.append({'case': name, 'status': 'passed', 'output': run.stdout})
        for name, source in NEGATIVE:
            path = root / (name + '.crb')
            path.write_text(source)
            proc = subprocess.run([compiler, 'check', str(path)], capture_output=True, text=True, timeout=120)
            if not proc.returncode:
                raise RuntimeError(name + ' unexpectedly accepted')
            expected = {'unavailable_specialization': ('error[N1]', 'typed receiver'), 'shared_receiver_mutation': ('error[N5]', 'shared reference'), 'wrong_receiver_owner': ('error[N1]', 'enclosing struct or enum'), 'consumed_receiver': ('error[N6]', 'ownership was moved')}[name]
            if not all((part in proc.stderr for part in expected)):
                raise RuntimeError(name + ' incorrect diagnostic: ' + proc.stderr)
            results.append({'case': name, 'status': 'rejected', 'exit': proc.returncode, 'diagnostic': proc.stderr})
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps({'cases': results, 'platform': 'macOS ARM64', 'sanitizer': 'UBSan'}, indent=2) + '\n')
    print(json.dumps({'passed': len(results), 'report': a.out}))
if __name__ == '__main__':
    main()
