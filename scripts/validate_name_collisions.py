#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused duplicate-name identity, provenance and unchanged-verdict checks."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

CASES = {
    'root_type_and_import': ({
        'src/group.crb':'// Root module type.\npub struct Group {}\n',
        'src/group/group.crb':'// Child module types.\npub struct Group {}\npub struct FrameRange {}\n',
        'src/main.crb':'// Root entry.\nuse demo::group::{Group, FrameRange};\nfn main() {}\n',
    }, ["existing: struct demo::Group", "incoming: struct demo::group::Group", "help: use 'as'", 'src/group.crb:2:', 'src/group/group.crb:2:', 'src/main.crb:2:19:']),
    'two_imports': ({
        'src/left/left.crb':'pub struct Group {}\n',
        'src/right/right.crb':'pub enum Group { End; }\n',
        'src/main.crb':'use demo::left::Group;\nuse demo::right::Group;\nfn main() {}\n',
    }, ['existing: struct demo::left::Group','incoming: enum demo::right::Group','previous import binds this name here','src/left/left.crb:1:','src/right/right.crb:1:','src/main.crb:2:']),
    'alias_collision': ({
        'src/left/left.crb':'pub struct First {}\n',
        'src/right/right.crb':'pub struct Second {}\n',
        'src/main.crb':'use demo::left::First as Entry;\nuse demo::right::Second as Entry;\nfn main() {}\n',
    }, ["name 'Entry'",'existing: struct demo::left::First','incoming: struct demo::right::Second','previous import binds this name here']),
    'duplicate_declarations': ({
        'src/one.crb':'pub struct Item {}\n',
        'src/two.crb':'pub enum Item { End; }\n',
        'src/main.crb':'fn main() {}\n',
    }, ['struct demo::Item','enum demo::Item','src/one.crb:1:','src/two.crb:1:','rename one declaration']),
    'module_type_ambiguity': ({
        'src/group/group.crb':'pub struct Group {}\n',
        'src/group/Group/source.crb':'pub struct Item {}\n',
        'src/main.crb':'use demo::group::Group;\nfn main() {}\n',
    }, ['struct demo::group::Group','module demo::group::Group','disambiguate this path']),
}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler',type=Path,required=True)
    parser.add_argument('--baseline',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    a=parser.parse_args();compiler=a.compiler.resolve();baseline=a.baseline.resolve();results=[]
    with tempfile.TemporaryDirectory(prefix='corbo-name-collisions-') as temp:
        root=Path(temp)
        for name,(files,fragments) in CASES.items():
            package=root/name;package.mkdir();(package/'package.toml').write_text('[package]\nname="demo"\n')
            for relative,source in files.items():
                path=package/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(source)
            old=subprocess.run([baseline,'check',package],capture_output=True,text=True,timeout=60)
            new=subprocess.run([compiler,'check',package],capture_output=True,text=True,timeout=60)
            assert old.returncode==new.returncode==14,(name,old,new)
            assert new.stderr.count('error[E0014]')==1,(name,new.stderr)
            for fragment in fragments:assert fragment in new.stderr,(name,fragment,new.stderr)
            assert 'note:' in new.stderr and '^' in new.stderr,(name,new.stderr)
            assert not new.stdout,(name,new.stdout)
            old_raw=subprocess.run([baseline,'--emit-package-c',package],capture_output=True,text=True,timeout=60)
            new_raw=subprocess.run([compiler,'--emit-package-c',package],capture_output=True,text=True,timeout=60)
            assert (old_raw.returncode,old_raw.stdout,old_raw.stderr)==(new_raw.returncode,new_raw.stdout,new_raw.stderr),(name,old_raw,new_raw)
            results.append(dict(case=name,exit=new.returncode,stderr=new.stderr,raw_protocol='unchanged'))
            print(name,'passed',flush=True)
        package=root/'root_type_and_import'
        (package/'src/main.crb').write_text('use demo::group::{Group as StoredGroup, FrameRange};\nfn main() { let root=Group {}; let stored=StoredGroup {}; let range=FrameRange {}; }\n')
        fixed=subprocess.run([compiler,'check',package],capture_output=True,text=True,timeout=60)
        assert fixed.returncode==0 and 'error[' not in fixed.stderr,fixed
        results.append(dict(case='alias_resolves_collision',exit=0));print('alias_resolves_collision passed',flush=True)
        for name,source,status,fragment in [
            ('syntax_diagnostic','fn main() { let = 3; }',7,'syntax error:'),
            ('type_diagnostic','fn main() { let value: i64 = true; }',8,'expected: i64'),
        ]:
            path=root/(name+'.crb');path.write_text(source)
            old=subprocess.run([baseline,'check',path],capture_output=True,text=True,timeout=60)
            new=subprocess.run([compiler,'check',path],capture_output=True,text=True,timeout=60)
            assert old.returncode==new.returncode==status,(name,old,new)
            assert fragment in new.stderr,(name,new.stderr)
            results.append(dict(case=name,exit=status,stderr=new.stderr));print(name,'passed',flush=True)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(results,indent=2)+'\n')

if __name__=='__main__':main()
