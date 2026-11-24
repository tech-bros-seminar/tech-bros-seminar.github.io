#!/usr/bin/env python3
"""Build a public static archive from an explicit, reviewed publication catalogue.

This script does not read the private research repository or discover artifacts.
Only the assets and files named in the curated catalogue enter dist/.
"""
from __future__ import annotations

import html
import json
import re
import shutil
from datetime import date
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://tech-bros-seminar.github.io'
SLUG = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
PRIVATE_REPO = 'github.com/thomasl2/math-research-lab'


def esc(value):
    escaped = html.escape(str(value), quote=True)
    # Keep catalogue text out of the decorative-icon replacement in layout().
    for arrow in '↗→←↓':
        escaped = escaped.replace(arrow, f'&#{ord(arrow)};')
    return escaped


def require_text(obj, field):
    value = obj.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} must contain nonempty text')
    return value


def valid_date(value):
    if not isinstance(value, str) or date.fromisoformat(value).isoformat() != value:
        raise ValueError('Dates must use YYYY-MM-DD')


def validate_prompt_links(publication):
    links = publication.get('prompt_links', [])
    if not isinstance(links, list):
        raise ValueError('prompt_links must be an array')
    for link in links:
        if not isinstance(link, dict) or set(link) != {'label', 'url'}:
            raise ValueError('Each prompt link needs exactly label and url')
        require_text(link, 'label')
        url = require_text(link, 'url')
        if re.search(r'[\s\x00-\x1f\x7f\\]', url):
            raise ValueError('Prompt URLs cannot contain whitespace, controls or backslashes')
        parsed = urlparse(url)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username is not None or parsed.password is not None:
            raise ValueError('Prompt links need absolute HTTPS URLs without credentials')
        # Accessing port validates its syntax and range without making a request.
        parsed.port


def public_artifact(root, value):
    if not isinstance(value, str) or not re.fullmatch(r'files/[A-Za-z0-9_./-]+', value):
        raise ValueError('Invalid artifact path')
    parts = PurePosixPath(value)
    if parts.is_absolute() or len(parts.parts) < 2 or parts.parts[0] != 'files' or '..' in parts.parts:
        raise ValueError('Artifacts must be explicit paths below content/files/')
    if parts.suffix.lower() not in {'.pdf', '.md', '.tex', '.txt'}:
        raise ValueError('Only PDF, Markdown, TeX and plain-text artifacts are allowed')
    if any(piece.startswith('.') for piece in parts.parts):
        raise ValueError('Hidden artifact paths are not allowed')
    base = (root / 'content').resolve()
    path = base.joinpath(*parts.parts)
    if any(parent.is_symlink() for parent in [path, *path.parents] if parent != base.parent):
        raise ValueError('Symlink artifacts are not allowed')
    if not path.is_file() or base not in path.resolve().parents:
        raise ValueError(f'Missing or unsafe public artifact: {value}')
    if path.stat().st_size == 0:
        raise ValueError('Publication artifacts must not be empty')
    return path


def notebook_sources(data):
    # Catalogue v1 kept the original Kourovka edition under "source".
    kourovka = dict(data['source'], short_title='Kourovka',
                    editors='E. I. Khukhro and V. D. Mazurov')
    return {'kourovka': kourovka, **data.get('notebooks', {})}


def source_for(data, problem):
    return notebook_sources(data)[problem.get('notebook', 'kourovka')]


def problem_name(data, problem):
    return f"{source_for(data, problem)['short_title']} {problem['number']}"


def entry_url(source, problem):
    return source['url'] + '#page=' + str(problem.get('pdf_page', problem['source_page']))


def entry_citation(source, problem):
    return (f"{problem['attribution']}. Problem {problem['number']}, in "
            f"{source['editors']} (eds.), {source['title']}, "
            f"{source['edition']}, p. {problem['source_page']}.")


def validate_catalog(data, root=ROOT):
    if not isinstance(data, dict) or data.get('format_version') != 1:
        raise ValueError('Unsupported catalogue format')
    expected = {'format_version', 'title', 'updated_at', 'source', 'problems', 'solutions'}
    if not expected <= set(data) or set(data) - expected - {'preprints', 'notebooks'}:
        raise ValueError('Unexpected catalogue fields')
    require_text(data, 'title')
    valid_date(data['updated_at'])
    if not isinstance(data['problems'], list) or not isinstance(data['solutions'], list):
        raise ValueError('Problems and solutions must be arrays')
    source_fields = {'title', 'edition', 'url', 'homepage', 'checked_at'}
    if not isinstance(data['source'], dict) or set(data['source']) != source_fields:
        raise ValueError('Invalid Kourovka source record')
    additional = data.get('notebooks', {})
    if not isinstance(additional, dict) or 'kourovka' in additional:
        raise ValueError('Invalid notebook registry')
    sources = notebook_sources(data)
    for key, source in sources.items():
        fields = source_fields | {'short_title', 'editors'}
        if not SLUG.fullmatch(key) or not isinstance(source, dict) or set(source) != fields:
            raise ValueError('Invalid notebook source record')
        for field in fields:
            require_text(source, field)
        valid_date(source['checked_at'])
        for field in ['url', 'homepage']:
            parsed = urlparse(source[field])
            if parsed.scheme != 'https' or not parsed.hostname or parsed.username is not None or parsed.password is not None:
                raise ValueError('Sources need an absolute HTTPS URL without credentials')
    problem_ids = set()
    for p in data['problems']:
        if not isinstance(p, dict) or (set(p) - {'notebook','pdf_page'}) != {'slug','number','title','area','category','attribution','description','statement','statement_latex','details','scope','source_page','status'}:
            raise ValueError('Invalid problem record')
        for field in ['slug','number','title','area','category','attribution','description','statement','statement_latex','status']:
            require_text(p, field)
        if not SLUG.fullmatch(p['slug']) or p['slug'] in problem_ids:
            raise ValueError('Duplicate or invalid problem slug')
        key = p.get('notebook', 'kourovka')
        if not isinstance(key, str) or key not in sources or ('notebook' in p and not p['slug'].startswith(key+'-')):
            raise ValueError('Problem needs a known notebook and matching slug')
        if 'notebook' not in p and any(p['slug'].startswith(n+'-') for n in additional):
            raise ValueError('Set the source notebook for this problem')
        problem_ids.add(p['slug'])
        if p['status'] not in {'available_to_study','under_investigation','proposed_solution_published','project_solution_published'}:
            raise ValueError('Invalid problem status')
        for field in ['details','scope']:
            if not isinstance(p.get(field), list) or not all(isinstance(x,str) and x.strip() for x in p[field]):
                raise ValueError(f'{field} must be a list of text')
        if any(type(p.get(field)) is not int or p[field] < 1 for field in ('source_page', 'pdf_page') if field == 'source_page' or field in p):
            raise ValueError('Invalid source page')
    solution_ids = set()
    required = {'slug','problem_slug','title','scope','status','version','published_at','authors','abstract','statement','proof_file','review_file','reviewed_by','reviewed_at','review_summary','release_approved_by','release_approved_at'}
    revision_fields = {'revises', 'revision_summary'}
    optional = {'source_file','withdrawal_reason','publication_type','lean_status','based_on'} | revision_fields
    for s in data['solutions']:
        if not isinstance(s, dict) or not required <= set(s) or set(s) - required - optional:
            raise ValueError('Invalid publication fields')
        for field in required - {'authors','reviewed_by'}:
            require_text(s, field)
        if not SLUG.fullmatch(s['slug']) or s['slug'] in solution_ids:
            raise ValueError('Duplicate or invalid publication slug')
        solution_ids.add(s['slug'])
        if s['problem_slug'] not in problem_ids:
            raise ValueError('Unknown publication problem')
        if s['status'] not in {'reviewed','withdrawn'}:
            raise ValueError('Unreviewed candidates cannot enter this publication catalogue')
        if s['scope'] not in {'full_solution','partial_result'}:
            raise ValueError('Publication scope must be explicit')
        if s.get('publication_type','human_reviewed') != 'human_reviewed':
            raise ValueError('Reviewed results must have Human reviewed publication type')
        for field in ['lean_status','based_on']:
            if field in s:
                require_text(s,field)
        for field in ['authors','reviewed_by']:
            if not isinstance(s[field],list) or not s[field] or not all(isinstance(x,str) and x.strip() for x in s[field]):
                raise ValueError(f'{field} must record real, nonempty attribution')
        for field in ['published_at','reviewed_at','release_approved_at']:
            valid_date(s[field])
        if s['reviewed_at'] > s['published_at'] or s['release_approved_at'] > s['published_at']:
            raise ValueError('Review and release authorization must precede publication')
        if s['status'] == 'withdrawn':
            require_text(s, 'withdrawal_reason')
        for field in ['proof_file','review_file','source_file']:
            if s.get(field):
                public_artifact(root, s[field])
    preprints = data.get('preprints', [])
    if not isinstance(preprints, list):
        raise ValueError('Preprints must be an array')
    preprint_required = {'slug','problem_slug','title','scope','status','version','manuscript_date','published_at','authors','attribution_note','abstract','statement','proof_file','source_file','review_file','review_summary','release_approved_by','release_approved_at'}
    for s in preprints:
        if not isinstance(s, dict) or not preprint_required <= set(s) or set(s) - preprint_required - {'withdrawal_reason','publication_type','lean_status','prompt_links'} - revision_fields:
            raise ValueError('Invalid preprint fields')
        for field in preprint_required - {'authors'}:
            require_text(s, field)
        if not SLUG.fullmatch(s['slug']) or s['slug'] in solution_ids:
            raise ValueError('Duplicate or invalid publication slug')
        solution_ids.add(s['slug'])
        if s['problem_slug'] not in problem_ids:
            raise ValueError('Unknown preprint problem')
        if s['status'] not in {'review_pending','withdrawn'}:
            raise ValueError('Preprints cannot claim reviewed acceptance')
        if s['scope'] not in {'full_solution','partial_result'}:
            raise ValueError('The scope of a proposed result must be explicit')
        if s.get('publication_type','ai_generated') != 'ai_generated':
            raise ValueError('AI manuscripts must have AI generated publication type')
        if 'lean_status' in s:
            require_text(s,'lean_status')
        validate_prompt_links(s)
        if not isinstance(s['authors'],list) or not all(isinstance(x,str) and x.strip() for x in s['authors']):
            raise ValueError('Preprint authors must be an array; disclose unspecified authorship in attribution_note')
        for field in ['manuscript_date','published_at','release_approved_at']:
            valid_date(s[field])
        if s['release_approved_at'] > s['published_at']:
            raise ValueError('Public preprints require prior release authorization')
        if s['status'] == 'withdrawn':
            require_text(s, 'withdrawal_reason')
        for field in ['proof_file','source_file','review_file']:
            public_artifact(root,s[field])
    validate_revisions(data['solutions'] + preprints)
    for s in data['solutions']:
        if s.get('based_on'):
            original=next((p for p in preprints if p['slug']==s['based_on']),None)
            if original is None or original['problem_slug'] != s['problem_slug']:
                raise ValueError('A Human reviewed version must link an AI original for the same problem')
            if original['proof_file']==s['proof_file']:
                raise ValueError('A Human reviewed exposition needs its own versioned file')
    for p in data['problems']:
        if p['status'] == 'project_solution_published' and not any(s['problem_slug']==p['slug'] and s['status']=='reviewed' and s['scope']=='full_solution' for s in data['solutions']):
            raise ValueError('A solved problem needs a reviewed full solution')
        if p['status'] == 'proposed_solution_published' and not any(s['problem_slug']==p['slug'] and s['status']=='review_pending' and s['scope']=='full_solution' for s in preprints):
            raise ValueError('A proposed-solution label needs a published provisional manuscript')
    serialized = json.dumps(data, ensure_ascii=False)
    if PRIVATE_REPO in serialized or re.search(r'(?:ghp_|github_pat_|sk-proj-)[A-Za-z0-9_-]{10,}', serialized):
        raise ValueError('Private repository links or credential-like strings must not be published')


def validate_revisions(papers):
    by_slug = {paper['slug']: paper for paper in papers}
    artifacts = {}
    for paper in papers:
        for field in ('proof_file', 'source_file', 'review_file'):
            if paper.get(field):
                artifacts.setdefault(PurePosixPath(paper[field]), set()).add(paper['slug'])

    successors = set()
    for paper in papers:
        if 'revises' not in paper and 'revision_summary' not in paper:
            continue
        previous = by_slug.get(require_text(paper, 'revises'))
        require_text(paper, 'revision_summary')
        if previous is None or previous['problem_slug'] != paper['problem_slug']:
            raise ValueError('A revision must refer to a publication for the same problem')
        version = paper['version']
        if not re.fullmatch(r'[1-9][0-9]*', version):
            raise ValueError('Use a positive integer for a new revision number')
        if previous['version'].isascii() and previous['version'].isdigit() and int(version) <= int(previous['version']):
            raise ValueError('A revision needs a higher version number than its predecessor')
        if paper['published_at'] < previous['published_at']:
            raise ValueError('A revision cannot predate its predecessor')
        key = (previous['slug'], version)
        if key in successors:
            raise ValueError('Two revisions of the same publication have the same version number')
        successors.add(key)
        for field in ('proof_file', 'source_file', 'review_file'):
            if paper.get(field) and len(artifacts[PurePosixPath(paper[field])]) > 1:
                raise ValueError('A revision needs its own versioned manuscript and review files')


def display_date(value):
    stamp = date.fromisoformat(value)
    return f'{stamp.day} {stamp.strftime("%B %Y")}'


LOGO = '<img class="brand-mark" src="/assets/cybernetic-brain.svg" width="44" height="44" alt="" aria-hidden="true">'
BOOK = '<svg class="book-icon" viewBox="0 0 54 60" fill="none" aria-hidden="true"><path d="M12 5h32v47H12a6 6 0 0 1 0-12h32M8 45V11a6 6 0 0 1 6-6M17 16h19M17 23h14M17 30h17M12 46h32" stroke="currentColor" stroke-width="1.2"/><path d="m26 35 3-4 3 4" stroke="#d29979"/></svg>'


def layout(title, description, body, path='/', extra_head=''):
    page_title = 'Tech bros seminar' if title == 'Tech bros seminar' else title + ' — Tech bros seminar'
    markup = f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(page_title)}</title>
<meta name="description" content="{esc(description)}"><meta name="theme-color" content="#163b32">
<link rel="canonical" href="{ORIGIN}{esc(path)}">
<meta property="og:title" content="{esc(page_title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:type" content="website"><meta property="og:url" content="{ORIGIN}{esc(path)}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/site.css">
<link rel="preload" href="/assets/fonts/NotoSerifDisplay-Regular.woff" as="font" type="font/woff" crossorigin>
<script src="/assets/site.js" defer></script>{extra_head}
</head><body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="header"><div class="container header-inner">
<a class="brand" href="/" aria-label="Tech bros seminar home">{LOGO}<span class="brand-word"><strong>Tech bros</strong><span>seminar</span></span></a>
<nav class="nav" aria-label="Main navigation"><a href="/#ai-generated">AI generated</a><a href="/#human-reviewed">Human reviewed</a><a href="/#problems">Problems</a><a href="/#seminar">Seminar</a><a class="source-link" href="/#sources">Notebooks</a></nav>
</div></header>
{body}
<footer class="footer"><div class="container footer-inner"><div><div class="footer-brand">Tech bros seminar</div><p>Mathematical arguments generated by AI and studied in our seminar.</p></div><div class="footer-links"><a href="/#seminar">How we work</a><a href="/#sources">Problem notebooks</a><a href="/catalog.json">Catalogue data</a></div></div></footer>
</body></html>'''
    paths = {'↗':'M3 13 13 3M4 3h9v9','→':'M2 8h12M9 3l5 5-5 5','←':'M14 8H2m5-5L2 8l5 5','↓':'M8 2v12m-5-5 5 5 5-5'}
    for symbol, shape in paths.items():
        markup = markup.replace(symbol, '<svg class="inline-arrow" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="'+shape+'" stroke="currentColor" stroke-width="1.2"/></svg>')
    return markup


def status_label(problem):
    return {'available_to_study':'Available to study','project_solution_published':'Human reviewed solution','proposed_solution_published':'AI generated solution'}.get(problem['status'],'In progress')


def problem_status_class(problem):
    return {'available_to_study':'available','project_solution_published':'reviewed','proposed_solution_published':'provisional'}.get(problem['status'],'in-progress')


def problem_destination(data, problem):
    category = {
        'proposed_solution_published': ('preprints', 'review_pending'),
        'project_solution_published': ('solutions', 'reviewed'),
    }.get(problem['status'])
    if category is None:
        return '/problems/' + problem['slug'] + '/'
    collection, status = category
    candidates = [paper for paper in data.get(collection, [])
                  if paper['problem_slug'] == problem['slug']
                  and paper['status'] == status and paper['scope'] == 'full_solution']
    if not candidates:
        raise ValueError('A solution badge needs an active full-solution manuscript')
    def order(paper):
        version = tuple((1, int(part)) if part.isdigit() else (0, part.casefold())
                        for part in re.split(r'(\d+)', paper['version']))
        return paper['published_at'], version, paper['slug']
    latest = max(candidates, key=order)
    return '/publications/' + latest['slug'] + '/'


def problem_row(data, p):
    notebook = source_for(data, p)['short_title']
    search = ' '.join([notebook,p['number'],p['title'],p['area'],p['description'],p['attribution']])
    destination = problem_destination(data, p)
    label = status_label(p)
    return f'''<article class="problem-row" data-problem="{esc(p['slug'])}" data-category="{esc(p['category'])}" data-search="{esc(search)}">
<div class="problem-number">{esc(p['number'])}<span>{esc(notebook)}</span></div>
<div class="problem-main"><span class="topic">{esc(p['area'])}</span><h3>{esc(p['title'])}</h3><p>{esc(p['description'])}</p></div>
<div class="problem-action"><a class="status status-link {problem_status_class(p)}" href="{esc(destination)}" aria-label="{esc(label)} for {esc(problem_name(data,p))}">{esc(label)}<span class="arrow" aria-hidden="true">↗</span></a></div>
</article>'''


def manuscript_links(s, ai):
    links = [f'<a href="/{esc(s["proof_file"])}">PDF</a>']
    if s.get('source_file'):
        links.append(f'<a href="/{esc(s["source_file"])}" download>TeX source</a>')
    review_label = 'AI review notes' if ai else 'Human review record'
    links.append(f'<a href="/{esc(s["review_file"])}">{review_label}</a>')
    if ai and s.get('prompt_links'):
        links.append(f'<a href="/publications/{esc(s["slug"])}/#prompts">Prompts</a>')
    return '<div class="paper-links">' + ' · '.join(links) + '</div>'


def prompt_section(publication):
    links = publication.get('prompt_links', [])
    if links:
        items = ''.join(f'<li><a href="{esc(link["url"])}" target="_blank" rel="noopener noreferrer">{esc(link["label"])} ↗</a></li>' for link in links)
        content = '<p>Public prompts and AI responses shared for this manuscript.</p><ul>' + items + '</ul>'
    else:
        content = '<p>Prompts have not yet been published for this version.</p>'
    return '<section id="prompts" aria-labelledby="prompts-title"><h2 id="prompts-title">Prompts and conversation</h2>' + content + '</section>'


def paper_entry(s, ai, problem_label=None):
    kind = 'AI generated' if ai else 'Human reviewed'
    kind_class = 'provisional ai-generated' if ai else 'reviewed human-reviewed'
    if s['status']=='withdrawn':
        kind_class += ' withdrawn'
    problem = esc(problem_label) + ' · ' if problem_label else ''
    withdrawn = ' · Withdrawn' if s['status']=='withdrawn' else ''
    return f'''<article class="publication-card"><div>
<span class="status {kind_class}">{kind}{withdrawn}</span><h4 class="paper-title"><a href="/publications/{esc(s['slug'])}/">{esc(s['title'])}</a></h4>
<p>{esc(s['abstract'])}</p>
<div class="publication-meta">{problem}Version {esc(s['version'])} · {display_date(s['published_at'])}</div>
{manuscript_links(s,ai)}
</div><a class="row-link" href="/publications/{esc(s['slug'])}/">Read paper ↗</a></article>'''


def publication_card(s):
    return paper_entry(s,False)


def preprint_card(s):
    return paper_entry(s,True)


def version_links(data,s):
    all_papers = data['solutions'] + data.get('preprints',[])
    originals = {p['slug'] for p in data.get('preprints',[])}
    links = []
    summary = ''
    if s.get('revises'):
        previous = next(paper for paper in all_papers if paper['slug'] == s['revises'])
        links.append(f'<li>Revises <a href="/publications/{esc(previous["slug"])}/">{esc(previous["title"])} (version {esc(previous["version"])})</a></li>')
        summary = f'<p>{esc(s["revision_summary"])}</p>'
    if s.get('based_on') and s['based_on'] != s.get('revises'):
        previous = next((p for p in all_papers if p['slug']==s['based_on']),None)
        if previous:
            label = 'AI generated original' if previous['slug'] in originals else 'Earlier Human reviewed version'
            links.append(f'<li><a href="/publications/{esc(previous["slug"])}/">{label}: version {esc(previous["version"])}</a></li>')
    for revision in all_papers:
        if revision.get('revises') == s['slug']:
            kind = 'AI generated' if revision['slug'] in originals else 'Human reviewed'
            withdrawn = ' (withdrawn)' if revision['status'] == 'withdrawn' else ''
            links.append(f'<li><a href="/publications/{esc(revision["slug"])}/">{kind} revision {esc(revision["version"])}{withdrawn}</a> · {esc(revision["revision_summary"])}</li>')
        elif revision.get('based_on')==s['slug']:
            links.append(f'<li><a href="/publications/{esc(revision["slug"])}/">Human reviewed version {esc(revision["version"])}</a></li>')
    return '<section class="version-links"><h2>Related versions</h2>'+summary+'<ul>'+''.join(links)+'</ul></section>' if links else ''


def home(data):
    problems = data['problems']
    labels = {p['slug']:problem_name(data,p) for p in problems}
    ai_papers = sorted(data.get('preprints',[]),key=lambda s:s['published_at'],reverse=True)
    human_papers = sorted(data['solutions'],key=lambda s:s['published_at'],reverse=True)
    ai_list = ''.join(paper_entry(s,True,labels[s['problem_slug']]) for s in ai_papers) or f'<div class="archive-empty">{BOOK}<div><h3>No AI generated manuscript has been published yet.</h3></div></div>'
    human_list = ''.join(paper_entry(s,False,labels[s['problem_slug']]) for s in human_papers) or f'<div class="archive-empty">{BOOK}<div><h3>No Human reviewed version has been published yet.</h3><p>The seminar studies the AI manuscripts after publication. The original AI version remains available when a reviewed version is added.</p></div></div>'
    source_links = ''.join(
        f'<a href="{esc(source["url"])}" target="_blank" rel="noopener noreferrer">'
        f'{esc(source["short_title"])} Notebook · {esc(source["edition"])} ↗</a>'
        for source in notebook_sources(data).values()
    )
    ai_count = sum(s['status']!='withdrawn' for s in ai_papers)
    human_count = sum(s['status']=='reviewed' for s in human_papers)
    publication_count = len(ai_papers)+len(human_papers)
    categories = list(dict.fromkeys((p['category'],p['area']) for p in problems))
    filters = '<button class="filter-button" data-filter="all" aria-pressed="true">All problems</button>'+''.join(f'<button class="filter-button" data-filter="{esc(key)}" aria-pressed="false">{esc(name)}</button>' for key,name in categories)
    body = f'''<main id="main"><div class="container">
<section class="hero" aria-labelledby="seminar-title"><div>
<div class="eyebrow"><span class="dot"></span>Group theory · Rings and algebras</div>
<h1 id="seminar-title">Tech bros<br><em>seminar</em></h1>
<p class="hero-copy">AI systems generate the mathematical arguments collected here. In Tech bros seminar, we read these proofs and try to understand them.</p>
<div class="actions"><a class="button" href="#publications">Read the papers <span aria-hidden="true">↗</span></a><a class="text-link" href="#seminar">How the seminar works</a></div>
</div><figure class="hero-art cyber-galois"><img src="/assets/cybernetic-galois-v3.png" width="1122" height="1402" alt="AI-generated pen-and-ink portrait of Évariste Galois, with his swept dark hair and cravat, textured synthetic facial panels, and fine emerald-lit seams." fetchpriority="high"></figure></section>
<div class="stats" aria-label="Publication counts"><div class="stat"><span class="stat-number">{len(problems):02d}</span><span class="stat-label">Problems<br>in focus</span></div><div class="stat"><span class="stat-number">{ai_count:02d}</span><span class="stat-label">AI generated<br>manuscripts</span></div><div class="stat"><span class="stat-number">{human_count:02d}</span><span class="stat-label">Human reviewed<br>versions</span></div></div>
<section id="problems" aria-labelledby="problems-title"><div class="section-label">01 / The questions</div><div class="section-heading"><h2 id="problems-title">Problems</h2><p>Choose a question from the Kourovka Notebook on group theory or the Dniester Notebook on rings and algebras.</p></div>
<div class="problem-tools"><div class="filters" role="group" aria-label="Filter problems by topic">{filters}</div><div class="search-wrap"><label class="sr-only" for="problem-search">Search problems</label><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="8.3" cy="8.3" r="5.7" stroke="currentColor" stroke-width="1.4"/><path d="m12.5 12.5 4.4 4.4" stroke="currentColor" stroke-width="1.4"/></svg><input id="problem-search" type="search" placeholder="Notebook, number, title, or topic" autocomplete="off" aria-controls="problem-list"></div></div>
<div class="results-bar"><span id="result-count" role="status" aria-live="polite">{len(problems)} problems in view</span><button class="reset-button" id="reset-filters" hidden>Clear filters</button></div>
<div id="problem-list">{''.join(problem_row(data,p) for p in problems)}</div><div class="empty-search" id="empty-search" hidden><p>No matching problems. Try another search or clear the filters.</p></div>
<noscript><p class="no-js-notice">All problems are listed. Search and topic filtering require JavaScript.</p></noscript>
<nav class="source-note" id="sources" aria-label="Source notebooks">{source_links}</nav>
</section></div>
<section class="publications" id="publications" aria-labelledby="papers-title"><div class="container">
<div class="section-label">02 / The public record</div><div class="section-heading"><h2 id="papers-title">Papers</h2><span class="archive-count">{publication_count} {'publication' if publication_count==1 else 'publications'}</span></div>
<section id="ai-generated" aria-labelledby="ai-title"><h3 class="archive-group-title" id="ai-title">AI generated</h3><p class="archive-intro">Written by AI and published before human review. AI review and Lean status are recorded separately.</p>{ai_list}</section>
<section id="human-reviewed" aria-labelledby="human-title"><h3 class="archive-group-title" id="human-title">Human reviewed</h3><p class="archive-intro">New versions that seminar participants have understood and checked, with the proof rewritten to make it easier to follow. Each version records its reviewers and links to the AI original.</p>{human_list}</section>
</div></section>
<div class="container"><section class="review-section" id="seminar" aria-labelledby="workflow-title"><span id="review"></span><div class="review-layout">
<div class="review-intro"><div class="section-label">03 / Our process</div><h2 id="workflow-title">How the<br>seminar works</h2><p>We publish AI generated manuscripts before human review, so everyone can read them. The seminar then studies the proofs.</p><p class="review-note">AI review, Lean verification, and human review are different checks. A partial or unavailable Lean formalization does not prevent publication as AI generated.</p><p class="review-note">Human reviewed refers to the seminar’s understanding and checking of a specific version.</p></div>
<ol class="review-steps">
<li class="review-step"><span class="step-number" aria-hidden="true">01</span><div><h3>Ask AI for a solution.</h3><p>The mathematical ideas and arguments in the first version come from AI.</p></div></li>
<li class="review-step"><span class="step-number" aria-hidden="true">02</span><div><h3>Ask AI to prepare the paper.</h3><p>We ask it to polish the exposition, review its argument, and attempt a Lean formalization when feasible. The paper records which checks actually took place.</p></div></li>
<li class="review-step"><span class="step-number" aria-hidden="true">03</span><div><h3>Publish the AI generated version.</h3><p>Human review is not a prerequisite for publication. The manuscript and the available review and formalization records are public. We also link the prompts and AI conversations behind each paper.</p></div></li>
<li class="review-step"><span class="step-number" aria-hidden="true">04</span><div><h3>Read it in the seminar.</h3><p>We try to understand every step. If we can understand and check the proof, we prepare a new Human reviewed version with a clearer explanation and a record of who reviewed it.</p></div></li>
</ol></div>
</section>
<section class="about" id="about" aria-labelledby="about-title"><div><div class="section-label">About the seminar</div><h2 id="about-title">AI generated arguments.<br>Human understanding.</h2></div><div>
<p>We ask AI to polish and review its solutions, and to formalize them in Lean where possible. We publish the <strong>AI generated</strong> manuscripts before human review, so everyone can read them. When we understand and check a proof in the seminar, we publish a new, more human-readable <strong>Human reviewed</strong> version. The original AI version remains available.</p>
<p>If you improve a published proof, release a new version, explain what changed and link the two manuscripts. Earlier versions stay available.</p>
<div class="about-links"><button class="text-link reset-button" data-copy-target="review-checklist" data-status-target="checklist-status">Copy the publication checklist <span aria-hidden="true">↗</span></button><a class="text-link" href="https://github.com/tech-bros-seminar/tech-bros-seminar.github.io/blob/main/CONTRIBUTING.md">Contributor guide ↗</a></div><span class="copy-status" id="checklist-status" role="status" aria-live="polite"></span>
<pre id="review-checklist" hidden>Tech bros seminar — publication checklist
1. Identify the notebook, edition, problem number, page, attribution and claimed scope.
2. Ask AI to polish the complete argument and review its dependencies and possible gaps.
3. Ask for a Lean formalization when feasible; record only the formalization and checks actually completed.
4. Publish the AI generated manuscript before human review, with its source, available AI review notes, and public prompt and conversation links.
5. Read and try to understand the proof in the seminar.
6. After understanding and checking the proof, publish a new, clearer Human reviewed version with the actual reviewers, date, and a link to the AI original.
7. When you improve a proof, add a new version to the research repository and this website. Credit the earlier work, link the versions, and check the deployed paper and downloads. Preserve corrections and withdrawals. Keep AI review, Lean verification, and human review distinct.</pre>
</div></section></div>
</main>'''
    return layout('Tech bros seminar','Solutions generated by AI, published before human review, and studied in Tech bros seminar. AI generated manuscripts and Human reviewed versions.',body)


FORMULAS = {
 'kourovka-18-78': '<math display="block" aria-label="Does simplicity of the twisted group algebra K alpha G imply that G is soluble?"><mrow><msup><mi>K</mi><mi>α</mi></msup><mi>G</mi><mspace width=".5em"/><mtext>simple</mtext><mspace width=".5em"/><mo>⟹</mo><mspace width=".5em"/><mi>G</mi><mspace width=".5em"/><mtext>soluble?</mtext></mrow></math><span class="formula-words">Finite group <var>G</var> · arbitrary field <var>K</var> · normalized 2-cocycle <var>α</var></span>',
 'kourovka-18-77': '<math display="block" aria-label="p to the e equals the largest irreducible complex character degree"><mrow><msup><mi>p</mi><mi>e</mi></msup><mo>=</mo><munder><mo>max</mo><mrow><mi>χ</mi><mo>∈</mo><msub><mi mathvariant="normal">Irr</mi><mi>ℂ</mi></msub><mo>(</mo><mi>G</mi><mo>)</mo></mrow></munder><mi>χ</mi><mo>(</mo><mn>1</mn><mo>)</mo></mrow></math><math display="block" aria-label="Does p greater than e imply the intersection of the maximum-degree kernels is trivial?"><mrow><mi>p</mi><mo>&gt;</mo><mi>e</mi><mo>⟹</mo><munder><mo>⋂</mo><mrow><mi>χ</mi><mo>(</mo><mn>1</mn><mo>)</mo><mo>=</mo><msup><mi>p</mi><mi>e</mi></msup></mrow></munder><mi mathvariant="normal">ker</mi><mi>χ</mi><mo>=</mo><mo>{</mo><mn>1</mn><mo>}</mo><mo>?</mo></mrow></math>',
 'kourovka-18-80': '<math display="block" aria-label="The Jacobson radical of K G equals its augmentation ideal"><mrow><mi>J</mi><mo>(</mo><mi>K</mi><mo>[</mo><mi>G</mi><mo>]</mo><mo>)</mo><mo>=</mo><msub><mi>I</mi><mi>K</mi></msub><mo>(</mo><mi>G</mi><mo>)</mo></mrow></math><span class="formula-words">if and only if, for some prime <var>p</var>,<br>char <var>K</var> = <var>p</var> and <var>G</var> is a locally finite <var>p</var>-group?</span>',
 'kourovka-4-2-b': '<math display="block" aria-label="G is finitely generated and infinite"><mrow><mi>G</mi><mo>=</mo><mo>⟨</mo><msub><mi>g</mi><mn>1</mn></msub><mo>,</mo><mo>…</mo><mo>,</mo><msub><mi>g</mi><mi>d</mi></msub><mo>⟩</mo><mo>,</mo><mspace width="1em"/><mo>|</mo><mi>G</mi><mo>|</mo><mo>=</mo><mo>∞</mo></mrow></math><math display="block" aria-label="For every element x in G, x to the fifth equals one"><mrow><mo>∀</mo><mi>x</mi><mo>∈</mo><mi>G</mi><mo>,</mo><mspace width=".5em"/><msup><mi>x</mi><mn>5</mn></msup><mo>=</mo><mn>1</mn></mrow></math>'
}



def problem_page(data,p,next_problem):
    source = source_for(data,p)
    source_url = entry_url(source,p)
    citation = entry_citation(source,p) + ' ' + source_url
    ai_papers = [s for s in data.get('preprints',[]) if s['problem_slug']==p['slug']]
    human_papers = [s for s in data['solutions'] if s['problem_slug']==p['slug']]
    if ai_papers or human_papers:
        published = '<h3>AI generated</h3><div class="paper-list">'+(''.join(paper_entry(s,True,problem_name(data,p)) for s in ai_papers) or '<p class="empty-list">No AI generated manuscript is listed for this problem.</p>')+'</div>'
        published += '<h3>Human reviewed</h3><div class="paper-list">'+(''.join(paper_entry(s,False,problem_name(data,p)) for s in human_papers) or '<p class="empty-list">No Human reviewed version has been published yet.</p>')+'</div>'
    else:
        published = '<p class="empty-list">No solution manuscript has been published for this problem.</p>'
    body = f'''<main id="main" class="container">
<div class="breadcrumb"><a href="/#problems">Problems</a><span aria-hidden="true">/</span><span>{esc(problem_name(data,p))}</span></div>
<header class="detail-header"><div class="eyebrow"><span class="dot"></span>{esc(source['short_title'])} problem {esc(p['number'])}</div><h1>{esc(p['title'])}</h1><div class="detail-meta"><span>{esc(p['area'])}</span><span aria-hidden="true">·</span><span>{esc(p['attribution'])}</span></div></header>
<div class="detail-layout"><article class="article"><h2>The question</h2><div class="statement"><p>{esc(p['statement'])}</p><div class="formula">{FORMULAS.get(p['slug'],'')}</div></div>
<h2>Reading the statement</h2>{''.join('<p>'+esc(x)+'</p>' for x in p['details'])}
<h2>Scope</h2><ul>{''.join('<li>'+esc(x)+'</li>' for x in p['scope'])}</ul>
<h2>Papers</h2>{published}
<h2>Source</h2><p class="citation" id="citation">{esc(citation)}</p><p><a href="{esc(source_url)}">Original notebook entry</a> · <a href="{esc(source['homepage'])}">Edition information</a></p><p class="source-note">Source checked {display_date(source['checked_at'])}. Publication status describes the seminar’s work on this question.</p>
</article><aside class="side-panel" aria-label="Problem status and downloads"><div class="side-label">Publication status</div><span class="status {problem_status_class(p)}">{esc(status_label(p))}</span><p>AI generated manuscripts are published before human review. Human reviewed versions record the seminar’s later understanding and checking of the proof.</p><hr class="side-rule"><div class="side-label">Take the question with you</div><a class="button" href="/downloads/{esc(p['slug'])}.md" download>Download statement <span aria-hidden="true">↓</span></a><button class="button secondary" data-copy-target="citation">Copy source citation</button><button class="button secondary" data-print>Print this page</button><span class="copy-status" id="copy-status" role="status" aria-live="polite"></span><hr class="side-rule"><p>Public status checked<br><strong>{display_date(data['updated_at'])}</strong></p><a class="text-link" href="/#seminar">How the seminar works ↗</a></aside></div>
<nav class="next-problem" aria-label="Problem navigation"><a href="/#problems">← All problems</a><a href="/problems/{esc(next_problem['slug'])}/">Next: {esc(problem_name(data,next_problem))} →</a></nav>
</main>'''
    return layout(problem_name(data,p),p['description'],body,'/problems/'+p['slug']+'/')


def solution_page(data,s):
    problem = next(p for p in data['problems'] if p['slug']==s['problem_slug'])
    scope = 'Full solution' if s['scope']=='full_solution' else 'Partial result'
    withdrawn = s['status']=='withdrawn'
    notice = '<div class="publication-notice"><p><strong>Withdrawn.</strong> '+esc(s['withdrawal_reason'])+'</p></div>' if withdrawn else ''
    review_verb = 'was reviewed' if withdrawn else 'has been understood and checked'
    source_button = f'<a class="button secondary" href="/{esc(s["source_file"])}" download>Download TeX source</a>' if s.get('source_file') else ''
    body = f'''<main id="main" class="container">
<div class="breadcrumb"><a href="/#human-reviewed">Human reviewed papers</a><span aria-hidden="true">/</span><a href="/problems/{esc(problem['slug'])}/">{esc(problem_name(data,problem))}</a></div>
<header class="detail-header"><div class="eyebrow">{esc(problem_name(data,problem))} · Version {esc(s['version'])}</div><h1>{esc(s['title'])}</h1><div class="detail-meta"><span class="status human-reviewed {'withdrawn' if withdrawn else 'reviewed'}">Human reviewed{' · Withdrawn' if withdrawn else ''}</span><span>{esc(', '.join(s['authors']))}</span><span>Published {display_date(s['published_at'])}</span></div>{manuscript_links(s,False)}</header>
<div class="detail-layout"><article class="article">{notice}<p>This version {review_verb} in the seminar. It presents the argument for human readers.</p>
<h2>Abstract</h2><p>{esc(s['abstract'])}</p><h2>Statement</h2><div class="statement"><p>{esc(s['statement'])}</p></div><p>{scope}. <a href="/problems/{esc(problem['slug'])}/">Read the original problem.</a></p>
<h2>Human review</h2><p>Reviewed by {esc(', '.join(s['reviewed_by']))} on {display_date(s['reviewed_at'])}.</p><p>{esc(s['review_summary'])}</p><p><a href="/{esc(s['review_file'])}">Read the human review record</a>.</p>
<h2>Lean</h2><p class="lean-status">{esc(s.get('lean_status','No Lean formalization is published for this version.'))}</p>
{version_links(data,s)}
<p>Human reviewed records the seminar’s understanding and checking of this version.</p>
</article><aside class="side-panel" aria-label="Publication details and downloads"><div class="side-label">Human reviewed · Version {esc(s['version'])}</div><p>Published {display_date(s['published_at'])}</p><a class="button" href="/{esc(s['proof_file'])}" download>Download PDF ↓</a>{source_button}<a class="button secondary" href="/{esc(s['review_file'])}" download>Human review record</a><button class="button secondary" data-print>Print this page</button><hr class="side-rule"><div class="side-label">Lean</div><p>{esc(s.get('lean_status','No Lean formalization is published for this version.'))}</p><a class="text-link" href="/#seminar">How the seminar works ↗</a></aside></div></main>'''
    return layout(s['title']+' — Human reviewed',s['abstract'],body,'/publications/'+s['slug']+'/')


def preprint_page(data,s):
    problem = next(p for p in data['problems'] if p['slug']==s['problem_slug'])
    scope = 'a full answer to the problem' if s['scope']=='full_solution' else 'a partial result'
    withdrawn = s['status']=='withdrawn'
    notice = '<div class="publication-notice"><p><strong>Withdrawn.</strong> '+esc(s['withdrawal_reason'])+'</p></div>' if withdrawn else '<div class="publication-notice"><p>Generated by AI and published before human review. The seminar has not yet reviewed this version.</p></div>'
    prompts_button = '<a class="button secondary" href="#prompts">Read the prompts ↗</a>' if s.get('prompt_links') else ''
    body = f'''<main id="main" class="container">
<div class="breadcrumb"><a href="/#ai-generated">AI generated papers</a><span aria-hidden="true">/</span><span>{esc(problem_name(data,problem))}</span></div>
<header class="detail-header"><div class="eyebrow">{esc(problem_name(data,problem))} · Manuscript version {esc(s['version'])}</div><h1>{esc(s['title'])}</h1><div class="detail-meta"><span class="status provisional ai-generated{' withdrawn' if withdrawn else ''}">AI generated{' · Withdrawn' if withdrawn else ''}</span><span>Published {display_date(s['published_at'])}</span></div>{manuscript_links(s,True)}</header>
<div class="detail-layout"><article class="article">{notice}<h2>Abstract</h2><p>{esc(s['abstract'])}</p>
<h2>Problem</h2><p>{esc(problem['statement'])}</p><p class="citation">{esc(problem['attribution'])} · {esc(problem_name(data,problem))}. <a href="{esc(entry_url(source_for(data,problem),problem))}">Original source ↗</a></p>
<h2>Claimed result</h2><div class="statement"><p>{esc(s['statement'])}</p></div><p>The manuscript claims {scope}.</p>
{prompt_section(s)}
<h2>AI review</h2><p>{esc(s['review_summary'])}</p><p><a href="/{esc(s['review_file'])}">Read the AI review notes and their scope</a>.</p>
<h2>Lean</h2><p class="lean-status">{esc(s.get('lean_status','No Lean formalization is published for this version.'))}</p>
<h2>Version and attribution</h2><p>{esc(s['attribution_note'])}</p><p>Manuscript dated {display_date(s['manuscript_date'])}; version {esc(s['version'])} published {display_date(s['published_at'])}. The PDF and TeX source above belong to this version.</p>
{version_links(data,s)}
</article><aside class="side-panel" aria-label="Manuscript details and downloads"><div class="side-label">Manuscript downloads</div><a class="button" href="/{esc(s['proof_file'])}" download>Download PDF ↓</a><a class="button secondary" href="/{esc(s['source_file'])}" download>Download TeX source</a><a class="button secondary" href="/{esc(s['review_file'])}" download>AI review notes</a>{prompts_button}<button class="button secondary" data-print>Print this page</button><hr class="side-rule"><div class="side-label">AI generated · Version {esc(s['version'])}</div><p>Published before human review.</p><div class="side-label">Lean</div><p>{esc(s.get('lean_status','No Lean formalization is published for this version.'))}</p><a class="text-link" href="/#seminar">How the seminar works ↗</a></aside></div></main>'''
    return layout(s['title']+' — AI generated',s['abstract'],body,'/publications/'+s['slug']+'/')


def build(root=ROOT):
    data=json.loads((root/'content/catalog.json').read_text())
    validate_catalog(data,root)
    dist=root/'dist'
    # Rebuild the deployment tree from the explicit public inputs only.
    if dist.exists():
        shutil.rmtree(dist)
    dist.mkdir()
    (dist/'.nojekyll').touch()
    shutil.copytree(root/'assets',dist/'assets')
    (dist/'index.html').write_text(home(data))
    (dist/'catalog.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    downloads=dist/'downloads'; downloads.mkdir()
    urls=['/']
    for i,p in enumerate(data['problems']):
        folder=dist/'problems'/p['slug'];folder.mkdir(parents=True)
        (folder/'index.html').write_text(problem_page(data,p,data['problems'][(i+1)%len(data['problems'])]))
        source=source_for(data,p)
        md=f"# {problem_name(data,p)} — {p['title']}\n\n{p['statement_latex']}\n\n## Scope\n\n"+'\n'.join('- '+x for x in p['scope'])+f"\n\n## Source\n\n{entry_citation(source,p)}\n\n{entry_url(source,p)}\n\nSource checked {source['checked_at']}. Project status: {status_label(p)}.\n\nThis is a problem statement, not a solution.\n"
        (downloads/(p['slug']+'.md')).write_text(md)
        urls.append('/problems/'+p['slug']+'/')
    for s in data['solutions']+data.get('preprints',[]):
        folder=dist/'publications'/s['slug'];folder.mkdir(parents=True)
        page=preprint_page(data,s) if s in data.get('preprints',[]) else solution_page(data,s)
        (folder/'index.html').write_text(page)
        for key in ['proof_file','review_file','source_file']:
            if s.get(key):
                path=public_artifact(root,s[key]);dest=dist/s[key];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest)
        urls.append('/publications/'+s['slug']+'/')
    not_found='<main id="main" class="container"><section class="detail-header"><h1>Page not found</h1><p>Return to the <a href="/">seminar papers</a> or the <a href="/#problems">problem index</a>.</p></section></main>'
    (dist/'404.html').write_text(layout('Page not found','Return to Tech bros seminar.',not_found,'/404.html','<meta name="robots" content="noindex">'))
    (dist/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+ORIGIN+'/sitemap.xml\n')
    (dist/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+ORIGIN+path+'</loc><lastmod>'+data['updated_at']+'</lastmod></url>' for path in urls)+'</urlset>\n')
    print(json.dumps({'problems':len(data['problems']),'publications':len(data['solutions'])+len(data.get('preprints',[])),'output':str(dist)}))


if __name__=='__main__':
    build()
