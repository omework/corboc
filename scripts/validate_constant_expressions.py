#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused constant reduction, lexical overrides and refusal boundaries."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

ACCEPT = {
    'associated_layout_and_overrides': (r'''
struct RawTable {
    #(configurable)
    pub const FRAME_SIZE: usize = 2;
    #(configurable)
    pub const GROUP_SIZE: usize = max(4 * Self::FRAME_SIZE, 3);
    data: [u8; Self::GROUP_SIZE];
    fn new() RawTable { RawTable { data: [0; Self::GROUP_SIZE] } }
    fn size(&self) usize { self.data.len() }
}
fn main() {
    let table = RawTable::new(); print(table.size());
    #(override: RawTable::FRAME_SIZE=3) {
        let table = RawTable::new(); print(table.size());
        #(override: RawTable::GROUP_SIZE=7) {
            #(override: RawTable::FRAME_SIZE=5) { let table = RawTable::new(); print(table.size()); }
        }
    }
    let table = RawTable::new(); print(table.size());
}
''', '8\n12\n7\n8\n'),
    'primitive_text_and_extrema': (r'''
const LOW: i64 = -(9223372036854775808);
const HIGH: u64 = 18446744073709551615;
const REM: i64 = LOW % -1;
const VALUE: i64 = min(12, max(3, 4)) + (9 / 3) * 2 - 1;
const YES: bool = true;
const ALSO: bool = YES;
const LABEL: &str = "table";
const OTHER: &str = LABEL;
const SMALL: u8 = 2 * 3;
const FLOAT: f64 = max(1.5, 2.25) + 0.25;
const FLOAT32: f32 = min(0.5, 1.0) * 2.0;
fn small(value: u8) u8 { value }
fn main() {
    print(LOW); print(HIGH); print(REM); print(VALUE); print(ALSO);
    let text = OTHER; let bytes = text.as_bytes(); print(bytes.len()); print(small(SMALL)); print(FLOAT); print(FLOAT32);
}
''', '-9223372036854775808\n18446744073709551615\n0\n9\ntrue\n5\n6\n2.5\n1\n'),
    'module_dependency_and_simultaneous_overrides': (r'''
#(configurable)
const BASE: i64 = 2;
#(configurable)
const DERIVED: i64 = BASE * 4;
const UNMARKED: i64 = DERIVED + 1;
#(configurable)
const LABEL: &str = "default";
fn report() { print(UNMARKED); let label = LABEL; let bytes = label.as_bytes(); print(bytes.len()); }
fn main() {
    report();
    #(override: BASE=3) { report(); }
    #(override: BASE=5, DERIVED=BASE+1, LABEL="selected") {
        report();
        #(override: BASE=8) { report(); }
    }
    report();
}
''', '9\n7\n13\n7\n4\n8\n4\n8\n9\n7\n'),
}
REJECT = {
    'overflow': ('const X: u8 = 255 + 1; fn main() {}', 'integer arithmetic overflows'),
    'division_zero': ('const X: i64 = 3 / (2 - 2); fn main() {}', 'division or remainder by zero'),
    'signed_division_overflow': ('const MIN: i64 = -9223372036854775808; const X: i64 = MIN / -1; fn main() {}', 'integer arithmetic overflows'),
    'cycle': ('const X: i64 = Y; const Y: i64 = X; fn main() {}', 'cyclic constant dependency'),
    'reference_type': ('const X: u8 = 2; const Y: u64 = X + 1; fn main() {}', 'constant reference type differs'),
    'function_call': ('fn value() i64 { 2 } const X: i64 = value(); fn main() {}', 'constant calls are restricted'),
    'aggregate': ('struct P { x: i64; } const X: P = P { x: 1 }; fn main() {}', None),
    'min_arity': ('const X: i64 = min(1); fn main() {}', 'constant calls are restricted'),
    'text_arithmetic': ('const X: &str = "a" + "b"; fn main() {}', 'arithmetic requires numeric constants'),
    'text_type': ('const TEXT: &str = 42; fn main() {}', 'numeric literal does not match'),
    'unsupported_unary': ('const VALUE: i64 = !2; fn main() {}', 'constant initializer must use'),
    'override_overflow': ('#(configurable) const X: u8 = 2; fn main() { #(override: X=255+1) {} }', 'integer arithmetic overflows'),
}

def run(command):
    return subprocess.run(list(map(str, command)), capture_output=True, text=True, timeout=180)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(); compiler=args.compiler.resolve(); results=[]
    with tempfile.TemporaryDirectory(prefix='corbo-constants-') as tmp:
        root=Path(tmp)
        for name,(source,expected) in ACCEPT.items():
            package=root/name; (package/'src').mkdir(parents=True)
            (package/'package.toml').write_text('[package]\nname="demo"\n')
            (package/'src/main.crb').write_text(source)
            c=run([compiler,'--emit-package-c',package]); assert c.returncode==0,(name,c.stdout,c.stderr)
            cfile=package/'program.c'; cfile.write_text(c.stdout); binary=package/'program'
            built=run(['cc','-std=c11','-pthread','-O1','-fsanitize=undefined','-fno-sanitize-recover=undefined',cfile,'-lm','-o',binary])
            assert built.returncode==0,(name,built.stderr)
            executed=run([binary]); assert executed.returncode==0 and executed.stdout==expected and not executed.stderr,(name,executed.stdout,executed.stderr)
            results.append({'case':name,'status':'passed','output':executed.stdout,'ubsan':True})
            print(name, 'passed',flush=True)
        for name,(source,message) in REJECT.items():
            file=root/(name+'.crb'); file.write_text(source)
            checked=run([compiler,'check',file]); assert checked.returncode!=0,(name,checked.stdout,checked.stderr)
            text=checked.stdout+checked.stderr
            assert message is None or message in text,(name,text)
            results.append({'case':name,'status':'rejected','diagnostic':text})
            print(name, 'rejected',flush=True)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps({'compiler':str(compiler),'platform':'host','results':results},indent=2)+'\n')

if __name__=='__main__': main()
