"""Apply reviewed text corrections (redesign/lang/fixes-<lang>.json) to pages in the working tree.
Each entry: file, old, new, count. A fix is applied only when `old` occurs exactly `count` times; otherwise nothing is written for that file.
usage: python3 redesign/apply_fixes.py <lang> [--scope=batch-one] [--only=slug,slug] [--write]"""
import json, sys, re, collections
lang = sys.argv[1]; write = '--write' in sys.argv
scope = next((a.split('=')[1] for a in sys.argv if a.startswith('--scope=')), None)
only = next((set(a.split('=')[1].split(',')) for a in sys.argv if a.startswith('--only=')), None)
by = collections.defaultdict(list)
for fx in json.load(open(f'redesign/lang/fixes-{lang}.json', encoding='utf8')):
    if scope and fx.get('scope') != scope: continue
    if only and fx['file'].split('/')[2] not in only: continue
    by[fx['file']].append(fx)
ok = bad = n = 0
for f, fixes in sorted(by.items()):
    h = h0 = open(f, encoding='utf8').read(); fail = []
    for fx in fixes:
        if h.count(fx['old']) != fx['count']:
            fail.append((h.count(fx['old']), fx['count'], fx['old'][:50])); continue
        h = h.replace(fx['old'], fx['new']); n += fx['count']
    if fail:
        bad += 1; print('FAIL', f, fail); continue
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        json.loads(b)
    ok += 1
    if write and h != h0: open(f, 'w', encoding='utf8').write(h)
print(lang, 'files ok', ok, 'failed', bad, 'replacements', n, 'written' if write else 'dry run')
