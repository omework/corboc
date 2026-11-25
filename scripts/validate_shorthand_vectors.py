#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused shorthand, standalone vector and async owned-record integration."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

CASES = {
 'shorthand_moves_and_globals': ({
    'src/constants/constants.crb': 'pub const NUMBER: i64 = 7;\n',
    'src/main.crb': '''use demo::constants::NUMBER;
struct Resource {
    number: i64;
    fn drop(&mut self) { print((*self).number); }
}
struct Holder { resource: Resource; NUMBER: i64; }
enum Outcome { Data { value: i64; }; End; }
fn wrap(resource: Resource) Holder { Holder { resource, NUMBER } }
fn main() {
    let resource = Resource { number: 42 };
    let holder = wrap(resource);
    let received = holder;
    print(received.NUMBER);
    let value: i64 = 9;
    let outcome = Outcome::Data { value };
    match outcome { Outcome::Data { value: number } => { print(number); }, Outcome::End => {}, }
}
'''}, '7\n9\n42\n'),
 'standalone_struct_vector': ({'src/main.crb': '''use std::Vector;
struct Point { value: i64; }
struct Table {
    groups: Vector<Point>;
    fn new() Self { let groups = Vector::new(); Self { groups } }
}
fn main() {
    let mut table = Table::new();
    print(table.groups.len());
    table.groups.push(Point { value: 42 });
    print(table.groups.len());
    match table.groups.pop() { Some(point) => { print(point.value); }, None => { print(0); }, }
    table.groups.push(Point { value: 7 });
    table.groups.clear();
    print(table.groups.is_empty());
}
'''}, '0\n1\n42\ntrue\n'),
 'standalone_scope_transfer': ({'src/main.crb': '''use std::Vector;
fn main() {
    let received = #(stack_region: max_size=64K, count=2) {
        let mut values = Vector<i64>::new();
        values.push(12);
        values
    };
    let mut received = received;
    match received.pop() { Some(value) => { print(value); }, None => { print(0); }, }
}
'''}, '12\n'),
 'pooled_compatibility': ({'src/main.crb': '''use std::Vector;
fn main() {
    let mut storage = Pool<Vector<i64>>::new(1);
    let mut values = storage.new();
    values.push(7);
    print(values.len());
    match values.pop() { Some(value) => { print(value); }, None => { print(0); }, }
}
'''}, '1\n7\n'),
}
BAD = {
 'moved_shorthand_value': '''struct Resource { number: i64; fn drop(&mut self) {} }
struct Holder { resource: Resource; }
fn main() { let resource = Resource { number: 1 }; let holder = Holder { resource }; print(resource.number); }
''',
 'undefined_shorthand_value': 'struct Holder { number: i64; } fn main() { let holder = Holder { number }; }',
 'thread_restriction': '''use std::Vector;
#(thread: transfer=false)
struct Local { number: i64; }
fn main() {
    let values: Vector<Local> = Vector::new();
    let execution = runtime::thread(move { print(values.len()); });
    drop(execution.join());
}
''',
}

def run(command):
    return subprocess.run(list(map(str,command)),capture_output=True,text=True,timeout=180)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--rawtable-source',type=Path,required=True)
    args=parser.parse_args();compiler=args.compiler.resolve();results=[]
    with tempfile.TemporaryDirectory(prefix='corbo-shorthand-vector-') as tmp:
        root=Path(tmp)
        cases=dict(CASES)
        source=args.rawtable_source.read_text().replace('use std::io::asyn::{File};','use std::io::asyn::{File, FileError};').replace('use std::io::{FileMode, FileError};','use std::io::FileMode;').replace('.async?', '.await?')
        path=json.dumps(str(root/'table.data'))
        source+='''
async fn exercise() i64 {
    let result = RawTable::new(PATH).await;
    match result {
        Ok(table) => {
            let mut table = table;
            table.groups.push(GroupMetadata { compressed: false, cursor: 0, frame_size: 1024, capacity: 16 });
            print(table.groups.len());
            1
        },
        Err(error) => { drop(error); 0 },
    }
}
fn main() {
    let task = runtime::spawn(exercise());
    match task.join() { Ok(n) => { print(n); }, Err(error) => { drop(error); print(0); }, }
}
'''.replace('PATH',path)
        cases['async_rawtable']=({'src/main.crb':source},'1\n1\n')
        for name,(files,expected) in cases.items():
            package=root/name;(package/'src').mkdir(parents=True)
            (package/'package.toml').write_text('[package]\nname="demo"\n')
            for relative,text in files.items():
                p=package/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
            emitted=run([compiler,'--emit-package-c',package,'--stdlib-dir',compiler.parent.parent/'share/corbo/stdlib/src'])
            assert emitted.returncode==0,(name,emitted.returncode,emitted.stdout,emitted.stderr)
            c=package/'program.c';c.write_text(emitted.stdout);program=package/'program'
            built=run(['cc','-std=c11','-pthread','-O1','-fsanitize=undefined','-fno-sanitize-recover=undefined','-I',compiler.parent.parent/'include',c,'-lm','-o',program])
            assert built.returncode==0,(name,built.stderr)
            executed=run([program]);assert executed.returncode==0 and executed.stdout==expected and not executed.stderr,(name,executed.returncode,executed.stdout,executed.stderr)
            results.append({'case':name,'status':'passed under fatal UBSan','output':executed.stdout});print(name,'passed',flush=True)
        for name,source in BAD.items():
            package=root/name;(package/'src').mkdir(parents=True);(package/'package.toml').write_text('[package]\nname="demo"\n');(package/'src/main.crb').write_text(source)
            result=run([compiler,'check',package]);assert result.returncode!=0,(name,result.stdout,result.stderr)
            if name=='thread_restriction':assert 'thread' in result.stderr.lower(),result.stderr
            results.append({'case':name,'status':'rejected','diagnostic':result.stdout+result.stderr});print(name,'rejected',flush=True)
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(results,indent=2)+'\n')

if __name__=='__main__':main()
