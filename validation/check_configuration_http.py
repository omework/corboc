#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused lexical-configuration and HTTP integration validation (host only)."""
from pathlib import Path
import argparse, json, platform, subprocess
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--corboc',type=Path,required=True)
parser.add_argument('--stdlib-dir',type=Path,required=True)
parser.add_argument('--keep',type=Path,required=True)
args=parser.parse_args()
root=args.keep.resolve();root.mkdir(parents=True,exist_ok=True)
compiler=args.corboc.resolve()
accepted={
 'nested_escape':('#(configurable)\nconst LIMIT: u64 = 8;\nfn helper() -> u64 { LIMIT }\nfn through() -> u64 { helper() }\nstruct Counter { value: u64 }\nimpl Counter {\n    fn new() -> Counter { Counter { value: LIMIT } }\n    fn get(&self) -> u64 { LIMIT + (*self).value }\n}\nfn main() {\n    print(through());\n    let escaped = #(override: LIMIT = 4) {\n        print(LIMIT);\n        print(through());\n        #(override: LIMIT = 2) { print(through()); }\n        Counter::new()\n    };\n    print(through());\n    print(escaped.get());\n}\n','8\n4\n4\n2\n8\n8\n'),
 'layouts':('''#(configurable) const N: usize = 8;
struct Block { bytes: [u8; N] }
impl Block { fn new() -> Block { Block { bytes: [0; N] } } fn len(&self) -> usize { let bytes = &(*self).bytes[..]; bytes.len() } }
fn main() { let a = Block::new(); let b = #(override: N=3) { Block::new() }; print(a.len()); print(b.len()); print(N); }''','8\n3\n8\n'),
 'values':('''#(configurable) const ENABLED: bool = false;
#(configurable) const VALUE: f64 = 1.5;
fn number() -> f64 { VALUE }
fn main() { print(ENABLED); #(override: ENABLED=true, VALUE=2.5,) { print(ENABLED); print(number()); } print(number()); }''','false\ntrue\n2.5\n1.5\n'),
}
rejected={
 'ordinary':'const N: u64 = 8; fn main() { #(override: N=4) { print(N); } }',
 'unknown':'fn main() { #(override: MISSING=4) {} }',
 'duplicate':'#(configurable) const N: u64=8; fn main() { #(override:N=2,N=3) {} }',
 'runtime':'#(configurable) const N:u64=8; fn main() { let x:u64=2; #(override:N=x) {} }',
 'range':'#(configurable) const N:u8=8; fn main() { #(override:N=256) {} }',
 'negative':'#(configurable) const N:u64=8; fn main() { #(override:N=-1) {} }',
 'type':'#(configurable) const N:bool=false; fn main() { #(override:N=2) {} }',
 'marker_target':'#(configurable) fn main() {}',
}

rejected['typed_constant']='const OTHER:u8=2; #(configurable) const N:u64=8; fn main(){#(override:N=OTHER){print(N);}}'
results=[]
def emit(source,label):
    path=root/(label+'.crb');path.write_text(source)
    return subprocess.run([compiler,'--emit-c',path],capture_output=True,timeout=120)
def execute(result,name,expected):
    assert result.returncode==0,(name,result.returncode,result.stdout[:300],result.stderr)
    c=root/(name+'.c');c.write_bytes(result.stdout);binary=root/(name+'.exe')
    subprocess.run(['cc','-std=c11','-pthread','-O1','-fsanitize=undefined','-fno-sanitize-recover=all',c,'-lm','-o',binary],check=True,timeout=120)
    run=subprocess.run([binary],capture_output=True,text=True,timeout=15)
    assert (run.returncode,run.stdout,run.stderr)==(0,expected,''),(name,run)
    results.append({'name':name,'passed':True});print('PASS',name,flush=True)
for name,(source,expected) in accepted.items():execute(emit(source,name),name,expected)
for name,source in rejected.items():
    result=emit(source,name);assert result.returncode in (7,8),(name,result.returncode,result.stdout,result.stderr)
    results.append({'name':name,'passed':True,'status':result.returncode});print('REFUSED',name,flush=True)

# One reusable partial reader; no socket or platform API is needed for parser semantics.
fixture=Path(__file__).parent/'fixtures/configuration_http/request_body.crb'
reader=fixture.read_text().split('fn main()')[0]
reader=reader.replace('let count: usize = if available < capacity { available } else { capacity };','let requested: usize = if available < capacity { available } else { capacity }; let count:usize=if requested<2{requested}else{2};')
def package(name,source):
    path=root/name;(path/'src').mkdir(parents=True,exist_ok=True)
    (path/'package.toml').write_text('[package]\nname="http_check"\n')
    (path/'src/main.crb').write_text(source)
    return subprocess.run([compiler,'--emit-package-c',path,'--stdlib-dir',args.stdlib_dir.resolve()],capture_output=True,timeout=120)
def message(text,role='request',extra='',limits=''):
    return reader+'fn main(){let text='+json.dumps(text)+';let mut input=Input::new(text); #(override: std::net::http::REQUEST_LINE_MAX_SIZE=128,std::net::http::HEADER_LINE_MAX_SIZE=128,std::net::http::HEADERS_MAX_SIZE=512,std::net::http::HEADER_COUNT_MAX=8) { '+limits+' let parsed=match http::'+role+'(&mut input){Ok(parsed)=>{parsed},Err(error)=>{drop(error);print(-2);return;},}; let mut message=match parsed{Some(message)=>{message},None=>{print(0);return;},}; print(1); '+extra+' } print(input.position);}'
def body():
    return 'let mut body=match message.body(){Some(body)=>{body},None=>{print(-3);return;},}; let mut bytes:[u8;8]=[0;8]; let mut total:usize=0; let mut done=false; while !done {match body.read(&mut bytes[..]){Ok(count)=>{if count==0{done=true;}else{total+=count;print(bytes[0]);}},Err(error)=>{drop(error);print(-4);return;},}}print(total);'
http_cases=[
    ('request_partial','POST /hello HTTP/1.1\r\nX: a\r\nX: b\r\nContent-Length: 5\r\n\r\nhelloNEXT','request','let fields=message.headers();print(fields.len());'+body(),['1','3','104','108','111','5'],len('POST /hello HTTP/1.1\r\nX: a\r\nX: b\r\nContent-Length: 5\r\n\r\nhello')),
    ('response_partial','HTTP/1.1 200 OK\r\nContent-Length: 3\r\n\r\nabcNEXT','response','print(message.status());'+body(),['1','200','97','99','3'],len('HTTP/1.1 200 OK\r\nContent-Length: 3\r\n\r\nabc')),
    ('chunked','POST / HTTP/1.1\r\nTransfer-Encoding: chunked\r\n\r\n3\r\nabc\r\n0\r\nX: z\r\n\r\nNEXT','request',body(),['1','97','99','3'],len('POST / HTTP/1.1\r\nTransfer-Encoding: chunked\r\n\r\n3\r\nabc\r\n0\r\nX: z\r\n\r\n')),
    ('no_body','GET / HTTP/1.1\r\n\r\nNEXT','request','match message.body(){Some(body)=>{drop(body);print(-3);},None=>{print(0);},}',['1','0'],18),
    ('zero_body','POST / HTTP/1.1\r\nContent-Length: 0\r\n\r\nNEXT','request',body(),['1','0'],len('POST / HTTP/1.1\r\nContent-Length: 0\r\n\r\n')),
]
for name,text,role,extra,lines,position in http_cases:
    execute(package(name,message(text,role,extra)),name,'\n'.join([*lines,str(position)])+'\n')
for name,text,expected in [
    ('clean_eof','','0\n'),('truncated','GET / HTTP/1.1\r\nX: a\r','-2\n'),
    ('framing_conflict','POST / HTTP/1.1\r\nContent-Length: 1\r\nTransfer-Encoding: chunked\r\n\r\n','-2\n'),
    ('bad_length','POST / HTTP/1.1\r\nContent-Length: 18446744073709551616\r\n\r\n','-2\n'),
]:execute(package(name,message(text)),name,expected)
for name,limit,expected in [('line_exact',14,'1\n18\n'),('line_over',13,'-2\n')]:
    source=message('GET / HTTP/1.1\r\n\r\n').replace('REQUEST_LINE_MAX_SIZE=128','REQUEST_LINE_MAX_SIZE='+str(limit))
    execute(package(name,source),name,expected)
source=message('GET / HTTP/1.1\r\nA: 1\r\nB: 2\r\n\r\n').replace('HEADER_COUNT_MAX=8','HEADER_COUNT_MAX=1')
execute(package('header_count',source),'header_count','-2\n')

# Qualified and aliased names must resolve to one constant identity.
module=root/'module_overrides';(module/'src/settings').mkdir(parents=True,exist_ok=True)
(module/'package.toml').write_text('[package]\nname="cfg_check"\n')
(module/'src/settings/settings.crb').write_text('#(configurable) pub const N:u64=8; pub fn read()->u64{N}\n')
def emit_module(source):
    (module/'src/main.crb').write_text(source)
    return subprocess.run([compiler,'--emit-package-c',module,'--stdlib-dir',args.stdlib_dir.resolve()],capture_output=True,timeout=120)
execute(emit_module('use cfg_check::settings::{N as SIZE,N as OTHER,read};fn main(){print(read());#(override:SIZE=2){print(read());}print(read());}'),'alias_override','8\n2\n8\n')
r=emit_module('use cfg_check::settings::{N as SIZE,N as OTHER};fn main(){#(override:SIZE=2,OTHER=3){}}')
assert r.returncode==8,('duplicate_alias',r.returncode,r.stdout);results.append({'name':'duplicate_alias','passed':True,'status':8});print('REFUSED duplicate_alias',flush=True)
(module/'src/settings/settings.crb').write_text('#(configurable) const N:u64=8; pub fn read()->u64{N}\n')
r=emit_module('use cfg_check::settings::read;fn main(){#(override:cfg_check::settings::N=2){print(read());}}')
assert r.returncode in (8,13),('private_override',r.returncode,r.stdout);results.append({'name':'private_override','passed':True,'status':r.returncode});print('REFUSED private_override',flush=True)
# The returned message keeps the input reader reserved; destruction cannot precede its use.
source=message('POST / HTTP/1.1\r\nContent-Length: 1\r\n\r\na',extra='drop(input);'+body())
r=package('reader_lifetime',source)
assert r.returncode==8,('reader_lifetime',r.returncode,r.stdout);results.append({'name':'reader_lifetime','passed':True,'status':8});print('REFUSED reader_lifetime',flush=True)
for name,property,value,text in [
    ('header_line_limit','HEADER_LINE_MAX_SIZE',3,'GET / HTTP/1.1\r\nLong: value\r\n\r\n'),
    ('header_total_limit','HEADERS_MAX_SIZE',7,'GET / HTTP/1.1\r\nA: 1\r\n\r\n'),
]:
    source=message(text).replace(property+'='+('128' if property=='HEADER_LINE_MAX_SIZE' else '512'),property+'='+str(value))
    execute(package(name,source),name,'-2\n')

source=message('GET / HTTP/1.1\r\nX: a\r\nX: b\r\n\r\n',extra='let fields=message.headers();match fields.get(1){Some(header)=>{let name=header.name();let bytes=name.as_bytes();print(bytes.len());let value=header.value();print(value[0]);},None=>{print(-7);},}')
execute(package('header_views',source),'header_views','1\n1\n98\n30\n')

# Direct regressions of the reused record, slice and enum summary mechanisms.
for name,expected in [('record_result_method','7\n'),('mixed_constructor',''),('slice_forward','1\n'),('borrowed_enum','true\n')]:
    path=Path(__file__).parent/'fixtures/core_extensions'/(name+'.crb')
    execute(emit(path.read_text(),name),name,expected)
for name,bytes_,expected in [('utf8_valid','[0xC3,0xA9]','2\n'),('utf8_invalid','[0xC0,0xAF]','0\n')]:
    source='enum Error{Bad} fn main(){let bytes:[u8;2]='+bytes_+';let view=&bytes[..];let checked:Result<&str,Error>=str::from_utf8(view);match checked{Ok(text)=>{let output=text.as_bytes();print(output.len());},Err(error)=>{drop(error);print(0);},}}'
    execute(emit(source,name),name,expected)
(root/'report.json').write_text(json.dumps({'platform':platform.platform(),'compiler':str(compiler),'cases':results},indent=2)+'\n')
