#!/usr/bin/env python3
"""Add missing hreflang ar/ur to EN canonical name pages whose AR+UR translations exist."""
import os, re, json, sys

REPO = os.path.dirname(os.path.abspath(__file__))

def needs_fix(slug):
    p = os.path.join(REPO, 'names', slug, 'index.html')
    if not os.path.exists(p):
        return False
    ar = os.path.exists(os.path.join(REPO, 'ar', 'names', slug, 'index.html'))
    ur = os.path.exists(os.path.join(REPO, 'ur', 'names', slug, 'index.html'))
    if not (ar and ur):
        return False
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()
    has_ar = bool(re.search(r'<link[^>]*hreflang="ar"', c))
    has_ur = bool(re.search(r'<link[^>]*hreflang="ur"', c))
    return not (has_ar and has_ur)

def fix_one(slug):
    p = os.path.join(REPO, 'names', slug, 'index.html')
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()

    has_ar = bool(re.search(r'<link[^>]*hreflang="ar"', c))
    has_ur = bool(re.search(r'<link[^>]*hreflang="ur"', c))

    ar_link = '<link rel="alternate" hreflang="ar" href="https://asrnaam.com/ar/names/' + slug + '/"/>'
    ur_link = '<link rel="alternate" hreflang="ur" href="https://asrnaam.com/ur/names/' + slug + '/"/>'

    to_insert = []
    if not has_ar:
        to_insert.append(ar_link)
    if not has_ur:
        to_insert.append(ur_link)
    if not to_insert:
        return False

    m = re.search(r'(?P<indent>[ \t]*)<link[^>]*hreflang="en"[^>]*>\s*\n', c)
    if m:
        indent = m.group('indent')
        insertion = ''.join(indent + l + '\n' for l in to_insert)
        new_c = c[:m.end()] + insertion + c[m.end():]
    else:
        m2 = re.search(r'(?P<indent>[ \t]*)<link[^>]*rel="canonical"[^>]*>\s*\n', c)
        if not m2:
            return False
        indent = m2.group('indent')
        insertion = ''.join(indent + l + '\n' for l in to_insert)
        new_c = c[:m2.end()] + insertion + c[m2.end():]

    if new_c == c:
        return False
    with open(p, 'w', encoding='utf-8') as f:
        f.write(new_c)
    return True

def list_to_fix():
    with open(os.path.join(REPO, 'names', 'names-index.json')) as f:
        data = json.load(f)
    slugs = [e['s'] for e in data]
    return [s for s in slugs if needs_fix(s)]

if __name__ == '__main__':
    todo = list_to_fix()
    print('slugs needing fix:', len(todo))
    print('first 10:', todo[:10])
    if len(sys.argv) > 1 and sys.argv[1] == '--apply':
        n = 0
        for s in todo:
            if fix_one(s):
                n += 1
        print('fixed', n)
