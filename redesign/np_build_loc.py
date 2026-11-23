"""AsrNaam name page redesign, translated pages (Urdu and Arabic template family).

Moves the existing blocks of a translated name page into the new layout used by the English pages.
Every block is cut from the page as raw HTML and pasted unchanged. Only wrappers, the mode switch and
the interface labels listed in redesign/locale/<locale>.json are added. The <head> is never touched
(apart from the version tag of asr-redesign.css). No Arabic-script or Urdu-script spelling is changed.

usage: python3 redesign/np_build_loc.py <locale> slug [slug ...] [--write] [--final] [--base=REF] [--no-pilot]   (from the repo root)
Without --write it only reports. --base=REF builds from the page as it is on that commit (to rebuild a page
that is already migrated in the working tree). --no-pilot builds the layout only, ignoring the content file. --final leaves out the "for review" tags on content added from
redesign/pilot/<locale>/<slug>.json (same keys as the English pilot files: page_fixes, fixes, drop, add,
groups, dyk, dyk_source). Anything the builder cannot place raises Skip: the page is then left alone."""
import re, sys, os, json, html as H

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from np_build import Skip, div_end, cut_div, nostyle, text_of, ABJAD, VER, IDX   # same helpers as the English builder

FINAL = '--final' in sys.argv
PILOT_KEYS = {'page_fixes', 'fixes', 'drop', 'add', 'groups', 'dyk', 'dyk_source'}
REVIEW_KEYS = {'gaps', 'needs_review', 'left_out'}   # notes for the reviewer, not for the builder (as are keys starting with _)
DIV = re.compile(r'<div class="asr-v2-divider".*?</div>', re.S)
COMMENT = re.compile(r'<!--.*?-->', re.S)


def locale(loc):
    return json.load(open(f'redesign/locale/{loc}.json', encoding='utf8'))


def pilot_of(loc, slug):
    p = f'redesign/pilot/{loc}/{slug}.json'
    return json.load(open(p, encoding='utf8')) if os.path.exists(p) and '--no-pilot' not in sys.argv else {}


def digits(n, L, key='digits'):
    d = L.get(key) or '0123456789'
    return ''.join(d[int(c)] if c.isdigit() else c for c in str(n))


def to_int(s):
    """number written in Western, Arabic-Indic or Urdu digits"""
    t = ''.join(str('٠١٢٣٤٥٦٧٨٩'.index(c)) if c in '٠١٢٣٤٥٦٧٨٩' else str('۰۱۲۳۴۵۶۷۸۹'.index(c)) if c in '۰۱۲۳۴۵۶۷۸۹' else c for c in s)
    return int(t) if t.isdigit() else None


def sections(layout):
    """the <section class="asr-v2 ..."> blocks of the old layout, in page order, keyed by their second class.
    Person pages carry several biography sections (asr-v2-bio), each with its own heading and text: those come back
    as a list, in page order. Any other section may appear once."""
    out, bios, rest = {}, [], layout
    for m in re.finditer(r'<section class="asr-v2 ([a-z0-9-]+)"[^>]*>.*?</section>', layout, re.S):
        if '<section' in m.group(0)[8:]:
            raise Skip('nested section in ' + m.group(1))
        if m.group(1) == 'asr-v2-bio':
            if any(text_of(m.group(0)) == text_of(b) for b in bios):
                raise Skip('biography section repeated with the same text')
            bios.append(m.group(0))
        elif m.group(1) in out:
            raise Skip('section twice: ' + m.group(1))
        else:
            out[m.group(1)] = m.group(0)
        rest = rest.replace(m.group(0), '', 1)
    return out, bios, rest


LOOSE = re.compile(r'<p class="section-label"[^>]*>(.*?)</p>\s*<h2[^>]*>(.*?)</h2>\s*(?=<div class="prose">)', re.S)


def loose_blocks(body, L):
    """the older Arabic pages have no layout wrapper: their sections are a label, a heading and a text box in a row.
    Returns [(role, label, heading, text box)] in page order and the body without them. A label that is not listed
    in the locale file under "loose" is not guessed at."""
    out = []
    while True:
        m = LOOSE.search(body)
        if not m:
            return out, body
        box, _ = cut_div(body, m.end())
        role = L.get('loose', {}).get(text_of(m.group(1)))
        if not role:
            raise Skip('loose section label not understood: ' + text_of(m.group(1))[:40])
        out.append((role, m.group(1), m.group(2), box))
        body = body[:m.start()] + body[m.end() + len(box):]


def parts(sec, L):
    """(kicker without its old number, title, body) of an old section"""
    if not sec:
        return '', '', ''
    body = re.sub(r'^<section[^>]*>', '', sec)
    body = re.sub(r'</section>$', '', body)
    k = re.search(r'<p class="asr-v2-kicker">(.*?)</p>', body, re.S)
    t = re.search(r'<h2 class="asr-v2-title">(.*?)</h2>', body, re.S)
    if k:
        body = body.replace(k.group(0), '', 1)
    if t:
        body = body.replace(t.group(0), '', 1)
    kick = re.sub(L['kicker_number'], '', k.group(1)) if k else ''   # old numbering removed: sections are renumbered
    return kick, (t.group(1) if t else ''), COMMENT.sub('', body).strip()


def build(h, loc, slug):
    L = locale(loc)
    T = L['labels']
    pilot = pilot_of(loc, slug)
    ignored = sorted(k for k in pilot if k not in PILOT_KEYS and k not in REVIEW_KEYS and not k.startswith('_'))
    draft = '' if FINAL else f'<span class="np-draft">{T["draft"]}</span>'
    for fx in pilot.get('page_fixes', []):
        if fx['old'] not in h:
            raise Skip('page fix not found: ' + fx['old'][:40])
        h = h.replace(fx['old'], fx['new'])
    if 'asr-np' in h:
        raise Skip('already migrated')
    if h.count('<article>') != 1 or h.count('<h1') != 1:
        raise Skip('article or h1 count')
    a1 = h.index('<article>') + len('<article>')
    closed = '</article>' in h[a1:]
    a2 = h.index('</article>', a1) if closed else h.index('</main>', a1)   # the Arabic pages never close <article>
    pre, body, post = h[:a1], h[a1:a2], h[a2:]
    for d in pilot.get('drop', []):
        m = re.search(r'<li\b(?:(?!</li>).)*?' + re.escape(d['match']) + r'(?:(?!</li>).)*</li>', body, re.S)
        if not m or body.count(d['match']) != 1:
            raise Skip('pilot drop not found once: ' + d['match'][:40])
        body = body[:m.start()] + body[m.end():]
    for fx in pilot.get('fixes', []):
        if body.count(fx['old']) != fx.get('count', body.count(fx['old']) or -1):
            raise Skip(f'pilot fix found {body.count(fx["old"])} times, not {fx.get("count", "1 or more")}: ' + fx['old'][:40])
        new = fx['new']
        if draft and text_of(new) and text_of(new) != text_of(fx['old']):
            # changed wording carries the review tag, placed before the closing tags the replacement ends with
            m = re.search(r'(?:\s*</[a-z0-9]+>)*\s*$', new)
            new = new[:m.start()] + ' ' + draft + new[m.start():]
        body = body.replace(fx['old'], new)

    # ---- hero
    if body.count('<div class="hero">') != 1:
        raise Skip('hero count')
    hero, body = cut_div(body, body.index('<div class="hero">'))
    ar = re.search(r'<div class="arabic-name"([^>]*)>(.*?)</div>', hero, re.S)
    badge = re.search(r'<div class="name-badge">(.*?)</div>', hero, re.S)
    h1 = re.search(r'<h1>(.*?)</h1>', hero, re.S)
    sub = re.search(r'<p class="hero-subtitle">(.*?)</p>', hero, re.S)
    if not (ar and h1):
        raise Skip('hero lacks the name or the h1')
    left = hero
    for m in (ar, badge, h1, sub):
        if m:
            left = left.replace(m.group(0), '', 1)
    if text_of(left):
        raise Skip('unplaced hero content: ' + text_of(left)[:60])
    name = text_of(ar.group(2))
    ar_attrs = ar.group(1) if 'dir=' in ar.group(1) else ar.group(1) + ' dir="rtl"'

    # ---- quick facts
    qf = re.search(r'<aside class="quick-facts"([^>]*)>(.*?)</aside>', body, re.S)
    if not qf and body.count('<div class="quick-facts">') == 1:      # the Arabic person pages use a <div> for the same box
        q0 = body.index('<div class="quick-facts">')
        qf = re.compile(r'<div class="quick-facts"([^>]*)>(.*)</div>', re.S).fullmatch(body, q0, div_end(body, q0))
    if not qf or body.count('class="quick-facts"') != 1:
        raise Skip('quick facts count')
    body = body.replace(qf.group(0), '', 1)
    qf_aria = re.search(r'aria-label="([^"]*)"', qf.group(1))
    rows, known = {}, {v: k for k, v in L['qf'].items()}
    known.update(L.get('qf_alt', {}))   # older wording of a label that is still on pages not yet corrected
    qleft = qf.group(2)
    for m in re.finditer(r'<div class="qf-row[^"]*"[^>]*><span class="qf-label">([^<]*)</span><span class="qf-value">(.*?)</span></div>', qf.group(2), re.S):
        if m.group(1) not in known:
            raise Skip('quick fact not understood: ' + m.group(1))
        if known[m.group(1)] in rows:
            raise Skip('quick fact twice: ' + m.group(1))
        rows[known[m.group(1)]] = (m.group(1), nostyle(m.group(2)))
        qleft = qleft.replace(m.group(0), '', 1)
    if text_of(qleft):
        raise Skip('unplaced quick fact: ' + text_of(qleft)[:60])
    for need in ('meaning', 'gender'):
        if need not in rows:
            raise Skip('quick facts lack ' + need)
    # the name inside interface sentences is the page's own spelling in the page language (its quick-fact row), unvocalised hero form otherwise
    if L.get('name_row') in rows and text_of(rows[L['name_row']][1]):
        name = text_of(rows[L['name_row']][1])

    # ---- old layout sections
    repairs = []            # faults of the old markup that the new page does not carry over; the check reports each
    mq_loose, tail, more_syn, bios = '', '', [], []
    n_layout = body.count('<div class="asr-layout-v2">')
    if n_layout == 1:
        layout, body = cut_div(body, body.index('<div class="asr-layout-v2">'))
        secs, bio_secs, lrest = sections(layout)
        lrest = COMMENT.sub('', DIV.sub('', lrest))
        if lrest.count('<div class="asr-mq">') == 1 and not any('<div class="asr-mq">' in x for x in secs.values()):
            # the "is it an Islamic name" box sits between two sections on some Arabic pages, not inside the first one
            mq_loose, lrest = cut_div(lrest, lrest.index('<div class="asr-mq">'))
        if text_of(lrest):
            raise Skip('unplaced layout content: ' + text_of(lrest)[:60])
        unknown = set(secs) - {'asr-v2-root', 'asr-v2-letters', 'asr-v2-synthesis', 'asr-v2-dict', 'asr-v2-bearers', 'asr-v2-pron', 'asr-v2-variants', 'asr-faq', 'asr-crosslang'}
        if unknown:
            raise Skip('section not understood: ' + ', '.join(sorted(unknown)))
        for need in ('asr-v2-letters', 'asr-faq'):
            if need not in secs:
                raise Skip('page lacks ' + need)
        rk, rt, rbody = parts(secs.get('asr-v2-root'), L)
        lk, lt, lbody = parts(secs.get('asr-v2-letters'), L)
        sk, st, sbody = parts(secs.get('asr-v2-synthesis'), L)
        dk, dt, dbody = parts(secs.get('asr-v2-dict'), L)
        bk, bt, bbody = parts(secs.get('asr-v2-bearers'), L)
        pk, pt, pbody = parts(secs.get('asr-v2-pron'), L)
        vk, vt, vbody = parts(secs.get('asr-v2-variants'), L)
        _, ft, fbody = parts(secs['asr-faq'], L)
        _, _, cbody = parts(secs.get('asr-crosslang'), L)
        for b in bio_secs:
            k0, t0, b0 = parts(b, L)
            if not t0 or not text_of(b0):
                raise Skip('biography section without a heading or without text')
            bios.append((k0, t0, b0))
    elif n_layout == 0:
        # the older Arabic pages: one letters section, the Islamic-name box, then label + heading + text box in a row,
        # closing links, and the language bar after </article>. They carry no FAQ.
        if body.count('<section class="asr-v2 asr-v2-letters">') != 1 or body.count('<section') != 1:
            raise Skip('older page: letters section count')
        m = re.search(r'<section class="asr-v2 asr-v2-letters">.*?</section>', body, re.S)
        lk, lt, lbody = parts(m.group(0), L)
        body = body.replace(m.group(0), '', 1)
        if body.count('<div class="asr-mq">') != 1:
            raise Skip('older page: Islamic-name box count')
        mq_loose, body = cut_div(body, body.index('<div class="asr-mq">'))
        if body.count('<div class="cta-row">') == 1:
            tail, body = cut_div(body, body.index('<div class="cta-row">'))
        else:
            m = re.search(r'<aside\b[^>]*>\s*<p>(?:(?!</p>).)*</p>\s*</aside>', body, re.S)
            if m and body.count('<aside') == 1:
                tail, body = m.group(0), body.replace(m.group(0), '', 1)
        if not re.search(r'<a [^>]*href=', tail):
            raise Skip('older page: closing links not found')
        blocks, body = loose_blocks(body, L)
        by = {}
        for role, lab, ttl, box in blocks:
            by.setdefault(role, []).append((lab, ttl, box))
        if any(len(by.get(r, [])) > 1 for r in ('dict', 'root')):
            raise Skip('older page: a section appears twice')
        dk, dt, dbody = by['dict'][0] if 'dict' in by else ('', '', '')
        rk, rt, rbody = by['root'][0] if 'root' in by else ('', '', '')
        syn = by.get('syn', [])
        sk, st, sbody = syn[0] if syn else ('', '', '')
        more_syn = syn[1:]
        bios = by.get('bio', [])
        bk = bt = bbody = pk = pt = pbody = vk = vt = vbody = ft = fbody = ''
        # after </article>: on some pages the related names (between their markers), then the language bar
        after = post[len('</article>'):]
        k = len(after) - len(after.lstrip())
        if after.startswith('<!-- AR-RELATED:START -->', k):
            r0 = after.index('<div class="related-section"', k) if '<div class="related-section"' in after else -1
            if r0 < 0 or after[k + len('<!-- AR-RELATED:START -->'):r0].strip():
                raise Skip('older page: related names after the article not understood')
            r1 = div_end(after, r0)
            m = re.match(r'\s*<!-- AR-RELATED:END -->', after[r1:])
            if not m:
                raise Skip('older page: related names after the article not closed by their marker')
            body += after[r0:r1]
            after = after[:k] + after[r1 + m.end():]
            repairs.append('related names moved from after the article into it')
        m = re.match(r'\s*(<section class="asr-v2 asr-crosslang">(.*?)</section>)', after, re.S)
        if not m:
            raise Skip('older page: language bar not found right after the article')
        cbody = m.group(2)
        post = '</article>' + after[m.end():]
        repairs.append('language bar moved from after the article into the hero')
    else:
        raise Skip('layout count')

    # ---- related names (wrapped on the Urdu pages, loose on the Arabic pages) and what is left
    rest = body
    rel_label, related = '', ''
    if '<div class="related-section"' in rest:
        related, rest = cut_div(rest, rest.index('<div class="related-section"'))
        related = re.sub(r'^<div class="related-section"[^>]*>', '', related)[:-len('</div>')]
    else:
        m = re.search(r'<p class="section-label"[^>]*>.*?</p>\s*<div class="related-grid">.*?</div>(?:\s*<p[^>]*><a [^>]*>[^<]*</a></p>)?', rest, re.S)
        if m:
            related, rest = m.group(0), rest.replace(m.group(0), '', 1)
    if related:
        m = re.search(r'<p class="section-label"[^>]*>(.*?)</p>', related, re.S)
        if not m:
            raise Skip('related names lack their label')
        rel_label, related = m.group(1), nostyle(related.replace(m.group(0), '', 1)).strip()
    rest = COMMENT.sub('', rest)
    rest = re.sub(r'<div class="content">|</div>', '', rest)
    if rest.strip():
        raise Skip('unplaced content: ' + (text_of(rest) or rest.strip())[:60])

    # ---- pieces
    mq = mq_loose
    if '<div class="asr-mq">' in rbody:
        if mq:
            raise Skip('two Islamic-name boxes')
        mq, rbody = cut_div(rbody, rbody.index('<div class="asr-mq">'))
    bbody = nostyle(bbody)
    def person_li(pp):
        if isinstance(pp, (list, tuple)):
            pp = dict(name=pp[0], meta=pp[1], note=pp[2])
        meta = '<span>·</span>'.join(f'<span>{H.escape(x.strip())}</span>' for x in pp.get('meta', '').split('·') if x.strip())
        return (f'<li><strong>{H.escape(pp["name"])}</strong>' + (f'<div>{meta}</div>' if meta else '')
                + f'<div>{H.escape(pp.get("note", ""))}{(" " + draft) if draft else ""}</div></li>')
    if pilot.get('add'):
        new_li = ''.join(person_li(pp) for pp in pilot['add'])
        if '</ul>' in bbody:
            k = bbody.index('</ul>')
            bbody = bbody[:k] + new_li + bbody[k:]
        else:
            bbody += f'<ul class="bearers-list">{new_li}</ul>'
            bk, bt = bk or T['bearers_kicker'], bt or T['bearers_title']
    nb = len(re.findall(r'<li\b', bbody))
    people = ''
    if pilot.get('groups'):
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
            people += f'<div class="np-pg"><h3 class="np-pg-h">{H.escape(gp["label"])}{(" " + draft) if draft else ""}</h3><ul class="bearers-list">{lis}</ul></div>'
        used = text_of(people.replace(draft, '')) if draft else text_of(people)
        for li in re.findall(r'<li\b.*?</li>', bbody, re.S):
            if text_of(li) not in used:
                raise Skip('existing bearer missing from pilot list: ' + text_of(li)[:40])
        nb = sum(len(gp['people']) for gp in pilot['groups'])
        bk, bt = bk or T['bearers_kicker'], bt or T['bearers_title']
    elif bbody:
        people = f'<div class="np-pg">{bbody}</div>'
    famous = nb >= 3
    gender_cls = 'girl' if rows['gender'][1] in L['female'] else 'boy' if rows['gender'][1] in L['male'] else ''
    kit_on = bool(L.get('kit'))
    num = iter(range(1, 20))
    def n():
        return digits(f'{next(num):02d}', L)

    out = []
    # hero: the same markup as the English hero, with the page's own texts
    cl = re.search(r'<p class="prose">(.*?)</p>', cbody, re.S)
    if cbody and not cl:
        cl = re.fullmatch(r'<p class="prose">([^<]*(?:<a [^>]*>[^<]*</a>[^<]*)+)', cbody.strip(), re.S)
        if cl:
            repairs.append('language bar paragraph had no closing tag: closed')
    out.append(f'<header class="asr-name-hero">'
               + (f'<p class="asr-name-hero-kicker">{badge.group(1).strip()}</p>' if badge else '')
               + f'<div class="asr-name-hero-arabic"{ar_attrs}>{ar.group(2)}</div><h1 class="asr-name-hero-roman">{h1.group(1)}</h1>'
               + (f'<div class="asr-name-hero-sub">{sub.group(1)}</div>' if sub else '')
               + (f'<p class="asr-name-hero-langs">{cl.group(1)}</p>' if cl else '') + '</header>')
    if cbody and not cl:
        raise Skip('language links not understood')

    # answer: four cards, the pronunciation strip, the "is it an Islamic name" paragraph
    def card(key, cls='', dd_attr=''):
        lab, val = rows[key]
        return f'<div class="r np-card{cls}"><dt>{lab}</dt><dd{dd_attr}>{val}</dd></div>'
    cards = card('meaning') + (card('origin') if 'origin' in rows else '')
    cards += card('gender', dd_attr=f' class="rd-tag {gender_cls}"' if gender_cls else '')
    sp = ''.join(f'<dt>{rows[k][0]}</dt><dd>{rows[k][1]}</dd>' for k in ('urdu', 'arabic') if k in rows)
    if sp:
        cards += f'<div class="r np-card np-card-sp">{sp}</div>'
    prow = ''
    if 'pron' in rows:
        prow += f'<div class="r"><dt>{rows["pron"][0]}</dt><dd dir="ltr" lang="en">{rows["pron"][1]}</dd></div>'
    if 'root' in rows:
        prow += f'<div class="r"><dt>{rows["root"][0]}</dt><dd>{rows["root"][1]}</dd></div>'
    for k2 in rows:
        if k2.startswith('x_'):     # further facts of a person page (dates, region, field), in page order
            prow += f'<div class="r"><dt>{rows[k2][0]}</dt><dd>{rows[k2][1]}</dd></div>'
    pron_box = ''
    if pbody:
        if re.fullmatch(r'<p>[^<]+</p>', pbody):
            pron_box = f'<div class="np-pron-note">{pbody}</div>'      # a single plain sentence, kept as it is
        elif not pbody.startswith('<div class="asr-pron"') or div_end(pbody, 0) != len(pbody):
            raise Skip('pronunciation block not understood')
        else:
            pron_box = nostyle(pbody.replace('<div class="asr-pron"', '<div class="asr-pron asr-pronunciation"', 1))
    pron = ''
    if prow or pron_box:
        pron = ('<section class="np-pron"' + (' aria-labelledby="np-pron-h"' if pt else '') + '>'
                + (f'<h2 id="np-pron-h" class="np-h2-small">{pt}</h2>' if pt else '')
                + (f'<dl class="np-pron-dl">{prow}</dl>' if prow else '') + pron_box + '</section>')
    out.append(f'<div class="asr-answer np-answer"' + (f' aria-label="{qf_aria.group(1)}"' if qf_aria else '') + '>'
               f'<dl class="np-cards">{cards}</dl>{pron}{mq}</div>')
    origin_label = rows['origin'][0] if 'origin' in rows else rk
    if pilot.get('dyk'):
        out.append(f'<a class="np-dyk" href="#origin"><span class="np-dyk-k">{T["dyk"]}</span><span class="np-dyk-t">{H.escape(pilot["dyk"])}</span>'
                   f'<span class="np-dyk-go">{origin_label} &darr;</span>'
                   + (f'<span class="np-dyk-src">{T["source"]} {H.escape(pilot["dyk_source"])}{" " + draft if draft else ""}</span>' if pilot.get('dyk_source') else '') + '</a>')

    g, jumps = [], []
    # reading: letters, the two letter facts, the synthesis and the abjad card
    facts = ''.join(f'<div class="r"><dt>{rows[k][0]}</dt><dd>{rows[k][1]}</dd></div>' for k in ('count', 'letters') if k in rows)
    gl = [text_of(x) for x in re.findall(r'asr-v2-letter-arabic[^>]*>([^<]+)', lbody)]
    portrait = ''
    if sbody or 'iuh' in rows:
        portrait = ('<div class="np-portrait">'
                    + (f'<p class="rd-kicker">{sk}</p>' if sk else '') + (f'<h3 class="np-h3">{st}</h3>' if st else '') + sbody
                    + ''.join(f'<p class="rd-kicker">{k2}</p><h3 class="np-h3">{t2}</h3>{b2}' for k2, t2, b2 in more_syn)
                    + (f'<p class="rd-kicker">{rows["iuh"][0]}</p><div class="prose"><p>{rows["iuh"][1]}</p></div>' if 'iuh' in rows else '') + '</div>')
    lucky = lucky_card(gl, rows, fbody, L)
    g.append(f'<section id="reading" class="np-sec np-letters"><p class="rd-kicker">{n()} · {lk}</p><h2 class="rd-h2">{lt}</h2>{lbody}'
             + (f'<dl class="np-facts">{facts}</dl>' if facts else '')
             + (f'<div class="np-portrait-row">{portrait}{lucky}</div>' if portrait or lucky else '') + '</section>')
    jumps.append(('reading', lk))
    # origin: the root, then the spellings, as numbered stops
    stops = []
    def stop(title, inner):
        return f'<li class="np-stop"><div class="np-stop-h"><span class="np-stop-t">{title}</span></div>{inner}</li>'
    if text_of(rbody):
        stops.append(stop(rk, rbody))
    elif rt:
        repairs.append('empty section left out (a heading with no text under it): ' + text_of(rt))
    if text_of(vbody):
        stops.append(stop(vk, (f'<h3 class="np-h3">{vt}</h3>' if vt else '') + nostyle(vbody)))
    if stops:
        g.append(f'<section id="origin" class="np-sec np-journey"><p class="rd-kicker">{n()} · {origin_label}</p>'
                 f'<h2 class="rd-h2">{rt or vt}</h2><ol class="np-stops">{"".join(stops)}</ol></section>')
        jumps.append(('origin', origin_label))
    elif pilot.get('dyk'):
        raise Skip('did-you-know strip points at an origin section this page does not have')
    # bearers: their own section with three or more, inside the story otherwise
    if famous:
        g.append(f'<section id="famous" class="np-sec np-famous" aria-labelledby="np-famous-h"><p class="rd-kicker">{bk}</p>'
                 f'<h2 id="np-famous-h" class="rd-h2">{bt}</h2><div class="np-people">{people}</div></section>')
        jumps.append(('famous', bk))
    story_bearers = '' if famous or not people else f'<div class="np-bearers"><p class="rd-kicker">{bk}</p><h3 class="np-h3">{bt}</h3>{people}</div>'
    if text_of(dbody) or story_bearers:
        g.append(f'<section id="story" class="np-sec np-story"><p class="rd-kicker">{n()} · {dk or bk}</p>'
                 f'<h2 class="rd-h2">{dt or bt}</h2>{dbody}{story_bearers}</section>')
        jumps.append(('story', dk or bk))
    # person pages: the biography sections, each under its own heading, in page order
    if bios:
        g.append('<section id="bio" class="np-sec np-story np-bio">'
                 + ''.join((f'<p class="rd-kicker">{k2}</p>' if k2 else '') + f'<h2 class="rd-h2">{t2}</h2>{b2}' for k2, t2, b2 in bios) + '</section>')
        jumps.append(('bio', bios[0][0] or bios[0][1]))
    # parent kit: pronunciation, a surname test, related names (only the surname test is new)
    rel_links = re.findall(r'<a href="(/' + loc + r'/names/([a-z0-9-]+)/)" class="related-card">(?:<span class="related-name">)?([^<]+)', related)
    if kit_on:
        chips = ''
        for href, s2, nm in rel_links[:8]:
            t = (' girl' if IDX[s2]['g'] == 'Female' else ' boy') if s2 in IDX and IDX[s2].get('g') in ('Female', 'Male') else ''
            chips += f'<a class="np-sib rd-tag{t}" href="{href}">{nm}</a>'
        kit = []
        if 'pron' in rows:
            kit.append(f'<div class="np-kit-box"><h3 class="np-h3">{rows["pron"][0]}</h3><p class="np-say" dir="ltr" lang="en">{rows["pron"][1]}</p></div>')
        kit.append(f'<div class="np-kit-box"><h3 class="np-h3">{T["surname_h"]}</h3>'
                   f'<label class="np-kit-label" for="np-surname">{T["surname_label"]}</label><input id="np-surname" class="np-input" type="text" autocomplete="off" maxlength="40">'
                   f'<p class="np-kit-out" aria-live="polite" data-np-first="{H.escape(name)}"><span class="np-full">{H.escape(name)}</span> <span class="np-initials"></span></p>'
                   f'<p class="np-kit-note">{T["surname_note"]}</p></div>')
        if chips:
            kit.append(f'<div class="np-kit-box"><h3 class="np-h3">{rel_label}</h3><p class="np-sibs">{chips}</p></div>')
        kn = n()
        g.append(f'<section id="kit" class="np-sec np-kit" aria-labelledby="np-kit-h"><p class="rd-kicker">{kn} · {T["kit_kicker"]}</p>'
                 f'<h2 id="np-kit-h" class="rd-h2">{T["kit_h2"].replace("{name}", H.escape(name))}</h2>'
                 f'<div class="np-kit-teaser np-my"><p>{T["kit_teaser"]}</p>'
                 f'<button type="button" class="np-go" data-np-go="baby">{T["kit_open"]}</button></div>'
                 f'<div class="np-kit-grid np-baby">{"".join(kit)}</div></section>')
        jumps.append(('kit', T['kit_kicker']))
    # questions: the page's own heading and items, in the bordered list the ad script anchors on
    if n_layout:
        fleft = re.sub(r'<details class="asr-faq-item">.*?</details>', '', fbody, flags=re.S)
        if text_of(fleft) or not ft:
            raise Skip('FAQ block not understood')
        items = ''.join(re.findall(r'<details class="asr-faq-item">.*?</details>', fbody, re.S))
        g.append(f'<section id="faq" class="np-sec np-faq"><h2>{ft}</h2><div class="faq-list">{items}</div></section>')
        jumps.append(('faq', ft))
    if related:
        g.append(f'<section class="np-sec np-more"><h2 class="rd-h2">{rel_label}</h2><div class="related-section">{related}</div></section>')
    if tail:
        g.append(f'<div class="np-sec np-tail">{tail}</div>')
    out.insert(len(out), f'<div class="np-jump" role="navigation" aria-label="{T["jump_aria"]}"><div class="np-jump-in">'
               + ''.join(f'<a href="#{i}">{t}</a>' for i, t in jumps) + '</div></div>')
    out.append(f'<div class="np-grid">{"".join(g)}</div>')
    new_body = '\n' + '\n'.join(out) + '\n'
    # the np- rules style every moved block; a style that picks an Arabic or Urdu typeface stays
    new_body = re.sub(r' style="([^"]*)"', lambda m: m.group(0) if re.search(r'Amiri|Naskh|Nastaliq', m.group(1)) else '', new_body)

    # labels the site script shows (play, save, share, search): read from the article by the script, see <locale>-js-change.md
    js = ''.join(f' data-l-{k}="{H.escape(T[k])}"' for k in ('play', 'save', 'saved', 'share', 'search') if T.get(k))
    art = f'<article class="asr-np" data-np-mode="me" data-np-name="{H.escape(name)}"{js}>'
    pre = pre[:-len('<article>')] + art
    pre = re.sub(r'(asr-redesign\.(?:css|js)\?v=)[0-9a-z]+', r'\g<1>' + VER, pre)
    post = re.sub(r'(asr-redesign\.(?:css|js)\?v=)[0-9a-z]+', r'\g<1>' + VER, post)
    if not closed:
        post = '</article>\n' + post
    # breadcrumb row with the mode switch; the page's own stylesheet loads here, after the site header
    if pre.count('<div class="breadcrumb"') == 1:
        b0 = pre.index('<div class="breadcrumb"')
        crumb = pre[b0:div_end(pre, b0)]
    elif pre.count('<div class="breadcrumb"') == 0 and pre.count('<nav class="breadcrumb"') == 1:
        b0 = pre.index('<nav class="breadcrumb"')       # the person pages mark the same row up as a <nav>
        crumb = pre[b0:pre.index('</nav>', b0) + len('</nav>')]
    else:
        raise Skip('breadcrumb count')
    switch = ''
    if kit_on:
        switch = (f'<div class="np-mode" role="group" aria-label="{T["mode_aria"]}">'
                  f'<button type="button" class="np-mode-b" data-np-mode="me" aria-pressed="true">{T["mode_me"]}</button>'
                  f'<button type="button" class="np-mode-b" data-np-mode="baby" aria-pressed="false">{T["mode_baby"]}</button></div>')
    preload = ''.join(f'<link rel="preload" href="{f}" as="font" type="font/woff2" crossorigin>' for f in L.get('preload_fonts', []))
    pre = pre.replace(crumb, f'{preload}<link rel="stylesheet" href="/asr-np.css?v={VER}"><link rel="stylesheet" href="/asr-np-rtl.css?v={VER}"><div class="np-crumbrow">{crumb}{switch}</div>', 1)
    page = pre + new_body + post
    return page, dict(famous=famous, bearers=nb, letters=len(gl), lucky=bool(lucky), pilot=sorted(pilot), ignored_pilot_keys=ignored, article_closed_by_builder=not closed, repairs=repairs)


def lucky_card(gl, rows, fbody, L):
    """the abjad card. The number in the ring is the one the page itself publishes; the letter sums are shown
    only when they add up to exactly that number. A page that publishes no number gets no card."""
    pub_total = pub_red = None
    caption = ''
    if 'abjad' in rows:
        nums = [to_int(x) for x in re.findall(r'[0-9٠-٩۰-۹]+', rows['abjad'][1])]
        if len(nums) == 2:
            pub_total, pub_red = nums
        caption = rows['abjad'][1]
        label = rows['abjad'][0]
    elif L.get('abjad_in_faq'):
        m = re.search(L['abjad_in_faq'], text_of(fbody))
        if m:
            pub_total, pub_red = to_int(m.group(1)), to_int(m.group(2))
        label = L['labels']['abjad']
    if pub_red is None:
        return ''
    vals = [(x, ABJAD[x]) for x in gl if x in ABJAD]
    total = sum(v for _, v in vals)
    steps, x = [total], total
    while x > 9:
        x = sum(map(int, str(x)))
        steps.append(x)
    work = ''
    if len(vals) == len(gl) and total == pub_total and x == pub_red:
        d = lambda v: digits(v, L, 'abjad_digits')
        # each number is isolated, so the sum runs right to left in the same order as the letters above it
        bd = lambda v: f'<bdi>{d(v)}</bdi>'
        eq = '+'.join(bd(v) for _, v in vals) + ' = ' + bd(total) + ''.join(f' ← {bd(s)}' for s in steps[1:])
        chips = ''.join(f'<span><i>{gph}</i>{d(v)}</span>' for gph, v in vals)
        work = f'<div class="rd-chips">{chips}</div><span class="np-eq">{eq}</span>'
    return (f'<div class="rd-lucky np-lucky"><span class="rd-kicker">{label}</span>'
            f'<dl class="np-lucky-dl"><div class="r"><dt>{label}</dt><dd>{digits(pub_red, L, "abjad_digits")}</dd></div></dl>'
            f'<div class="work">{work}' + (f'<span class="np-lucky-pub">{caption}</span>' if caption else '') + '</div></div>')


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    loc, slugs = args[0], args[1:]
    for slug in slugs:
        p = f'{loc}/names/{slug}/index.html'
        base = [a.split('=', 1)[1] for a in sys.argv if a.startswith('--base=')]
        if base:
            import subprocess
            h = subprocess.check_output(['git', 'show', f'{base[0]}:{p}']).decode('utf8')
        else:
            h = open(p, encoding='utf8').read()
        try:
            page, info = build(h, loc, slug)
        except Skip as e:
            print(loc, slug, 'SKIP', e)
            continue
        print(loc, slug, 'OK', info, len(h), '->', len(page))
        if '--write' in sys.argv:
            open(p, 'w', encoding='utf8').write(page)
