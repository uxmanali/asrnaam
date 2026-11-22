"""Arabic name pages: five template faults, each already reviewed and live on the 12 batch-one pages.
usage (repo root): python3 ar_template_fixes.py [--write]"""
import glob, sys, json, re, collections
PAT = [('ثلاث قراءات, معنى الاسم', 'ثلاث قراءات: معنى الاسم'),      # Latin comma before a list
       (' ، رسمه العربي', '، رسمه العربي'),                          # space before the Arabic comma (JSON-LD headline)
       ('>الف<', '>ألف<'),                                            # letter name without its hamza
       ('النطق اللاتيني', 'الرسم اللاتيني'),                          # label said pronunciation, value is the Latin spelling
       ('aria-label="Breadcrumb"', 'aria-label="مسار التنقل"')]       # English screen-reader label
write = '--write' in sys.argv; c = collections.Counter(); n = 0
for f in sorted(glob.glob('ar/names/*/index.html')):
    h = h0 = open(f, encoding='utf8').read()
    for a, b in PAT:
        if a in h: c[a] += 1; h = h.replace(a, b)
    if h == h0: continue
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S): json.loads(blk)
    n += 1
    if write: open(f, 'w', encoding='utf8').write(h)
print('pages changed', n, 'written' if write else 'dry run'); [print(' ', v, k) for k, v in c.items()]
