#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused universal-borrow and for-loop compilation/execution observations."""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=Path('build/iteration/results.json'))
    args = parser.parse_args()
    compiler = args.compiler.resolve()
    cases = {
        'arrays': ('''struct Record { number: i64 }
fn touch(r:&mut Record){let n=&mut (*r).number;*n+=1;}
fn read(r:&Record)->i64{(*r).number}
fn main() {
    let mut n: i64 = 3;
    let view = n.mut_ref();
    *view = 4;
    let nr=n.ref();print(*nr);
    let mut data = [1, 2, 3, 4];
    for slot in data.mut_ref() {
        if *slot == 2 { continue; }
        *slot += 10;
        if *slot == 13 { break; }
    }
    for item in data.ref() { print(*item); }
    let mut record = Record { number: 7 };
    touch(record.mut_ref());
    print(read(record.ref()));
    let corbo_for_source=100;
    let mut total:i64=0;
    for item in [5, 6] {total += item;}
    print(total);
    print(corbo_for_source);
}
''', '4\n11\n2\n13\n4\n8\n11\n100\n'),
        'next': ('''struct Counter { at:i64, stop:i64 }
impl Counter {
    fn next(&mut self)->Option<i64> {
        let at=&mut (*self).at;
        if *at >= (*self).stop {return None;}
        let result=*at;*at+=1;Some(result)
    }
}
fn source()->Counter {print(77);Counter {at:4,stop:6}}
fn main() {
    let mut counter=Counter {at:0,stop:4};
    for item in counter.mut_ref() {print(item);}
    for mut item in source() {item+=10;print(item);}
}
''', '0\n1\n2\n3\n77\n14\n15\n'),
        'aggregate-fields': ('''struct Entry {number:i64}
struct Tracker {buffer:[Entry;2]}
impl Tracker {
    fn update(&mut self) {
        for slot in (*self).buffer.mut_ref() {
            let number=&mut (*slot).number;
            *number+=1;
        }
    }
}
fn main(){
    let mut tracker=Tracker {buffer:[Entry{number:1},Entry{number:2}]};
    tracker.update();
    print(tracker.buffer[0].number);
}
''', '2\n'),
        'slices-nested': ('''fn visit(values:&mut [i64]) {
    for item in values { *item+=1; }
}
fn main(){
    let mut values=[1,2,3];visit(&mut values[..]);
    let mut total:i64=0;
    for x in values.ref(){for y in [1,2]{total+=*x+y;}}
    print(total);
    let empty:[i64;0]=[];
    for unused in empty.ref(){print(*unused);}
}
''', '27\n'),
        'cleanup': ('''struct Item {value:i64}
impl Item {fn drop(&mut self){print((*self).value);}}
struct Source {at:i64}
impl Source {
    fn next(&mut self)->Option<Item>{
        let at=&mut (*self).at;
        if *at>=3{return None;}
        *at+=1;Some(Item {value:*at})
    }
    fn drop(&mut self){print(99);}
}
fn main(){for item in Source {at:0}{if item.value==2{break;}}}
''', '1\n2\n99\n'),
    }
    refusals = {
        'immutable': 'fn main(){let value=1;let r=value.mut_ref();*r=2;}',
        'dangling': 'fn bad()->&i64 {let value=1;value.ref()} fn main(){}',
        'reference-level': 'fn read(value:&i64){} fn main(){let n=1;let r=&n;read(r.ref());}',
        'arity': 'fn main(){let value=1;value.ref(2);}',
        'moved-iterator': 'struct S {n:i64} impl S {fn next(&mut self)->Option<i64>{None}} fn main(){let s=S{n:0};for x in s {} print(s.n);}',
    }
    results=[]
    with tempfile.TemporaryDirectory(prefix='corboc-iteration-') as directory:
        root=Path(directory)
        for name,(source,expected) in cases.items():
            path=root/(name+'.crb');path.write_text(source)
            generated=subprocess.run([str(compiler),'--emit-c',str(path)],capture_output=True,text=True,timeout=90)
            assert generated.returncode==0,(name,generated.returncode,generated.stdout[-2000:],generated.stderr)
            c=root/(name+'.c');c.write_text(generated.stdout);binary=root/name
            subprocess.run(['cc','-std=c11','-pthread','-O1',str(c),'-lm','-o',str(binary)],check=True,capture_output=True,timeout=60)
            executed=subprocess.run([str(binary)],capture_output=True,text=True,timeout=15)
            assert (executed.returncode,executed.stdout)==(0,expected),(name,executed.returncode,executed.stdout,executed.stderr)
            results.append({'case':name,'status':'passed','stdout':executed.stdout})
            print(name,'passed',flush=True)
        for name,source in refusals.items():
            path=root/(name+'.crb');path.write_text(source)
            result=subprocess.run([str(compiler),'check',str(path)],capture_output=True,text=True,timeout=60)
            assert result.returncode!=0 and 'error[' in result.stderr,(name,result.returncode,result.stdout,result.stderr)
            results.append({'case':name,'status':'refused','stderr':result.stderr})
            print(name,'refused as expected',flush=True)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(results,indent=2)+'\n')


if __name__=='__main__':
    main()
