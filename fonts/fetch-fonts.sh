#!/usr/bin/env bash
# Fetch the woff2 binaries for AsrNaam's self-hosted fonts.
# Run from the repository root on a network-enabled machine:
#   bash fonts/fetch-fonts.sh
#
# Pulls the subsetted Latin + Arabic woff2 directly from Google's CDN
# (fonts.gstatic.com — the SIL OFL / Apache 2.0 licensed binaries).
set -euo pipefail
cd "$(dirname "$0")"

python3 <<'PYEOF'
import re, urllib.request
FAMILY_MAP = {
    'Amiri': 'amiri',
    'Cinzel': 'cinzel',
    'Cormorant Garamond': 'cormorant-garamond',
    'Inter': 'inter',
    'Noto Naskh Arabic': 'noto-naskh-arabic',
}
LATIN_FAMS = {'Cinzel','Cormorant Garamond','Inter'}
ARABIC_FAMS = {'Amiri','Noto Naskh Arabic'}
url = ('https://fonts.googleapis.com/css2'
       '?family=Amiri:ital,wght@0,400;0,700;1,400'
       '&family=Cinzel:wght@400;500;600'
       '&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400;1,500'
       '&family=Noto+Naskh+Arabic:wght@400;500;700'
       '&family=Inter:wght@300;400;500;600'
       '&display=swap')
req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120'})
raw = urllib.request.urlopen(req).read().decode()
block_re = re.compile(r'@font-face\s*\{([^}]+)\}', re.S)
fam_re = re.compile(r"font-family:\s*'([^']+)'")
style_re = re.compile(r"font-style:\s*(\w+)")
weight_re = re.compile(r"font-weight:\s*(\d+)")
src_re = re.compile(r"src:\s*url\(([^)]+)\)")
seen = set()
for m in block_re.finditer(raw):
    body = m.group(1)
    fm = fam_re.search(body); st = style_re.search(body); wt = weight_re.search(body); sr = src_re.search(body)
    if not (fm and st and wt and sr): continue
    fam = fm.group(1)
    if fam not in FAMILY_MAP: continue
    ur = re.search(r'unicode-range:\s*([^;]+);', body)
    if ur:
        urv = ur.group(1)
        if fam in LATIN_FAMS and 'U+0000' not in urv and 'U+0100' not in urv: continue
        if fam in ARABIC_FAMS and 'U+06' not in urv: continue
    key = (fam, st.group(1), wt.group(1))
    if key in seen: continue
    seen.add(key)
    short = FAMILY_MAP[fam]
    suffix = wt.group(1) + ('i' if st.group(1) == 'italic' else '')
    outname = f"{short}-{suffix}.woff2"
    woff_url = sr.group(1).strip('"\'')
    print(f"  -> {outname}")
    urllib.request.urlretrieve(woff_url, outname)
print("All fonts downloaded.")
PYEOF
