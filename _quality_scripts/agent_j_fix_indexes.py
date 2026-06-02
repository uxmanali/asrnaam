#!/usr/bin/env python3
"""Agent J (corrective): rebuild AR/UR A-Z index pages with a clean purpose-built
head (correct canonical/hreflang/GA, no leaked name-specific tags), and add the
index URLs to the sitemaps with an exact <loc> check."""
import os, re, json, glob, datetime
TODAY=datetime.date.today().isoformat()
corpus={e['s']:e for e in json.load(open('names/names-index.json',encoding='utf-8'))}
GA=('<script async src="https://www.googletagmanager.com/gtag/js?id=G-SZ6NJWMRGF"></script>'
    '<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}'
    "gtag('js',new Date());gtag('config','G-SZ6NJWMRGF');</script>")

CFG={
 'ar':dict(lab=lambda e:e.get('a') or e.get('n'),
   title='فهرس الأسماء الإسلامية (أ–ي) — المعنى وقراءة الحروف | أَسْرَنام',
   desc='تصفّح كل الأسماء الإسلامية أبجديًا: المعنى، الجذر العربي، وقراءة علم الحروف على أَسْرَنام.',
   h1='كل الأسماء الإسلامية — فهرس أبجدي', back='الصفحة الرئيسية'),
 'ur':dict(lab=lambda e:e.get('u') or e.get('a') or e.get('n'),
   title='اسلامی ناموں کی فہرست (الف–ے) — معنی اور حروف کی قرات | اَسرنام',
   desc='تمام اسلامی ناموں کو حروفِ تہجی کے مطابق دیکھیں: معنی، عربی جڑ، اور علمِ حروف کی قرات۔',
   h1='تمام اسلامی نام — حروفِ تہجی کی فہرست', back='ہوم پیج'),
}

def build(lang):
    cfg=CFG[lang]
    slugs=sorted(os.path.basename(d.rstrip('/')) for d in glob.glob(f'{lang}/names/*/') if os.path.basename(d.rstrip('/'))!='')
    slugs=[s for s in slugs if s and os.path.exists(f'{lang}/names/{s}/index.html')]
    groups={}
    for s in slugs: groups.setdefault(s[0].upper(),[]).append(s)
    head=(f'<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
      f'<title>{cfg["title"]}</title>'
      f'<meta name="description" content="{cfg["desc"]}">'
      f'<meta name="robots" content="index,follow">'
      f'<link rel="canonical" href="https://asrnaam.com/{lang}/names/">'
      f'<link rel="alternate" hreflang="en" href="https://asrnaam.com/names/"/>'
      f'<link rel="alternate" hreflang="ar" href="https://asrnaam.com/ar/names/"/>'
      f'<link rel="alternate" hreflang="ur" href="https://asrnaam.com/ur/names/"/>'
      f'<link rel="alternate" hreflang="x-default" href="https://asrnaam.com/names/"/>'
      f'<link rel="preconnect" href="https://www.googletagmanager.com" crossorigin>'
      f'<link rel="stylesheet" href="/fonts/fonts.css">'
      f'<link rel="stylesheet" href="/asr-enhance.css">'
      f'{GA}')
    # quick A-Z jump bar
    jump=' · '.join(f'<a href="#L-{L}">{L}</a>' for L in sorted(groups))
    body=[f'<main><article class="prose" style="max-width:1100px;margin:0 auto;padding:1.5rem;">',
          f'<h1>{cfg["h1"]}</h1>',
          f'<p style="color:#6B6B6B;">{len(slugs)}</p>',
          f'<nav class="asr-azjump" style="margin:1rem 0;line-height:2;">{jump}</nav>']
    for L in sorted(groups):
        body.append(f'<section><h2 id="L-{L}" style="margin-top:1.6rem;">{L}</h2>'
                    f'<div class="related-grid" style="display:flex;flex-wrap:wrap;gap:.4rem;">')
        for s in groups[L]:
            lab=cfg['lab'](corpus.get(s,{'n':s}))
            body.append(f'<a href="/{lang}/names/{s}/" class="related-card" '
                        f'style="display:inline-block;padding:.4rem .8rem;border:1px solid #e3ddd0;'
                        f'border-radius:4px;text-decoration:none;">{lab}</a>')
        body.append('</div></section>')
    body.append(f'<p style="margin-top:2rem;"><a href="/{lang}/">{cfg["back"]}</a> · '
                f'<a href="/names/" lang="en">English A–Z</a></p></article></main>')
    foot=('<footer style="text-align:center;padding:2rem;font-size:.85rem;color:#6B6B6B;">'
          '© AsrNaam · <a href="/" lang="en">English</a> · <a href="/ar/">العربية</a> · '
          '<a href="/ur/">اردو</a></footer>')
    html=f'<!doctype html><html lang="{lang}" dir="rtl"><head>{head}</head><body>{"".join(body)}{foot}</body></html>'
    open(f'{lang}/names/index.html','w',encoding='utf-8').write(html)
    return len(slugs)

def add_sitemap(lang):
    f=f'sitemap-{lang}.xml'
    c=open(f,encoding='utf-8').read()
    loc=f'<loc>https://asrnaam.com/{lang}/names/</loc>'
    if loc in c: return 'already'
    entry=(f'<url>{loc}<lastmod>{TODAY}</lastmod><changefreq>weekly</changefreq>'
           f'<priority>0.9</priority></url>\n')
    c=c.replace('</urlset>',entry+'</urlset>',1)
    open(f,'w',encoding='utf-8').write(c); return 'added'

rep={}
for lang in ('ar','ur'):
    rep[lang]=dict(index_names=build(lang), sitemap=add_sitemap(lang))
print(json.dumps(rep,indent=1,ensure_ascii=False))
