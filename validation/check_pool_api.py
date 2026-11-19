#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused Pool constructor and fallible allocation checks, without a broad corpus run."""
import argparse,json,platform,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--corboc',required=True,type=Path);p.add_argument('--stdlib-dir',required=True,type=Path);p.add_argument('--keep',required=True,type=Path);a=p.parse_args();root=a.keep.resolve();root.mkdir(parents=True,exist_ok=True);compiler=a.corboc.resolve();std=a.stdlib_dir.resolve()
PRE='use std::{Pool,PoolError,Vector};\n'
ACCEPT={
'primitive':('fn main(){let mut p=Pool<i64>::new(1);let first=p.new(7);match p.try(8){Ok(v)=>{drop(v);print(0);},Err(e)=>{match e{PoolError.Full=>{print(*first);},}}}drop(first);let r:Result<A<i64>,PoolError>=p.try();match r{Ok(v)=>{print(*v);},Err(e)=>{drop(e);print(-1);},}}','7\n0\n'),
'point':('struct Point{x:i64,y:i64} fn main(){let mut p=Pool<Point>::new(1);let result:Result<A<Point>,PoolError>=p.try({x:4,y:9});match result{Ok(v)=>{print((*v).x);print((*v).y);},Err(e)=>{drop(e);print(-1);},}}','4\n9\n'),
'cleanup':('struct Token{id:i64} impl Token{fn drop(&mut self){print((*self).id);}} fn main(){let mut p=Pool<Token>::new(1);let held=p.new(Token{id:1});let candidate=Token{id:2};let failed=p.try(candidate);match failed{Ok(v)=>{drop(v);},Err(e)=>{match e{PoolError.Full=>{print(99);},}}}drop(held);let unused=p.try(Token{id:3});}','2\n99\n1\n3\n'),
'once':('fn make(n:&mut i64)->i64{*n=*n+1;*n} fn main(){let mut p=Pool<i64>::new(1);let held=p.new(10);let mut calls:i64=0;let failed=p.try(make(&mut calls));print(calls);drop(failed);print(*held);}','1\n10\n'),
'enum_arms':('enum Item{Left(i64),Right(i64)} fn main(){let mut p=Pool<Item>::new(1);let left=p.new(Item.Left(1));match p.try(Item.Right(2)){Ok(v)=>{print(1);drop(v);},Err(e)=>{drop(e);print(-1);},}match p.try(Item.Left(3)){Ok(v)=>{print(-2);drop(v);},Err(e)=>{match e{PoolError.Full=>{print(2);},}}}drop(left);}','1\n2\n'),
'forward':('fn make(p:&mut Pool<i64>)->Result<A<i64>,PoolError>{let value=p.try(42)?;Ok(value)} fn main(){let mut p=Pool<i64>::new(1);match make(&mut p){Ok(v)=>{print(*v);},Err(e)=>{drop(e);print(-1);},}}','42\n'),
'vector':('fn main(){let mut p=Pool<Vector<i64>>::new(1);let result=p.try();let mut vector=match result{Ok(v)=>{v},Err(e)=>{drop(e);return;},};vector.push(42);print(vector.len());}','1\n'),
'borrowed_field':('struct View{data:&i64} fn main(){let mut p=Pool<View>::new(1);let number:i64=42;let result=p.try(View{data:&number});match result{Ok(v)=>{print(*(*v).data);},Err(e)=>{drop(e);},}}','42\n'),
'defaults':('struct Point{x:i64,y:i64} fn main(){let mut p=Pool<Point>::new(2);let first=p.new();match p.try({}){Ok(v)=>{print((*v).x);print((*v).y);},Err(e)=>{drop(e);print(-1);},}drop(first);}','0\n0\n'),
}
REJECT={
'old_notation':'fn main(){let mut p=pool<i64>(1);drop(p);}',
'missing_new':'fn main(){let mut p=Pool<i64>(1);drop(p);}',
'zero_capacity':'fn main(){let mut p=Pool<i64>::new(0);drop(p);}',
'immutable':'fn main(){let p=Pool<i64>::new(1);let r=p.try(1);drop(r);}',
'wrong_type':'fn main(){let mut p=Pool<i64>::new(1);let r=p.try(true);drop(r);}',
'moved_input':'fn main(){let mut p=Pool<i64>::new(1);let input:i64=7;let r=p.try(input);print(input);drop(r);}',
'dead_pool':'fn main(){let mut p=Pool<i64>::new(1);let r=p.try(1);drop(p);match r{Ok(v)=>{print(*v);},Err(e)=>{drop(e);},}}',
'dead_field':'struct View{data:&i64} fn main(){let mut p=Pool<View>::new(1);let number:i64=42;let result=p.try(View{data:&number});drop(number);match result{Ok(v)=>{print(*(*v).data);},Err(e)=>{drop(e);},}}',
'escaping_pool':'fn bad()->Result<A<i64>,PoolError>{let mut p=Pool<i64>::new(1);p.try(1)} fn main(){drop(bad());}',
}
rows=[]
def emit(name,source):
 pkg=root/name;(pkg/'src').mkdir(parents=True,exist_ok=True);(pkg/'package.toml').write_text('[package]\nname="pool_check"\n');(pkg/'src/main.crb').write_text(PRE+source+'\n');return subprocess.run([compiler,'--emit-package-c',pkg,'--stdlib-dir',std],capture_output=True,timeout=120)
for name,(source,expected) in ACCEPT.items():
 r=emit(name,source);assert r.returncode==0,(name,r.returncode,r.stdout[:300],r.stderr);c=root/(name+'.c');c.write_bytes(r.stdout);exe=root/(name+'.exe');subprocess.run(['cc','-std=c11','-pthread','-O1','-fsanitize=undefined','-fno-sanitize-recover=all',c,'-lm','-o',exe],check=True,timeout=120);r=subprocess.run([exe],capture_output=True,text=True,timeout=15);assert(r.returncode,r.stdout,r.stderr)==(0,expected,''),(name,r);rows.append({'name':name,'passed':True});print('PASS',name,flush=True)
for name,source in REJECT.items():
 r=emit(name,source);assert r.returncode in (7,8),(name,r.returncode,r.stdout[:300],r.stderr);rows.append({'name':name,'passed':True,'status':r.returncode});print('REFUSED',name,flush=True)
(root/'report.json').write_text(json.dumps({'platform':platform.platform(),'cases':rows},indent=2)+'\n')
