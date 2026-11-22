#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused tuple selectors and for-pattern checks; no broad corpus campaign."""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

CASES = {'wal-fields': {'source': '#(configurable)\n'
                          'pub const WAL_CONCURRENT_CONSUMER_NUMBER:u16=2;\n'
                          'enum SlotState { Pending, Consumed }\n'
                          'struct Tracker { '
                          'buffer:[(u64,SlotState);WAL_CONCURRENT_CONSUMER_NUMBER] }\n'
                          'impl Tracker {\n'
                          ' fn update(&mut self, offset:u64){\n'
                          '  for slot in self.buffer.mut_ref(){if slot.0==offset '
                          '{slot.1=SlotState.Consumed;}}\n'
                          ' }\n'
                          '}\n'
                          'fn main(){let mut '
                          'tracker=Tracker{buffer:[(1,SlotState.Pending),(2,SlotState.Pending)]};tracker.update(2);for '
                          'slot in '
                          'tracker.buffer.ref(){print(slot.0);print(slot.1==SlotState.Consumed);}}\n'
                          '\n',
                'stdout': '1\nfalse\n2\ntrue\n'},
 'borrow-pattern': {'source': 'fn main(){let mut rows=[(1,2),(3,4)];for (x,y) in '
                              'rows.mut_ref(){*x+=*y;}for (x,y) in '
                              'rows.ref(){print(*x);print(*y);}}\n',
                    'stdout': '3\n2\n7\n4\n'},
 'triple': {'source': 'fn main(){let mut rows=[(1,2,3),(4,5,6)];for (a,b,c) in '
                      'rows.mut_ref(){*c=*a+*b;continue;}for slot in rows.ref(){print(slot.2);}}\n',
            'stdout': '3\n9\n'},
 'owned': {'source': 'fn main(){for (a,b) in [(1,2),(3,4)]{print(a+b);}}\n', 'stdout': '3\n7\n'},
 'fields': {'source': 'fn main(){let mut t=(1,2);print(t.0);t.1=7;print(t.1);let '
                      'x:f64=.5;print(x==0.5);}\n',
            'stdout': '1\n7\ntrue\n'},
 'enum-pattern': {'source': 'enum S{Pending,Consumed} fn main(){let mut rows=[(1,S.Pending)];for '
                            '(a,b) in rows.mut_ref(){*b=S.Consumed;}for (a,b) in '
                            'rows.ref(){print(*b==S.Consumed);}}',
                  'stdout': 'true\n'}}

REFUSALS = {'bad-arity': {'source': 'fn main(){let rows=[(1,2,3)];for (a,b) in rows.ref(){print(*a);}}\n',
               'message': 'tuple arity'},
 'bad-index': {'source': 'fn main(){let t=(1,2);print(t.3);}\n', 'message': 'tuple index'},
 'shared-write': {'source': 'fn main(){let rows=[(1,2)];for (a,b) in rows.ref(){*a=3;}}\n',
                  'message': 'shared reference'},
 'move-source': {'source': 'fn main(){let rows=[(1,2)];for (a,b) in '
                           'rows{print(a+b);}print(rows[0].0);}\n',
                 'message': 'moved'},
 'bad-comma': {'source': 'fn main(){for (a b) in [(1,2)] {}}\n', 'message': "expected ',' or ')'"},
 'bad-one': {'source': 'fn main(){for (a) in [(1,2)] {}}\n', 'message': 'at least two'},
 'borrow-escape': {'source': 'fn bad()->&mut i64 {let mut rows=[(1,2)];for (a,b) in '
                             'rows.mut_ref(){return a;} let mut n=1;&mut n} fn main(){}\n',
                   'message': 'error[N4]'}}



def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler',type=Path,required=True)
    parser.add_argument('--out',type=Path,default=Path('build/tuple-for/results.json'))
    args=parser.parse_args();compiler=args.compiler.resolve();results=[]
    with tempfile.TemporaryDirectory(prefix='corboc-tuple-for-') as directory:
        root=Path(directory)
        for name,case in CASES.items():
            path=root/(name+'.crb');path.write_text(case['source'])
            generated=subprocess.run([str(compiler),'--emit-c',str(path)],capture_output=True,text=True,timeout=90)
            if generated.returncode:
                detail=subprocess.run([str(compiler),'check',str(path)],capture_output=True,text=True,timeout=60)
                raise AssertionError((name,generated.returncode,detail.stderr,generated.stdout[-1000:]))
            c=root/(name+'.c');c.write_text(generated.stdout);binary=root/name
            built=subprocess.run(['cc','-std=c11','-pthread','-O1','-fsanitize=undefined','-fno-sanitize-recover=all',str(c),'-lm','-o',str(binary)],capture_output=True,text=True,timeout=60)
            assert built.returncode==0,(name,built.stderr)
            ran=subprocess.run([str(binary)],capture_output=True,text=True,timeout=15)
            assert (ran.returncode,ran.stdout)==(0,case['stdout']),(name,ran.returncode,ran.stdout,ran.stderr)
            results.append({'case':name,'status':'passed','stdout':ran.stdout,'ubsan':True})
            print(name,'passed',flush=True)
        for name,case in REFUSALS.items():
            path=root/(name+'.crb');path.write_text(case['source'])
            result=subprocess.run([str(compiler),'check',str(path)],capture_output=True,text=True,timeout=60)
            assert result.returncode in (7,8) and case['message'] in result.stderr,(name,result.returncode,result.stderr)
            assert str(path.resolve())+':' in result.stderr and '^' in result.stderr,(name,result.stderr)
            results.append({'case':name,'status':'refused','exit':result.returncode,'stderr':result.stderr})
            print(name,'refused as expected',flush=True)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(results,indent=2)+'\n')


if __name__=='__main__':main()
