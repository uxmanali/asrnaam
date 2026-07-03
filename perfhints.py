"""
Add preconnect + dns-prefetch to googletagmanager, and preload the most
critical font, on every page that loads the gtag script and doesn't already
have the hints. Redirect stub pages (short, no gtag) are skipped naturally.
"""
from pathlib import Path
import re

ROOT = Path('.')
GTAG_MARK = 'www.googletagmanager.com/gtag/js'
PRECONNECT = '<link rel="preconnect" href="https://www.googletagmanager.com" crossorigin>'
DNS = '<link rel="dns-prefetch" href="https://www.googletagmanager.com">'
PRELOAD_FONT = '<link rel="preload" href="/fonts/cormorant-garamond-400.woff2" as="font" type="font/woff2" crossorigin>'

# Only include font preload on pages that actually reference cormorant-garamond
FONT_FILE = 'cormorant-garamond-400.woff2'
FONT_CSS = '/fonts/fonts.css'

changed = 0
skipped_stub = 0
skipped_no_gtag = 0
skipped_had = 0
total = 0

for p in ROOT.rglob('index.html'):
    # Exclude the private tooling if any
    s = str(p)
    if s.startswith('_') or '/.' in s or '/scripts/' in s:
        continue
    total += 1
    try:
        t = p.read_text(encoding='utf-8')
    except Exception:
        continue

    # Skip redirect stubs — very short + no gtag
    if len(t) < 2000 or GTAG_MARK not in t:
        skipped_no_gtag += 1
        continue

    if PRECONNECT in t:
        skipped_had += 1
        continue

    # Insert hints right BEFORE the gtag <script async ...> line
    # Pattern: <script async src="https://www.googletagmanager.com/gtag/js?id=G-..."></script>
    # We prefix the preconnect + dns-prefetch on the line above.

    lines = []
    hints = PRECONNECT + '\n' + DNS
    if FONT_FILE in t or FONT_CSS in t:
        hints = PRELOAD_FONT + '\n' + hints

    # Use regex to find the gtag script line
    pattern = re.compile(r'([ \t]*)(<script async src="https://www\.googletagmanager\.com/gtag/js\?[^"]+"></script>)')
    m = pattern.search(t)
    if not m:
        skipped_no_gtag += 1
        continue

    indent = m.group(1)
    insertion = ''.join(indent + line + '\n' for line in hints.split('\n'))
    new = t[:m.start()] + insertion + t[m.start():]

    if new != t:
        p.write_text(new, encoding='utf-8')
        changed += 1

print(f'Scanned:    {total}')
print(f'Changed:    {changed}')
print(f'Had hints:  {skipped_had}')
print(f'No gtag:    {skipped_no_gtag}')
