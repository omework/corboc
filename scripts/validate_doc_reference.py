#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Validate the offline reference graph and a small real doc-server scenario."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import select
import socket
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

class Page(HTMLParser):
    """Collect emitted IDs and local resource links without executing the page."""
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        if tag == 'a' and 'href' in attrs:
            self.links.append(attrs['href'])
        if tag in ('script', 'link'):
            self.links.append(attrs.get('src') or attrs.get('href', ''))


def graph(root):
    """Require local links and search targets to resolve in the generated snapshot."""
    pages = {}
    for path in root.glob('*.html'):
        page = Page()
        page.feed(path.read_text())
        pages[path.name] = page
    links = 0
    def check(source, target):
        nonlocal links
        split = urllib.parse.urlsplit(target)
        if split.scheme or split.netloc:
            return
        name = split.path or source
        assert (root / name).is_file(), (source, target, 'missing file')
        if split.fragment and name in pages:
            assert urllib.parse.unquote(split.fragment) in pages[name].ids, (source, target, 'missing anchor')
        links += 1
    for name, page in pages.items():
        for target in page.links:
            check(name, target)
    text = (root / 'search-index.js').read_text()
    index = json.loads(text.removeprefix('window.CORBO_SEARCH=').rstrip(';\n'))
    for entry in index:
        check('index.html', entry['url'])
    names = {entry['name'] for entry in index}
    required = {'core::' + n for n in ('i32', 'i64', 'u8', 'u16', 'u32', 'u64', 'f32', 'f64', 'bool', 'usize', 'A', 'Option', 'Result', 'array', 'slice', 'tuple', 'fn', 'str', 'reference')}
    required |= {'std::Pool', 'std::Vector', 'std::HashMap', 'std::String', 'runtime::Handle', 'runtime::AsyncHandle', 'runtime::Future'}
    assert required <= names, required - names
    assert any(e['name'] == 'std::encoding::binary::BigEndian::read_u64' for e in index)
    return dict(pages=len(pages), resolved_local_links=links, searchable_entries=len(index), compiler_type_coverage='passed')


def server(compiler, root):
    """Exercise actual Corbo serving, short reads, HEAD, errors and CLI parsing."""
    process = subprocess.Popen([str(compiler), 'doc', '--no-open', '--port', '0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        deadline = time.monotonic() + 15
        url = None
        log = []
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise AssertionError(('server exited', process.returncode, process.stderr.read()))
            ready, _, _ = select.select([process.stderr], [], [], .1)
            if not ready:
                continue
            line = process.stderr.readline()
            log.append(line)
            match = re.search(r'http://127\.0\.0\.1:(\d+)/', line)
            if match:
                url = match[0]
                break
        assert url, ''.join(log)
        fetched = 0
        for name, mime in [('index.html', 'text/html'), ('search.js', 'text/javascript'), ('search-index.js', 'text/javascript'), ('type-std-Vector.html', 'text/html'), ('type-core-A.html', 'text/html')]:
            with urllib.request.urlopen(url + name, timeout=5) as response:
                assert response.status == 200
                assert mime in response.headers['Content-Type']
                assert response.read() == (root / name).read_bytes(), name
                fetched += 1
        with urllib.request.urlopen(urllib.request.Request(url, method='HEAD'), timeout=5) as response:
            assert response.status == 200 and response.read() == b''
        for path, method, expected in [('absent.html', 'GET', 404), ('%2e%2e/secret', 'GET', 400), ('index.html', 'POST', 405)]:
            try:
                urllib.request.urlopen(urllib.request.Request(url + path, method=method), timeout=5)
                raise AssertionError((path, 'unexpected success'))
            except urllib.error.HTTPError as error:
                assert error.code == expected, (path, error.code)
        port = urllib.parse.urlsplit(url).port
        with socket.create_connection(('127.0.0.1', port), timeout=5) as connection:
            for part in (b'GET /index.html HTTP/1.1\r\n', b'Host: localhost\r\n', b'\r\n'):
                connection.sendall(part)
            received = bytearray()
            while chunk := connection.recv(16384):
                received.extend(chunk)
            assert received.partition(b'\r\n\r\n')[2] == (root / 'index.html').read_bytes()
        for args in [('--port',), ('--port', '65536'), ('--port', '-1'), ('--port', 'abc'), ('--unknown',)]:
            result = subprocess.run([str(compiler), 'doc', *args], capture_output=True, timeout=5)
            assert result.returncode == 6 and b'usage: corboc doc' in result.stderr, args
        return dict(http='passed', assets_compared=fetched, head='passed', partial_request='passed', traversal_and_errors='passed', invalid_cli='passed', url=url)
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--docs', required=True, type=Path)
    parser.add_argument('--compiler', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = {'graph': graph(args.docs.resolve())}
    if args.compiler:
        result['server'] = server(args.compiler.resolve(), args.docs.resolve())
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
