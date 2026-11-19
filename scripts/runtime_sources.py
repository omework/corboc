#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Embed the readable native runtime in corboc; --check detects stale output."""
import argparse
import subprocess
import sys
import tempfile
from corbo_sources import source_root, lock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'src/runtime_sources/runtime_sources.crb'

# Ordering preserves the backend's existing declarations and dependencies.
SOURCES = (
    ('c_runtime_header', '', ('corbo_runtime.h',)),
    ('c_runtime_api', '', ('runtime_api.c.inc',)),
    ('base_runtime', '', ('memory/datastack.c.inc', 'collections/vector.c.inc',
                          'memory/region_release.c.inc')),
    ('task_runtime', '', ('async/scheduler.c.inc',)),
    ('pool_runtime', '', ('memory/pools.c.inc', 'collections/vector_owned.c.inc')),
    ('task_value_runtime', '', ('async/values.c.inc',)),
    ('native_runtime', '', ('async/threads.c.inc',)),
    ('reclaim_runtime', 'threaded: bool', ('memory/reclaim.c.inc',)),
    ('map_runtime', '', ('collections/hashmap.c.inc',)),
    ('readiness_runtime', '', ('async/readiness.c.inc',)),
    ('completion_runtime', '', ('async/completion.c.inc',)),
)


def literal(data):
    chunks = []
    for start in range(0, len(data), 512):
        part = data[start:start + 512]
        lines = [', '.join(str(byte) for byte in part[i:i + 24]) + ','
                 for i in range(0, len(part), 24)]
        chunks.append('    { let bytes: [u8; ' + str(len(part)) + '] = [\n'
                      + ''.join('        ' + line + '\n' for line in lines)
                      + '    ]; byte_text(&bytes[..]); }\n')
    return ''.join(chunks)


def pack(data):
    """Bounded LZ byte stream: literal runs or 16-bit backward distances."""
    output=bytearray();literals=bytearray();latest={};at=0
    def flush():
        while literals:
            part=literals[:128];del literals[:128];output.append(len(part)-1);output.extend(part)
    while at<len(data):
        key=data[at:at+3];previous=latest.get(key,-65536);length=0
        if len(key)==3 and 0<at-previous<=65535:
            while length<130 and at+length<len(data) and data[previous+length]==data[at+length]:length+=1
        if length>=3:
            flush();distance=at-previous;output.extend((128+length-3,distance&255,distance>>8));step=length
        else:literals.append(data[at]);step=1
        for index in range(at,at+step):latest[data[index:index+3]]=index
        at+=step
    flush()
    # Independent expansion check catches encoder and overlapping-match mistakes.
    expanded=bytearray();at=0
    while at<len(output):
        token=output[at];at+=1
        if token<128:
            expanded.extend(output[at:at+token+1]);at+=token+1
        else:
            distance=output[at]+256*output[at+1];at+=2
            for _ in range((token&127)+3):expanded.append(expanded[-distance])
    assert expanded==data
    return bytes(output)


def packed_literal(data):
    # ASCII hex avoids one AST expression per packed byte during bootstrapping.
    encoded = pack(data).hex()
    return ('    { let encoded = "' + encoded + '"; '
            'let bytes = encoded.as_bytes(); resource_unpack(bytes); }\n')


UNPACK = """fn resource_nibble(byte:u8) -> u8 {
    if byte <= 57 { byte - 48 } else { byte - 87 }
}
fn resource_byte(input:&[u8], at:u64) -> u8 {
    let hi = resource_nibble(input[at * 2]);
    let lo = resource_nibble(input[at * 2 + 1]);
    hi * 16 + lo
}
fn resource_unpack(input:&[u8]) {
    let mut history:[u8;65536]=[0;65536];
    let mut at:u64=0;let mut written:u64=0;
    while at<(input.len() as u64)/2 {
        let token=resource_byte(&input[0..input.len()], copy(at)) as u64;at=at+1;
        if token<128 {
            let end=at+token+1;
            while at<end {let byte=resource_byte(&input[0..input.len()], copy(at));history[written%65536]=copy(byte);character(byte as i32);written=written+1;at=at+1;}
        } else {
            let distance=resource_byte(&input[0..input.len()], copy(at)) as u64+(resource_byte(&input[0..input.len()], at+1) as u64)*256;at=at+2;
            let mut remaining=(token&127)+3;
            while remaining!=0 {let byte=history[(written-distance)%65536];history[written%65536]=copy(byte);character(byte as i32);written=written+1;remaining=remaining-1;}
        }
    }
}

"""

def render(source, implementation="c", compiler=None, runtime_source=None):
    runtime = Path(runtime_source).resolve() if runtime_source else source / lock()['runtime']
    sections = None
    if implementation == 'corbo':
        if compiler is None:
            compiler = ROOT / 'build/install/bin/corboc'
        with tempfile.TemporaryDirectory(prefix='corboc-runtime-') as temporary:
            result = subprocess.run([sys.executable, runtime / 'corbo/build.py', '--compiler', str(Path(compiler).resolve()), '--out', temporary], capture_output=True, text=True, timeout=180)
            if result.returncode:
                raise RuntimeError(result.stdout + result.stderr)
            sections = {name: (Path(temporary)/(name+'.c.inc')).read_bytes() for name,_,_ in SOURCES}

    output = ['// SPDX-License-Identifier: MIT OR Apache-2.0\n',
              '// Generated by scripts/runtime_sources.py. Do not edit.\n',
              '// Shared runtime is pinned by corbo.lock.\n',
              '// Runtime implementation: ' + implementation + '.\n',
              'use bootstrap::target_c::{byte_text,character};\n\n']
    if sections is not None:output.append(UNPACK)
    for function, parameters, paths in SOURCES:
        output.append(f'pub fn {function}({parameters}) {{\n')
        if sections is not None:
            output.append(packed_literal(sections[function]))
            output.append('}\n\n')
            continue
        for path in paths:
            output.append(f'    // runtime/{path}\n')
            pending = bytearray()
            conditional = False
            for line in (runtime / path).read_bytes().splitlines(keepends=True):
                if line == b'#if CORBO_THREADED\n':
                    assert parameters == 'threaded: bool' and not conditional
                    output.append(literal(pending))
                    pending.clear()
                    output.append('    if threaded {\n')
                    conditional = True
                elif line == b'#endif /* CORBO_THREADED */\n':
                    assert conditional
                    output.append(literal(pending))
                    pending.clear()
                    output.append('    }\n')
                    conditional = False
                else:
                    pending.extend(line)
            assert not conditional, path
            output.append(literal(pending))
        output.append('}\n\n')
    return ''.join(output).rstrip() + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--source', type=Path, help='Verify a local checkout against corbo.lock')
    parser.add_argument('--implementation', choices=['c','corbo'], default=lock().get('runtime_implementation','c'))
    parser.add_argument('--compiler', type=Path)
    parser.add_argument('--runtime-source', type=Path, help='Explicit development runtime override; does not alter the source lock')
    args = parser.parse_args()
    generated = render(source_root(args.source), args.implementation, args.compiler, args.runtime_source)
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != generated:
            parser.exit(1, 'Runtime bridge is stale; run python3 scripts/runtime_sources.py\n')
        print('Runtime bridge matches the readable native sources.')
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(generated)
        print('Updated ' + str(OUTPUT.relative_to(ROOT)))


if __name__ == '__main__':
    main()
