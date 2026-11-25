#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused primitive Option struct-field construction and projection checks."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

CASES = {
    'dispatcher': ('''
pub struct Dispatcher {
    #(configurable)
    pub const MAX_CONCURRENT_WRITE: usize = 16;
    group_size_at_offset: usize;
    offset: usize;
    limit: Option<usize>;
    buffer: [usize; Self::MAX_CONCURRENT_WRITE];

    pub fn new() Self {
        Self { group_size_at_offset: 0, offset: 0, limit: None,
            buffer: [0; Self::MAX_CONCURRENT_WRITE] }
    }
}
fn main() {
    let value = Dispatcher::new();
    print(value.buffer.len());
    match value.limit { Some(n) => { print(n); }, None => { print(0); }, }
    #(override: Dispatcher::MAX_CONCURRENT_WRITE=3) {
        let other = Dispatcher::new(); print(other.buffer.len());
    }
}
''', '16\n0\n3\n'),
    'some_reuse_and_mutation': ('''
struct Record {
    limit: Option<usize>;
    flag: Option<bool>;
    fn new(limit: Option<usize>) Self {
        Self { limit: limit, flag: Some(true) }
    }
}
fn main() {
    let mut value = Record::new(Some(42));
    match value.limit { Some(n) => { print(n); }, None => { print(0); }, }
    value.limit = None;
    match value.limit { Some(n) => { print(n); }, None => { print(1); }, }
    match value.flag { Some(flag) => { print(flag); }, None => { print(false); }, }
}
''', '42\n1\ntrue\n'),
}
BAD = {
    'wrong_payload': 'struct Record { limit: Option<usize>; fn new() Self { Self { limit: Some(false) } } } fn main() {}',
    'wrong_array_length': 'struct Record { limit: Option<usize>; buffer: [usize; 16]; fn new() Self { Self { limit: None, buffer: [0, 16] } } } fn main() {}',
}

def run(command):
    return subprocess.run(list(map(str, command)), capture_output=True, text=True, timeout=120)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(); compiler=args.compiler.resolve(); results=[]
    with tempfile.TemporaryDirectory(prefix='corbo-option-fields-') as tmp:
        root=Path(tmp)
        for name,(source,expected) in CASES.items():
            package=root/name; (package/'src').mkdir(parents=True)
            (package/'package.toml').write_text('[package]\nname="demo"\n')
            (package/'src/main.crb').write_text(source)
            emitted=run([compiler,'--emit-package-c',package])
            assert emitted.returncode==0,(name,emitted.stdout,emitted.stderr)
            c=package/'program.c'; c.write_text(emitted.stdout); binary=package/'program'
            built=run(['cc','-std=c11','-pthread','-O1','-fsanitize=undefined','-fno-sanitize-recover=undefined',c,'-lm','-o',binary])
            assert built.returncode==0,(name,built.stderr)
            result=run([binary]); assert result.returncode==0 and result.stdout==expected and not result.stderr,(name,result.stdout,result.stderr)
            results.append({'case':name,'status':'passed under fatal UBSan','output':result.stdout}); print(name,'passed',flush=True)
        for name,source in BAD.items():
            file=root/(name+'.crb');file.write_text(source)
            result=run([compiler,'check',file]);assert result.returncode!=0,(name,result.stdout,result.stderr)
            results.append({'case':name,'status':'rejected','diagnostic':result.stdout+result.stderr});print(name,'rejected',flush=True)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(results,indent=2)+'\n')

if __name__=='__main__': main()
