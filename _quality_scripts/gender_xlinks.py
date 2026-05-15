import re, os, csv, json
from pathlib import Path
REPO = Path("/tmp/work-quality/asrnaam")
NAMES = REPO / "names"

rows = list(csv.DictReader(open('/tmp/work-quality/quality-tracker.csv')))
slug_to_gender = {r['slug']: r['gender'] for r in rows}
decisions = json.load(open('/tmp/work-quality/dedup-decisions.json'))
for d in decisions:
    canon_g = slug_to_gender.get(d['canonical'],'')
    for redir in d['redirects']:
        slug_to_gender[redir] = canon_g

LINK_PATTERN = re.compile(
    r'(<a\b[^>]*?)\bhref="/names/([a-z0-9-]+)/"([^>]*?\bclass="[^"]*?)\b(boy|girl)\b([^"]*?")', re.S)
LINK_PATTERN_REV = re.compile(
    r'(<a\b[^>]*?\bclass="[^"]*?)\b(boy|girl)\b([^"]*?")([^>]*?\bhref="/names/([a-z0-9-]+)/")', re.S)

total_fixes = 0
files_changed = 0

class C: 
    n = 0
ctr = C()

def fix(m):
    before, target_slug, mid, color, after = m.group(1,2,3,4,5)
    tg = slug_to_gender.get(target_slug,'')
    if not tg: return m.group(0)
    want = 'boy' if tg=='Male' else 'girl' if tg=='Female' else None
    if want is None or want==color: return m.group(0)
    ctr.n += 1
    return f'{before}href="/names/{target_slug}/"{mid}{want}{after}'

def fix2(m):
    before, color, mid, after_block, target_slug = m.group(1,2,3,4,5)
    tg = slug_to_gender.get(target_slug,'')
    if not tg: return m.group(0)
    want = 'boy' if tg=='Male' else 'girl' if tg=='Female' else None
    if want is None or want==color: return m.group(0)
    ctr.n += 1
    return f'{before}{want}{mid}{after_block}'

for d in os.listdir(NAMES):
    p = NAMES / d / "index.html"
    if not p.is_file(): continue
    t = p.read_text(encoding="utf-8", errors="replace")
    if '<meta http-equiv="refresh"' in t[:1500]: continue
    before_n = ctr.n
    new_t = LINK_PATTERN.sub(fix, t)
    new_t = LINK_PATTERN_REV.sub(fix2, new_t)
    if new_t != t:
        p.write_text(new_t, encoding="utf-8")
        files_changed += 1
    after_n = ctr.n
    total_fixes += (after_n - before_n)

# Also fix names/index.html similarly
idx = NAMES / "index.html"
t = idx.read_text(encoding="utf-8")
before_n = ctr.n
new_t = LINK_PATTERN.sub(fix, t)
new_t = LINK_PATTERN_REV.sub(fix2, new_t)
if new_t != t:
    idx.write_text(new_t, encoding="utf-8")
print(f"names/index.html fixes: {ctr.n - before_n}")

print(f"Total files changed: {files_changed}; cross-link gender fixes applied: {ctr.n}")
