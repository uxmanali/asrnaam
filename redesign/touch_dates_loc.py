"""Set the modified date on translated name pages that git shows as changed against a base ref.
Updates article:modified_time and JSON-LD dateModified where the page already has them (adds nothing),
and the page's <lastmod> in sitemap-<lang>.xml.
usage (repo root): python3 touch_dates_loc.py --base origin/main --today YYYY-MM-DD [--write]"""
import re, sys, subprocess
base = sys.argv[sys.argv.index('--base') + 1]; today = sys.argv[sys.argv.index('--today') + 1]; write = '--write' in sys.argv
files = subprocess.run(['git', 'diff', '--name-only', base, '--', 'ur/names', 'ar/names', 'hi/names', 'tr/names'], capture_output=True, text=True).stdout.split()
maps, n = {}, 0
for f in files:
    lang, slug = f.split('/')[0], f.split('/')[2]
    h = open(f, encoding='utf8').read()
    h2 = re.sub(r'(article:modified_time" content=")[^"]*(")', r'\g<1>' + today + r'\2', h)
    h2 = re.sub(r'("dateModified":\s*")[^"]*(")', r'\g<1>' + today + r'\2', h2)
    sm = f'sitemap-{lang}.xml'
    try:
        s = maps.get(sm) or open(sm, encoding='utf8').read()
        s2, k = re.subn(r'(<loc>https://asrnaam\.com/%s/names/%s/</loc><lastmod>)[^<]*(</lastmod>)' % (lang, re.escape(slug)), r'\g<1>' + today + r'\2', s)
        maps[sm] = s2
    except FileNotFoundError:
        k = 0
    n += 1
    if write and h2 != h: open(f, 'w', encoding='utf8').write(h2)
if write:
    for sm, s in maps.items(): open(sm, 'w', encoding='utf8').write(s)
print('pages', n, 'sitemaps', sorted(maps), 'written' if write else 'dry run')
