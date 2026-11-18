#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused generic identities, caller-owned tuple graphs and multi-wait registry regressions."""
import argparse,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(ROOT/"scripts"))
from corbo_sources import source_root
CORBO=source_root()
FIX=ROOT/'validation/fixtures/core_mechanisms'
EXPECTED={'nested_enum':'','tuple_tasks':'7\n8\n9\n10\n','nested_methods':'11\ntrue\n','deep':'4\n5\n','contract_nested':'11\ntrue\n','borrowed_tuple':'10\n20\n10\n20\n','tuple-relay':'1\n2\n','tuple_references':'3\n4\n9\n10\n11\n12\n','tuple_independent':'1\n2\n3\n4\n1\n4\n'}
REFUSED={
 'task_target_dropped':(FIX/'tuple_tasks.crb').read_text().replace('match first.join()', 'drop(a);match first.join()'),
 'task_target_written':(FIX/'tuple_tasks.crb').read_text().replace('match first.join()', 'a=99;match first.join()'),
 'nested_mismatch':(FIX/'nested_methods.crb').read_text().replace('Pair::new(11,true)','Pair<i64,i64>::new(11,true)'),
 'tuple_dead_source':(FIX/'tuple_independent.crb').read_text().replace('print(x.get());','drop(a);print(x.get());'),
 'tuple_write_reserved':(FIX/'tuple_independent.crb').read_text().replace('print(x.get());','a=99;print(x.get());'),
 'tuple_second_call_reserved':(FIX/'tuple_independent.crb').read_text().replace('print(z.get());','c=99;print(z.get());'),
 'tuple_local_escape':'struct View{value:&i64} fn pair(x:&i64)->(View,View){let n:i64=7;(View{value:x},View{value:&n})} fn main(){}',
}
def run(command,**kw):return subprocess.run([str(x)for x in command],capture_output=True,text=True,timeout=180,**kw)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--corboc',type=Path,required=True);p.add_argument('--keep',type=Path,required=True);p.add_argument('--cc',default='cc');p.add_argument('--runner',default='');p.add_argument('--reuse-c',type=Path);a=p.parse_args();a.keep.mkdir(parents=True,exist_ok=True)
 for name,expected in EXPECTED.items():
  c=a.keep/(name+'.c')
  if a.reuse_c:c.write_bytes((a.reuse_c/c.name).read_bytes())
  else:
   r=run([a.corboc.resolve(),'--emit-c',FIX/(name+'.crb')]);assert r.returncode==0 and r.stdout.startswith('#'),(name,r.returncode,r.stdout,r.stderr);c.write_text(r.stdout)
  for opt in ['0','2']:
   exe=a.keep/(name+'-O'+opt+'.exe');r=run([*shlex.split(a.cc),'-std=c11','-pthread','-O'+opt,'-fsanitize=undefined','-fno-sanitize-recover=all',c,'-lm','-o',exe]);assert r.returncode==0,(name,r.stderr)
   r=run([*shlex.split(a.runner),exe]);assert (r.returncode,r.stdout,r.stderr)==(0,expected,''),(name,opt,r);print('executed',name,'O'+opt,flush=True)
 if not a.reuse_c:
  for name,source in REFUSED.items():
   f=a.keep/(name+'.crb');f.write_text(source);r=run([a.corboc.resolve(),'--emit-c',f]);assert r.returncode==8,(name,r.returncode,r.stdout,r.stderr);expected_rule='4'if name=='tuple_local_escape'else'5';assert name=='nested_mismatch' or r.stdout.splitlines()[0]==expected_rule,(name,r.stdout);print('refused',name,flush=True)
  exe=a.keep/'readiness';r=run(['cc','-std=c11','-O2','-pthread','-I'+str(CORBO/'runtime'),'-fsanitize=undefined','-fno-sanitize-recover=all',FIX/'readiness.c','-o',exe]);assert r.returncode==0,r.stderr
  r=run([exe]);assert (r.returncode,r.stdout,r.stderr)==(0,'readiness registry passed\n',''),r;print('executed readiness transitions',flush=True)
if __name__=='__main__':main()
