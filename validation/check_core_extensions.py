#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Paired target annotations, foreign C headers and recorded composition regressions."""
import argparse
import os
from pathlib import Path
import shlex
import subprocess
ROOT=Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(ROOT/"scripts"))
from corbo_sources import source_root
CORBO=source_root()
FIXTURES=ROOT/'validation/fixtures/core_extensions'
EXPECTED={'propagation_reference':'7\n','propagation_record_reference':'7\n','tuple_moves':'1\n2\n','c_opaque':'43\n','propagation_async':'5\ntrue\n','propagation_unit':'7\n','propagation_record':'7\n','transient_scope':'3\n7\n','foreign_c':'42\n7\n','tuple_nested':'1\n2\n','tuple_mixed':'1\n2\n','scalar_pop':'7\n','mixed_constructor':'','slice_forward':'1\n','record_result_method':'7\n','borrowed_enum':'true\n','slice_parameter':'3\n','mixed_multi':'3\n7\n','propagation':'8\ntrue\n10\n0\n42\ntrue\n','propagation_conversion':'1\n','propagation_arguments':'2\n1\ntrue\n'}
REFUSED={
 'question_live_reference':'fn maybe(value:&i64)->Option<&i64>{Some(value)} fn f()->Option<i64>{let mut n:i64=7;let view=maybe(&n)?;n=8;Some(*view)} fn main(){}',
 'tuple_moved_after_join':'fn pair(value:i64)->(i64,i64){(value,2)} fn main(){let x:i64=1;let (a,b)=if true{pair(x)}else{(x,2)};print(x);print(a);print(b);}',
 'question_outside_envelope':'fn source()->Result<i64,bool>{Ok(1)} fn main(){let x=source()?;print(x);}',
 'question_mixed_option_result':'fn source()->Option<i64>{Some(1)} fn f()->Result<i64,bool>{let x=source()?;Ok(x)} fn main(){}',
 'question_without_conversion':'enum Left{Failed} enum Right{Failed} fn source()->Result<i64,Left>{Err(Left.Failed)} fn f()->Result<i64,Right>{let x=source()?;Ok(x)} fn main(){}',

 'unmatched_end':'#(endif) fn main(){}',
 'missing_end':'#(if: target.os == "macos") fn main(){}',
 'old_parenthesized_body':'#(if: target.os == "macos" {fn main(){}})',
 'bad_target_property':'#(if: target.fiction == "x") fn main(){} #(endif)',
 'bad_false_condition':'#(if: target.os == "never") #(if: typo.os == "x") fn f(){} #(endif) #(endif) fn main(){}',
 'c_outside_unchecked':'fn main(){@c {int x=0;}}',
 'c_header_flags':'fn main(){@unchecked{@c(includes={"x.h\" -O2"}){}}}',
 'c_header_not_literal':'fn main(){@unchecked{@c(includes={header}){}}}',
 'c_unknown_parameter':'fn main(){@unchecked{@c(flags={"x.h"}){}}}',
 'c_missing_brace':'fn main(){@unchecked{@c(includes={"stdint.h"}){ int x=0; }}',
 'c_unknown_binding':'fn main(){@unchecked{@c {${missing}=1;}}}',
 'c_moved_binding':'fn main(){let x:i64=1;let y=x;@unchecked{@c{printf("%lld",(long long)${x});}}drop(y);}',
 'slice_use_after_move':'fn main(){let a:[u8;2]=[1,2];let first=&a[..];let second=first;print(first[0]);print(second[0]);}',
 'tuple_type_mismatch':'fn pair()->(bool,i64){(true,2)} fn main(){let (a,b)=if true{pair()}else{(1,2)};print(a);print(b);}',
 'pop_shared':'fn main(){let mut p=Pool<Vector<i64>>::new(1);let mut v=p.new();v.push(7);let view=&v[..];drop(v.pop());print(view[0]);}',
}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--corboc',type=Path,required=True);p.add_argument('--keep',type=Path,required=True);p.add_argument('--cc',default='cc');p.add_argument('--runner',default='');p.add_argument('--reuse-c',type=Path);p.add_argument('--only',action='append',choices=list(EXPECTED));a=p.parse_args();root=a.keep.resolve();root.mkdir(parents=True,exist_ok=True)
 def emit(source,label):
  path=root/(label+'.crb');path.write_text(source)
  return subprocess.run([a.corboc.resolve(),'--emit-c',path],capture_output=True,timeout=90)
 for name,expected in EXPECTED.items():
  if a.only and name not in a.only:continue
  if not (FIXTURES/(name+'.crb')).exists():continue
  c=root/(name+'.c')
  if a.reuse_c:c.write_bytes((a.reuse_c/(name+'.c')).read_bytes())
  else:
   r=emit((FIXTURES/(name+'.crb')).read_text(),name);assert r.returncode==0 and r.stdout.startswith(b'#'),(name,r.returncode,r.stdout[:200],r.stderr);c.write_bytes(r.stdout)
  if name=='foreign_c':assert c.read_bytes().count(b'#include \"stdint.h\"')==1,'header was not deduplicated'
  exe=root/(name+'.exe');subprocess.run([*shlex.split(a.cc),'-std=c11','-pthread','-O2','-fsanitize=undefined','-fno-sanitize-recover=all',c,'-lm','-o',exe],check=True,timeout=180)
  r=subprocess.run([*shlex.split(a.runner),exe],capture_output=True,text=True,timeout=30);assert (r.returncode,r.stdout,r.stderr)==(0,expected,''),(name,r);print('executed:',name,flush=True)
 if not a.reuse_c and not a.only:
  for name,source in REFUSED.items():
   r=emit(source,name);expected_status=3 if name in {'c_header_flags','c_header_not_literal','c_unknown_parameter'} else 7 if name in {'unmatched_end','missing_end','old_parenthesized_body','bad_target_property','bad_false_condition','c_outside_unchecked','c_missing_brace'} else 8;assert r.returncode==expected_status,(name,r.returncode,r.stdout,r.stderr);print('refused:',name,'status',r.returncode,flush=True)
  # A native header contributes declarations; immutable substitutions are C rvalues.
  header=root/'operand.h';header.write_text('#define CORBO_TEST_VALUE 44\n')
  r=emit('fn main(){let mut value:i64=0;@unchecked{@c(includes={"'+str(header)+'"}){${value}=CORBO_TEST_VALUE;}}print(value);}', 'custom_header')
  assert r.returncode==0,(r.returncode,r.stdout,r.stderr)
  c=root/'custom_header.c';c.write_bytes(r.stdout);exe=root/'custom_header.exe'
  subprocess.run([*shlex.split(a.cc),'-std=c11','-O2',c,'-lm','-o',exe],check=True,timeout=60)
  r=subprocess.run([exe],capture_output=True,text=True,timeout=10);assert (r.returncode,r.stdout)==(0,'44\n'),r
  r=emit('fn main(){let value:i64=0;@unchecked{@c{${value}=1;}}}', 'immutable_c')
  assert r.returncode==0,(r.returncode,r.stdout,r.stderr)
  c=root/'immutable_c.c';c.write_bytes(r.stdout)
  r=subprocess.run([*shlex.split(a.cc),'-std=c11','-c',c,'-o',root/'immutable.o'],capture_output=True,timeout=60)
  assert r.returncode!=0,'C accepted assignment to an immutable operand'
  print('passed: custom header and immutable C operand',flush=True)
  # Target selection happens before resolving imports or collecting headers.
  pkg=root/'package';(pkg/'src').mkdir(parents=True,exist_ok=True);(pkg/'package.toml').write_text('[package]\nname="selection"\n');(pkg/'src/main.crb').write_text('''#(if: target.os == "never")
use nonexistent::missing;
fn chosen()->i64{99}
fn ignored(){@unchecked{@c(includes={"this_header_must_not_be_emitted.h"}){invalid C ignored;}}}
#(endif)
fn chosen()->i64{11}
fn main(){print(chosen());}
''')
  r=subprocess.run([a.corboc.resolve(),'--emit-package-c',pkg,'--stdlib-dir',CORBO/'stdlib/src'],capture_output=True,timeout=90);assert r.returncode==0 and b'#include "this_header' not in r.stdout,(r.returncode,r.stdout[:100]);print('passed: selection before imports/includes',flush=True)
if __name__=='__main__':main()
