"""AsrNaam name page redesign (brief: claude/name-page-redesign-brief.md), Phase 0.

Moves the existing blocks of an English name page into the new layout. Every block is cut from the
page as raw HTML and pasted unchanged; only wrappers, headings for the new sections and the mode
switch are added. The <head> is never touched.

usage: python3 redesign/np_build.py slug [slug ...] [--write]   (run from the repo root)
Without --write it only reports; with --write it rewrites names/<slug>/index.html.
This folder is excluded from publishing (.assetsignore)."""
import re, sys, json, html as H

IDX = {x['s']: x for x in json.load(open('names/names-index.json', encoding='utf8'))}
ABJAD = {'ا': 1, 'أ': 1, 'إ': 1, 'آ': 1, 'ٱ': 1, 'ء': 1, 'ب': 2, 'پ': 2, 'ج': 3, 'چ': 3, 'د': 4, 'ه': 5, 'ة': 5, 'ہ': 5,
         'ھ': 5, 'ح': 8, 'و': 6, 'ؤ': 6, 'ز': 7, 'ژ': 7, 'ط': 9, 'ي': 10, 'ى': 10, 'ی': 10, 'ئ': 10, 'ك': 20, 'ک': 20,
         'گ': 20, 'ل': 30, 'م': 40, 'ن': 50, 'س': 60, 'ع': 70, 'ف': 80, 'ص': 90, 'ق': 100, 'ر': 200, 'ش': 300,
         'ت': 400, 'ث': 500, 'خ': 600, 'ذ': 700, 'ض': 800, 'ظ': 900, 'غ': 1000}


class Skip(Exception):
    pass


def cut(s, start, end, required=True):
    """return (block, s_without_block) for the first start..end span"""
    i = s.find(start)
    if i < 0:
        if required:
            raise Skip('missing ' + start)
        return '', s
    j = s.find(end, i + len(start))
    if j < 0:
        raise Skip('unclosed ' + start)
    j += len(end)
    return s[i:j], s[:i] + s[j:]


def marker(s, name, required=False):
    return cut(s, f'<!-- {name}:START -->', f'<!-- {name}:END -->', required)


def inner_of(block, start_marker, end_marker):
    i = block.find(start_marker)
    j = block.find(end_marker, i)
    return block[i + len(start_marker):j] if i >= 0 and j >= 0 else ''


def text_of(x):
    t = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', x, flags=re.S)
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', ' ', t))).strip()


def section_by_class(s, cls):
    """cut <section class="asr-v2 asr-v2-<cls>">..</section> (no nested sections inside these)"""
    i = s.find(f'<section class="asr-v2 asr-v2-{cls}"')
    if i < 0:
        return '', s
    j = s.find('</section>', i) + len('</section>')
    return s[i:j], s[:i] + s[j:]


def strip_section(sec):
    """the inside of a v2 section without its kicker and title; returns (kicker, title, body)"""
    k = re.search(r'<p class="asr-v2-kicker">(.*?)</p>', sec, re.S)
    t = re.search(r'<h2 class="asr-v2-title">(.*?)</h2>', sec, re.S)
    body = re.sub(r'^<section[^>]*>', '', sec)
    body = re.sub(r'</section>$', '', body)
    if k:
        body = body.replace(k.group(0), '', 1)
    if t:
        body = body.replace(t.group(0), '', 1)
    kick = re.sub(r'^Section \d+ · ', '', k.group(1)) if k else ''   # old numbering removed: sections are renumbered 01-06
    return kick, (t.group(1) if t else ''), body


def lucky_card(gl, published):
    parts = [(g, ABJAD[g]) for g in gl if g in ABJAD]
    total = sum(v for _, v in parts)
    steps = [total]
    x = total
    while x > 9:
        x = sum(map(int, str(x)))
        steps.append(x)
    eq = '+'.join(str(v) for _, v in parts) + ' = ' + str(total) + ''.join(f' → {s}' for s in steps[1:])
    chips = ''.join(f'<span><i>{g}</i>{v}</span>' for g, v in parts)
    return (f'<div class="rd-lucky np-lucky"><span class="rd-kicker">Abjad lucky number</span>'
            f'<dl class="np-lucky-dl"><div class="r"><dt>Lucky number</dt><dd data-asr-field="lucky">{published}</dd></div></dl>'
            f'<div class="work"><div class="rd-chips">{chips}</div>{H.escape(eq)}</div></div>')


def build(h, slug):
    x = IDX[slug]
    name = x['n']
    if '<article class="asr-name-article">' not in h:
        raise Skip('no plain article tag')
    if 'asr-np' in h:
        raise Skip('already migrated')
    a0 = h.index('<article class="asr-name-article">')
    a1 = a0 + len('<article class="asr-name-article">')
    a2 = h.index('</article>', a1)
    pre, body, post = h[:a1], h[a1:a2], h[a2:]
    pre = pre.replace('<article class="asr-name-article">', '<article class="asr-name-article asr-np" data-np-mode="me">')
    # ---- hero
    old_hero = False
    hero, body = cut(body, '<header class="asr-name-hero"', '</header>', required=False)
    if not hero:
        hero, body = cut(body, '<div class="hero">', '</div>\n<div class="content">', required=True)
        hero = hero[:-len('\n<div class="content">')]
        body = body.replace('<div class="content"><span id="reading"></span>', '<div class="content">', 1)
        body = '\n<div class="content">' + body if not body.lstrip().startswith('\n<div class="content">') else body
        hero = convert_old_hero(hero, slug)
        old_hero = True
    # hero sub line must not be a <p> (house rule: the first long <p> is the Islamic paragraph)
    hero = re.sub(r'<p class="asr-name-hero-sub">(.*?)</p>', r'<div class="asr-name-hero-sub">\1</div>', hero, flags=re.S)
    # ---- answer
    answer, body = marker(body, 'ANSWER', required=True)
    fields = {}
    for m in re.finditer(r'<div class="r"><dt>([^<]*)</dt>(<dd [^>]*data-asr-field="([^"]+)"[^>]*>.*?</dd>)</div>', answer, re.S):
        fields[m.group(3)] = (m.group(1), m.group(2))
    need = ['meaning-dict', 'origin', 'gender', 'urdu', 'urdu-meaning', 'pronunciation', 'lucky']
    miss = [f for f in need if f not in fields]
    if miss:
        raise Skip('answer lacks ' + ','.join(miss))
    islamic = re.search(r'<p class="asr-answer-islamic">.*?</p>', answer, re.S)
    islamic = islamic.group(0) if islamic else ''
    jump_text = re.search(r'<a class="asr-answer-jump"[^>]*>(.*?)</a>', answer, re.S)
    jump_text = jump_text.group(1) if jump_text else ''
    # ---- remove the cross-language bar (allowed removal: duplicate of the hero links)
    _, body = marker(body, 'ASR:CROSSLANG')
    # ---- layout v2
    layout, body = marker(body, 'LAYOUT-V2', required=True)
    root, layout = section_by_class(layout, 'root')
    letters, layout = section_by_class(layout, 'letters')
    synth, layout = section_by_class(layout, 'synthesis')
    dictsec, layout = section_by_class(layout, 'dict')
    bearers, layout = section_by_class(layout, 'bearers')
    leftover_layout = re.sub(r'<div class="asr-v2-divider".*?</svg></div>', '', layout, flags=re.S)
    leftover_layout = re.sub(r'<!-- LAYOUT-V2:(START|END) -->|</?div[^>]*>', '', leftover_layout).strip()
    if text_of(leftover_layout):
        raise Skip('unplaced layout content: ' + text_of(leftover_layout)[:60])
    # ---- the rest, by markers
    pron, body = marker(body, 'PRON')
    share, body = marker(body, 'SHARE-HERO')
    blocks = {}
    community, body = marker(body, 'ASR:COMMUNITY')
    for nm in ['ASRLINK', 'ASRMORE', 'OBS-CALLOUT', 'INLINE-RA', 'LETTERCLUSTER', 'VARIATIONS', 'HERO-RA', 'RELATED', 'SHARED', 'QURANIC', 'TRUST']:
        blocks[nm], body = marker(body, nm)
    # FAQ and the call to action
    faq = ''
    i = body.find('<div class="faq-list">')
    if i < 0:
        raise Skip('no faq-list')
    k = body.rfind('<p class="section-label">', 0, i)
    k = body.rfind('<!-- WEAPON 2', 0, i) if body.rfind('<!-- WEAPON 2', 0, i) >= 0 else k
    j = body.find('<div class="cta-box">', i)
    if j < 0:
        j = body.find('</div>\n</div>', i)
    faq_end = body.rfind('</div>', i, j) + len('</div>')
    faq, body = body[k:faq_end], body[:k] + body[faq_end:]
    cta, body = cut(body, '<div class="cta-box">', '</div>', required=False)
    # what is left inside <div class="content"> is the spelling chips and variants block(s)
    rest = body.strip()
    if rest.startswith('<div class="content">'):
        rest = rest[len('<div class="content">'):]
    if rest.rstrip().endswith('</div>'):
        rest = rest.rstrip()[:-len('</div>')]
    rest = rest.replace('<span id="reading"></span>', '')
    spell = ''
    if text_of(re.sub(r'<!--.*?-->', '', rest, flags=re.S)):
        if not re.search(r'spelling|variant|asr-xlink', rest):
            raise Skip('unplaced content: ' + text_of(rest)[:80])
        spell = rest.strip()
    # ---- pieces of sections
    rk, rt, rbody = strip_section(root)
    lk, lt, lbody = strip_section(letters)
    sk, st, sbody = strip_section(synth)
    dk, dt, dbody = strip_section(dictsec)
    bk, bt, bbody = strip_section(bearers) if bearers else ('', '', '')
    quranic = ''
    m = re.search(r'<div class="asr-v2-quranic-nest">.*?</div>\s*$', dbody, re.S)
    if m:
        quranic = m.group(0)
        dbody = dbody[:m.start()]
    gl = re.findall(r'asr-v2-letter-arabic[^>]*>([^<]+)', lbody)
    lucky_pub = re.sub(r'<[^>]+>', '', fields['lucky'][1]).strip()
    # the Ilm ul Huroof qf-row inside the pronunciation block carries data-asr-field="meaning-iuh": keep it once, in section 01
    iuh_row = ''
    m = re.search(r'<div class="qf-row"[^>]*><span class="qf-label">Ilm ul Huroof</span>.*?</span></div>', pron, re.S)
    if m:
        iuh_row = m.group(0)
        pron = pron.replace(iuh_row, '')
    pron_h = re.search(r'<h2 class="pron-h2"[^>]*>(.*?)</h2>', pron, re.S)
    pron_title = pron_h.group(1) if pron_h else f'How to Pronounce {name}'
    pron_box = re.search(r'<div class="asr-pronunciation".*</div>', pron, re.S)
    pron_box = pron_box.group(0) if pron_box else ''
    pron_box = re.sub(r' style="[^"]*"', '', pron_box)  # restyled by the np- rules; saves bytes
    nb = len(re.findall(r'<li>', bbody))
    rail = nb >= 3
    gender_cls = 'girl' if x['g'] == 'Female' else 'boy'
    def card(field, label, cls=''):
        dtx, dd = fields[field]
        return f'<div class="r np-card{cls}"><dt>{dtx}</dt>{dd}</div>'
    gender_dd = fields['gender'][1].replace('data-asr-field="gender"', f'class="rd-tag {gender_cls}" data-asr-field="gender"', 1)
    out = []
    out.append(hero)
    out.append(f'<div class="asr-answer np-answer" aria-label="Quick answer about {H.escape(name)}">'
               f'<dl class="asr-answer-rows np-cards">'
               f'{card("meaning-dict", "Meaning")}{card("origin", "Origin")}'
               f'<div class="r np-card"><dt>{fields["gender"][0]}</dt>{gender_dd}</div>'
               f'<div class="r np-card np-card-ur"><dt>{fields["urdu-meaning"][0]}</dt>{fields["urdu"][1]}{fields["urdu-meaning"][1]}</div>'
               f'</dl>'
               f'<section class="np-pron" aria-labelledby="np-pron-h"><h2 id="np-pron-h" class="np-h2-small">{pron_title}</h2>'
               f'<dl class="np-pron-dl"><div class="r"><dt>{fields["pronunciation"][0]}</dt>{fields["pronunciation"][1]}</div></dl>'
               f'{pron_box}</section>'
               f'{islamic}</div>')
    jumps = ['<a href="#reading">Letter reading</a>', '<a href="#origin">Origin</a>', '<a href="#story">Story</a>']
    if rail:
        jumps.append(f'<a href="#famous">Famous {H.escape(name)}s</a>')
    jumps += ['<a href="#kit" class="np-baby-only">Parent kit</a>', '<a href="#faq">Questions</a>']
    out.append(f'<nav class="np-jump" aria-label="On this page"><span class="rd-kicker">On this page</span>{"".join(jumps)}'
               f'<a class="np-jump-reading" href="#reading">{jump_text}</a></nav>')
    g = []
    # 01 letters
    g.append(f'<section id="reading" class="np-sec np-letters"><p class="rd-kicker">01 · {lk}</p>'
             f'<h2 class="rd-h2">{H.escape(name)}: letter-by-letter reading</h2><h3 class="np-h3">{lt}</h3>{lbody}'
             f'<div class="np-portrait-row"><div class="np-portrait"><p class="rd-kicker"><span class="np-my">Your portrait</span><span class="np-baby">Your child\'s portrait</span> · {sk}</p>'
             f'<h3 class="np-h3">{st}</h3>{sbody}</div>{lucky_card(gl, lucky_pub)}</div>'
             f'{iuh_row}</section>')
    # 02 origin and history
    src = re.search(r'asr-source-line', rbody)
    has_q = bool(re.search(r'\b\d{1,3}:\d{1,3}\b', text_of(quranic)))
    stops = [f'<li class="np-stop"><p class="np-stop-k">Formed{" <span class=\"np-conf\">Established</span>" if src else ""}</p>'
             f'<p class="rd-kicker">{rk}</p><h3 class="np-h3">{rt}</h3>{rbody}</li>']
    if text_of(quranic):
        stops.append(f'<li class="np-stop"><p class="np-stop-k">Blessed{" <span class=\"np-conf\">Established</span>" if has_q else ""}</p>{quranic}</li>')
    trav = spell + blocks['VARIATIONS'] + blocks['ASRLINK']
    if text_of(trav):
        stops.append(f'<li class="np-stop"><p class="np-stop-k">Travelled</p>{trav}</li>')
    g.append(f'<section id="origin" class="np-sec np-journey"><p class="rd-kicker">02 · How the name was formed</p>'
             f'<h2 class="rd-h2">{H.escape(name)}: origin and history</h2><ol class="np-stops">{"".join(stops)}</ol></section>')
    # rail (3 or more bearers) placed by CSS; otherwise the bearers stay inside the story
    if rail:
        g.append(f'<aside id="famous" class="np-rail" aria-labelledby="np-famous-h"><p class="rd-kicker">{bk}</p>'
                 f'<h2 id="np-famous-h" class="rd-h2">Famous {H.escape(name)}s</h2><h3 class="np-h3">{bt}</h3>{bbody}'
                 f'<p class="np-rail-note">Only people with a verifiable source are listed.</p></aside>')
    story_bearers = '' if rail or not bbody else f'<div class="np-bearers"><p class="rd-kicker">{bk}</p><h3 class="np-h3">{bt}</h3>{bbody}</div>'
    g.append(f'<section id="story" class="np-sec np-story"><p class="rd-kicker">03 · {dk}</p>'
             f'<h2 class="rd-h2">The story of the name {H.escape(name)}</h2><h3 class="np-h3">{dt}</h3>{dbody}{story_bearers}</section>')
    # 04 parent kit (baby mode)
    sib = re.findall(r'<a href="(/names/[a-z0-9-]+/)" class="related-card"[^>]*>.*?</a>', blocks['RELATED'], re.S)[:8]
    sib_links = ''
    for href in sib:
        s2 = href.split('/')[2]
        if s2 in IDX:
            t = 'girl' if IDX[s2]['g'] == 'Female' else 'boy'
            sib_links += f'<a class="np-sib rd-tag {t}" href="{href}">{H.escape(IDX[s2]["n"])}</a>'
    g.append(f'<section id="kit" class="np-sec np-kit np-baby" aria-labelledby="np-kit-h"><p class="rd-kicker">04 · Parent kit</p>'
             f'<h2 id="np-kit-h" class="rd-h2">Naming a baby {H.escape(name)}</h2>'
             f'<div class="np-kit-grid"><div class="np-kit-box"><h3 class="np-h3">Try it with your surname</h3>'
             f'<label class="np-kit-label" for="np-surname">Surname</label><input id="np-surname" class="np-input" type="text" autocomplete="off" maxlength="40" placeholder="Your surname">'
             f'<p class="np-kit-out" aria-live="polite" data-np-first="{H.escape(name)}"><span class="np-full">{H.escape(name)}</span> <span class="np-initials"></span></p>'
             f'<p class="np-kit-note">Nothing you type leaves this page.</p></div>'
             + (f'<div class="np-kit-box"><h3 class="np-h3">Pairs well for siblings</h3><p class="np-sibs">{sib_links}</p></div>' if sib_links else '')
             + '</div></section>')
    # 05 share
    if share:
        g.append(f'<section id="share" class="np-sec np-keep"><p class="rd-kicker">05 · Keep it</p>{share}</section>')
    # next-name box
    nxt = blocks['OBS-CALLOUT'] + blocks['INLINE-RA'] + blocks['HERO-RA'] + cta
    if text_of(nxt):
        g.append(f'<div class="np-next">{nxt}</div>')
    # 06 FAQ
    g.append(f'<section id="faq" class="np-sec np-faq"><p class="rd-kicker">06 · Questions</p>{faq}</section>')
    # more names like X
    more = blocks['RELATED'] + blocks['SHARED'] + blocks['ASRMORE'] + blocks['LETTERCLUSTER']
    g.append(f'<section class="np-sec np-more"><h2 class="rd-h2">More names like {H.escape(name)}</h2>{more}</section>')
    g.append(blocks['TRUST'])
    if community:
        g.append(community)
    out.append(f'<div class="np-grid{" has-rail" if rail else ""}">{"".join(g)}</div>')
    if blocks['QURANIC'] and text_of(blocks['QURANIC']):
        raise Skip('second QURANIC block has text')
    new_body = '\n' + '\n'.join(out) + '\n'
    page = pre + new_body + post
    # mode switch in the breadcrumb row
    switch = ('<div class="np-mode" role="group" aria-label="Reading mode">'
              '<button type="button" class="np-mode-b" data-np-mode="me" aria-pressed="true">This is my name</button>'
              '<button type="button" class="np-mode-b" data-np-mode="baby" aria-pressed="false">I\'m naming a baby</button></div>')
    page = page.replace('<!-- ASR:BREADCRUMB:END -->', '<!-- ASR:BREADCRUMB:END -->\n' + switch, 1)
    return page, dict(old_hero=old_hero, rail=rail, bearers=nb, letters=len(gl))


def convert_old_hero(hero, slug):
    """old-generation hero -> emerald hero markup (Phase 3 shape), keeping the H1 and sub text"""
    ar = re.search(r'<div class="arabic-name"[^>]*>(.*?)</div>', hero, re.S).group(1)
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', hero, re.S).group(1)
    sub = re.search(r'<p class="hero-subtitle">(.*?)</p>', hero, re.S)
    badge = re.search(r'<div class="name-badge">(.*?)</div>', hero, re.S)
    badge_t = re.sub(r'<[^>]+>', '', badge.group(1)).replace('&nbsp;', ' ') if badge else ''
    badge_t = re.sub(r'\s+', ' ', badge_t).strip()
    langs = []
    import os
    for loc, label, attrs in (('ur', 'اردو میں پڑھیں', 'lang="ur" dir="rtl"'), ('ar', 'اقرأ بالعربية', 'lang="ar" dir="rtl"'), ('hi', 'हिन्दी में पढ़ें', 'lang="hi"'), ('tr', 'Türkçe oku', 'lang="tr"')):
        if os.path.exists(f'{loc}/names/{slug}/index.html'):
            langs.append(f'<a href="/{loc}/names/{slug}/" hreflang="{loc}" {attrs} data-lang="{loc}">{label}</a>')
    return (f'<header class="asr-name-hero"><p class="asr-name-hero-kicker">{badge_t}</p>'
            f'<div class="asr-name-hero-arabic" lang="ar" dir="rtl">{ar}</div><h1 class="asr-name-hero-roman">{h1}</h1>'
            + (f'<p class="asr-name-hero-sub">{sub.group(1)}</p>' if sub else '')
            + (f'<p class="asr-name-hero-langs">{"<span class=\"sep\" aria-hidden=\"true\">·</span>".join(langs)}</p>' if langs else '')
            + '</header>')


if __name__ == '__main__':
    write = '--write' in sys.argv
    for slug in [a for a in sys.argv[1:] if not a.startswith('--')]:
        p = f'names/{slug}/index.html'
        h = open(p, encoding='utf8').read()
        try:
            page, info = build(h, slug)
        except Skip as e:
            print(slug, 'SKIP', e)
            continue
        print(slug, 'OK', info, len(h), '->', len(page))
        if write:
            open(p, 'w', encoding='utf8').write(page)
