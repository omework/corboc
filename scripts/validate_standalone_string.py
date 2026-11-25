#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused standalone String construction, loans, transfers and regional cleanup."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

GOOD = {
'utf8_and_views': ('''use std::String;
fn prefix(text: &String) &str { &text[..2] }
fn main() {
    let mut text: String = String::new();
    print(text.is_empty());
    text.push_str("été");
    let suffix = ",ok";
    text.push_str(suffix);
    print(text.byte_len());
    let bytes = text.as_bytes();
    print(bytes.len());
    print(bytes[0]);
    let head = prefix(text.ref());
    print(head.byte_len());
    let tail = &text[5..];
    print(tail.byte_len());
    text.push_str("!");
    print(text.byte_len());
}
''', 'true\n8\n8\n195\n2\n3\n9\n'),
'moves_and_cleanup': ('''use std::String;
use runtime::metrics::memory_stats;
struct Holder { text: String; }
fn make() String {
    let mut text = String::new();
    text.push_str("hello");
    text
}
fn exercise() usize {
    let received = #(stack_region: max_size=64K, count=2) { make() };
    let holder = Holder { text: received };
    let moved = holder;
    moved.text.byte_len()
}
fn main() {
    let before = memory_stats();
    print(exercise());
    let after = memory_stats();
    print(before.occupied() == after.occupied());
}
''', '5\ntrue\n'),
'borrowed_split': ('''use std::String;
fn main() {
    let mut text = String::new();
    text.push_str("été,ok,");
    let mut pieces = text.split(",");
    loop {
        match pieces.next() {
            Some(piece) => { print(piece.byte_len()); },
            None => { break; },
        }
    }
}
''', '5\n2\n0\n'),
'pooled_and_inline_compatibility': ('''use std::String;
fn main() {
    let mut strings = Pool<String>::new(1);
    let mut pooled = strings.new();
    pooled.push_str("old");
    print(pooled.byte_len());
    let mut inline = String<8>::new();
    drop(inline.set("inline"));
    print(inline.len());
    let mut owned = String::new();
    owned.push_str("new");
    print(owned.byte_len());
}
''', '3\n6\n3\n'),
'string_in_vector': ('''use std::{String, Vector};
fn main() {
    let mut values: Vector<String> = Vector::new();
    let mut text = String::new();
    text.push_str("owned");
    values.push(text);
    match values.pop() { Some(text) => { print(text.byte_len()); }, None => {}, }
    let mut second = String::new();
    second.push_str("cleanup");
    values.push(second);
}
''', '5\n'),
}
BAD = {
'live_text_borrow': '''use std::String;
fn main() { let mut text = String::new(); text.push_str("ok"); let view = &text[..]; drop(text); print(view.byte_len()); }
''',
'live_byte_borrow': '''use std::String;
fn main() { let mut text = String::new(); text.push_str("ok"); let view = text.as_bytes(); text.push_str("!"); print(view.len()); }
''',
'moved_owner': '''use std::String;
fn main() { let text = String::new(); let received = text; print(text.byte_len()); }
''',
'escaping_view': '''use std::String;
fn main() { let view = { let mut text = String::new(); text.push_str("ok"); text.as_str() }; print(view.byte_len()); }
''',
}
FAIL = {
'utf8_boundary': '''use std::String;
fn main() { let mut text = String::new(); text.push_str("é"); let view = &text[..1]; print(view.byte_len()); }
''',
'region_limit': '''use std::String;
fn main() { #(stack_region: max_size=1K, count=1) { let mut text = String::new(); text.push_str("''' + 'x' * 2048 + '''"); } }
''',
}

def run(command):
    return subprocess.run(list(map(str, command)), text=True, capture_output=True, timeout=180)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--case',action='append')
    args=parser.parse_args(); compiler=args.compiler.resolve(); prefix=compiler.parent.parent; results=[]
    with tempfile.TemporaryDirectory(prefix='corbo-string-') as directory:
        for name,case in {**GOOD, **BAD, **FAIL}.items():
            if args.case and name not in args.case: continue
            package=Path(directory)/name;(package/'src').mkdir(parents=True)
            (package/'package.toml').write_text('[package]\nname="string_probe"\n')
            source,expected=case if name in GOOD else (case,None)
            (package/'src/main.crb').write_text(source)
            if name in BAD:
                checked=run([compiler,'check',package])
                assert checked.returncode!=0 and 'rule violation' in checked.stderr,(name,checked.stdout,checked.stderr)
                results.append({'case':name,'status':'rejected','diagnostic':checked.stderr})
            else:
                emitted=run([compiler,'--emit-package-c',package,'--stdlib-dir',prefix/'share/corbo/stdlib/src'])
                if emitted.returncode:
                    diagnostic=run([compiler,'check',package]);raise AssertionError((name,emitted.stdout,diagnostic.stderr))
                c=package/'program.c';c.write_text(emitted.stdout);program=package/'program'
                built=run(['cc','-std=c11','-pthread','-O1','-fsanitize=undefined','-fno-sanitize-recover=undefined','-I',prefix/'include',c,'-lm','-o',program])
                assert built.returncode==0,(name,built.stderr)
                executed=run([program])
                if name in GOOD:
                    assert executed.returncode==0 and executed.stdout==expected and not executed.stderr,(name,executed.returncode,executed.stdout,executed.stderr)
                    results.append({'case':name,'status':'passed under fatal UBSan','output':executed.stdout})
                else:
                    assert executed.returncode!=0 and 'runtime error:' not in executed.stderr,(name,executed.returncode,executed.stdout,executed.stderr)
                    results.append({'case':name,'status':'runtime constraint rejected','diagnostic':executed.stdout+executed.stderr})
            print(name,results[-1]['status'],flush=True)
    args.out.write_text(json.dumps(results,indent=2)+'\n')

if __name__=='__main__': main()
