#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
from pathlib import Path
import shutil,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from corbo_sources import source_root
import argparse,subprocess
parser=argparse.ArgumentParser(description="Build a host-running, test-only target emitter; this is not a native target compiler binary.")
parser.add_argument('--target',choices=['linux','macos','windows'],required=True)
parser.add_argument('--keep',type=Path,required=True)
parser.add_argument('--seed',type=Path,required=True)
args=parser.parse_args();repo=Path(__file__).resolve().parents[1]
root=repo;corbo=source_root();target=args.target;args.keep.mkdir(parents=True,exist_ok=True);out=args.keep/('compiler-'+target);shutil.copytree(root,out,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.git','.deps','build','__pycache__'))
def body(path,name,new):
 s=path.read_text();pos=0
 while True:
  m=re.search(r'fn '+name+r'\([^)]*\)\s*->\s*\w+\s*\{',s[pos:])
  if not m:break
  a=pos+m.end();b=a;depth=1
  while depth:
   depth+=(s[b]=='{')-(s[b]=='}');b+=1
  s=s[:a]+' '+new+' '+s[b-1:];pos=a+len(new)+2
 path.write_text(s)
os={'linux':4,'windows':2,'macos':3}[target];main=out/'src/main.crb'
for name,val in [('target_os',os),('target_family',2 if target=='windows' else 1),('target_arch',6),('target_pointer_width',8)]:body(main,name,str(val))
asm=out/'src/lowering_asm/lowering_asm.crb'
for name,val in [('arm_target',False),('darwin_target',target=='macos'),('windows_target',target=='windows')]:body(asm,name,str(val).lower())
checks=out/'src/native_checks/native_checks.crb'
for name in ['valid_register','has_register_class']:body(checks,name,'true')
generated=args.keep/('emitter-'+target+'.c');binary=args.keep/('emitter-'+target)
with generated.open('wb')as output:
 subprocess.run([args.seed.resolve(),'--emit-package-c',out,'--stdlib-dir',corbo/'stdlib/src'],stdout=output,check=True,timeout=120)
subprocess.run(['cc','-std=c11','-pthread','-O1',generated,'-lm','-o',binary],check=True,timeout=180)
print(binary)
