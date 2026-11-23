#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Focused syntax/rule/implementation-limit classification and provenance checks."""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--compiler', type=Path, required=True)
p.add_argument('--baseline', type=Path, required=True)
p.add_argument('--out', type=Path, default=Path('build/diagnostic-categories/results.json'))
a = p.parse_args()
compiler, baseline = a.compiler.resolve(), a.baseline.resolve()
results = []
cases = [
    ('binding syntax', 'fn main(){\n let = 42;\n}\n', 7, 2,
     ['syntax error:', 'expected a binding name', 'found: `=`']),
    ('parameter syntax', 'fn wrong(value i64) {}\nfn main(){}\n', 7, 1,
     ['syntax error:', "expected ':'", 'found: `i64`']),
    ('function syntax', 'struct Item{} impl Item{fn wrong {}}\nfn main(){}\n', 7, 1,
     ['syntax error:', "expected '('", 'found: `{`']),
    ('top-level function syntax', 'fn wrong {}\nfn main(){}\n', 7, 1,
     ['syntax error:', "expected '('", 'found: `{`']),
    ('type rule', 'fn main(){\n let value:i64=true;\n}\n', 8, 2,
     ['rule violation:', 'expected: i64', 'actual: bool']),
    ('move rule', 'struct Item{value:i64}\nfn main(){\n let item=Item{value:1};\n let other=item;\n print(item.value);\n}\n', 8, 5,
     ['rule violation:', 'moved', 'ownership moved here']),
    ('statement limitation', 'fn main(){\n print([1,2]);\n}\n', 9, 2,
     ['compiler limitation:', 'expression statement', "context: function 'main'"]),
    ('signature limitation', 'fn inspect(value: Option<&i64>) {}\nfn main(){}\n', 9, 1,
     ['compiler limitation:', 'Option parameters carrying references, allocations or handles',
      "context: function 'inspect'", 'not a demonstrated language-rule violation']),
]
with tempfile.TemporaryDirectory(prefix='corboc-diagnostic-category-') as temp:
    root = Path(temp)
    for name, source, status, line, fragments in cases:
        path = root / (name.replace(' ', '_') + '.crb')
        path.write_text(source)
        before = subprocess.run([baseline, 'check', path], capture_output=True, text=True, timeout=45)
        after = subprocess.run([compiler, 'check', path], capture_output=True, text=True, timeout=45)
        assert before.returncode == after.returncode == status, (name, before, after)
        for fragment in fragments:
            assert fragment in after.stderr, (name, fragment, after.stderr)
        assert f'{path.resolve()}:{line}:' in after.stderr and '^' in after.stderr, (name, after.stderr)
        assert not after.stdout.strip(), (name, after.stdout)
        if name == 'signature limitation':
            assert f'{path.resolve()}:1:19:' in after.stderr, after.stderr
        # Human explanations must not leak into the legacy raw frontend protocol.
        old = subprocess.run([baseline, '--verify', path], capture_output=True, text=True, timeout=45)
        new = subprocess.run([compiler, '--verify', path], capture_output=True, text=True, timeout=45)
        # Syntax expectations add descriptive parser codes only in human mode.
        assert old.returncode == new.returncode, (name, old, new)
        if name == 'signature limitation':
            assert new.stdout.split() == ['9', '18'] and not new.stderr, new
        else:
            assert (old.stdout, old.stderr) == (new.stdout, new.stderr), (name, old, new)
        results.append({'case': name, 'exit': status, 'stderr': after.stderr})
        print(name, 'passed', flush=True)
    accepted = root / 'accepted.crb'
    accepted.write_text('enum E{Value(i64)} impl E{fn read(&self)->i64{match self{E.Value(n)=>{n}}}} fn main(){let e=E.Value(42);print(e.read());}\n')
    run = subprocess.run([compiler, 'check', accepted], capture_output=True, text=True, timeout=45)
    assert run.returncode == 0 and 'error[' not in run.stderr, run
    results.append({'case': 'accepted enum method has no spurious diagnostics', 'exit': 0})
a.out.parent.mkdir(parents=True, exist_ok=True)
a.out.write_text(json.dumps(results, indent=2) + '\n')
