"""Urdu name pages: three template wordings, decided 23 Nov 2026 (Usman: lighter, decent words the culture accepts; check a dictionary).
1. «حاملہ» means a pregnant woman (Rekhta dictionary, haamila). A woman who bears a name is «اس نام کی حامل»; Rekhta's own usage note:
   in Urdu «حامل» means "one who holds something" and takes no feminine ending («آپ کی بات بڑی اہمیت کی حامل ہے»).
2. «N ہجے» for syllables reads as "N spellings" to most readers and the same pages use «ہجے» for spelling. Plain wording: «بولنے میں N حصے».
3. «کا اصل کیا ہے»: «اصل» (origin) is feminine, so «کی اصل کیا ہے».
usage (repo root): python3 redesign/ur_wording_fixes.py [--write]"""
import glob, re, sys, json, collections
write = '--write' in sys.argv; c = collections.Counter(); n = 0
for f in sorted(glob.glob('ur/names/*/index.html')):
    h = h0 = open(f, encoding='utf8').read()
    h, k = re.subn('اپن[ےی] حاملہ', 'اپنی حامل', h); c['اپنی حامل'] += k
    h, k = re.subn('ہے کہ حاملہ', 'ہے کہ اس کی حامل', h); c['اس کی حامل'] += k
    h, k = re.subn('حاملہ', 'اس نام کی حامل', h); c['اس نام کی حامل'] += k
    h, k = re.subn('(?<![۰-۹0-9])۱ ہجے', 'بولنے میں ۱ حصہ', h); c['۱ حصہ'] += k
    h, k = re.subn('([۰-۹0-9]+) ہجے', r'بولنے میں \1 حصے', h); c['N حصے'] += k
    h, k = re.subn('کا اصل کیا ہے', 'کی اصل کیا ہے', h); c['کی اصل'] += k
    if h == h0: continue
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S): json.loads(b)
    n += 1
    if write: open(f, 'w', encoding='utf8').write(h)
print('pages changed', n, 'written' if write else 'dry run', dict(c))
