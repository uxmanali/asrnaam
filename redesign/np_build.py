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


import os
PILOT = {}
for _f in (os.listdir('redesign/pilot') if os.path.isdir('redesign/pilot') else []):
    if _f.endswith('.json'):
        PILOT[_f[:-5]] = json.load(open('redesign/pilot/' + _f, encoding='utf8'))
FINAL = '--final' in sys.argv   # production build: no review tags
DRAFT = '' if FINAL else '<span class="np-draft">New, for your review</span>'
VER = '20261122v'   # version tag for asr-redesign.css and asr-redesign.js on migrated pages


def div_end(s, i):
    """index just past the </div> that closes the <div ...> starting at index i (nested divs counted)"""
    depth = 0
    for m in re.finditer(r'<div\b|</div>', s[i:]):
        depth += 1 if m.group(0) != '</div>' else -1
        if depth == 0:
            return i + m.end()
    raise Skip('unbalanced div')


def cut_div(s, i):
    """cut the <div ...>...</div> that starts at index i; returns (block, s_without_block)"""
    j = div_end(s, i)
    return s[i:j], s[:i] + s[j:]


def nostyle(x):
    """drop inline style attributes from a moved block: the np- rules style it, and it saves bytes"""
    return re.sub(r' style="[^"]*"', '', x)


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
    # corrections that apply to the whole page, head included (each is listed in the pilot file and reported by the check)
    for fx in (PILOT.get(slug) or {}).get('page_fixes', []):
        if fx['old'] not in h:
            raise Skip('page fix not found: ' + fx['old'][:40])
        h = h.replace(fx['old'], fx['new'])
    if '<article class="asr-name-article">' not in h:
        raise Skip('no plain article tag')
    if 'asr-np' in h:
        raise Skip('already migrated')
    a0 = h.index('<article class="asr-name-article">')
    a1 = a0 + len('<article class="asr-name-article">')
    a2 = h.index('</article>', a1)
    pre, body, post = h[:a1], h[a1:a2], h[a2:]
    pilot0 = PILOT.get(slug) or {}
    for d in pilot0.get('drop', []):
        m = re.search(r'<li\b(?:(?!</li>).)*?' + re.escape(d['match']), body, re.S)
        if not m or body.count(d['match']) != 1:
            raise Skip('pilot drop not found once: ' + d['match'][:40])
        body = body[:m.start()] + body[m.end():]
    for fx in pilot0.get('fixes', []):
        if fx['old'] not in body:
            raise Skip('pilot fix not found: ' + fx['old'][:40])
        body = body.replace(fx['old'], fx['new'])
    ART = '<article class="asr-name-article asr-np" data-np-mode="me">'
    pre = pre.replace('<article class="asr-name-article">', ART)
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
    extra_rows = [m.group(0) for m in re.finditer(r'<div class="r"><dt>[^<]*</dt><dd(?![^>]*data-asr-field)[^>]*>.*?</dd></div>', answer, re.S)]
    n_rows = len(re.findall(r'<div class="r">', answer))
    if n_rows != len(fields) + len(extra_rows):
        raise Skip('answer rows not all understood')
    need = ['meaning-dict', 'gender', 'urdu', 'urdu-meaning', 'lucky']
    miss = [f for f in need if f not in fields]
    if miss:
        raise Skip('answer lacks ' + ','.join(miss))
    # the hidden script line is read by the sound-match scan: it stays, unchanged
    ans_script = re.search(r'<(div|p) class="asr-answer-script">.*?</\1>', answer, re.S)
    ans_script = ans_script.group(0) if ans_script else ''
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
    for nm in ['ASRLINK', 'ASRMORE', 'OBS-CALLOUT', 'INLINE-RA', 'LETTERCLUSTER', 'VARIATIONS', 'HERO-RA', 'RELATED', 'SHARED', 'QURANIC', 'TRUST', 'THEMES']:
        blocks[nm], body = marker(body, nm)
    # FAQ (two generations of markup) and the call to action
    if body.count('<div class="faq-list">') != 1:
        raise Skip('faq-list count is not 1')
    faq_h2 = True
    if '<div class="faq-section">' in body:
        faq, body = cut_div(body, body.index('<div class="faq-section">'))
        faq_h2 = bool(re.search(r'<h2\b', faq))
    else:
        m = re.search(r'(?:<!-- WEAPON 2[^>]*-->\s*)?<p class="section-label[^"]*"[^>]*>(?:(?!</p>).)*</p>\s*(?:<h2[^>]*>(?:(?!</h2>).)*</h2>\s*)?(?=<div class="faq-list">)', body, re.S)
        k = m.start() if m else body.index('<div class="faq-list">')
        faq_h2 = bool(m and '<h2' in m.group(0))
        faq_end = div_end(body, body.index('<div class="faq-list">'))
        faq, body = body[k:faq_end], body[:k] + body[faq_end:]
    cta = ''
    if '<div class="cta-box">' in body:
        cta, body = cut_div(body, body.index('<div class="cta-box">'))
    # what is left inside <div class="content">: loose related-names blocks, style blocks, and the spelling chips and variants
    rest = body.strip()
    if rest.startswith('<div class="content">'):
        rest = rest[len('<div class="content">'):]
    if rest.rstrip().endswith('</div>'):
        rest = rest.rstrip()[:-len('</div>')]
    rest = rest.replace('<span id="reading"></span>', '')
    loose_related = ''
    while '<div class="related-section"' in rest:
        blk, rest = cut_div(rest, rest.index('<div class="related-section"'))
        loose_related += blk
    loose_styles = ''.join(re.findall(r'<style\b.*?</style>', rest, re.S))
    rest = re.sub(r'<style\b.*?</style>', '', rest, flags=re.S)
    spell = ''
    if text_of(re.sub(r'<!--.*?-->', '', rest, flags=re.S)):
        probe = re.sub(r'<!--.*?-->', '', rest, flags=re.S)
        while '<div class="spellings-section' in probe:
            _, probe = cut_div(probe, probe.index('<div class="spellings-section'))
        probe = re.sub(r'<p class="(?:section-label|spellings-intro|spellings-hook)"[^>]*>.*?</p>', '', probe, flags=re.S)
        while '<div class="spellings-grid' in probe:
            _, probe = cut_div(probe, probe.index('<div class="spellings-grid'))
        if text_of(probe):
            raise Skip('unplaced content: ' + text_of(probe)[:80])
        spell = nostyle(rest.strip())
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
        iuh_row = nostyle(iuh_row)
    pron_h = re.search(r'<h2 class="pron-h2"[^>]*>(.*?)</h2>', pron, re.S)
    pron_title = pron_h.group(1) if pron_h else f'How to Pronounce {name}'
    pron_box = re.search(r'<div class="asr-pronunciation".*</div>', pron, re.S)
    pron_box = pron_box.group(0) if pron_box else ''
    pron_box = nostyle(pron_box)  # restyled by the np- rules; saves bytes
    pilot = PILOT.get(slug)
    bbody = nostyle(bbody)
    def person_li(pp):
        if isinstance(pp, (list, tuple)):
            pp = dict(name=pp[0], meta=pp[1], note=pp[2])
        tag = (' ' + DRAFT) if DRAFT else ''
        if '<li><strong>' in bbody and 'bearer-meta' not in bbody and '<div>' in bbody:
            parts = [x.strip() for x in pp['meta'].split('·')]
            meta = '<span>·</span>'.join(f'<span>{H.escape(x)}</span>' for x in parts)
            return f'<li><strong>{H.escape(pp["name"])}</strong><div>{meta}</div><div>{H.escape(pp["note"])}{tag}</div></li>'
        return f'<li><strong>{H.escape(pp["name"])}</strong> <span class="bearer-meta">({H.escape(pp["meta"])})</span>. {H.escape(pp["note"])}{tag}</li>'
    if pilot0.get('add'):
        if '</ul>' not in bbody:
            raise Skip('no bearer list to add to')
        k = bbody.rindex('</ul>')
        bbody = bbody[:k] + ''.join(person_li(pp) for pp in pilot0['add']) + bbody[k:]
    nb = len(re.findall(r'<li\b', bbody))
    if pilot:
        nb = sum(len(gp['people']) for gp in pilot.get('groups', [])) or nb
    rail = nb >= 3
    gender_cls = 'girl' if x['g'] == 'Female' else 'boy'
    NM = H.escape(name)
    def card(field, label, cls=''):
        dtx, dd = fields[field]
        return f'<div class="r np-card{cls}"><dt>{dtx}</dt>{dd}</div>'
    gender_dd = fields['gender'][1].replace('data-asr-field="gender"', f'class="rd-tag {gender_cls}" data-asr-field="gender"', 1)
    out = []
    out.append(hero)
    out.append(f'<div class="asr-answer np-answer" aria-label="Quick answer about {NM}">'
               f'{ans_script}<dl class="asr-answer-rows np-cards">'
               f'{card("meaning-dict", "Meaning")}{card("origin", "Origin") if "origin" in fields else ""}'
               f'<div class="r np-card"><dt>{fields["gender"][0]}</dt>{gender_dd}</div>'
               f'<div class="r np-card np-card-ur"><dt>{fields["urdu-meaning"][0]}</dt>{fields["urdu"][1]}{fields["urdu-meaning"][1]}</div>'
               f'</dl>'
               + (f'<section class="np-pron" aria-labelledby="np-pron-h"><h2 id="np-pron-h" class="np-h2-small">{pron_title}</h2>'
                  f'<dl class="np-pron-dl"><div class="r"><dt>{fields["pronunciation"][0]}</dt>{fields["pronunciation"][1]}</div>{"".join(extra_rows)}</dl>'
                  f'{pron_box}</section>' if 'pronunciation' in fields else
                  (f'<section class="np-pron">{"<h2 class=\"np-h2-small\">" + pron_title + "</h2>" if pron_h else ""}<dl class="np-pron-dl">{"".join(extra_rows)}</dl>{pron_box}</section>' if extra_rows or pron_box or pron_h else ''))
               + f'{islamic}</div>')
    if pilot and pilot.get('dyk'):
        out.append(f'<a class="np-dyk" href="#origin"><span class="np-dyk-k">Did you know</span><span class="np-dyk-t">{H.escape(pilot["dyk"])}</span>'
                   f'<span class="np-dyk-go">Origin and history &darr;</span>'
                   + (f'<span class="np-dyk-src">Source: {H.escape(pilot["dyk_source"])}{" " + DRAFT if DRAFT else ""}</span>' if pilot.get('dyk_source') else '') + '</a>')
    jumps = ['<a href="#reading">Letter reading</a>', '<a href="#origin">How it was formed</a>', '<a href="#story">Story</a>']
    if rail:
        jumps.append(f'<a href="#famous">Famous {NM}s</a>')
    jumps += ['<a href="#kit">Parent kit</a>', '<a href="#faq">Questions</a>']
    # a div with the navigation role, not <nav>: the pages' older inline styles make every bare <nav> a sticky header bar
    out.append(f'<div class="np-jump" role="navigation" aria-label="On this page"><div class="np-jump-in">{"".join(jumps)}'
               f'<a class="np-jump-reading" href="#reading">{jump_text}</a></div></div>')
    g = []
    # 01 letters
    edge = (f'<div class="np-edge"><p class="rd-kicker">Growth edge {DRAFT}</p><p>{H.escape(pilot["edge"])}</p></div>'
            if pilot and pilot.get('edge') else '')
    g.append(f'<section id="reading" class="np-sec np-letters"><p class="rd-kicker">01 · {lk}</p>'
             f'<h2 class="rd-h2">{NM}: letter-by-letter reading</h2><h3 class="np-h3">{lt}</h3>{lbody}'
             f'<div class="np-portrait-row"><div class="np-portrait"><p class="rd-kicker"><span class="np-my">Your portrait</span><span class="np-baby">Your child\'s portrait</span> · {sk}</p>'
             f'<h3 class="np-h3">{st}</h3>{sbody}{edge}{iuh_row}</div>{lucky_card(gl, lucky_pub)}</div></section>')
    # 02 origin and history: numbered stops, each only with content
    src = re.search(r'asr-source-line', rbody)
    qrefs = []
    for r_ in re.findall(r'\b(\d{1,3}:\d{1,3})\b', text_of(quranic)):
        if r_ not in qrefs:
            qrefs.append(r_)
    def foot(conf, source):
        if not conf and not source:
            return ''
        return (f'<p class="np-stop-f">{"<span class=\"np-conf\">" + conf + "</span>" if conf else ""}'
                f'{"<span class=\"np-src\">Source: " + H.escape(source) + "</span>" if source else ""}</p>')
    def stop(title, sub, inner):
        return (f'<li class="np-stop"><div class="np-stop-h"><span class="np-stop-t">{title}</span>'
                f'{"<span class=\"np-stop-sub\">" + sub + "</span>" if sub else ""}</div>{inner}</li>')
    stops = []
    if pilot and pilot.get('born'):
        bn = pilot['born']
        stops.append(stop('Born', H.escape(bn['sub']), f'<p class="np-stop-p">{H.escape(bn["text"])}</p>{foot("Established", bn["source"])}{DRAFT}'))
    fv = ''
    if pilot and pilot.get('formed_verse'):
        fv = (f'<div class="np-verse-mini"><span lang="ar" dir="rtl">{pilot["formed_verse"]["ar"]}</span>'
              f'<p>{pilot["formed_verse"]["html"]}</p>{DRAFT}</div>')
    stops.append(stop('Formed', rk, f'<h3 class="np-h3">{rt}</h3>{rbody}{fv}{foot("Established" if src else "", "")}'))
    if text_of(quranic):
        stops.append(stop('Blessed', 'Quran', f'{quranic}{foot("Established" if qrefs else "", ("Quran " + ", ".join(qrefs[:4])) if qrefs else "")}'))
    trav = spell + nostyle(blocks['VARIATIONS'] + blocks['ASRLINK'])
    if text_of(trav):
        th = ''
        if pilot and pilot.get('travelled'):
            tv = pilot['travelled']
            th = f'<p class="np-stop-p">{H.escape(tv["text"])}</p>{foot("Established", tv["source"])}{DRAFT}'
        stops.append(stop('Travelled', 'Spellings and variants', th + trav))
    g.append(f'<section id="origin" class="np-sec np-journey"><p class="rd-kicker">02 · How the name was formed</p>'
             f'<h2 class="rd-h2">{NM}: origin and history</h2><ol class="np-stops">{"".join(stops)}</ol></section>')
    # famous bearers: a section in the page flow when there are 3 or more; otherwise they stay inside the story
    if rail:
        if pilot and pilot.get('groups'):
            grp = ''
            for gp in pilot['groups']:
                lis = ''
                for pp in gp['people']:
                    if isinstance(pp, dict) and 'existing' in pp:
                        mm = re.search(r'<li\b[^>]*>(?:(?!</li>).)*' + re.escape(pp['existing']) + r'.*?</li>', bbody, re.S)
                        if not mm:
                            raise Skip('pilot bearer not on page: ' + pp['existing'])
                        lis += mm.group(0)
                    else:
                        lis += person_li(pp)
                grp += f'<div class="np-pg"><h3 class="np-pg-h">{H.escape(gp["label"])}</h3><ul class="bearers-list">{lis}</ul></div>'
            used = text_of(grp)
            for li in re.findall(r'<li\b.*?</li>', bbody, re.S):
                if text_of(li) not in used:
                    raise Skip('existing bearer missing from pilot list: ' + text_of(li)[:40])
            people = grp
        else:
            people = f'<div class="np-pg">{bbody}</div>'
        g.append(f'<section id="famous" class="np-sec np-famous" aria-labelledby="np-famous-h"><p class="rd-kicker">{bk or "Bearers"}</p>'
                 f'<h2 id="np-famous-h" class="rd-h2">Famous {NM}s</h2>{"<h3 class=\"np-h3\">" + bt + "</h3>" if bt else ""}'
                 f'<div class="np-people">{people}</div>'
                 + (f'<p class="np-people-note">Only people with a verifiable source are listed. {DRAFT}</p>' if pilot and pilot.get("groups") else '')
                 + '</section>')
    story_bearers = '' if rail or not bbody else f'<div class="np-bearers"><p class="rd-kicker">{bk}</p><h3 class="np-h3">{bt}</h3>{bbody}</div>'
    g.append(f'<section id="story" class="np-sec np-story"><p class="rd-kicker">03 · {dk}</p>'
             f'<h2 class="rd-h2">The story of the name {NM}</h2><h3 class="np-h3">{dt}</h3>{dbody}{story_bearers}</section>')
    # 04 parent kit: a short invitation in "my name" mode, the kit itself in baby mode
    # sibling chips come from the "parents who searched this name also found" row (the small cards)
    sib = re.findall(r'<a href="(/names/[a-z0-9-]+/)" class="related-card[^"]* sm"', blocks['RELATED'])[:8]
    sib_links = ''
    for href in sib:
        s2 = href.split('/')[2]
        if s2 in IDX:
            t = 'girl' if IDX[s2]['g'] == 'Female' else 'boy'
            sib_links += f'<a class="np-sib rd-tag {t}" href="{href}">{H.escape(IDX[s2]["n"])}</a>'
    pron_txt = text_of(fields['pronunciation'][1]) if 'pronunciation' in fields else ''
    variants = re.findall(r'<a href="(/names/[a-z0-9-]+/)" class="spelling-chip" data-variant>([^<]+)</a>', spell)
    kit = ([f'<div class="np-kit-box"><h3 class="np-h3">Say it right</h3><p class="np-say">{H.escape(pron_txt)}</p>'
           f'<p class="np-kit-note">Stress and vowel length are in the pronunciation guide above.</p></div>'] if pron_txt else []) + [
           f'<div class="np-kit-box"><h3 class="np-h3">Try it with your surname</h3>'
           f'<label class="np-kit-label" for="np-surname">Your surname</label><input id="np-surname" class="np-input" type="text" autocomplete="off" maxlength="40" placeholder="e.g. Ali">'
           f'<p class="np-kit-out" aria-live="polite" data-np-first="{NM}"><span class="np-full">{NM}</span> <span class="np-initials"></span></p>'
           f'<p class="np-kit-note">Nothing you type leaves this page.</p></div>']
    if sib_links:
        kit.append(f'<div class="np-kit-box"><h3 class="np-h3">Pairs well for siblings</h3><p class="np-kit-note">Parents who looked at {NM} also looked at</p><p class="np-sibs">{sib_links}</p></div>')
    if variants:
        vl = ', '.join(f'<a href="{hf}">{H.escape(vn)}</a>' for hf, vn in variants)
        kit.append(f'<div class="np-kit-box"><h3 class="np-h3">Choosing the spelling</h3><p class="np-kit-p"><strong>{NM}</strong> is the spelling on this page. '
                   f'Other spellings with their own reading: {vl}.</p></div>')
    g.append(f'<section id="kit" class="np-sec np-kit" aria-labelledby="np-kit-h"><p class="rd-kicker">04 · For parents</p>'
             f'<h2 id="np-kit-h" class="rd-h2">Parent kit: naming a baby {NM}</h2>'
             f'<div class="np-kit-teaser np-my"><p>Naming a baby? Switch to the parent view for pronunciation, a surname test and sibling names.</p>'
             f'<button type="button" class="np-go" data-np-go="baby">Open parent view</button></div>'
             f'<div class="np-kit-grid np-baby">{"".join(kit)}</div></section>')
    # 05 share: a preview of the card beside the existing share block (same markup and IDs)
    if share:
        ar_name = re.search(r'<div class="asr-name-hero-arabic"[^>]*>(.*?)</div>', hero, re.S)
        sub_t = re.search(r'<div class="asr-name-hero-sub">(.*?)</div>', hero, re.S)
        mock = (f'<div class="np-cardmock" aria-hidden="true"><span class="np-cm-k">AsrNaam · Ilm ul Huroof</span>'
                f'<span class="np-cm-ar" lang="ar" dir="rtl">{ar_name.group(1) if ar_name else ""}</span><span class="np-cm-n">{NM}</span>'
                f'<span class="np-cm-s">{text_of(sub_t.group(1)) if sub_t else ""}</span><span class="np-cm-f">asrnaam.com</span></div>')
        g.append(f'<section id="share" class="np-sec np-keep" aria-labelledby="np-keep-h">{mock}<div class="np-keep-b">'
                 f'<h2 id="np-keep-h" class="rd-h2">Keep your {NM} name card</h2>{share}</div></section>')
    if pilot and pilot.get('dua'):
        g.append(f'<section class="np-dua" aria-labelledby="np-dua-h"><svg aria-hidden="true" width="32" height="32" viewBox="0 0 72 72" fill="none" stroke="currentColor" stroke-width="2.4">'
                 f'<rect x="18" y="18" width="36" height="36"/><rect x="18" y="18" width="36" height="36" transform="rotate(45 36 36)"/><circle cx="36" cy="36" r="7"/></svg>'
                 f'<h2 id="np-dua-h">A dua for every {NM}</h2><p>{H.escape(pilot["dua"])}</p>{DRAFT}</section>')
    # next-name box
    nxt = nostyle(blocks['OBS-CALLOUT'] + blocks['INLINE-RA'] + blocks['HERO-RA']) + cta
    if text_of(nxt):
        g.append(f'<div class="np-next">{nxt}</div>')
    # 06 FAQ (its own label and heading stay; the number is added by CSS)
    faq_head = '' if faq_h2 else f'<p class="rd-kicker">06 · Frequently Asked Questions</p><h2 class="rd-h2">About the name {NM}</h2>'
    g.append(f'<section id="faq" class="np-sec np-faq{"" if faq_h2 else " np-faq-b"}">{faq_head}{faq}{loose_styles}</section>')
    # more names like X
    more = nostyle(loose_related) + blocks['RELATED'] + blocks['SHARED'] + blocks['ASRMORE'] + blocks['THEMES'] + blocks['LETTERCLUSTER']
    g.append(f'<section class="np-sec np-more"><h2 class="rd-h2">More names like {NM}</h2>{more}</section>')
    g.append(blocks['TRUST'])
    if community:
        g.append(community)
    out.append(f'<div class="np-grid">{"".join(g)}</div>')
    if blocks['QURANIC'] and text_of(blocks['QURANIC']):
        raise Skip('second QURANIC block has text')
    new_body = '\n' + '\n'.join(out) + '\n'
    # the np- rules style every moved block, so the old style blocks and inline styles inside the article are dead weight;
    # a style that picks an Arabic or Urdu typeface stays
    new_body = re.sub(r'<style\b.*?</style>', '', new_body, flags=re.S)
    new_body = re.sub(r' style="([^"]*)"', lambda m: m.group(0) if re.search(r'Amiri|Naskh|Nastaliq', m.group(1)) else '', new_body)
    # version the two changed files on this page, so a stored copy of the old stylesheet can never be used with the new markup
    pre = re.sub(r'(asr-redesign\.(?:css|js)\?v=)[0-9a-z]+', r'\g<1>' + VER, pre)
    post = re.sub(r'(asr-redesign\.(?:css|js)\?v=)[0-9a-z]+', r'\g<1>' + VER, post)
    page = pre + new_body + post
    # mode switch in the breadcrumb row
    switch = ('<div class="np-mode" role="group" aria-label="Who are you reading for">'
              '<button type="button" class="np-mode-b" data-np-mode="me" aria-pressed="true">This is my name</button>'
              '<button type="button" class="np-mode-b" data-np-mode="baby" aria-pressed="false">I\'m naming a baby</button></div>')
    # the page's own stylesheet loads here, in the body after the site header: the header never waits for it,
    # and pages that are not migrated never fetch it
    if '<!-- ASR:BREADCRUMB:START -->' not in page:
        raise Skip('no breadcrumb marker')
    page = page.replace('<!-- ASR:BREADCRUMB:START -->', f'<link rel="stylesheet" href="/asr-np.css?v={VER}"><div class="np-crumbrow"><!-- ASR:BREADCRUMB:START -->', 1)
    page = page.replace('<!-- ASR:BREADCRUMB:END -->', '<!-- ASR:BREADCRUMB:END -->' + switch + '</div>', 1)
    return page, dict(old_hero=old_hero, rail=rail, bearers=nb, letters=len(gl), pilot=bool(pilot))


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
