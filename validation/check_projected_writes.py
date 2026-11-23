#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Regression checks for recursive assignment places, not receiver special cases."""
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

prefix = '''enum SlotState { Available, Busy, Consumed }
struct Tracker { buffer: [(u64, SlotState); 5] }
impl Tracker {
'''
suffix = '''
}
fn main() {
    let mut tracker = Tracker { buffer: [(0, SlotState.Available); 5] };
    tracker.change(42);
    print(tracker.buffer[0].0);
}
'''
cases = {
    'field_index': 'fn change(&mut self, from:u64){self.buffer[0]=(from,SlotState.Consumed);}',
    'explicit_deref': 'fn change(&mut self, from:u64){(*self).buffer[0]=(from,SlotState.Consumed);}',
    'tuple_component': 'fn change(&mut self, from:u64){self.buffer[0].0=from;self.buffer[0].1=SlotState.Consumed;}',
    'compound_component': 'fn change(&mut self, from:u64){self.buffer[0].0+=from;}',
    'slice_alias': 'fn change(&mut self, from:u64){let buffer=&mut self.buffer[..];buffer[0]=(from,SlotState.Consumed);}',
    'borrowed_loop': '''fn change(&mut self, from:u64){
        for slot in self.buffer.mut_ref(){slot.0=from;slot.1=SlotState.Consumed;}
    }''',
    'compaction': '''fn change(&mut self, from:u64){
        self.buffer[1]=(from,SlotState.Consumed);
        let mut index:usize=0;
        for slot in self.buffer.ref() {
            if slot.0>0 {self.buffer[index]=(slot.0,slot.1);index+=1;}
        }
        while index<self.buffer.len(){self.buffer[index]=(0,SlotState.Available);index+=1;}
    }''',
}
packages = {name: prefix + body + suffix for name, body in cases.items()}
packages['inferred_local_array'] = """
enum SlotState{Available,Consumed}
fn main(){let zero:u64=0;let mut rows=[(zero,SlotState.Available);2];rows[0]=(42,SlotState.Consumed);print(rows[0].0);}
"""
packages['nested_field'] = '''
enum SlotState{Available,Consumed}
struct Inner{buffer:[(u64,SlotState);2]}
struct Outer{inner:Inner}
impl Outer{fn change(&mut self,value:u64){self.inner.buffer[0]=(value,SlotState.Consumed);}}
fn main(){let mut o=Outer{inner:Inner{buffer:[(0,SlotState.Available);2]}};o.change(42);print(o.inner.buffer[0].0);}
'''
packages['record_element'] = '''
struct Entry{value:u64}
struct Outer{entries:[Entry;2]}
impl Outer{fn change(&mut self,value:u64){self.entries[0]=Entry{value:value};}}
fn main(){let mut o=Outer{entries:[Entry{value:0};2]};o.change(42);print(o.entries[0].value);}
'''
packages['async_receiver'] = """
enum SlotState{Available,Consumed}
struct Tracker{buffer:[(u64,SlotState);2]}
impl Tracker{async fn change(&mut self,value:u64){yield;self.buffer[0]=(value,SlotState.Consumed);}}
async fn run()->u64{
    let mut t=Tracker{buffer:[(0,SlotState.Available);2]};
    t.change(42).await;
    t.buffer[0].0
}
fn main(){let execution=runtime::spawn(run());match execution.join(){Ok(value)=>{print(value);},Err(_e)=>{print(0);},};}
"""
packages['runtime_bound'] = prefix + 'fn change(&mut self, from:u64){self.buffer[from]=(1,SlotState.Available);}' + suffix
for name, source in packages.items():
    package = out / name
    (package / 'src').mkdir(parents=True, exist_ok=True)
    (package / 'package.toml').write_text('[package]\nname="projected_write"\n')
    (package / 'src/main.crb').write_text(source + '\n')
    generated = subprocess.run([compiler, '--emit-package-c', package], capture_output=True, text=True, timeout=60)
    assert generated.returncode == 0, (name, generated.returncode, generated.stdout[-1000:], generated.stderr)
    c = package / 'probe.c'; c.write_text(generated.stdout)
    binary = package / 'probe'
    built = subprocess.run(['cc', '-std=c11', '-O1', '-pthread', '-fsanitize=undefined', '-fno-sanitize-recover=all', c, '-lm', '-o', binary], capture_output=True, text=True, timeout=60)
    assert built.returncode == 0, (name, built.stderr[-2000:])
    ran = subprocess.run([binary], capture_output=True, text=True, timeout=15)
    if name == 'runtime_bound':
        assert ran.returncode != 0 and 'indice' in ran.stderr, (name, ran)
        assert 'runtime error:' not in ran.stderr, (name, ran)
        print(name, 'trapped before access', flush=True)
    else:
        assert (ran.returncode, ran.stdout) == (0, '42\n'), (name, ran)
        print(name, 'passed', flush=True)

for name, body, rule in [
    ('field_move', 'fn change(&mut self,from:u64){for slot in self.buffer{self.buffer[0]=(from,slot.1);}}', 'N3'),
    ('readonly', 'fn change(&self,from:u64){self.buffer[0]=(from,SlotState.Consumed);}', 'N5'),
    ('wrong_type', 'fn change(&mut self,from:u64){self.buffer[0]=(true,SlotState.Consumed);}', 'N1'),
    ('wrong_arity', 'fn change(&mut self,from:u64){self.buffer[0]=(from,SlotState.Consumed,from);}', 'N1'),
    ('fixed_bound', 'fn change(&mut self,from:u64){self.buffer[5]=(from,SlotState.Consumed);}', 'N1'),
]:
    path = out / (name + '.crb'); path.write_text(prefix + body + suffix)
    checked = subprocess.run([compiler, 'check', path], capture_output=True, text=True, timeout=60)
    diagnostic = checked.stdout + checked.stderr
    assert checked.returncode != 0 and 'error[' + rule + ']' in diagnostic, (name, checked)
    assert 'has not been initialized' not in diagnostic, (name, diagnostic)
    print(name, 'rejected with', rule, flush=True)
