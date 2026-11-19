#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Check the freestanding runtime boundary and packed resource decoding."""
import argparse
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from runtime_sources import UNPACK, pack, packed_literal


def expand(stream):
    output = bytearray()
    at = 0
    while at < len(stream):
        token = stream[at]
        at += 1
        if token < 128:
            output.extend(stream[at:at + token + 1])
            at += token + 1
        else:
            distance = int.from_bytes(stream[at:at + 2], 'little')
            at += 2
            for _ in range((token & 127) + 3):
                output.append(output[-distance])
    return bytes(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler', type=Path, required=True)
    parser.add_argument('--keep', type=Path, required=True)
    args = parser.parse_args()
    compiler = args.compiler.resolve()
    args.keep.mkdir(parents=True, exist_ok=True)
    cases = {
        'scalar': 'fn plus(value:i64)->i64{value+1}',
        'opaque': 'fn peek(pointer:usize)->usize{let mut result:usize=0;@unchecked{@c{${result}=*(uintptr_t*)${pointer};}}result}',
        'entry': 'fn main(){}',
        'array': 'fn count()->i64{let values:[i64;2]=[1,2];values[0]}',
        'owned': 'fn work(){let mut memory=pool<i64>(1);let value=memory.new(1);drop(value);}',
        'async': 'async fn work()->i64{yield;1}',
        'borrowing': 'fn value(data:&i64)->i64{*data}',
        'unchecked_missing': 'fn value(){@c{int x=1;}}',
    }
    for name, source in cases.items():
        path = args.keep / (name + '.crb')
        path.write_text(source)
        result = subprocess.run([compiler, '--emit-runtime-c', path], capture_output=True, timeout=120)
        (args.keep / (name + '.c')).write_bytes(result.stdout)
        (args.keep / (name + '.stderr')).write_bytes(result.stderr)
        accepted = name in ('scalar', 'opaque')
        assert (result.returncode == 0) == accepted, (name, result)
        if accepted:
            assert not result.stderr
            assert all(text not in result.stdout for text in (b'reserve(', b'reclaim_scope(', b'mark'))
    # Exercise overlap, literal boundaries, a history wrap and incompressible bytes.
    samples = [b'', bytes(range(128)), bytes(range(256)) * 3, b'A' * 70000,
               bytes((i * 73 + i // 251) % 256 for i in range(140000))]
    for sample in samples:
        assert expand(pack(sample)) == sample
    # Execute the actual emitted Corbo decoder, including its 64 KiB history wrap.
    sample = samples[-1]
    source = 'fn character(byte:i32){@unchecked{@c{putchar((int)${byte});}}}\n' + UNPACK
    source += 'fn main(){' + packed_literal(sample) + '}'
    path = args.keep / 'decode.crb'
    path.write_text(source)
    generated = args.keep / 'decode.c'
    with generated.open('wb') as output:
        subprocess.run([compiler, '--emit-c', path], stdout=output, check=True, timeout=120)
    binary = args.keep / 'decode'
    subprocess.run(['cc', '-std=c11', '-pthread', '-O2', '-fsanitize=undefined', '-fno-sanitize-recover=all', generated, '-lm', '-o', binary], check=True, timeout=120)
    result = subprocess.run([binary], capture_output=True, timeout=30)
    assert (result.returncode, result.stdout, result.stderr) == (0, sample, b'')
    print('Runtime boundary: 2 accepts, 6 refusals; packing: 5 round trips and Corbo decoder execution passed.')


if __name__ == '__main__':
    main()
