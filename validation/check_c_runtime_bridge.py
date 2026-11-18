#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""C runtime header/library, generated type layouts and explicit aggregate operands."""
import argparse,shlex,subprocess,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(ROOT/"scripts"))
from corbo_sources import source_root
CORBO=source_root()
FIX=ROOT/'validation/fixtures/c_runtime_bridge'
EXPECTED={'names':'2\n3\n','aggregates':'11\n12\n14\n6\n17\n18\n19\n','descriptors':'12\n5\n8\n','envelopes':'4\n6\n3\n','wide':'14\n25\n','regions':'10\n20\n','cleanup':'42\n43\n','trust':'2\n','generics':'3\ntrue\n'}
REFUSED={
 'outside_unchecked':'struct Point{x:i64} fn main(){let p=Point{x:1};@c{(void)${p};}}',
 'unknown_operand':'fn main(){@unchecked{@c{(void)${missing};}}}',
 'moved_operand':'struct Point{x:i64} fn main(){let p=Point{x:1};let q=p;@unchecked{@c{(void)${p};}}drop(q);}',
}
C_REFUSED={
 'immutable_record':'struct Point{x:i64} fn main(){let p=Point{x:1};@unchecked{@c{${p}.f_x=2;}}}',
 'immutable_array':'fn main(){let a:[i64;1]=[1];@unchecked{@c{${a}.items[0]=2;}}}',
 'immutable_descriptor':'fn main(){let mut pool=pool<i64>(1);let value=pool.new(1);@unchecked{@c{${value}.pool=NULL;}}}',
}
EXTERNAL='''struct Point{x:i64} fn main(){let mut point=Point{x:3};let mut p=pool<i64>(1);let mut v=p.new(5);@unchecked{@c(includes={"HEADER"}){
 assert(point_value(&${point})==3);assert(external_info().position==corbo_datastack_info().position);
 CorboStackMark mark=corbo_datastack_mark();external_allocate();assert(external_info().position>mark.position);corbo_datastack_rewind(mark);
 external_store(&${v},17);${point}.f_x=7;
}}print(point.x);print(*v);}'''
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--corboc',type=Path,required=True);p.add_argument('--keep',type=Path,required=True);p.add_argument('--cc',default='cc');p.add_argument('--ar',default='ar');p.add_argument('--runner',default='');p.add_argument('--reuse-c',type=Path);a=p.parse_args();root=a.keep.resolve();root.mkdir(parents=True,exist_ok=True);cc=shlex.split(a.cc);runner=shlex.split(a.runner);san=['-fsanitize=undefined','-fno-sanitize-recover=all']
 def run(command,**kw):return subprocess.run([str(x)for x in command],capture_output=True,text=True,timeout=180,**kw)
 def emit(source,name):
  f=root/(name+'.crb');f.write_text(source);r=run([a.corboc.resolve(),'--emit-c',f]);return r
 def execute(c,name,expected,extra=()):
  for opt in ['0','2']:
   exe=root/(name+'-O'+opt+'.exe');r=run([*cc,'-std=c11','-pthread','-O'+opt,*san,c,*extra,'-lm','-o',exe]);assert r.returncode==0,(name,r.stderr)
   r=run([*runner,exe]);assert(r.returncode,r.stdout,r.stderr)==(0,expected,''),(name,opt,r);print('executed',name,'O'+opt,flush=True)
 for name,expected in EXPECTED.items():
  c=root/(name+'.c')
  if a.reuse_c:c.write_bytes((a.reuse_c/c.name).read_bytes())
  else:
   r=emit((FIX/(name+'.crb')).read_text(),name);assert r.returncode==0 and r.stdout.startswith(('/*','#')),(name,r);c.write_text(r.stdout)
  execute(c,name,expected)
 # Copy the standalone source tree so cross compilers can access it in their mounted workspace.
 rt=root/'runtime';shutil.copytree(CORBO/'runtime',rt,dirs_exist_ok=True)
 obj=root/'runtime.o';lib=root/'libcorbo_runtime.a';r=run([*cc,'-std=c11','-O2',*san,'-c',rt/'corbo_runtime.c','-o',obj]);assert r.returncode==0,r.stderr
 lib.unlink(missing_ok=True);r=run([*shlex.split(a.ar),'rcs',lib,obj]);assert r.returncode==0,r.stderr
 c=root/'library.c';c.write_bytes((FIX/'library.c').read_bytes());execute(c,'library','C runtime library passed\n',['-I'+str(rt),lib])
 # A separately compiled C object calls the very same runtime instance as generated Corbo.
 helper=root/'helper.c';helper.write_text('#include "corbo_runtime.h"\nCorboStackInfo external_info(void){return corbo_datastack_info();}\nvoid external_allocate(void){*(int64_t*)corbo_datastack_alloc(sizeof(int64_t),_Alignof(int64_t),1)=9;}\nvoid external_store(CorboAllocation*p,int64_t value){*(int64_t*)corbo_allocation_data(p)=value;}\n')
 header=root/'helper.h';header.write_text('#include <assert.h>\n#include "corbo_runtime.h"\nstatic inline int64_t point_value(const Corbo_Point*p){return p->f_x;}\nCorboStackInfo external_info(void);void external_allocate(void);void external_store(CorboAllocation*,int64_t);\n')
 r=emit(EXTERNAL.replace('HEADER',str(header)),'external');assert r.returncode==0,(r.returncode,r.stdout,r.stderr);c=root/'external.c';c.write_text(r.stdout);obj=root/'helper.o'
 r=run([*cc,'-std=c11','-O2',*san,'-I'+str(rt),'-c',helper,'-o',obj]);assert r.returncode==0,r.stderr
 execute(c,'external','7\n17\n',['-I'+str(rt),obj])
 if not a.reuse_c:
  for name,source in REFUSED.items():
   r=emit(source,name);assert r.returncode==(7 if name=='outside_unchecked'else 8),(name,r);print('refused',name,flush=True)
  for name,source in C_REFUSED.items():
   r=emit(source,name);assert r.returncode==0,(name,r);c=root/(name+'.c');c.write_text(r.stdout);r=run([*cc,'-std=c11','-pthread','-c',c,'-o',root/(name+'.o')]);assert r.returncode!=0,(name,'C accepted an immutable operand assignment');print('C refused',name,flush=True)
if __name__=='__main__':main()
