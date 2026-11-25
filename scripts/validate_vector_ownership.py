#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused standalone vector element ownership and dependency integration."""
import argparse, json, subprocess, tempfile
from pathlib import Path

RESOURCE = '''struct Resource {
    value: i64;
    fn drop(&mut self) { print((*self).value); }
}
'''
GOOD = {
'resource_cleanup': ('use std::Vector;\n' + RESOURCE + '''
struct Holder { value: Resource; }
fn main() {
    let mut values: Vector<Holder> = Vector::new();
    let resource = Resource { value: 12 };
    values.push(Holder { value: resource });
    values.push(Holder { value: Resource { value: 24 } });
    let mut received = values;
    match received.pop() { Some(value) => { print(value.value.value); }, None => {}, }
    received.clear();
    received.push(Holder { value: Resource { value: 36 } });
}
''', '24\n24\n12\n36\n'),
'references': ('''use std::Vector;
fn main() {
    let first: i64 = 12;
    let second: i64 = 24;
    let mut values: Vector<&i64> = Vector::new();
    values.push(&first);
    values.push(&second);
    let mut received = values;
    match received.pop() { Some(value) => { print(*value); }, None => {}, }
    match received.pop() { Some(value) => { print(*value); }, None => {}, }
}
''', '24\n12\n'),
'mutable_reference': ('''use std::Vector;
fn main() {
    let mut number: i64 = 12;
    let mut values: Vector<&mut i64> = Vector::new();
    values.push(&mut number);
    match values.pop() { Some(value) => { *value = 24; print(*value); }, None => {}, }
}
''', '24\n'),
'borrowed_record': ('''use std::Vector;
struct View { value: &i64; }
fn main() {
    let number: i64 = 42;
    let mut values: Vector<View> = Vector::new();
    values.push(View { value: &number });
    match values.pop() { Some(view) => { print(*view.value); }, None => {}, }
}
''', '42\n'),
'pool_allocation': ('use std::{Vector, Pool};\n' + RESOURCE + '''
fn main() {
    let mut resources = Pool<Resource>::new(2);
    let mut values: Vector<A<Resource>> = Vector::new();
    let first = resources.new(Resource { value: 12 });
    values.push(first);
    values.push(resources.new(Resource { value: 24 }));
    match values.pop() { Some(value) => { print((*value).value); }, None => {}, }
}
''', '24\n24\n12\n'),
'nested_vector': ('use std::Vector;\n' + RESOURCE + '''
fn main() {
    let mut inner: Vector<Resource> = Vector::new();
    inner.push(Resource { value: 12 });
    let mut outer: Vector<Vector<Resource>> = Vector::new();
    outer.push(inner);
}
''', '12\n'),
}
GOOD['helper_dependencies'] = ('''use std::Vector;
fn make(value: &i64) Vector<&i64> {
    let mut values: Vector<&i64> = Vector::new();
    values.push(value);
    values
}
fn append_inner(values: &mut Vector<&i64>, value: &i64) { values.push(value); }
fn append(values: &mut Vector<&i64>, value: &i64) { append_inner(&mut *values, value); }
fn main() {
    let number: i64 = 42;
    let mut values = make(&number);
    append(&mut values, &number);
    match values.pop() { Some(value) => { print(*value); }, None => {}, }
    match values.pop() { Some(value) => { print(*value); }, None => {}, }
}
''', '42\n42\n')
GOOD['handle'] = ('''use std::Vector;
struct Launcher { fn start() runtime::Handle<i64> { runtime::thread({ 42 }) } }
fn main() {
    let execution = Launcher::start();
    let mut values: Vector<runtime::Handle<i64>> = Vector::new();
    values.push(execution);
    match values.pop() {
        Some(execution) => { match execution.join() { Ok(value) => { print(value); }, Err(error) => { drop(error); }, } },
        None => {},
    }
}
''', '42\n')

GOOD['owned_field'] = ('use std::{Vector, Pool};\n' + RESOURCE + '''
struct Owned { item: A<Resource>; }
fn main() {
    let mut pool = Pool<Resource>::new(1);
    let mut values: Vector<Owned> = Vector::new();
    values.push(Owned { item: pool.new(Resource { value: 42 }) });
    match values.pop() { Some(value) => { drop(value); }, None => {}, }
    let replacement = pool.new(Resource { value: 7 });
}
''', '42\n7\n')

GOOD['text_and_slice'] = ('''use std::Vector;
fn main() {
    let bytes: [u8; 2] = [7, 9];
    let mut views: Vector<&[u8]> = Vector::new();
    views.push(&bytes[..]);
    match views.pop() { Some(view) => { print(view[1]); }, None => {}, }
    let mut words: Vector<&str> = Vector::new();
    words.push("ok");
    match words.pop() { Some(word) => { let bytes = word.as_bytes(); print(bytes.len()); }, None => {}, }
}
''', '9\n2\n')

BAD = {
'use_after_move': 'use std::Vector;\n' + RESOURCE + '''
fn main() { let value = Resource { value: 1 }; let mut values: Vector<Resource> = Vector::new(); values.push(value); print(value.value); }
''',
'borrow_mutation': '''use std::Vector;
fn main() { let mut number: i64 = 1; let mut values: Vector<&i64> = Vector::new(); values.push(&number); number = 2; match values.pop() { Some(value) => { print(*value); }, None => {}, } }
''',
'dangling_insert': '''use std::Vector;
fn main() { let mut values: Vector<&i64> = Vector::new(); { let number: i64 = 1; values.push(&number); } match values.pop() { Some(value) => { print(*value); }, None => {}, } }
''',
'pool_lifetime': '''use std::{Vector, Pool};
fn main() { let mut pool = Pool<i64>::new(1); let mut values: Vector<A<i64>> = Vector::new(); values.push(pool.new(1)); drop(pool); match values.pop() { Some(value) => { print(*value); }, None => {}, } }
''',
}

BAD['helper_borrow_mutation'] = '''use std::Vector;
fn append_inner(values: &mut Vector<&i64>, value: &i64) { values.push(value); }
fn append(values: &mut Vector<&i64>, value: &i64) { append_inner(&mut *values, value); }
fn main() {
    let mut number: i64 = 1;
    let mut values: Vector<&i64> = Vector::new();
    append(&mut values, &number);
    number = 2;
    match values.pop() { Some(value) => { print(*value); }, None => {}, }
}
'''

BAD['repeated_insertion'] = '''use std::Vector;
fn main() {
    let mut number: i64 = 1;
    let mut values: Vector<&i64> = Vector::new();
    let mut count: i64 = 0;
    while count < 2 { values.push(&number); count += 1; }
    match values.pop() { Some(value) => { print(*value); }, None => {}, }
    number = 2;
    match values.pop() { Some(value) => { print(*value); }, None => {}, }
}
'''

def run(command):
    return subprocess.run(list(map(str, command)), text=True, capture_output=True, timeout=180)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--case', action='append')
    args=parser.parse_args(); compiler=args.compiler.resolve(); prefix=compiler.parent.parent; results=[]
    with tempfile.TemporaryDirectory(prefix='corbo-vector-ownership-') as tmp:
        for name,case in {**GOOD, **BAD}.items():
            if args.case and name not in args.case: continue
            package=Path(tmp)/name; (package/'src').mkdir(parents=True)
            (package/'package.toml').write_text('[package]\nname="demo"\n')
            good=name in GOOD; source,expected=case if good else (case,None)
            (package/'src/main.crb').write_text(source)
            if not good:
                result=run([compiler,'check',package])
                assert result.returncode!=0,(name,'unexpected acceptance')
                assert 'rule violation' in result.stderr,(name,result.stdout,result.stderr)
                results.append({'case':name,'status':'rejected','diagnostic':result.stderr})
            else:
                emitted=run([compiler,'--emit-package-c',package,'--stdlib-dir',prefix/'share/corbo/stdlib/src'])
                if emitted.returncode:
                    diagnostic=run([compiler,'check',package]); raise AssertionError((name,emitted.stdout,diagnostic.stderr))
                c=package/'program.c';c.write_text(emitted.stdout);program=package/'program'
                built=run(['cc','-std=c11','-pthread','-O1','-fsanitize=undefined','-fno-sanitize-recover=undefined','-I',prefix/'include',c,'-lm','-o',program])
                assert built.returncode==0,(name,built.stderr)
                result=run([program]);assert result.returncode==0 and result.stdout==expected and not result.stderr,(name,result.returncode,result.stdout,result.stderr)
                results.append({'case':name,'status':'passed under fatal UBSan','output':result.stdout})
            print(name,results[-1]['status'],flush=True)
    args.out.write_text(json.dumps(results,indent=2)+'\n')

if __name__=='__main__': main()
