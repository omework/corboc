#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused member annotation parsing, specialization and contract regressions."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

CONFIG = r'''struct Settings {
    value: i64;
    #(configurable)
    pub const LIMIT: i64 = 4;
    pub fn limit() i64 { Settings::LIMIT }
}
enum Mode {
    End;
    #(configurable)
    pub const LIMIT: i64 = 6;
    pub fn limit() i64 { Mode::LIMIT }
}
fn main() {
    print(Settings::limit()); print(Mode::limit());
    #(override: Settings::LIMIT=9, Mode::LIMIT=11) {
        print(Settings::LIMIT); print(Settings::limit());
        print(Mode::LIMIT); print(Mode::limit());
        #(override: Settings::LIMIT=12) {
            print(Settings::limit()); print(Mode::limit());
        }
        print(Settings::limit());
    }
    print(Settings::limit()); print(Mode::limit());
}
'''
GENERIC = r'''struct Utility {
    #(type: T)
    pub fn identity(value: T) T { value }
    #(type: T)
    #(lock: on=self)
    pub fn instance(&self, value: T) T { value }
}
enum Choice {
    End;
    #(type: T)
    pub fn identity(value: T) T { value }
    #(type: T)
    #(lock: on=self)
    pub fn instance(&self, value: T) T { value }
}
fn main() {
    print(Utility::identity(21)); print(Utility::identity(true));
    print(Choice::identity(42)); print(Choice::identity(false));
    let utility = Utility {}; print(utility.instance(7));
    let choice = Choice::End; print(choice.instance(8));
}
'''
LOCK = r'''struct Number {
    value: i64;
    #(lock: on=self)
    fn read(&self) i64 { self.value }
}
enum Mode {
    End;
    #(lock: on=self)
    fn read(&self) i64 { 5 }
}
fn main() { let n = Number { value: 3 }; print(n.read()); let m = Mode::End; print(m.read()); }
'''
CONDITIONAL = r'''struct Number {
    value: i64;
    #(if: target.os == "macos" || target.os == "linux" || target.os == "windows")
        #(configurable)
        pub const LIMIT: i64 = 3;
        #(lock: on=self)
        fn read(&self) i64 { self.value }
    #(endif)
}
fn main() { let n = Number { value: Number::LIMIT }; print(n.read()); }
'''
BRANCH = r'''struct Factory {
    #(type: T)
    #(branch: join=result.join())
    fn start(value: T) runtime::Handle<T> { runtime::thread({ move value; value }) }
}
enum Other {
    End;
    #(branch: join=result.join())
    fn start() runtime::Handle<i64> { runtime::thread({ 9 }) }
}
fn main() {
    let one = Factory::start(8);
    match one.join() { Ok(n) => { print(n); }, Err(e) => { drop(e); }, }
    let two = Other::start();
    match two.join() { Ok(n) => { print(n); }, Err(e) => { drop(e); }, }
}
'''
ASYNC = r'''struct Utility {
    #(type: T)
    async fn identity(value: T) T { value }
    #(type: T)
    #(lock: on=self)
    async fn instance(&self, value: T) T { value }
}
enum Choice {
    End;
    #(type: T)
    async fn identity(value: T) T { value }
    #(type: T)
    #(lock: on=self)
    async fn instance(&self, value: T) T { value }
}
async fn run() i64 {
    let first = Utility::identity(20).await;
    let second = Choice::identity(22).await;
    let utility = Utility {};
    let third = utility.instance(3).await;
    let choice = Choice::End;
    let fourth = choice.instance(4).await;
    first + second + third + fourth
}
fn main() {
    let execution = runtime::spawn(run());
    match execution.join() { Ok(n) => { print(n); }, Err(e) => { drop(e); }, }
}
'''
CASES = {
    'associated_configuration': (CONFIG, '4\n6\n9\n9\n11\n11\n12\n11\n9\n4\n6\n'),
    'generic_members': (GENERIC, '21\ntrue\n42\nfalse\n7\n8\n'),
    'method_lock_contracts': (LOCK, '3\n5\n'),
    'conditional_members': (CONDITIONAL, '3\n'),
    'branch_members': (BRANCH, '8\n9\n'),
    'async_generic_members': (ASYNC, '49\n'),
}
NEGATIVE = {
    'configurable_method': 'struct X { #(configurable) fn bad() {} } fn main() {}',
    'lock_constant': 'struct X { #(lock: on=self) const BAD: i64=1; } fn main() {}',
    'type_constant': 'enum X { End; #(type: T) const BAD: i64=1; } fn main() {}',
    'configurable_field': 'struct X { #(configurable) value: i64; } fn main() {}',
    'unknown_member_annotation': 'enum X { End; #(unknown) fn bad() {} } fn main() {}',
    'unmarked_override': 'struct X { pub const LIMIT: i64=1; } fn main() { #(override: X::LIMIT=2) { print(X::LIMIT); } }',
    'out_of_range_override': 'enum X { End; #(configurable) pub const LIMIT: u8=1; } fn main() { #(override: X::LIMIT=256) { print(X::LIMIT); } }',
}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler',required=True)
    parser.add_argument('--stdlib',required=True)
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    compiler=str(Path(args.compiler).resolve()); std=str(Path(args.stdlib).resolve())
    results=[]
    with tempfile.TemporaryDirectory(prefix='corbo-member-annotations-') as tmp:
        root=Path(tmp)
        for name,(source,expected) in CASES.items():
            package=root/name; (package/'src').mkdir(parents=True)
            (package/'package.toml').write_text('[package]\nname="demo"\n')
            (package/'src/main.crb').write_text(source)
            emitted=subprocess.run([compiler,'--emit-package-c',str(package),'--stdlib-dir',std],capture_output=True,timeout=120)
            assert emitted.returncode==0,(name,emitted.returncode,emitted.stderr.decode(),emitted.stdout[:200])
            c=package/'main.c';c.write_bytes(emitted.stdout);binary=package/'demo'
            subprocess.run(['cc','-std=c11','-pthread','-O1','-fsanitize=undefined','-fno-sanitize-recover=all',str(c),'-lm','-o',str(binary)],check=True,capture_output=True,timeout=120)
            run=subprocess.run([str(binary)],capture_output=True,text=True,timeout=15)
            assert run.returncode==0 and run.stdout==expected,(name,run.returncode,run.stdout,run.stderr)
            results.append(dict(case=name,status='executed, fatal UBSan',output=run.stdout));print(name,'passed',flush=True)
        # Imported owners retain configuration and generic methods.
        package=root/'imported_members'; (package/'src/settings').mkdir(parents=True)
        (package/'package.toml').write_text('[package]\nname="demo"\n')
        definitions='pub struct Settings { #(configurable) pub const LIMIT:i64=4; pub fn limit() i64 { Settings::LIMIT } #(type: T) pub fn identity(x:T) T {x} }'
        module=package/'src/settings/settings.crb'; module.write_text(definitions)
        (package/'src/main.crb').write_text('use demo::settings::Settings; fn main() { #(override: Settings::LIMIT=9) { print(Settings::limit()); print(Settings::identity(42)); } print(Settings::limit()); }')
        emitted=subprocess.run([compiler,'--emit-package-c',str(package),'--stdlib-dir',std],capture_output=True,timeout=120)
        assert emitted.returncode==0,('imported_members',emitted.returncode,emitted.stderr.decode(),emitted.stdout[:200])
        c=package/'main.c';c.write_bytes(emitted.stdout);binary=package/'demo'
        subprocess.run(['cc','-std=c11','-pthread','-O1','-fsanitize=undefined','-fno-sanitize-recover=all',str(c),'-lm','-o',str(binary)],check=True,capture_output=True,timeout=120)
        run=subprocess.run([str(binary)],capture_output=True,text=True,timeout=15)
        assert run.returncode==0 and run.stdout=='9\n42\n4\n',('imported_members',run.stdout,run.stderr)
        results.append(dict(case='imported_members',status='executed, fatal UBSan',output=run.stdout))
        print('imported_members passed',flush=True)
        for name,source in NEGATIVE.items():
            path=root/(name+'.crb');path.write_text(source)
            run=subprocess.run([compiler,'check',str(path)],capture_output=True,text=True,timeout=60)
            assert run.returncode!=0,(name,'unexpectedly accepted')
            assert 'error[' in run.stderr,(name,'missing diagnostic',run.stderr)
            results.append(dict(case=name,status='rejected',diagnostic=run.stderr));print(name,'rejected',flush=True)
    output=Path(args.out);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(results,indent=2)+'\n')

if __name__=='__main__':main()
