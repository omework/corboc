#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused bounded-channel API, ownership and async wait integration checks."""
import argparse,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    """Run three combined witnesses and five directly related compiler refusals."""
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--compiler',type=Path,required=True)
    p.add_argument('--stdlib',type=Path,default=ROOT/'.deps/corbo/stdlib/src')
    p.add_argument('--out',type=Path,default=ROOT/'build/channels/validation')
    a=p.parse_args();compiler=a.compiler.resolve();stdlib=a.stdlib.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
    results=[]
    for name,expected in [('channels_sync',['41','42','0','5050']),('channels_async',['210','201','202']),('channels_ownership',['101','102','103'])]:
        emitted=subprocess.run([str(compiler),'--emit-package-c',str(ROOT/'validation/fixtures'/name),'--stdlib-dir',str(stdlib)],capture_output=True,text=True,timeout=90)
        assert emitted.returncode==0,(name,emitted.returncode,emitted.stdout[:500],emitted.stderr)
        source=out/(name+'.c');source.write_text(emitted.stdout);binary=out/name
        subprocess.run(['cc','-pthread','-O1','-fsanitize=undefined','-fno-sanitize-recover=all',str(source),'-lm','-o',str(binary)],check=True,timeout=90)
        run=subprocess.run([str(binary)],capture_output=True,text=True,timeout=20)
        assert run.returncode==0 and run.stdout.split()==expected and not run.stderr,(name,run.returncode,run.stdout,run.stderr)
        results.append({'case':name,'status':'executed, fatal UBSan','stdout':run.stdout.split()});print(name,'passed',flush=True)
    for source in sorted((ROOT/'validation/fixtures/channel_refusals').glob('*.crb')):
        package=out/('reject_'+source.stem);(package/'src').mkdir(parents=True,exist_ok=True)
        (package/'package.toml').write_text('[package]\nname="channel_refusal"\n');(package/'src/main.crb').write_text(source.read_text())
        run=subprocess.run([str(compiler),'--emit-package-c',str(package),'--stdlib-dir',str(stdlib)],capture_output=True,text=True,timeout=45)
        assert run.returncode in (8,9,13),(source.name,run.returncode,run.stdout[:200],run.stderr)
        results.append({'case':source.stem,'status':'rejected','exit':run.returncode,'diagnostic':run.stdout.strip()});print(source.stem,'rejected',flush=True)
    (out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
if __name__=='__main__':main()
