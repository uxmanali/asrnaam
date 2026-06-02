#!/usr/bin/env python3
"""
Agent J - AR/UR internal linking + browsable indexes.

Closes the biggest crawl gap (the ~2,256 'Discovered - not indexed'):
AR/UR canonical pages had NO related-name links and there was NO AR/UR A-Z
index, so ~4,000 pages were reachable only via hreflang.

Does, idempotently:
1. Inject a localized 'related names' block (reusing the curated EN relations,
   labelled with Arabic/Urdu names) before </main> on every ar|ur/names/<slug>/.
2. Build ar/names/index.html and ur/names/index.html (A-Z, RTL, localized),
   reusing an existing page's <head> for identical styling + GA.
3. Link the new index from /ar/ and /ur/ homepages.
4. Add the two index URLs to sitemap-ar.xml / sitemap-ur.xml.
"""
import os, re, json, glob, datetime

TODAY = datetime.date.today().isoformat()
corpus = {e['s']: e for e in json.load(open('names/names-index.json', encoding='utf-8'))}

L = {
 'ar': dict(label=lambda e: e.get('a') or e.get('n'), dir='rtl',
            head_title='فهرس الأسماء الإسلامية (أ–ي) — المعنى وقراءة الحروف | أَسْرَنام',
            rel_h='أسماء ذات صلة', browse='تصفّح جميع الأسماء (أ–ي)',
            idx_h='كل الأسماء الإسلامية — فهرس أبجدي', src='ar/names/renad/index.html'),
 'ur': dict(label=lambda e: e.get('u') or e.get('a') or e.get('n'), dir='rtl',
            head_title='اسلامی ناموں کی فہرست (الف–ے) — معنی اور حروف کی قرات | اَسرنام',
            rel_h='متعلقہ نام', browse='تمام نام دیکھیں (الف–ے)',
            idx_h='تمام اسلامی نام — حروفِ تہجی کی فہرست', src='ur/names/renad/index.html'),
}

def en_related(slug):
    p = f'names/{slug}/index.html'
    if not os.path.exists(p): return []
    c = open(p, encoding='utf-8').read()
    m = re.search(r'<!-- RELATED:START -->(.*?)</main>', c, re.S)
    region = m.group(1) if m else ''
    out=[]
    for s in re.findall(r'href="/names/([a-z0-9-]+)/"', region):
        if s != slug and s not in out: out.append(s)
    return out

def related_for(lang, slug, lang_slugs):
    rel = [s for s in en_related(slug) if s in lang_slugs][:6]
    if len(rel) < 3:  # fallback: alphabetical neighbours that exist in this lang
        ordered = sorted(lang_slugs)
        if slug in ordered:
            i = ordered.index(slug)
            for s in ordered[i+1:i+8] + ordered[max(0,i-7):i][::-1]:
                if s != slug and s not in rel:
                    rel.append(s)
                if len(rel) >= 6: break
    return rel[:6]

def rel_block(lang, slug, rel):
    cfg = L[lang]
    cards = ''.join(
        f'<a href="/{lang}/names/{r}/" class="related-card">{cfg["label"](corpus.get(r,{"n":r}))}</a>'
        for r in rel)
    return (f'\n<!-- {lang.upper()}-RELATED:START -->\n'
            f'<div class="related-section" dir="{cfg["dir"]}"><p class="section-label" '
            f'style="margin:3rem 0 1rem;">{cfg["rel_h"]}</p>'
            f'<div class="related-grid">{cards}</div>'
            f'<p style="margin-top:1rem;"><a href="/{lang}/names/">{cfg["browse"]}</a></p></div>\n'
            f'<!-- {lang.upper()}-RELATED:END -->\n')

def inject_related(lang):
    marker = f'<!-- {lang.upper()}-RELATED:START -->'
    dirs = [os.path.basename(d.rstrip('/')) for d in glob.glob(f'{lang}/names/*/')]
    lang_slugs = set(dirs)
    done=0
    for slug in dirs:
        p = f'{lang}/names/{slug}/index.html'
        c = open(p, encoding='utf-8').read()
        if marker in c or '</main>' not in c:
            continue
        rel = related_for(lang, slug, lang_slugs)
        if not rel: continue
        c = c.replace('</main>', rel_block(lang, slug, rel) + '</main>', 1)
        open(p,'w',encoding='utf-8').write(c)
        done+=1
    return done, sorted(lang_slugs)

def build_index(lang, lang_slugs):
    cfg = L[lang]
    head_src = open(cfg['src'], encoding='utf-8').read()
    head = re.search(r'<head>(.*?)</head>', head_src, re.S).group(1)
    # retitle + recanonical for the index
    head = re.sub(r'<title>.*?</title>', f'<title>{cfg["head_title"]}</title>', head, 1, re.S)
    head = re.sub(r'(<link[^>]*rel="canonical"[^>]*href=")[^"]*(")',
                  rf'\g<1>https://asrnaam.com/{lang}/names/\g<2>', head, 1)
    # group by first slug letter
    groups={}
    for s in sorted(lang_slugs):
        groups.setdefault(s[0].upper(), []).append(s)
    body=[f'<main><article class="prose"><h1>{cfg["idx_h"]}</h1>',
          f'<p>{len(lang_slugs)}</p>']
    for letter in sorted(groups):
        body.append(f'<section><h2 id="L-{letter}">{letter}</h2><div class="related-grid">')
        for s in groups[letter]:
            lab = cfg['label'](corpus.get(s, {'n': s}))
            body.append(f'<a href="/{lang}/names/{s}/" class="related-card">{lab}</a>')
        body.append('</div></section>')
    body.append(f'<p><a href="/{lang}/">↩</a> · <a href="/names/" lang="en">English A–Z</a></p>')
    body.append('</article></main>')
    html = (f'<!doctype html><html lang="{lang}" dir="{cfg["dir"]}"><head>{head}</head>'
            f'<body>{"".join(body)}'
            f'<footer><p style="font-size:.85rem;">© AsrNaam · '
            f'<a href="/" lang="en">English</a> · <a href="/ar/">العربية</a> · <a href="/ur/">اردو</a></p></footer>'
            f'</body></html>')
    os.makedirs(f'{lang}/names', exist_ok=True)
    open(f'{lang}/names/index.html','w',encoding='utf-8').write(html)

def link_from_home(lang):
    p=f'{lang}/index.html'
    if not os.path.exists(p): return False
    c=open(p,encoding='utf-8').read()
    if f'href="/{lang}/names/"' in c: return False
    link=(f'<p class="asr-allnames-link" style="margin:1.2rem 0;"><a href="/{lang}/names/">'
          f'{L[lang]["browse"]}</a></p>')
    if '</main>' in c: c=c.replace('</main>', link+'</main>',1)
    else: c=c.replace('</body>', link+'</body>',1)
    open(p,'w',encoding='utf-8').write(c); return True

def add_to_sitemap(lang):
    f=f'sitemap-{lang}.xml'
    if not os.path.exists(f): return False
    c=open(f,encoding='utf-8').read()
    url=f'https://asrnaam.com/{lang}/names/'
    if url in c: return False
    entry=f'<url><loc>{url}</loc><lastmod>{TODAY}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>\n'
    c=c.replace('</urlset>', entry+'</urlset>',1)
    open(f,'w',encoding='utf-8').write(c); return True

report={}
for lang in ('ar','ur'):
    n, slugs = inject_related(lang)
    build_index(lang, slugs)
    report[lang]=dict(related_injected=n, index_names=len(slugs),
                      home_linked=link_from_home(lang), sitemap=add_to_sitemap(lang))
print(json.dumps(report, indent=1, ensure_ascii=False))
