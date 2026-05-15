#!/usr/bin/env python3
"""Enrichment applier. Reads CURATED dict, applies to HTML markers, updates CSV."""
import os, re, csv, sys, json

REPO = os.path.dirname(os.path.abspath(__file__))
NAMES = os.path.join(REPO, 'names')
TRACKER = os.path.join(REPO, 'quality-tracker.csv')

def apply_marker(html, marker_name, inner_html):
    """Replace content between <!-- MARKER:START --> and <!-- MARKER:END -->"""
    start = f'<!-- {marker_name}:START -->'
    end = f'<!-- {marker_name}:END -->'
    pat = re.compile(re.escape(start) + r'.*?' + re.escape(end), re.DOTALL)
    new_block = start + '\n' + inner_html + '\n' + end
    if not pat.search(html):
        return html, False
    return pat.sub(new_block, html), True


def render_root(slug, english, root_text):
    return f'<p class="section-label">Arabic Root Meaning</p><h2>Root of <em>{english}</em></h2><div class="prose"><p>{root_text}</p></div>'

def render_iuh(slug, english, iuh_text):
    return f'<p class="section-label">Ilm ul Haroof Meaning</p><h2>What <em>{english}</em> reveals</h2><div class="prose"><p>{iuh_text}</p></div>'

def render_bearers(english, bearers):
    """bearers: list of dicts: {name, meta, desc}"""
    if not bearers:
        return f' <p class="section-label" style="margin:3rem 0 .4rem;">Famous Bearers</p>\n <p class="related-intro">No widely-attested historical or contemporary figure carries this exact spelling of <em>{english}</em>. The name\'s resonance comes from its meaning and its letters — not from a single famous bearer.</p>'
    items = ''
    for b in bearers:
        meta = f' <span class="bearer-meta">({b["meta"]})</span>' if b.get('meta') else ''
        items += f'  <li><strong>{b["name"]}</strong>{meta} — {b["desc"]}</li>\n'
    return (
        f' <p class="section-label" style="margin:3rem 0 .4rem;">Famous Bearers</p>\n'
        f' <p class="related-intro">Notable people who have carried the name <em>{english}</em>.</p>\n'
        f' <ul class="bearers-list">\n{items} </ul>'
    )

def apply_to_page(slug, data, tracker_row, modified_count):
    """Apply data dict {root, iuh, bearers} to the slug's HTML page."""
    p = os.path.join(NAMES, slug, 'index.html')
    if not os.path.isfile(p):
        return False, 'no_file'
    with open(p, encoding='utf-8') as f:
        html = f.read()
    english = tracker_row.get('english', slug.replace('-',' ').title())
    changed = False
    if 'root' in data and data['root']:
        new_html, ok = apply_marker(html, 'MEAN-ROOT', render_root(slug, english, data['root']))
        if ok and new_html != html:
            html = new_html; changed = True
    if 'iuh' in data and data['iuh']:
        new_html, ok = apply_marker(html, 'MEAN-IUH', render_iuh(slug, english, data['iuh']))
        if ok and new_html != html:
            html = new_html; changed = True
    if 'bearers' in data:
        new_html, ok = apply_marker(html, 'BEARERS', render_bearers(english, data['bearers']))
        if ok and new_html != html:
            html = new_html; changed = True
    if changed:
        with open(p, 'w', encoding='utf-8') as f:
            f.write(html)
    return changed, None

def main(curated_path):
    with open(curated_path) as f:
        curated = json.load(f)
    # Load tracker
    with open(TRACKER, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    by_slug = {r['slug']: r for r in rows}

    applied_root = 0; applied_iuh = 0; applied_bearer = 0
    for slug, data in curated.items():
        row = by_slug.get(slug)
        if not row: continue
        ok, err = apply_to_page(slug, data, row, 0)
        if not ok: continue
        if data.get('root'):
            row['meaning_root'] = data['root']
            applied_root += 1
        if data.get('iuh'):
            row['meaning_iuh'] = data['iuh']
            applied_iuh += 1
        if data.get('bearers'):
            row['famous_bearers_count'] = str(len(data['bearers']))
            row['bearers_count_visible'] = str(len(data['bearers']))
            applied_bearer += 1
    # Write tracker
    with open(TRACKER, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f'roots={applied_root} iuh={applied_iuh} bearers={applied_bearer}')

if __name__ == '__main__':
    main(sys.argv[1])
