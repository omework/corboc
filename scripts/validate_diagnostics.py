#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused human-diagnostic checks; original source, imports and rewrite origins."""
import argparse,json,os,platform,subprocess,tempfile
from validate_file_watch import Watch
from pathlib import Path


def main():
    """Compare a small set of failures against their original source coordinates."""
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--compiler',type=Path,required=True)
    p.add_argument('--out',type=Path,default=Path('build/diagnostics/results.json'));a=p.parse_args()
    compiler=a.compiler.resolve();results=[]
    with tempfile.TemporaryDirectory(prefix='corboc-diagnostics-') as temporary:
        root=Path(temporary);env=dict(os.environ,PATH=str(root/'empty-path'))
        cases=[
            ('type','fn main() {\n    let value: i64 = true;\n}\n',8,'error[N1]','true',2),
            ('move','struct Item { value: i64 }\nfn main() {\n    let item = Item { value: 1 };\n    let moved = item;\n    print(item.value);\n}\n',8,'error[N6]','item.value',5),
            ('syntax','fn main() {\n    let = 42;\n}\n',7,'expected a binding name','let = 42',2),
            ('unclosed','fn main() {\n    let value = 42;\n',7,'not closed','fn main()',1),
            ('for-loop','fn main() {\n    let buffer = [1, 2];\n    for slot buffer { print(slot); }\n}\n',7,"expected 'in'",'for slot buffer',3),
            ('initializer','fn main() {\n    let value: i64;\n}\n',7,"expected '=' and an initializer",'let value',2),
            ('separator','fn main() {\n    print(1) print(2);\n}\n',7,"expected ';'",'print(1) print(2)',2),
            ('lex','fn main() {\n    print("unterminated);\n}\n',3,'unterminated string','unterminated',2),
            ('generic','#(type: T)\nfn identity(value: T) -> T { value }\n\nfn main() {\n    let value: i64 = identity(true);\n}\n',8,'error[','identity(true)',5),
            ('closure','fn main() {\n    let read = || -> i64 { true };\n    print(read());\n}\n',8,'error[','true',2),
        ]
        for name,source,status,message,excerpt,line in cases:
            file=root/(name+'.crb');file.write_text(source)
            run=subprocess.run([str(compiler),'check',str(file)],env=env,capture_output=True,text=True,timeout=45)
            assert run.returncode==status,(name,run.returncode,run.stdout,run.stderr)
            assert str(file.resolve())+':'+str(line)+':' in run.stderr,(name,run.stderr)
            assert message in run.stderr and excerpt in run.stderr and '^' in run.stderr,(name,run.stderr)
            assert not run.stdout.strip(),(name,'raw diagnostic leaked to stdout',run.stdout)
            assert '__din_package_' not in run.stderr and '__corbo_specialized_' not in run.stderr,(name,run.stderr)
            results.append({'case':name,'exit':status,'stderr':run.stderr});print(name,'passed',flush=True)
        missing=root/'missing_import.crb';missing.write_text('use missing::answer;\nfn main(){print(answer());}\n')
        run=subprocess.run([str(compiler),'check',str(missing)],env=env,capture_output=True,text=True,timeout=30)
        assert run.returncode==13 and str(missing.resolve())+':1:' in run.stderr and 'import' in run.stderr,(run.returncode,run.stderr)
        results.append({'case':'unresolved import','exit':13,'stderr':run.stderr});print('unresolved import passed',flush=True)
        watched=root/'watched.crb';watched.write_text('fn main(){\n    let value:i64=true;\n}\n')
        watch=Watch(compiler,watched,env,root)
        try:
            watch.wait(str(watched.resolve())+':2:');watch.wait('check failed')
            watched.write_text('fn main(){print(42); }\n');watch.wait('check passed')
            watched.write_text('fn main(){\n\n\n    let value:i64=true;\n}\n')
            watch.wait(str(watched.resolve())+':4:');watch.wait('check failed')
            results.append({'case':'watch refreshes source locations after recovery','status':'passed'});print('watch locations passed',flush=True)
        finally:watch.close()
        package=root/'project';(package/'src/helper').mkdir(parents=True)
        (package/'package.toml').write_text('[package]\nname="project"\n')
        (package/'src/main.crb').write_text('use project::helper::answer;\nfn main(){print(answer());}\n')
        helper=package/'src/helper/helper.crb';helper.write_text('pub fn answer()->i64 {\n    true\n}\n')
        run=subprocess.run([str(compiler),'check',str(package)],env=env,capture_output=True,text=True,timeout=45)
        assert run.returncode==8 and str(helper.resolve())+':2:' in run.stderr and '^' in run.stderr,(run.returncode,run.stderr)
        results.append({'case':'imported source','exit':8,'stderr':run.stderr});print('imported source passed',flush=True)
        raw=subprocess.run([str(compiler),'--emit-package-c',str(package)],env=env,capture_output=True,text=True,timeout=45)
        assert raw.returncode==8 and raw.stdout.split() and all(word.isdigit() for word in raw.stdout.split()),('machine protocol',raw)
        results.append({'case':'legacy machine protocol','exit':8});print('legacy machine protocol passed',flush=True)
        if platform.system()=='Darwin' and platform.machine()=='arm64':
            run=subprocess.run([str(compiler),'build',str(package),'-o',str(root/'failed-build')],env=env,capture_output=True,text=True,timeout=30)
            assert run.returncode==8 and str(helper.resolve())+':2:' in run.stderr and '^' in run.stderr,(run.returncode,run.stdout,run.stderr)
            results.append({'case':'normal build source diagnostic','exit':8,'stderr':run.stderr});print('build source passed',flush=True)
        (package/'package.toml').write_text('[package]\nname=\n')
        run=subprocess.run([str(compiler),'check',str(package)],env=env,capture_output=True,text=True,timeout=30)
        assert run.returncode==12 and str((package/'package.toml').resolve()) in run.stderr and 'manifest' in run.stderr,(run.returncode,run.stderr)
        results.append({'case':'manifest path','exit':12,'stderr':run.stderr});print('manifest path passed',flush=True)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(results,indent=2)+'\n')

if __name__=='__main__':main()
