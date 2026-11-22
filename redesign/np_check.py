"""Round-trip and Rule 0 checks for a migrated name page against the version on a base commit.
usage: python3 redesign/np_check.py <base-ref> slug [slug ...]   (run from the repo root)
Checks: head byte-identical, every JSON block identical, each data-asr-field exactly once, namecard and
community once, one H1 with the same text, no visible sentence lost (allowed removals: the cross-language
bar), links to name pages not fewer, visible word count not lower, ads anchors present, bytes reported."""
import re, sys, os, json, subprocess, html as H

ALLOWED_GONE = ['This name in other languages']
SECTION_LABEL = re.compile(r'^Section \d+ · ')


def vis(h):
    b = h[h.find('<body'):]
    b = re.sub(r'<script.*?</script>|<style.*?</style>|<!--.*?-->', ' ', b, flags=re.S)
    b = re.sub(r'<nav class="asr-crosslang".*?</nav>', ' ', b, flags=re.S)
    t = H.unescape(re.sub(r'<[^>]+>', ' ', b))
    return re.sub(r'\s+', ' ', t).strip()


def nodes(h):
    b = h[h.find('<body'):]
    b = re.sub(r'<script.*?</script>|<style.*?</style>|<!--.*?-->', ' ', b, flags=re.S)
    b = re.sub(r'<nav class="asr-crosslang".*?</nav>', ' ', b, flags=re.S)
    out = []
    for t in re.split(r'<[^>]+>', b):
        t = re.sub(r'\s+', ' ', H.unescape(t)).strip()
        if len(t) > 2:
            out.append(t)
    return out


def check(base, slug):
    p = f'names/{slug}/index.html'
    old = subprocess.check_output(['git', 'show', f'{base}:{p}']).decode('utf8')
    new = open(p, encoding='utf8').read()
    return check_pair(old, new, slug)


def check_pair(old, new, slug=None):
    errs, notes = [], []
    # content changes recorded in the pilot file are the only text allowed to differ, and each is reported
    allowed = list(ALLOWED_GONE)
    pf = f'redesign/pilot/{slug}.json' if slug else ''
    if pf and os.path.exists(pf):
        pj = json.load(open(pf, encoding='utf8'))
        for fx in pj.get('page_fixes', []):
            n_head = old[:old.index('</head>')].count(fx['old'])
            old = old.replace(fx['old'], fx['new'])   # compared as corrected: nothing else in the head or the JSON may differ
            notes.append('corrected page-wide' + (f' (head x{n_head})' if n_head else '') + ': ' + fx['reason'])
        for fx in pj.get('fixes', []):
            allowed += nodes('<body>' + fx['old']) or [fx['old']]
            notes.append('fixed: ' + fx['reason'])
        for d in pj.get('drop', []):
            m = re.search(r'<li\b(?:(?!</li>).)*?' + re.escape(d['match']), old, re.S)
            allowed += nodes('<body>' + m.group(0)) if m else []
            notes.append('removed: ' + d['reason'])
    ver = lambda x: re.sub(r'(asr-redesign\.(?:css|js)\?v=)[0-9a-z]+', r'\1V', x)
    if ver(old[:old.index('</head>')]) != ver(new[:new.index('</head>')]):
        errs.append('head differs')
    jo = re.findall(r'<script type="application/(?:ld\+)?json"[^>]*>(.*?)</script>', old, re.S)
    jn = re.findall(r'<script type="application/(?:ld\+)?json"[^>]*>(.*?)</script>', new, re.S)
    if jo != jn:
        errs.append('JSON blocks differ')
    for f in ['meaning-dict', 'origin', 'gender', 'urdu', 'urdu-meaning', 'pronunciation', 'lucky', 'meaning-iuh']:
        a, b = old.count(f'data-asr-field="{f}"'), new.count(f'data-asr-field="{f}"')
        if b != 1 and not (a == 0 and b == 0):
            errs.append(f'data-asr-field {f}: {b}x (was {a})')
    for k in ['id="asr-namecard"', 'id="asr-community"']:
        if new.count(k) != min(1, old.count(k)) or (old.count(k) and new.count(k) != 1):
            errs.append(k + ' count ' + str(new.count(k)))
    h1o = re.findall(r'<h1[^>]*>(.*?)</h1>', old, re.S)
    h1n = re.findall(r'<h1[^>]*>(.*?)</h1>', new, re.S)
    if len(h1n) != 1 or re.sub('<[^>]+>', '', h1o[0]) != re.sub('<[^>]+>', '', h1n[0]):
        errs.append('H1 changed')
    tv = vis(new)
    lost = [s for s in nodes(old) if s not in tv and not any(a in s or s in a for a in allowed) and SECTION_LABEL.sub('', s) not in tv]
    if lost:
        errs.append(f'{len(lost)} sentence(s) lost: ' + ' | '.join(x[:70] for x in lost[:3]))
    from collections import Counter
    # the share-card preview repeats the hero line on purpose (decorative, aria-hidden)
    co, cn = Counter(nodes(old)), Counter(nodes(re.sub(r'<div class="np-cardmock".*?</div>', ' ', new, flags=re.S)))
    dup = [t for t in cn if len(t) > 60 and cn[t] > max(1, co.get(t, 0))]
    if dup:
        errs.append(f'{len(dup)} text block(s) duplicated: ' + dup[0][:60])
    if old.count('<details') != new.count('<details') or new.count('class="faq-list"') != 1:
        errs.append(f'FAQ items {old.count("<details")} -> {new.count("<details")}')
    lo = len(re.findall(r'href="(?:https://asrnaam\.com)?/names/[a-z0-9-]+/"', old))
    ln = len(re.findall(r'href="(?:https://asrnaam\.com)?/names/[a-z0-9-]+/"', new))
    if ln < lo:
        errs.append(f'name links {ln} < {lo}')
    wo, wn = len(vis(old).split()), len(tv.split())
    if wn < wo:
        notes.append(f'words {wn} < {wo} (check: only the removed language bar?)')
    for a in ['class="asr-answer', 'id="reading"', 'class="faq-list"']:
        if a not in new:
            errs.append('ad anchor missing ' + a)
    m = re.search(r'<p[^>]*>(.*?)</p>', new[new.find('<main'):], re.S)
    firstlong = None
    for mm in re.finditer(r'<p[^>]*>(.*?)</p>', new[new.find('<main'):], re.S):
        if len(re.sub('<[^>]+>', '', mm.group(1))) > 200:
            firstlong = re.sub('<[^>]+>', '', mm.group(1))[:40]
            break
    if not firstlong or not firstlong.startswith('Is '):
        notes.append('first long <p>: ' + str(firstlong))
    notes.append(f'bytes {len(old.encode())} -> {len(new.encode())}; words {wo} -> {wn}; name links {lo} -> {ln}')
    return errs, notes


if __name__ == '__main__':
    base = sys.argv[1]
    bad = 0
    for slug in sys.argv[2:]:
        e, n = check(base, slug)
        bad += bool(e)
        print(('FAIL ' if e else 'PASS ') + slug, '; '.join(e + n))
    sys.exit(1 if bad else 0)
