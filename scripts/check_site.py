#!/usr/bin/env python3
"""Check the generated public Site without reading private repository data.

Checks publication metadata, local document links and deployment text. These
checks cannot establish mathematical correctness or authenticate a reviewer.
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys.dont_write_bytecode = True
import build

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {'.html', '.css', '.js', '.json', '.svg', '.xml', '.md', '.tex', '.txt'}
PRIVATE_LINK = re.compile(
    r'(?:github\.com/|api\.github\.com/repos/|raw\.githubusercontent\.com/|'
    r'codeload\.github\.com/)thomasl2/math-research-lab(?:\.git)?'
    r'(?=$|[/#?\s\"\x27<>),])', re.IGNORECASE
)
CREDENTIAL = re.compile(
    r'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|'
    r'sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,})'
)
CSS_URL = re.compile(r'url\(\s*([\"\x27]?)(.*?)\1\s*\)', re.DOTALL)


class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = None
        self.main_count = 0
        self.title = []
        self.in_title = False
        self.ids = set()
        self.duplicate_ids = set()
        self.links = []
        self.element_references = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html':
            self.lang = attrs.get('lang')
        elif tag == 'main':
            self.main_count += 1
        elif tag == 'title':
            self.in_title = True
        if attrs.get('id'):
            if attrs['id'] in self.ids:
                self.duplicate_ids.add(attrs['id'])
            self.ids.add(attrs['id'])
        for key in ('href', 'src', 'poster'):
            if attrs.get(key):
                self.links.append(attrs[key])
        for key in ('aria-labelledby', 'aria-describedby', 'aria-controls'):
            if attrs.get(key):
                self.element_references.extend(attrs[key].split())
        for key in ('data-copy-target', 'data-status-target'):
            if attrs.get(key):
                self.element_references.append(attrs[key])

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, text):
        if self.in_title:
            self.title.append(text)


def check_site(root=ROOT):
    root = Path(root).resolve()
    dist = root / 'dist'
    if not (dist / 'index.html').is_file():
        raise ValueError('Build the Site before checking it: dist/index.html is missing')
    catalogue = json.loads((root / 'content/catalog.json').read_text(encoding='utf-8'))
    build.validate_catalog(catalogue, root)
    published_catalogue = json.loads((dist / 'catalog.json').read_text(encoding='utf-8'))
    if published_catalogue != catalogue:
        raise ValueError('The deployed catalogue differs from source; rebuild the Site')

    errors = []
    documents = {}
    links = []
    files = []
    text_count = 0
    for path in sorted(dist.rglob('*')):
        relative = path.relative_to(dist)
        if path.is_symlink():
            errors.append(f'{relative}: deployment symlinks are not allowed')
            continue
        if relative.as_posix() == '.nojekyll' and path.is_file() and path.stat().st_size == 0:
            files.append(path)
            continue
        if any(part.startswith('.') for part in relative.parts):
            # Do not inspect hidden files, credentials or runtime manifests.
            errors.append(f'{relative}: hidden paths must not enter the public deployment')
            continue
        if not path.is_file():
            continue
        files.append(path)
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != '_headers':
            continue
        text = path.read_text(encoding='utf-8')
        text_count += 1
        if PRIVATE_LINK.search(text):
            errors.append(f'{relative}: contains a private research repository link')
        if CREDENTIAL.search(text):
            # Report the file, never the matched credential-like value.
            errors.append(f'{relative}: contains a credential-shaped string')
        if path.suffix.lower() in {'.html', '.svg'}:
            document = Document()
            document.feed(text)
            document.close()
            documents[path] = document
            links.extend((path, target) for target in document.links)
            if path.suffix.lower() == '.html':
                if not document.lang or not document.lang.strip():
                    errors.append(f'{relative}: missing document language')
                if not ''.join(document.title).strip():
                    errors.append(f'{relative}: missing document title')
                if document.main_count != 1:
                    errors.append(f'{relative}: expected one main landmark')
            if document.duplicate_ids:
                errors.append(f'{relative}: duplicate element IDs')
            for reference in document.element_references:
                if reference not in document.ids:
                    errors.append(f'{relative}: missing element target {reference}')
        elif path.suffix.lower() == '.css':
            links.extend((path, match[1].strip()) for match in CSS_URL.findall(text))

    local_links = 0
    for current, target in links:
        relative = current.relative_to(dist)
        parsed = urlsplit(target)
        if parsed.netloc or parsed.scheme in {'http', 'https', 'mailto', 'tel', 'data'}:
            continue
        if parsed.scheme:
            errors.append(f'{relative}: unsupported link scheme')
            continue
        local_links += 1
        pathname = unquote(parsed.path)
        if not pathname:
            destination = current
        elif pathname.startswith('/'):
            destination = dist / pathname.lstrip('/')
        else:
            destination = current.parent / pathname
        destination = destination.resolve()
        if destination != dist and dist not in destination.parents:
            errors.append(f'{relative}: link escapes the public deployment')
            continue
        if destination.is_dir():
            destination = destination / 'index.html'
        if not destination.is_file():
            errors.append(f'{relative}: missing local target {target}')
            continue
        fragment = unquote(parsed.fragment)
        if fragment and destination.suffix.lower() in {'.html', '.svg'}:
            document = documents.get(destination)
            if document is None or fragment not in document.ids:
                errors.append(f'{relative}: missing fragment in {target}')

    if errors:
        raise ValueError('\n'.join(errors))
    return {
        'ok': True,
        'problems': len(catalogue['problems']),
        'publications': len(catalogue['solutions']) + len(catalogue.get('preprints', [])),
        'reviewed_results': sum(s['status']=='reviewed' for s in catalogue['solutions']),
        'preprints': len(catalogue.get('preprints', [])),
        'html_pages': sum(path.suffix.lower() == '.html' for path in documents),
        'local_links_checked': local_links,
        'deployment_files': len(files),
        'deployment_text_files_checked': text_count,
        'publication_metadata_validated': True,
    }


if __name__ == '__main__':
    try:
        print(json.dumps(check_site(), sort_keys=True))
    except (ValueError, OSError, TypeError, KeyError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}))
        raise SystemExit(1)
