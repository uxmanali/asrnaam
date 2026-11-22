"""Round-trip check for a migrated translated name page (Urdu, Arabic) against the version on a base commit.
usage: python3 redesign/np_check_loc.py <base-ref> <locale> slug [slug ...] [-v]   (run from the repo root)

Fails unless all of this holds:
  - everything up to </head> identical (html lang and dir, title, canonical, hreflang, JSON-LD), apart from the
    version tag of asr-redesign.css and the page_fixes listed in the content file;
  - every JSON block identical; one H1, same markup; the name in the hero identical, letter for letter;
  - the page outside the article identical, apart from the version tag, the stylesheet link and the breadcrumb row wrapper;
  - no text lost, apart from text a listed fix or drop removes and the old section numbers;
  - no text block repeated; FAQ items the same, in the same order; no internal link lost;
  - every piece of text that is new on the page is accounted for: an interface label from redesign/locale/<locale>.json,
    a string from the content file redesign/pilot/<locale>/<slug>.json, or the abjad sum worked from the letters.
    Anything else is an error, so nothing rides in unlisted.
Reports every content-file change by name, the labels that are new wording, and Latin-script text left on the page."""
import re, sys, os, json, subprocess, html as H
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from np_build import ABJAD

VERBOSE = '-v' in sys.argv


def strip(b):
    return re.sub(r'<script.*?</script>|<style.*?</style>|<!--.*?-->', ' ', b, flags=re.S)


def nodes(h):
    b = strip(h[h.find('<body'):])
    out = []
    for t in re.split(r'<[^>]+>', b):
        t = re.sub(r'\s+', ' ', H.unescape(t)).strip()
        if len(t) > 1:
            out.append(t)
    return out


def vis(h):
    b = strip(h[h.find('<body'):])
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', ' ', b))).strip()


def tx(x):
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', ' ', x))).strip()


def ver(x):
    return re.sub(r'(asr-redesign\.(?:css|js)\?v=)[0-9a-z]+', r'\1V', x)


def check(base, loc, slug):
    p = f'{loc}/names/{slug}/index.html'
    old = subprocess.check_output(['git', 'show', f'{base}:{p}']).decode('utf8')
    new = open(p, encoding='utf8').read()
    L = json.load(open(f'redesign/locale/{loc}.json', encoding='utf8'))
    pf = f'redesign/pilot/{loc}/{slug}.json'
    pilot = json.load(open(pf, encoding='utf8')) if os.path.exists(pf) else {}
    return check_pair(old, new, L, pilot)


def check_pair(old, new, L, pilot):
    errs, notes = [], []
    T = L['labels']
    gone_ok = []            # text a listed change is allowed to remove
    added_ok = set()        # text a listed change or a label is allowed to add
    if 'asr-np' not in new:
        return ['page is not migrated'], notes
    # ---- content-file changes, each reported by name
    for fx in pilot.get('page_fixes', []):
        n_head = old[:old.index('</head>')].count(fx['old'])
        if fx['old'] not in old:
            errs.append('page fix not on the old page: ' + fx['old'][:40])
        old = old.replace(fx['old'], fx['new'])     # compared as corrected: nothing else in the head or the JSON may differ
        notes.append(f'CONTENT page-wide fix (head x{n_head}): {tx(fx["old"])[:50]} -> {tx(fx["new"])[:50]} [{fx.get("reason", "no reason given")}]')
    for fx in pilot.get('fixes', []):
        gone_ok += nodes('<body>' + fx['old'])
        added_ok.update(nodes('<body>' + fx['new']))
        a, b = tx(fx['old']), tx(fx['new'])
        notes.append('CONTENT fix: ' + (f'removes "{a[:70]}"' if not b else f'"{a[:50]}" -> "{b[:50]}"') + f' [{fx.get("reason", "no reason given")}]')
    for d in pilot.get('drop', []):
        m = re.search(r'<li\b(?:(?!</li>).)*?' + re.escape(d['match']) + r'(?:(?!</li>).)*</li>', old, re.S)
        gone_ok += nodes('<body>' + m.group(0)) if m else []
        notes.append(f'CONTENT removed: {d["match"][:60]} [{d.get("reason", "no reason given")}]')
    people = list(pilot.get('add', []))
    for gp in pilot.get('groups', []):
        added_ok.add(gp['label'])
        notes.append(f'CONTENT bearer group heading: {gp["label"]}')
        people += [pp for pp in gp['people'] if not (isinstance(pp, dict) and 'existing' in pp)]
    for pp in people:
        if isinstance(pp, (list, tuple)):
            pp = dict(name=pp[0], meta=pp[1], note=pp[2])
        added_ok.update([pp['name'], pp.get('note', ''), '·'] + [x.strip() for x in pp.get('meta', '').split('·')])
        notes.append(f'CONTENT bearer added: {pp["name"]} | {pp.get("meta", "")} | {pp.get("note", "")}')
        if pp['name'] not in new:
            errs.append('content-file bearer not on the page: ' + pp['name'])
    if pilot.get('dyk'):
        added_ok.update([pilot['dyk'], T['dyk'], (T['source'] + ' ' + pilot.get('dyk_source', '')).strip(), T['source']])
        notes.append(f'CONTENT did-you-know: {pilot["dyk"]} | {T["source"]} {pilot.get("dyk_source", "")}')
        if pilot['dyk'] not in H.unescape(new):
            errs.append('content-file did-you-know not on the page')

    # ---- head, JSON, H1, the name
    if ver(old[:old.index('</head>')]) != ver(new[:new.index('</head>')]):
        errs.append('head differs')
    jo = re.findall(r'<script type="application/(?:ld\+)?json"[^>]*>(.*?)</script>', old, re.S)
    jn = re.findall(r'<script type="application/(?:ld\+)?json"[^>]*>(.*?)</script>', new, re.S)
    if jo != jn:
        errs.append('JSON blocks differ')
    for pat, what in ((r'<html[^>]*>', 'html lang/dir'), (r'<link rel="canonical"[^>]*>', 'canonical'), (r'<link rel="alternate"[^>]*>', 'hreflang')):
        if re.findall(pat, old) != re.findall(pat, new):
            errs.append(what + ' changed')
    h1o, h1n = re.findall(r'<h1[^>]*>(.*?)</h1>', old, re.S), re.findall(r'<h1[^>]*>(.*?)</h1>', new, re.S)
    if len(h1n) != 1 or h1o != h1n:
        errs.append('H1 changed')
    no = re.search(r'<div class="arabic-name"[^>]*>(.*?)</div>', old, re.S)
    nn = re.search(r'<div class="asr-name-hero-arabic"[^>]*>(.*?)</div>', new, re.S)
    if not (no and nn) or no.group(1) != nn.group(1):
        errs.append('the name in the hero changed')
    name = tx(nn.group(1)) if nn else ''

    # ---- outside the article
    def outside(h):
        b = h[h.index('</head>'):]
        a0 = re.search(r'<article[^>]*>', b)
        a1 = b.find('</article>')
        if a1 < 0:
            a1 = b.index('</main>')
        pre, post = b[:a0.start()], b[a1:].replace('</article>', '', 1)
        pre = re.sub(r'<link rel="preload" href="/fonts/[^"]+" as="font" type="font/woff2" crossorigin>', '', pre)
        pre = re.sub(r'<link rel="stylesheet" href="/asr-np(?:-rtl|-hitr)?\.css\?v=[0-9a-z]+">', '', pre)
        pre = re.sub(r'<div class="np-mode".*?</div>', '', pre, flags=re.S)
        pre = pre.replace('<div class="np-crumbrow">', '')
        pre = re.sub(r'(<div class="breadcrumb".*?</div>)</div>', r'\1', pre, flags=re.S) if 'np-crumbrow' in h else pre
        return ver(re.sub(r'\s+', ' ', pre)).strip(), ver(re.sub(r'\s+', ' ', post)).strip()
    if outside(old) != outside(new):
        a, b = outside(old), outside(new)
        k = 0 if a[0] != b[0] else 1
        i = next((i for i, (x, y) in enumerate(zip(a[k], b[k])) if x != y), min(len(a[k]), len(b[k])))
        errs.append(f'page outside the article differs ({"before" if k == 0 else "after"} it) near: {b[k][max(0, i - 40):i + 60]}')

    # ---- text lost
    tv = vis(new)
    knum = re.compile(L['kicker_number'])
    lost = []
    for s in nodes(old):
        if s in tv or knum.sub('', s) in tv:
            continue
        if any(s in g or g in s for g in gone_ok):
            continue
        lost.append(s)
    if lost:
        errs.append(f'{len(lost)} text block(s) lost: ' + ' | '.join(x[:70] for x in lost[:3]))
    # ---- text repeated
    co, cn = Counter(nodes(old)), Counter(nodes(new))
    dup = [t for t in cn if len(t) > 60 and cn[t] > max(1, co.get(t, 0))]
    if dup:
        errs.append(f'{len(dup)} text block(s) repeated: ' + dup[0][:60])
    # ---- FAQ, links, ad anchors
    so = [tx(x) for x in re.findall(r'<summary[^>]*>(.*?)</summary>', old, re.S)]
    sn = [tx(x) for x in re.findall(r'<summary[^>]*>(.*?)</summary>', new, re.S)]
    if so != sn or old.count('<details') != new.count('<details'):
        errs.append(f'FAQ items changed ({len(so)} -> {len(sn)})')
    if new.count('class="faq-list"') != 1:
        errs.append('faq-list count is not 1')
    lo = Counter(re.findall(r'href="(/[^"]*)"', old[old.find('<body'):]))
    ln = Counter(re.findall(r'href="(/[^"]*)"', new[new.find('<body'):]))
    lo.pop('/asr-np.css', None)
    miss = [u for u in lo if u not in ln and not any(u in fx['old'] for fx in pilot.get('fixes', []))]
    if miss:
        errs.append('internal link lost: ' + ', '.join(miss[:4]))
    for a in ['class="asr-answer', 'id="reading"', 'class="faq-list"']:
        if a not in new:
            errs.append('ad anchor missing ' + a)
    if new.count('<article') != 1 or new.count('</article>') != 1:
        errs.append('article tags unbalanced')
    if old.count('</article>') == 0:
        notes.append('fixed markup: the old page never closed <article>; the new page does')

    # ---- everything new must be accounted for
    label_texts = {v for v in T.values() if '{name}' not in v}
    templates = [v.split('{name}') for v in T.values() if '{name}' in v]   # a label with the name in it: the name must be one the old page shows
    old_set = set(nodes(old))
    old_vis = vis(old)
    digs = '0-9٠-٩۰-۹'
    section_no = re.compile(rf'^[{digs}]{{2}} · (.+)$')
    letters = set(ABJAD)
    unexplained, new_labels_used, computed = [], [], 0
    for s in nodes(new):
        if s in old_set or s in added_ok:
            continue
        m = section_no.match(s)
        if m and (m.group(1) in old_vis or m.group(1) in label_texts):     # renumbered section label
            continue
        if s in label_texts or any(s.startswith(x) and s.endswith(y) and s[len(x):len(s) - len(y)] in old_vis for x, y in templates):
            new_labels_used.append(s)
            continue
        if s.endswith(' ↓') and s[:-2] in old_vis:                            # the did-you-know link to the origin section
            continue
        if re.fullmatch(rf'[{digs}]+', s) or re.fullmatch(rf'[{digs}+=←→ ]+', s) or (len(s) <= 2 and s in letters):
            computed += 1                                                      # abjad card: letter values and their sum
            continue
        if s in old_vis:                                                       # same words, split differently by the new markup
            continue
        unexplained.append(s)
    if unexplained:
        errs.append(f'{len(unexplained)} new text block(s) not accounted for: ' + ' | '.join(x[:60] for x in unexplained[:4]))
    # the abjad card must agree with what the page itself publishes
    ring = re.search(r'<dl class="np-lucky-dl"><div class="r"><dt>[^<]*</dt><dd>([^<]*)</dd>', new)
    if ring and ring.group(1) not in old_vis:
        errs.append('abjad card shows a number the old page does not publish: ' + ring.group(1))
    jsl = re.search(r'<article class="asr-np"([^>]*)>', new)
    js_labels = dict(re.findall(r'data-l-([a-z]+)="([^"]*)"', jsl.group(1))) if jsl else {}
    for k, v in js_labels.items():
        if H.unescape(v) != T.get(k):
            errs.append('script label not from the label file: ' + k)
    npn = re.search(r'data-np-name="([^"]*)"', jsl.group(1)) if jsl else None
    if not npn or H.unescape(npn.group(1)) not in old_set:
        errs.append('the name given to the site script is not a name the old page shows')
    latin = sorted(set(re.findall(r'[A-Za-zÀ-ɏ][A-Za-zÀ-ɏ\'’ʿ.-]*(?: [A-Za-zÀ-ɏ][A-Za-zÀ-ɏ\'’ʿ.-]*)*', H.unescape(strip(re.sub(r'<[^>]+>', ' ', new[re.search(r'<article[^>]*>', new).end():new.index('</article>')]))))))
    notes.append(f'labels added from the label file: {len(set(new_labels_used))}; abjad card values worked from the letters: {computed}')
    if latin:
        notes.append('Latin-script text in the article: ' + ', '.join(latin[:14]))
    wo, wn = len(old_vis.split()), len(tv.split())
    notes.append(f'bytes {len(old.encode())} -> {len(new.encode())}; words {wo} -> {wn}; FAQ {len(sn)}; internal links {sum(lo.values())} -> {sum(ln.values())}')
    return errs, notes


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    base, loc, slugs = args[0], args[1], args[2:]
    bad = 0
    for slug in slugs:
        e, n = check(base, loc, slug)
        bad += bool(e)
        print(('FAIL ' if e else 'PASS ') + f'{loc}/{slug}', '; '.join(e))
        for x in n:
            if VERBOSE or x.startswith('CONTENT') or x.startswith('fixed') or x.startswith('note'):
                print('     ' + x)
    sys.exit(1 if bad else 0)
