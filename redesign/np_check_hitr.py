"""Round-trip check for migrated Hindi and Turkish name pages (redesign/np_build_hitr.py).

Compares the page in the working tree with the same page at <base-ref> and fails on anything that is not layout:
  head identical apart from the version tag; html lang/dir, canonical and hreflang untouched; every JSON-LD block identical;
  one H1 with the same text; the same FAQ questions and answers; no text lost; no text added except the interface labels
  from redesign/locale/<lang>.json and the lucky-number working (both reported); no long text duplicated;
  no internal link lost; each data-asr-field kept once; site header, footer and script tags untouched;
  every Arabic-script and Devanagari word of the old page still present, letter for letter (INC-01).

usage: python3 redesign/np_check_hitr.py <base-ref> <hi|tr> slug [slug ...]   (run from the repo root)"""
import re, sys, json, subprocess, html as H
from collections import Counter

AR = r'[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]+'
DEV = r'[ऀ-ॿ]+'


def norm_ver(s):
    return re.sub(r'(asr-(?:redesign|np)\.(?:css|js)\?v=)[0-9a-z]+', r'\1V', s)


def texts(body):
    """text nodes of the body, in order (scripts and styles left out)"""
    b = re.sub(r'<script.*?</script>|<style.*?</style>|<!--.*?-->', ' ', body, flags=re.S)
    out = []
    for t in re.split(r'<[^>]+>', b):
        t = re.sub(r'\s+', ' ', H.unescape(t)).strip()
        if t:
            out.append(t)
    return out


def split_page(h):
    i = h.index('</head>')
    return h[:i], h[i:]


def label_values(L):
    vals = set()
    for k in ('kicker', 'jump', 'aria', 'js'):
        vals |= set(L.get(k, {}).values())
    return vals


def check_pair(old, new, loc):
    L = json.load(open(f'redesign/locale/{loc}.json', encoding='utf8'))
    fails, notes = [], []
    oh, ob = split_page(old)
    nh, nb = split_page(new)
    if norm_ver(oh) != norm_ver(nh):
        fails.append('head differs beyond the version tag')
    for name, pat in (('html tag', r'<html[^>]*>'), ('canonical', r'<link rel="canonical"[^>]*>'), ('hreflang', r'<link rel="alternate"[^>]*>'),
                      ('title', r'<title>.*?</title>'), ('meta description', r'<meta name="description"[^>]*>')):
        if re.findall(pat, old, re.S) != re.findall(pat, new, re.S):
            fails.append(name + ' changed')
    if re.findall(r'<script type="application/ld\+json">.*?</script>', old, re.S) != re.findall(r'<script type="application/ld\+json">.*?</script>', new, re.S):
        fails.append('JSON-LD changed')
    o1, n1 = re.findall(r'<h1[^>]*>(.*?)</h1>', old, re.S), re.findall(r'<h1[^>]*>(.*?)</h1>', new, re.S)
    if len(n1) != 1 or o1 != n1:
        fails.append('H1 changed')
    faq = lambda s: re.findall(r'<details>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>', s, re.S)
    if faq(ob) != faq(nb) or ob.count('<details') != nb.count('<details'):
        fails.append(f'FAQ changed ({ob.count("<details")} -> {nb.count("<details")})')
    # text nodes
    ot, nt = Counter(texts(ob)), Counter(texts(nb))
    lost = ot - nt
    if lost:
        fails.append('text lost: ' + ' | '.join(list(lost)[:4]))
    added = nt - ot
    allowed = set()
    for i in range(1, 9):
        for k in L['kicker'].values():
            allowed.add(f'{i:02d} · {k}')
    allowed |= set(L['jump'].values())
    grid_letters = set(re.findall(r'<span class="hi-letter-ar"[^>]*>([^<]+)</span>', nb))
    work = re.search(r'<div class="work"[^>]*>(.*?)</div>\s*</div>', nb, re.S)
    work_texts = set(texts(work.group(0))) if work else set()
    labels_added, other_added = [], []
    for t, c in added.items():
        if t in allowed:
            labels_added.append(t)
        elif t in work_texts and (t in grid_letters or re.fullmatch(r'[\d+=→ ]+', t)):
            pass
        else:
            other_added.append(t)
    if other_added:
        fails.append('text added that is not a label: ' + ' | '.join(other_added[:4]))
    if labels_added:
        notes.append('labels added: ' + ' | '.join(sorted(labels_added)))
    if work:
        notes.append('lucky working: ' + re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', ' ', work.group(0)))).strip())
    dup = [t for t, c in nt.items() if len(t) > 60 and c > ot.get(t, 0)]
    if dup:
        fails.append('text duplicated: ' + dup[0][:60])
    # links, fields, scripts, header, footer
    hrefs = lambda s: Counter(re.findall(r'<a\b[^>]*\bhref="([^"]+)"', s))
    lost_links = hrefs(ob) - hrefs(nb)
    if lost_links:
        fails.append('links lost: ' + ', '.join(list(lost_links)[:4]))
    new_links = [k for k in (hrefs(nb) - hrefs(ob)) if not k.startswith('#')]
    if new_links:
        fails.append('links added: ' + ', '.join(new_links[:4]))
    of, nf = Counter(re.findall(r'data-asr-field="([^"]+)"', old)), Counter(re.findall(r'data-asr-field="([^"]+)"', new))
    if of != nf or any(v != 1 for v in nf.values()):
        fails.append(f'data-asr-field changed: {dict(of)} -> {dict(nf)}')
    if re.findall(r'<script\b[^>]*>', norm_ver(old)) != re.findall(r'<script\b[^>]*>', norm_ver(new)):
        fails.append('script tags changed')
    for name, pat in (('ad anchors', r'class="[^"]*\basr-ad\b|adsbygoogle|data-ad-'), ):
        if len(re.findall(pat, old)) != len(re.findall(pat, new)):
            fails.append(name + ' count changed')
    part = lambda s, a, b: s[s.index(a):s.index(b) + len(b)] if a in s and b in s else None
    if part(ob, '<nav class="asr-nav"', '</nav>') != part(nb, '<nav class="asr-nav"', '</nav>'):
        fails.append('site header changed')
    if norm_ver(part(ob, '<footer', '</html>') or '') != norm_ver(part(nb, '<footer', '</html>') or ''):
        fails.append('footer or closing scripts changed')
    # INC-01: every Arabic-script and Devanagari run of the old page is still there; additions are labels or lucky chips only
    for name, pat in (('Arabic-script', AR), ('Devanagari', DEV)):
        o, n = Counter(re.findall(pat, old)), Counter(re.findall(pat, new))
        if o - n:
            fails.append(f'{name} text lost or altered: ' + ' '.join(list(o - n)[:6]))
        extra = n - o
        label_runs = Counter()
        for v in label_values(L) | allowed:
            label_runs.update(re.findall(pat, v))
        # the page's own name is copied once, letter for letter, into data-l-name (read by the save and play buttons)
        own = re.search(r'<div class="dev-name">([^<]+)</div>', old)
        dn = re.search(r'data-l-name="([^"]*)"', new)
        own_runs = Counter(re.findall(pat, own.group(1))) if own and dn and H.unescape(dn.group(1)) == H.unescape(own.group(1)) else Counter()
        bad = [k for k, c in extra.items() if k not in label_runs and not (name == 'Arabic-script' and k in grid_letters) and c > own_runs.get(k, 0)]
        if bad:
            fails.append(f'{name} text added outside labels: ' + ' '.join(bad[:6]))
    # attribute labels replaced
    oa, na = Counter(re.findall(r'aria-label="([^"]*)"', ob)), Counter(re.findall(r'aria-label="([^"]*)"', nb))
    if oa != na:
        notes.append('aria-labels: removed ' + str(list((oa - na).keys())) + ' added ' + str(list((na - oa).keys())))
    for k in (na - oa):
        if k not in L['aria'].values():
            fails.append('aria-label added that is not in the label file: ' + k)
    dn = re.search(r'data-l-name="([^"]*)"', new)
    own = re.search(r'<div class="dev-name">([^<]+)</div>', old)
    if dn and (not own or H.unescape(dn.group(1)) != H.unescape(own.group(1))):
        fails.append('data-l-name is not the page name')
    # listed repairs: the old article did not balance its <div> tags (see repair_divs in the builder); the new one must
    art = lambda s: s[s.index('<article'):s.index('</article>')] if '<article' in s and '</article>' in s else ''
    bal = lambda s: len(re.findall(r'<div\b', s)) - s.count('</div>')
    if bal(art(old)):
        notes.append('fixed markup: the old article ' + ('never closed its language bar' if bal(art(old)) > 0 else 'had a stray closing tag after the letter grid') + '; the new page balances')
    if bal(art(new)):
        fails.append('the new article does not balance its div tags')
    st = len(re.findall(r' style="', ob)) - len(re.findall(r' style="', nb))
    if st:
        notes.append(f'inline styles dropped: {st}')
    return fails, notes



def _nodates(s):
    """The modified date moves when a page is deployed; it is not part of the round trip."""
    import re as _re
    s = _re.sub(r'(article:modified_time" content=")[^"]*', r'\1DATE', s)
    return _re.sub(r'("dateModified":\s*")[^"]*', r'\1DATE', s)

def check(base, loc, slug):
    p = f'{loc}/names/{slug}/index.html'
    old = subprocess.run(['git', 'show', f'{base}:{p}'], capture_output=True, text=True, encoding='utf8')
    if old.returncode:
        return ['no such page at ' + base], []
    return check_pair(_nodates(old.stdout), _nodates(open(p, encoding='utf8').read()), loc)


if __name__ == '__main__':
    if len(sys.argv) < 4 or sys.argv[2] not in ('hi', 'tr'):
        sys.exit('usage: python3 redesign/np_check_hitr.py <base-ref> <hi|tr> slug [slug ...]')
    base, loc = sys.argv[1], sys.argv[2]
    bad = 0
    for slug in sys.argv[3:]:
        fails, notes = check(base, loc, slug)
        print(loc, slug, 'FAIL' if fails else 'PASS')
        for f in fails:
            print('   FAIL', f)
        for n in notes:
            print('   note', n)
        bad += bool(fails)
    sys.exit(1 if bad else 0)
