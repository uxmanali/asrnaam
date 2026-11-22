"""Arabic name pages: the first FAQ answer ("what does the name mean") is cut off mid-phrase on some pages.
Restore it from the page's own dictionary-meaning row. No new text is written.
usage: python3 ar_faq_cutoff.py <repo-root> [--write]"""
import re, sys, glob, json, html, os
root = sys.argv[1]; write = '--write' in sys.argv
done, odd = [], []
HOLD = {'ammar': 'meaning row itself holds stray template text', 'hatice': 'fixed with batch one', 'ayyub': 'fixed with batch one'}
for p in sorted(glob.glob(os.path.join(root, 'ar/names/*/index.html'))):
    if p.split('/')[-2] in HOLD:
        continue
    h = open(p, encoding='utf8').read()
    m = re.search(r'<span class="qf-label">المعنى المعجمي</span><span class="qf-value">(.*?)</span></div>', h, re.S)
    f = re.search(r'(<details class="asr-faq-item"><summary>ما معنى اسم [^<]*</summary><div class="prose"><p>)(.*?)(</p>)', h, re.S)
    if not m or not f:
        continue
    M, A = m.group(1).strip(), f.group(2).strip()
    if '<' in M or '<' in A:
        continue
    stem = A[:-1] if A.endswith('.') else A
    if not (A != M and len(M) > len(stem) and M.startswith(stem) and M != stem):
        continue
    if M[len(stem):].strip(' .،,') == '':
        continue                      # only punctuation differs: not a cut-off
    new = M if M[-1] in '.؟!' else M + '.'
    jold, jnew = json.dumps(A, ensure_ascii=False), json.dumps(new, ensure_ascii=False)
    body_old = f.group(1) + f.group(2) + f.group(3)
    if h.count(body_old) != 1 or h.count('"text": ' + jold) != 1:
        odd.append((p, h.count(body_old), h.count('"text": ' + jold))); continue
    h2 = h.replace(body_old, f.group(1) + new + f.group(3)).replace('"text": ' + jold, '"text": ' + jnew)
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h2, re.S):
        json.loads(b)
    done.append((p[len(root):].lstrip('/'), A, new))
    if write:
        open(p, 'w', encoding='utf8').write(h2)
print(len(done), 'pages', 'written' if write else 'dry run'); print('odd:', odd)
for p, a, n in done:
    print(p.split('/')[2], '|', a[-45:], '=>', n[-70:])
