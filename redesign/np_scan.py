"""Dry-run the builder and the round-trip check over every English name page (in memory, nothing written).
usage: python3 redesign/np_scan.py   -> redesign/scan.json  {slug: {ok, reason, hero, bearers, faq, src, bytes...}}"""
import os, re, sys, json, collections
sys.path.insert(0, 'redesign')
import np_build as B
import np_check as C
res = {}
for slug in sorted(os.listdir('names')):
    p = f'names/{slug}/index.html'
    if not os.path.isfile(p):
        continue
    h = open(p, encoding='utf8').read()
    if 'asr-layout-v2' not in h or 'http-equiv="refresh"' in h:
        continue
    if slug not in B.IDX:
        res[slug] = dict(ok=False, reason='not in names-index'); continue
    rec = dict(hero='new' if 'class="asr-name-hero"' in h else 'old', faq=h.count('<details'), src='asr-source-line' in h)
    try:
        page, info = B.build(h, slug)
    except B.Skip as e:
        rec.update(ok=False, reason=re.sub(r'[:].*', '', str(e))[:40], detail=str(e)[:90]); res[slug] = rec; continue
    except Exception as e:
        rec.update(ok=False, reason='error ' + type(e).__name__, detail=str(e)[:90]); res[slug] = rec; continue
    errs, notes = C.check_pair(h, page)
    rec.update(ok=not errs, reason='; '.join(errs)[:120] if errs else '', bearers=info['bearers'], b0=len(h.encode()), b1=len(page.encode()))
    res[slug] = rec
json.dump(res, open('redesign/scan.json', 'w'), indent=0)
ok = [s for s, r in res.items() if r['ok']]
print('name pages', len(res), 'build+check OK', len(ok))
c = collections.Counter(re.sub(r'\d+', 'N', r['reason'])[:60] for r in res.values() if not r['ok'])
for k, v in c.most_common(25):
    print(' ', v, k)
