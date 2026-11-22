#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused file-check/watch integration with local and installed-STD imports."""
import argparse,json,os,queue,shutil,subprocess,tempfile,threading,time
from pathlib import Path

class Watch:
    """Keep watcher output nonblocking and terminate the child on every exit path."""
    def __init__(self, compiler, target, env, cwd, before=False):
        arguments=['check','--watch',str(target)] if before else ['check',str(target),'--watch']
        self.process=subprocess.Popen([str(compiler),*arguments],cwd=cwd,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,bufsize=1)
        self.lines=queue.Queue()
        def consume():
            for line in self.process.stderr:self.lines.put(line.strip())
        self.reader=threading.Thread(target=consume,daemon=True);self.reader.start()
    def wait(self, text, timeout=12):
        """Wait for one expected transition, retaining useful diagnostics on failure."""
        deadline=time.monotonic()+timeout;seen=[]
        while time.monotonic()<deadline:
            assert self.process.poll() is None,('watch exited',self.process.returncode,seen)
            try:line=self.lines.get(timeout=.1)
            except queue.Empty:continue
            seen.append(line)
            if text in line:return
        raise AssertionError(('watch timeout',text,seen))
    def quiet(self):
        """Assert ignored neighbors do not trigger a new pass after queues settle."""
        time.sleep(.8);seen=[]
        while not self.lines.empty():seen.append(self.lines.get_nowait())
        assert not any('checking ' in line for line in seen),seen
    def close(self):
        """Do not leave a background compiler after validation."""
        self.process.terminate()
        try:self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:self.process.kill();self.process.wait(timeout=5)
        self.reader.join(timeout=2);self.process.stderr.close()

def main():
    """Check standalone/library sources and one transitive dependency graph."""
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--compiler',type=Path,required=True)
    p.add_argument('--out',type=Path,default=Path('build/check-file/results.json'));a=p.parse_args();results=[]
    with tempfile.TemporaryDirectory(prefix='corboc-file-watch-') as temporary:
        base=Path(temporary);prefix=base/'install';(prefix/'bin').mkdir(parents=True)
        compiler=prefix/'bin/corboc';shutil.copy2(a.compiler.resolve(),compiler)
        # An isolated installed STD lets us test STD changes without modifying the pin.
        stdlib=prefix/'share/corbo/stdlib/src/helper';stdlib.mkdir(parents=True)
        helper=stdlib/'helper.crb';good='pub fn answer()->i64 {42}\n';helper.write_text(good)
        env=dict(os.environ,PATH=str(base/'empty-path'))
        def check(label,target,expected=0):
            run=subprocess.run([str(compiler),'check',str(target)],cwd=base,env=env,capture_output=True,text=True,timeout=30)
            assert run.returncode==expected,(label,run.returncode,run.stdout,run.stderr)
            assert '#include' not in run.stdout,(label,'unexpected code generation')
            results.append({'case':label,'exit':run.returncode});print(label,'passed',flush=True)
        source=base/'standalone.crb'
        original='use std::helper::answer;\nfn main(){print(answer());}\n'
        source.write_text(original);check('standalone with STD import',source)
        source.write_text('use std::helper::answer;\npub fn value()->i64 {answer()}\n')
        check('library file without main',source)
        source.write_text('fn main(){missing;}\n');check('standalone semantic rejection',source,8)
        source.write_text('fn main(){ let = }\n')
        watch=Watch(compiler,source,env,base)
        try:
            watch.wait('check failed');watch.wait('watching sources')
            source.write_text(original);watch.wait('check passed')
            helper.write_text('pub fn answer()->i64 {missing}\n');watch.wait('check failed')
            replacement=helper.with_suffix('.tmp');replacement.write_text(good);replacement.replace(helper)
            watch.wait('check passed')
            (base/'unrelated.crb').write_text('invalid');watch.quiet()
            source.unlink();watch.wait('source scan failed')
            source.write_text(original);watch.wait('check passed')
            results.append({'case':'standalone watch: initial error, source/STD edits, atomic save, deletion recovery, ignored neighbor','status':'passed'})
        finally:watch.close()
        project=base/'project';(project/'src/local').mkdir(parents=True)
        (project/'package.toml').write_text('[package]\nname="project"\n[dependencies]\nfirst={path="../first"}\n')
        main_file=project/'src/main.crb';main_source='use project::local::value;\nfn main(){print(value());}\n';main_file.write_text(main_source)
        local=project/'src/local/local.crb';local.write_text('use first::value as external;\npub fn value()->i64 {external()}\n')
        first=base/'first';(first/'src').mkdir(parents=True)
        (first/'src/lib.crb').write_text('use second::value as nested;\npub fn value()->i64 {nested()}\n')
        first_manifest=first/'package.toml';first_manifest.write_text('[package]\nname="first"\n[dependencies]\nsecond={path="../second"}\n')
        second=base/'second';(second/'src').mkdir(parents=True)
        (second/'package.toml').write_text('[package]\nname="second"\n');second_source=second/'src/lib.crb';second_good='pub fn value()->i64 {42}\n';second_source.write_text(second_good)
        check('file resolves enclosing package and transitive imports',main_file)
        check('module file uses enclosing package context',local)
        watch=Watch(compiler,main_file,env,base,before=True)
        try:
            watch.wait('check passed');watch.wait('watching sources')
            second_source.write_text('pub fn value()->i64 {missing}\n');watch.wait('check failed')
            second_source.write_text(second_good);watch.wait('check passed')
            # A changed manifest changes the watched graph, not just the next verdict.
            third=base/'third';(third/'src').mkdir(parents=True)
            (third/'package.toml').write_text('[package]\nname="second"\n');third_source=third/'src/lib.crb';third_source.write_text(second_good)
            first_manifest.write_text('[package]\nname="first"\n[dependencies]\nsecond={path="../third"}\n');watch.wait('check passed')
            third_source.write_text('pub fn value()->i64 {missing}\n');watch.wait('check failed')
            third_source.write_text(second_good);watch.wait('check passed')
            main_file.unlink();watch.wait('check failed')
            main_file.write_text(main_source);watch.wait('check passed')
            results.append({'case':'package-file watch: transitive path edit, manifest graph refresh, selected-file deletion recovery, both flag orders','status':'passed'})
        finally:watch.close()
        assert not (project/'build').exists();assert not list(base.rglob('.corboc.*'))
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(results,indent=2)+'\n')

if __name__=='__main__':main()
