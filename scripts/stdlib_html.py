#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Build an offline, searchable STD/core/runtime reference from pinned inputs."""
import argparse
from collections import defaultdict
import hashlib
import html
from html.parser import HTMLParser
import importlib
import json
from pathlib import Path
import re
import posixpath
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path(__file__).with_name('doc_assets')
TYPE_KINDS = {'struct', 'enum', 'type', 'primitive', 'generated type', 'runtime contract', 'c_type'}


def slug(value):
    """Produce a stable, single-component URL accepted by the local server."""
    return re.sub(r'[^a-zA-Z0-9_.-]+', '-', value).strip('-')


def generate(corbo, stdlib, output, revision):
    """Collect source and compiler-provided entries, then emit linked static pages."""
    sys.path.insert(0, str(corbo / 'scripts'))
    source_docs = importlib.import_module('source_docs')
    records = []
    summaries = defaultdict(list)
    sources = {}
    def source_record(path, module, internal=False):
        text = path.read_text(encoding='utf-8')
        entries, annotations = source_docs.inventory(text)
        public_types = {e.name for e in entries if e.public and e.kind in TYPE_KINDS}
        try:
            identity = path.relative_to(corbo).as_posix()
        except ValueError:
            identity = 'stdlib/src/' + path.relative_to(stdlib).as_posix()
        url = 'source-' + slug(identity) + '.html'
        sources[url] = (identity, text)
        summary = '\n'.join(line[3:].strip() for line in text.splitlines() if line.startswith('//!'))
        if summary:
            summaries[module].append(summary)
        for entry in entries:
            if not internal and not (entry.owner in public_types if entry.owner else entry.public):
                continue
            if entry.name.startswith('__din_'):
                continue
            description = source_docs.documentation(text, entry, annotations)
            if not description:
                raise ValueError(f'Missing documentation: {identity}::{entry.name}')
            line = text.count('\n', 0, entry.start) + 1
            annotation_heads = []
            at = entry.start
            while True:
                at = len(text[:at].rstrip())
                if at not in annotations:
                    break
                start = annotations[at]
                head = text[start:at]
                if not re.match(r'#\s*\(\s*(?:if|endif)\b', head):
                    annotation_heads.insert(0, head)
                at = start
            records.append(dict(name=entry.name, module=module, owner=entry.owner,
                full=module + '::' + ((entry.owner + '::') if entry.owner else '') + entry.name,
                kind=entry.kind, signature=source_docs.heading(text, entry), annotations=annotation_heads,
                description=description, conditions=list(entry.conditions),
                source=url + '#L' + str(line), internal=internal,
                members=[dict(name=m.name, kind=m.kind, owner=m.owner, description=source_docs.documentation(text, m, annotations)) for m in source_docs.flatten(entry.children)]))
    for path in sorted(stdlib.rglob('*.crb')):
        parts = path.relative_to(stdlib).parts
        if parts[0] == 'sys':
            module = 'std::' + '::'.join(parts[:-1])
            source_record(path, module, internal=True)
        else:
            module = '::'.join(('std', *parts[:-1]))
            if parts[0] == 'runtime':
                module = '::'.join(parts[:-1])
            source_record(path, module)
    for path in sorted((corbo / 'runtime/corbo').glob('*.crb')):
        source_record(path, 'implementation::runtime::' + path.stem, internal=True)
    abi = corbo / 'runtime/corbo_runtime.h'
    if abi.exists():
        text = abi.read_text()
        source_url = 'source-runtime-corbo_runtime.h.html'
        sources[source_url] = ('runtime/corbo_runtime.h', text)
        for entry in source_docs.c_inventory(text):
            records.append(dict(name=entry.name, module='implementation::c_abi', owner=None,
                full='implementation::c_abi::' + entry.name, kind=entry.kind,
                signature=source_docs.heading(text, entry),
                description=source_docs.c_documentation(text, entry), conditions=[],
                source=source_url + '#L' + str(text.count('\n', 0, entry.start) + 1),
                internal=True, members=[dict(name=m.name, kind=m.kind, owner=m.owner, description=source_docs.c_documentation(text, m)) for m in source_docs.flatten(entry.children)]))
    for path in sorted((corbo / 'examples/features').rglob('*.crb')):
        identity = path.relative_to(corbo).as_posix()
        sources['source-' + slug(identity) + '.html'] = (identity, path.read_text())
    sources['source-compiler-builtin-reference.json.html'] = ('compiler/docs/BUILTIN_REFERENCE.json', (ROOT / 'docs/BUILTIN_REFERENCE.json').read_text())
    catalog = json.loads((ROOT / 'docs/BUILTIN_REFERENCE.json').read_text())['items']
    grammar = (corbo / 'CORE_GRAMMAR.ebnf').read_text()
    primitive_rule = re.search(r'primitif\s*=([\s\S]*?);', grammar)
    primitives = set(re.findall(r'"([^"]+)"', primitive_rule[1]))
    documented = {item['name'] for item in catalog if item['kind'] == 'primitive'}
    if primitives - documented:
        raise ValueError('Undocumented compiler primitives: ' + ', '.join(sorted(primitives - documented)))
    native_exports = {r['full'] for r in records if r.get('source', '').startswith('source-stdlib-src-collections.crb.html') and r['kind'] == 'struct' and not r['members']}
    native_catalog = {item['module'] + '::' + item['name'] for item in catalog if item.get('methods')}
    if native_exports - native_catalog:
        raise ValueError('Undocumented compiler export methods: ' + ', '.join(sorted(native_exports - native_catalog)))

    for item in catalog:
        full = item['module'] + '::' + item['name']
        existing = next((r for r in records if r['full'] == full and r['kind'] in TYPE_KINDS), None)
        if existing:
            existing['description'] += '\n\n' + item['description']
            existing['compiler'] = True
            existing['examples'] = item.get('examples', [])
        else:
            existing = dict(item, full=full, owner=None, conditions=[], members=[], compiler=True)
            records.append(existing)
        for name, signature, description in item.get('methods', []):
            records.append(dict(name=name, module=item['module'], owner=item['name'],
                full=full + '::' + name, kind='method', signature=signature,
                description=description, conditions=[], members=[], compiler=True))
    modules = set(r['module'] for r in records)
    for module in list(modules):
        parts = module.split('::')
        modules.update('::'.join(parts[:i]) for i in range(1, len(parts)))
    by_module = defaultdict(list)
    types = {}
    for record in records:
        by_module[record['module']].append(record)
        if record['kind'] in TYPE_KINDS:
            types.setdefault(record['module'] + '::' + record['name'], []).append(record)
    urls = {name: 'type-' + slug(name) + '.html' for name in types}
    anchors = defaultdict(int)
    for record in records:
        owner = record['module'] + '::' + (record['owner'] or record['name'])
        if record['kind'] in TYPE_KINDS:
            record['url'] = urls[owner]
        else:
            base = urls[owner] if record['owner'] and owner in urls else 'module-' + slug(record['module']) + '.html'
            anchor = slug(record['name'])
            anchors[(base, anchor)] += 1
            count = anchors[(base, anchor)]
            record['url'] = base + '#' + anchor + (('-' + str(count)) if count > 1 else '')
    for record in records:
        record['anchor'] = record['url'].split('#')[-1] if '#' in record['url'] else 'definition-' + hashlib.sha256((record['full'] + record.get('source', '') + str(record['conditions'])).encode()).hexdigest()[:12]
    by_name = defaultdict(list)
    for name, entries in types.items():
        by_name[entries[0]['name']].append(name)
    def signature(text, module):
        def token(match):
            word = match[0]
            target = word if word in urls else module + '::' + word
            if target not in urls:
                choices = by_name.get(word, [])
                target = choices[0] if len(choices) == 1 else None
            escaped = html.escape(word)
            if target in urls:
                return f'<a class="type-link" href="{urls[target]}">{escaped}</a>'
            if word in {'pub', 'fn', 'struct', 'enum', 'async', 'self', 'mut', 'const', 'let', 'return', 'move'}:
                return '<span class="keyword">' + escaped + '</span>'
            return escaped
        pieces = re.split(r'((?:[A-Za-z_]\w*::)*[A-Za-z_]\w*)', text)
        return ''.join(token(re.match(r'.*', p)) if i % 2 else html.escape(p) for i, p in enumerate(pieces))
    guides = {'README.md': 'guide-language.html'}
    guides.update({p.relative_to(corbo).as_posix(): 'guide-' + slug(p.relative_to(corbo).as_posix()) + '.html'
                   for p in sorted((corbo / 'docs').glob('*.md')) if not p.stem.endswith('-fr')})
    source_links = {identity: url for url, (identity, _) in sources.items()}
    def inline(text, base):
        parts = re.split(r'(\[[^\]]+\]\([^\)]+\))', text)
        output = []
        for part in parts:
            match = re.fullmatch(r'\[([^\]]+)\]\(([^\)]+)\)', part)
            if match:
                label, target = match.groups()
                href = None
                if target.startswith(('https://', 'http://', 'mailto:', '#')):
                    href = target
                else:
                    path, sep, fragment = target.partition('#')
                    identity = posixpath.normpath(posixpath.join(posixpath.dirname(base), path))
                    href = guides.get(identity) or source_links.get(identity)
                    if identity == 'CORE_GRAMMAR.ebnf': href = 'guide-grammar.html'
                    if href and sep: href += '#' + fragment
                label = re.sub(r'`([^`]+)`', r'<code>\1</code>', html.escape(label))
                output.append('<a href="' + html.escape(href, quote=True) + '">' + label + '</a>' if href else label)
            else:
                output.append(re.sub(r'`([^`]+)`', r'<code>\1</code>', html.escape(part)))
        return re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', ''.join(output))
    def prose(text, base='README.md'):
        result = []
        chunks = re.split(r'```[^\n]*\n([\s\S]*?)```', text)
        for i, chunk in enumerate(chunks):
            if i % 2:
                result.append('<pre><code>' + html.escape(chunk.rstrip()) + '</code></pre>')
                continue
            lines = chunk.splitlines(); at = 0
            while at < len(lines):
                line = lines[at].strip()
                if not line or line.startswith('<!--'): at += 1; continue
                anchor = re.fullmatch(r'<a id="([^"]+)"></a>', line)
                if anchor:
                    result.append('<a id="' + html.escape(anchor[1], quote=True) + '"></a>'); at += 1; continue
                heading = re.match(r'^(#{1,6})\s+(.+)', line)
                if heading:
                    level = min(len(heading[1]) + 1, 6)
                    result.append(f'<h{level} id="{slug(heading[2].lower())}">' + inline(heading[2], base) + f'</h{level}>'); at += 1; continue
                if line.startswith('|'):
                    rows = []
                    while at < len(lines) and lines[at].strip().startswith('|'):
                        row = [c.strip() for c in lines[at].strip().strip('|').split('|')]
                        if not all(re.fullmatch(r':?-+:?', c.replace(' ', '')) for c in row): rows.append(row)
                        at += 1
                    result.append('<table>' + ''.join('<tr>' + ''.join('<' + ('th' if n == 0 else 'td') + '>' + inline(c, base) + '</' + ('th' if n == 0 else 'td') + '>' for c in row) + '</tr>' for n, row in enumerate(rows)) + '</table>'); continue
                if re.match(r'^[-*] ', line):
                    items = []
                    while at < len(lines) and re.match(r'^[-*] ', lines[at].strip()):
                        items.append('<li>' + inline(lines[at].strip()[2:], base) + '</li>'); at += 1
                    result.append('<ul>' + ''.join(items) + '</ul>'); continue
                paragraph = [line]; at += 1
                while at < len(lines) and lines[at].strip() and not re.match(r'^(#|[-*] |\||<)', lines[at].strip()):
                    paragraph.append(lines[at].strip()); at += 1
                result.append('<p>' + inline(' '.join(paragraph), base) + '</p>')
        return ''.join(result)
    def navigation():
        groups = []
        for root in ('std', 'core', 'runtime', 'language', 'implementation'):
            group = [m for m in sorted(modules) if m == root or m.startswith(root + '::')]
            label = {'std': 'Standard library', 'core': 'Compiler types', 'runtime': 'Runtime API', 'language': 'Language', 'implementation': 'Implementation sources'}[root]
            links = ''.join(f'<a style="--depth:{m.count("::")}" href="module-{slug(m)}.html">{html.escape(m)}</a>' for m in group)
            groups.append(f'<details {"open" if root != "implementation" else ""}><summary>{label}</summary>{links}</details>')
        return ''.join(groups)
    nav = navigation()
    def page(title, content, crumb='Reference'):
        return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} — Corbo</title><link rel="stylesheet" href="style.css">
<script defer src="search-index.js"></script><script defer src="search.js"></script></head>
<body><a class="skip" href="#content">Skip to content</a><header><a class="brand" href="index.html">Corbo <span>Reference</span></a>
<label class="search"><span class="sr-only">Search types, functions and packages</span><input id="search" type="search" autocomplete="off" placeholder="Search the reference…" aria-controls="search-results"><kbd>/</kbd></label></header>
<aside aria-label="Reference navigation"><a class="overview" href="index.html">Overview</a><a class="overview" href="guide-language.html">Language tour</a><a class="overview" href="guide-grammar.html">Grammar</a><a class="overview" href="guide-compiler.html">Compiler commands</a><a class="overview" href="guide-index.html">Guides and specifications</a>{nav}<p class="revision">STD {html.escape(revision[:12])}<br>Offline reference</p></aside>
<main id="content"><section id="search-results" hidden aria-label="Search results" aria-live="polite"></section>
<article><div class="breadcrumbs"><a href="index.html">Reference</a> / {crumb}</div><h1>{html.escape(title)}</h1>{content}</article>
<footer>Generated from STD/runtime source comments and the compiler API catalog. Compiler-provided entries are labeled explicitly.</footer></main></body></html>'''
    def entry(record, heading=True):
        label = 'Compiler/runtime contract' if record['kind'] == 'runtime contract' else 'Compiler-provided' if record.get('compiler') else ('Internal source' if record.get('internal') else 'Source declaration')
        anchor = record['anchor']
        content = '<section class="entry" id="' + html.escape(anchor, quote=True) + '">'
        if heading:
            content += '<h2>' + html.escape(record['name']) + '</h2>'
        content += '<div class="origin">' + label
        if record.get('source'):
            content += ' · <a href="' + record['source'] + '">View source</a>'
        if record.get('compiler'):
            content += ' · <a href="source-compiler-builtin-reference.json.html">Compiler API catalog</a>'
        annotations = ''.join(html.escape(head) + '\n' for head in record.get('annotations', []))
        content += '</div><pre class="signature"><code>' + annotations + signature(record['signature'], record['module']) + '</code></pre>'
        if record['conditions']:
            content += '<p class="condition">Available when <code>' + html.escape(' and '.join(record['conditions'])) + '</code></p>'
        content += prose(record['description'])
        if record.get('variants'):
            content += '<h3>Variants</h3><ul>' + ''.join('<li><code>' + html.escape(v) + '</code></li>' for v in record['variants']) + '</ul>'
        if record['members']:
            content += '<h3>Members</h3><p class="muted">Implementation fields are shown for reference; this does not grant public field access.</p><dl>'
            content += ''.join('<dt id="' + anchor + '-member-' + str(i) + '"><code>' + html.escape(m['name']) + '</code></dt><dd>' + prose(m['description']) + '</dd>' for i, m in enumerate(record['members'])) + '</dl>'
        if record.get('examples'):
            content += '<h3>Complete examples</h3><ul>' + ''.join('<li><a href="' + source_links[path] + '">' + html.escape(path) + '</a></li>' for path in record['examples'] if path in source_links) + '</ul>'
        return content + '</section>'
    output.mkdir(parents=True, exist_ok=True)
    def write(name, title, body, crumb='Reference'):
        (output / name).write_text(page(title, body, crumb), encoding='utf-8')
    for module in sorted(modules):
        parent = module.rsplit('::', 1)[0] if '::' in module else None
        crumb = '<a href="module-' + slug(parent) + '.html">' + html.escape(parent) + '</a>' if parent else html.escape(module)
        body = ''.join(prose(s) for s in dict.fromkeys(summaries[module]))
        if module in ('core', 'language'):
            body += '<p class="condition">This is a documentation group, not a package to import. Primitive and compiler-generated names use their language spelling.</p>'
        children = [m for m in sorted(modules) if m.startswith(module + '::') and m.count('::') == module.count('::') + 1]
        if children:
            body += '<h2>Packages</h2><ul class="package-list">' + ''.join('<li><a href="module-' + slug(m) + '.html">' + html.escape(m) + '</a></li>' for m in children) + '</ul>'
        owned = [r for r in by_module[module] if not r['owner']]
        if owned:
            body += '<h2>Declarations</h2><table><thead><tr><th>Name</th><th>Description</th></tr></thead><tbody>'
            body += ''.join('<tr><td><a href="' + r['url'] + '">' + html.escape(r['name']) + '</a><small>' + html.escape(r['kind']) + '</small></td><td>' + html.escape(r['description'].split('\n')[0]) + '</td></tr>' for r in owned)
            body += '</tbody></table>'
        body += ''.join(entry(r) for r in owned if r['kind'] not in TYPE_KINDS)
        write('module-' + slug(module) + '.html', module, body, crumb)
    for name, definitions in types.items():
        first = definitions[0]
        methods = [r for r in records if r['module'] == first['module'] and r['owner'] == first['name']]
        body = ''.join(entry(r, False) for r in definitions)
        if methods:
            body += '<h2>Methods and associated constants</h2><nav class="method-list">' + ''.join('<a href="' + m['url'] + '">' + html.escape(m['name']) + '</a>' for m in methods) + '</nav>'
            body += ''.join(entry(r) for r in methods)
        write(urls[name], name, body, '<a href="module-' + slug(first['module']) + '.html">' + html.escape(first['module']) + '</a>')
    for url, (identity, text) in sources.items():
        body = '<p>Source snapshot bundled with this reference.</p><pre class="source"><code>' + ''.join(f'<span id="L{i}" class="source-line"><a href="#L{i}">{i}</a>{html.escape(line)}\n</span>' for i, line in enumerate(text.splitlines(), 1)) + '</code></pre>'
        write(url, identity, body)
    # The complete language tour keeps its feature examples offline as well.
    tour = (corbo / 'README.md').read_text()
    write('guide-language.html', 'Language tour', prose(tour))
    write('guide-compiler.html', 'Compiler commands', prose((ROOT / 'README.md').read_text()))
    guide_index = []
    for identity, url in guides.items():
        if identity == 'README.md': continue
        text = (corbo / identity).read_text()
        title = next((line[2:].strip() for line in text.splitlines() if line.startswith('# ')), Path(identity).stem)
        note = '<p class="condition">Design/specification material may contain historical syntax. The language tour and definition-local method guide show the current source form.</p>'
        write(url, title, note + prose(text, identity))
        guide_index.append('<li><a href="' + url + '">' + html.escape(title) + '</a></li>')
    write('guide-index.html', 'Guides and specifications', '<p>Source-backed design documents and implementation guides. Historical observations are preserved as evidence, not presented as new API guarantees.</p><ul>' + ''.join(guide_index) + '</ul>')

    write('guide-grammar.html', 'Core grammar', '<pre><code>' + html.escape((corbo / 'CORE_GRAMMAR.ebnf').read_text()) + '</code></pre>')
    body = '<p class="lead">The standard library, compiler types and runtime — in one offline reference.</p><p>Browse a package, follow a type in a signature, or press <kbd>/</kbd> to search. Target conditions and implementation origins stay visible.</p>'
    body += '<h2>Start here</h2><ul class="package-list">' + ''.join('<li><a href="module-' + slug(m) + '.html">' + html.escape(m) + '</a></li>' for m in ('std::io', 'std::net', 'std::encoding', 'std::crypto', 'std::sync', 'std::iter', 'core', 'runtime', 'language')) + '</ul>'
    body += '<h2>About this snapshot</h2><p>' + str(len(records)) + ' documented declarations, compiler-provided APIs and runtime entries. Private implementation sources are separated from application APIs.</p>'
    write('index.html', 'Corbo reference', body)
    search = [dict(name=r['full'], label=r['name'], kind=r['kind'], url=r['url'], summary=r['description'].split('\n')[0], signature=r['signature']) for r in records]
    search += [dict(name=r['module'] + '::' + (m.get('owner') or r['name']) + '::' + m['name'], label=m['name'], kind=m['kind'], url=r['url'].split('#')[0] + '#' + r['anchor'] + '-member-' + str(i), summary=m['description'].split('\n')[0], signature='') for r in records for i, m in enumerate(r['members'])]
    search += [dict(name='Guide: ' + Path(identity).stem, label=Path(identity).stem, kind='guide', url=url, summary='Browse the bundled source-backed guide.', signature='') for identity, url in guides.items()]
    search += [dict(name=m, label=m, kind='package', url='module-' + slug(m) + '.html', summary='Browse this package.', signature='') for m in sorted(modules)]
    (output / 'search-index.js').write_text('window.CORBO_SEARCH=' + json.dumps(search, ensure_ascii=True).replace('</', '<\\/') + ';\n')
    for name in ('style.css', 'search.js'):
        shutil.copy2(ASSETS / name, output / name)
    # Historic design links may point at renamed headings. Keep their document
    # destinations usable; current API/source anchors remain exact.
    class Anchors(HTMLParser):
        def __init__(self): super().__init__(); self.ids = set()
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if 'id' in attrs: self.ids.add(attrs['id'])
    available = {}
    for path in output.glob('*.html'):
        parsed = Anchors(); parsed.feed(path.read_text()); available[path.name] = parsed.ids
    repaired = 0
    for path in output.glob('guide-*.html'):
        def repair(match):
            nonlocal repaired
            target = html.unescape(match[1]); name, sep, anchor = target.partition('#')
            name = name or path.name
            if sep and name in available and anchor not in available[name]:
                repaired += 1; return 'href="' + html.escape(name, quote=True) + '"'
            return match[0]
        path.write_text(re.sub(r'href="([^"]+)"', repair, path.read_text()))
    manifest = dict(revision=revision, catalog_sha256=hashlib.sha256((ROOT / "docs/BUILTIN_REFERENCE.json").read_bytes()).hexdigest(), historical_anchor_fallbacks=repaired, declarations=len(records), packages=len(modules), source_files=len(sources), builtin_entries=len(catalog), files=sorted(p.name for p in output.iterdir() if p.is_file()))
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corbo-root', type=Path, required=True)
    parser.add_argument('--stdlib-root', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--revision')
    args = parser.parse_args()
    corbo = args.corbo_root.resolve()
    revision = args.revision or subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=corbo, text=True).strip()
    result = generate(corbo, (args.stdlib_root or corbo / 'stdlib/src').resolve(), args.out.resolve(), revision)
    print(json.dumps({k: v for k, v in result.items() if k != 'files'}, indent=2))


if __name__ == '__main__':
    main()
