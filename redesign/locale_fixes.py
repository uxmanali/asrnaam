"""Apply the locale_fixes recorded in redesign/pilot/*.json to translated pages (exact text, exact count, or it stops).
usage: python3 redesign/locale_fixes.py slug [slug ...]   (run from the repo root; safe to re-run)"""
import json, sys
for slug in sys.argv[1:]:
    for fx in json.load(open(f'redesign/pilot/{slug}.json', encoding='utf8')).get('locale_fixes', []):
        t = open(fx['file'], encoding='utf8').read()
        n = t.count(fx['old'])
        if n == 0 and fx['new'] in t:
            print(slug, fx['file'], 'already applied'); continue
        if n != fx['count']:
            sys.exit(f"STOP {fx['file']}: expected {fx['count']} of {fx['old']!r}, found {n}")
        open(fx['file'], 'w', encoding='utf8').write(t.replace(fx['old'], fx['new']))
        print(slug, fx['file'], 'replaced', n)
