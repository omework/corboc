#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused semantic diagnostic observations, with unchanged-verdict comparisons."""
import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def audit_sites():
    """Every normative refusal has a catalog identity; state writes are observed."""
    catalog=json.loads((ROOT/'docs/SEMANTIC_DIAGNOSTIC_SITES.json').read_text())
    service=(ROOT/'src/semantic_diagnostics/semantic.crb').read_text()
    block=service.split('// BEGIN FAILURE SITES\n',1)[1].split('// END FAILURE SITES',1)[0]
    array=block[block.index('{')+1:block.rindex('}')]
    reasons=json.loads('['+array+']')
    assert len(reasons)==len(catalog)+1
    for entry in catalog:assert reasons[entry['id']]==entry['message'],entry
    def close(text,start,opening='(',closing=')'):
        depth=0;quoted=False;at=start
        while at<len(text):
            char=text[at]
            if quoted:
                if char=='\\':at+=2;continue
                if char=='"':quoted=False
            elif char=='"':quoted=True
            elif char==opening:depth+=1
            elif char==closing:
                depth-=1
                if depth==0:return at
            at+=1
        raise AssertionError(('unclosed diagnostic call',start))
    found=set();writes=0
    for path in (ROOT/'src').rglob('*.crb'):
        if 'runtime_sources' in path.parts:continue
        text=path.read_text()
        for match in re.finditer(r'\b(?:violation_site|report_violation_site|type_violation)\(',text):
            finish=close(text,text.index('(',match.start()))
            last=text[match.end():finish].rsplit(',',1)[-1].strip()
            if last.isdigit():found.add(int(last))
        for match in re.finditer(r'values\[\w+\]\s*=\s*CheckedValue\s*\{',text):
            finish=close(text,text.index('{',match.start()),'{','}')
            assert re.match(r';\s*record_checked\(',text[finish+1:]),(path,text[match.start():finish+100])
            writes+=1
        if path.parent.name!='verify' or path.name!='diagnostics.crb':
            assert not re.search(r'\b(?:violation|report_violation)\s*\(',text),path
    active={entry['id'] for entry in catalog if not entry.get('retired',False)}
    assert found==active,{'missing':sorted(active-found),'unexpected':sorted(found-active)}
    return {'failure_sites':len(catalog),'observed_state_writes':writes,'status':'passed'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler',type=Path,required=True)
    parser.add_argument('--baseline',type=Path,required=True)
    parser.add_argument('--out',type=Path,default=ROOT/'build/semantic/results.json')
    args=parser.parse_args();compiler=args.compiler.resolve();baseline=args.baseline.resolve()
    audit=audit_sites();results=[]
    cases=[
        ('binding-types','fn main(){\n let value:i64=true;\n}\n', ['expected: i64','actual: bool']),
        ('operand-types','fn main(){\n let left:i64=1;\n let right:bool=true;\n let result=left+right;\n}\n',['expected: i64','actual: bool','value declared here']),
        ('argument-types','fn take(value:i64){}\nfn main(){\n take(true);\n}\n',['expected: i64','actual: bool','parameter type required here']),
        ('named-types','struct First{value:i64}\nstruct Second{value:i64}\nfn main(){\n let value:First=Second{value:1};\n}\n',['expected: First','actual: Second']),
        ('undefined-name','fn main(){\n print(missing);\n}\n',['current scope','missing']),
        ('moved-value','struct Item{value:i64}\nfn main(){\n let item=Item{value:1};\n let moved=item;\n print(item.value);\n}\n',['ownership was moved','ownership moved here','value declared here']),
        ('dropped-value','fn main(){\n let value:i64=1;\n drop(value);\n print(value);\n}\n',['explicitly destroyed','value destroyed here']),
        ('immutable','fn main(){\n let value:i64=1;\n value=2;\n}\n',['immutable','value declared here']),
        ('shared-write','fn main(){\n let mut value:i64=1;\n let view=&value;\n *view=2;\n}\n',['shared reference','borrow created here']),
        ('borrow-escape','fn leak()->&i64{\n let value:i64=1;\n let view=&value;\n return view;\n}\nfn main(){}\n',['outlive','borrow created here','borrowed target declared here']),
        ('drop-with-borrow','struct Item{value:i64}\nfn main(){\n let item=Item{value:1};\n let view=&item;\n drop(item);\n print((*view).value);\n}\n',['borrow','borrow created here']),
    ]
    with tempfile.TemporaryDirectory(prefix='corboc-semantic-') as temporary:
        root=Path(temporary)
        for name,source,expected in cases:
            path=root/(name+'.crb');path.write_text(source)
            old=subprocess.run([str(baseline),'check',str(path)],capture_output=True,text=True,timeout=60)
            new=subprocess.run([str(compiler),'check',str(path)],capture_output=True,text=True,timeout=60)
            assert new.returncode==old.returncode!=0,(name,old.returncode,new.returncode,new.stderr)
            for fragment in expected:assert fragment in new.stderr,(name,fragment,new.stderr)
            assert str(path.resolve())+':' in new.stderr and '^' in new.stderr,(name,new.stderr)
            assert not new.stdout.strip(),(name,new.stdout)
            assert '__din_package_' not in new.stderr and '__corbo_specialized_' not in new.stderr,(name,new.stderr)
            if name=='moved-value':assert str(path.resolve())+':4:' in new.stderr,new.stderr
            if name=='dropped-value':assert str(path.resolve())+':3:' in new.stderr,new.stderr
            if name=='shared-write':assert str(path.resolve())+':3:' in new.stderr,new.stderr
            results.append({'case':name,'exit':new.returncode,'baseline_exit':old.returncode,'stderr':new.stderr})
            print(name,'passed',flush=True)
        source=root/'accepted.crb';source.write_text('fn main(){let mut data=[1,2];for item in data.mut_ref(){*item+=1;}for item in data.ref(){print(*item);}}\n')
        for binary in [baseline,compiler]:
            run=subprocess.run([str(binary),'check',str(source)],capture_output=True,text=True,timeout=60)
            assert run.returncode==0,(str(binary),run.returncode,run.stderr)
        results.append({'case':'accepted iteration regression','exit':0});print('accepted regression passed',flush=True)
        source.write_text('fn main(){let value:i64=true;}\n')
        old=subprocess.run([str(baseline),'--verify',str(source)],capture_output=True,text=True,timeout=60)
        new=subprocess.run([str(compiler),'--verify',str(source)],capture_output=True,text=True,timeout=60)
        assert (new.returncode,new.stdout,new.stderr)==(old.returncode,old.stdout,old.stderr),('raw protocol',old,new)
        results.append({'case':'raw machine protocol unchanged','exit':new.returncode});print('raw protocol passed',flush=True)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps({'audit':audit,'observations':results},indent=2)+'\n')


if __name__=='__main__':main()
