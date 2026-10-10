"""Render homepage publications from the site's BibTeX and editorial notes.

Run: python3 bin/render_research.py
No external packages or network access required.
"""
import argparse
import html
import json
from pathlib import Path
import re

REPO = Path(__file__).resolve().parents[1]
BASEURL = ''
TOPICS = {
    'post-training': 'Post-training', 'distillation': 'Distillation',
    'alignment': 'Alignment', 'personalization': 'Personalization',
    'evaluation': 'Evaluation',
}


def braced(text, start):
    """Read a balanced BibTeX brace value, including nested braces."""
    depth = 1
    i = start + 1
    while i < len(text):
        if text[i] == '\\':
            i += 2
            continue
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if not depth:
                return text[start + 1:i], i + 1
        i += 1
    raise ValueError('Unclosed BibTeX brace')


def read_bibliography(path):
    """Read article records; reject unsupported field syntax explicitly."""
    text = path.read_text()
    records = []
    for match in re.finditer(r'@article\s*\{', text, re.I):
        body, _ = braced(text, match.end() - 1)
        key, body = body.split(',', 1)
        record = {'key': key.strip()}
        position = 0
        while position < len(body):
            field = re.match(r'\s*,?\s*(\w+)\s*=\s*', body[position:])
            if not field:
                if body[position:].strip(' \n\t\r,'):
                    raise ValueError(f'Invalid field in {key}')
                break
            position += field.end()
            if body[position] != '{':
                raise ValueError(f'Use braced field values in {key}')
            value, position = braced(body, position)
            record[field[1].lower()] = value.strip()
        records.append(record)
    keys = [record['key'] for record in records]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate bibliography keys')
    return sorted(records, key=lambda paper: int(paper['year']), reverse=True)


def escape(value):
    return html.escape(str(value), quote=True)


def authors(value):
    names = []
    for name in value.split(' and '):
        if ',' in name:
            last, first = name.split(',', 1)
            star = '*' if '*' in last else ''
            name = f'{first.strip()} {last.replace("*", "").strip()}{star}'
        name = ' '.join(name.split())
        names.append(f'<strong>{escape(name)}</strong>' if name.rstrip('*') == 'Noah Lee' else escape(name))
    return ', '.join(names)


def paper_url(paper):
    return 'https://arxiv.org/abs/' + paper['arxiv'].removeprefix('arXiv:')


def featured(paper, note):
    title, url = escape(paper['title']), escape(paper_url(paper))
    preview = paper['preview']
    if Path(preview).name != preview:
        raise ValueError('Preview must be a filename')
    if not (REPO / 'assets/img/publication_preview' / preview).is_file():
        raise ValueError(f'Missing preview image: {preview}')
    image = escape(BASEURL + '/assets/img/publication_preview/' + preview)
    alt = escape(note['image_alt'])
    tags = escape(' · '.join(TOPICS[t] for t in note['topics']))
    code = f'<a href="{escape(paper["code"])}">Code ↗</a>' if paper.get('code') else ''
    return f'''<article class="paper">
  <a class="paper-image" href="{image}" data-figure data-paper="{url}" data-title="{title}" aria-label="Enlarge figure: {title}"><img src="{image}" alt="{alt}" loading="lazy"><span class="figure-hint" aria-hidden="true">Enlarge ↗</span></a>
  <div class="paper-copy">
    <p class="paper-meta">{escape(paper['journal'])} · {escape(paper['year'])} <span>{tags}</span></p>
    <h3><a href="{url}">{title}</a></h3>
    <p class="takeaway">{escape(note['takeaway'])}</p>
    <p class="authors">{authors(paper['author'])}</p>
    <div class="paper-links"><a href="{url}">Paper ↗</a>{code}</div>
    <details class="paper-summary"><summary>Quick summary<span class="sr-only">: {title}</span></summary>
      <div><p><strong>{escape(note['question'])}</strong></p><p>{escape(note['summary'])}</p><a href="{url}">Read the abstract ↗</a></div>
    </details>
  </div>
</article>'''


def render_publications():
    papers = read_bibliography(REPO / '_bibliography/papers.bib')
    notes = json.loads((REPO / '_data/research_publications.json').read_text())
    missing = set(notes) - {paper['key'] for paper in papers}
    if missing:
        raise ValueError(f'Notes reference missing publications: {missing}')
    chosen = sorted(
        (paper for paper in papers if 'featured_order' in notes.get(paper['key'], {})),
        key=lambda paper: notes[paper['key']]['featured_order'],
    )
    cards = '\n'.join(featured(paper, notes[paper['key']]) for paper in chosen)
    archive = []
    used_topics = set()
    for paper in papers:
        topics = notes.get(paper['key'], {}).get('topics', [])
        unknown = set(topics) - set(TOPICS)
        if unknown:
            raise ValueError(f'Unknown topics: {unknown}')
        used_topics.update(topics)
        archive.append(f'<a data-topics="{escape(" ".join(topics))}" href="{escape(paper_url(paper))}"><span class="year">{escape(paper["year"])}</span><span>{escape(paper["title"])}</span><span class="venue">{escape(paper["journal"])}</span></a>')
    buttons = ''.join(
        f'<button type="button" data-topic="{key}" aria-pressed="{str(key == "all").lower()}" aria-controls="archive-list">{label}</button>'
        for key, label in {'all': 'All topics', **{k: v for k, v in TOPICS.items() if k in used_topics}}.items()
    )
    years = [int(paper['year']) for paper in papers]
    count_label = f"{len(papers)} {'paper' if len(papers) == 1 else 'papers'}"
    publications = f'''<div class="papers">{cards}</div>
<details id="all-publications"><summary>Browse all publications <span>{count_label} · {min(years)}–{max(years)}</span></summary>
  <div class="archive-controls"><div class="topic-filters" role="group" aria-label="Filter publications by research topic" hidden>{buttons}</div><p id="filter-status" role="status" aria-live="polite" aria-atomic="true">Showing all {count_label}.</p></div>
  <div class="archive" id="archive-list">{''.join(archive)}</div>
</details>'''
    return publications


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Render homepage publications from BibTeX.')
    parser.add_argument('--source', type=Path, default=REPO)
    parser.add_argument('--baseurl', default='')
    args = parser.parse_args()
    REPO = args.source.resolve()
    BASEURL = '/' + args.baseurl.strip('/') if args.baseurl.strip('/') else ''
    print(render_publications())
