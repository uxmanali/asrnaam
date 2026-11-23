"""AsrNaam name page redesign: Hindi and Turkish name pages (the "quick-facts / hi-letter-grid" template family).

Moves the existing blocks of a hi/ or tr/ name page into the new layout used by the English pages
(same np-* class names, one stylesheet). Every block is cut from the page as raw HTML and pasted
unchanged. Only wrappers, classes and the interface labels from redesign/locale/<lang>.json are added.
No sentence of the page is reworded, no fact is added, and a section with no content on the page is left out.
The <head> is not touched apart from the version tag on asr-redesign.css.

usage: python3 redesign/np_build_hitr.py <hi|tr> slug [slug ...] [--write] [--final]   (run from the repo root)
Without --write it only reports. --final is accepted for symmetry with np_build.py (these pages carry no review tags).
A page the builder does not fully understand is skipped with the reason, never guessed at."""
import re, sys, json, html as H, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from np_build import Skip, div_end, text_of, ABJAD, VER   # noqa: E402

LOCALES = ('hi', 'tr')


def labels(loc):
    return json.load(open(f'redesign/locale/{loc}.json', encoding='utf8'))


def nodes(s):
    """the top-level blocks of the old <div class="content">, in page order, as (kind, raw html)"""
    kinds = {'quick-facts': 'qf', 'asr-mq': 'mq', 'prose': 'prose', 'hi-letter-grid': 'grid', 'name-list': 'names', 'crosslang': 'xl'}
    out, i = [], 0
    while True:
        i = re.compile(r'\s*').match(s, i).end()
        if i >= len(s):
            return out
        if s.startswith('<!-- MQ:START -->', i):
            j = s.find('<!-- MQ:END -->', i)
            if j < 0:
                raise Skip('unclosed MQ marker')
            j += len('<!-- MQ:END -->')
            out.append(('mq', s[i:j]))
        elif s.startswith('<div class="', i):
            cls = re.match(r'<div class="([^"]+)"', s[i:]).group(1)
            if cls not in kinds:
                raise Skip('unknown block: div.' + cls)
            j = div_end(s, i)
            out.append((kinds[cls], s[i:j]))
        elif s.startswith('<h2>', i):
            j = s.index('</h2>', i) + 5
            out.append(('h2', s[i:j]))
        elif s.startswith('<ul class="hi-letter-list">', i):
            j = s.index('</ul>', i) + 5
            out.append(('list', s[i:j]))
        elif s.startswith('<details>', i):
            j = s.index('</details>', i) + 10
            out.append(('faq', s[i:j]))
        elif s.startswith('<p class="asr-correct">', i):
            j = s.index('</p>', i) + 4
            out.append(('correct', s[i:j]))
        else:
            raise Skip('unknown block: ' + s[i:i + 60].replace('\n', ' '))
        i = j


def qf_rows(qf):
    """rows of the quick-facts box as (label, attributes of the value span, inner html of the value)"""
    rows = []
    inner = qf[len('<div class="quick-facts">'):-len('</div>')]
    i = 0
    while True:
        i = re.compile(r'\s*').match(inner, i).end()
        if i >= len(inner):
            return rows
        if not inner.startswith('<div class="qf-row">', i):
            raise Skip('quick-facts holds something that is not a row')
        j = div_end(inner, i)
        row = inner[i + len('<div class="qf-row">'):j - len('</div>')]
        m = re.fullmatch(r'<span class="qf-label">([^<]*)</span><span class="qf-value"([^>]*)>(.*)</span>', row, re.S)
        if not m:
            raise Skip('fact row not understood: ' + text_of(row)[:40])
        rows.append((m.group(1), m.group(2), m.group(3)))
        i = j


XL_OPEN = re.compile(r'<div class="crosslang">[^<]*(?:<a [^>]*>[^<]*</a>[^<]*)+</div>$')


def repair_divs(content):
    """Two faults of the old markup, each repaired only in the exact shape seen on the pages and reported by the check.
    1. The language bar lost its own closing tag (the pages that carry a Turkish link): the one </div> left closes the bar,
       so the content wrapper is never closed. The missing tag is supplied.
    2. One stray </div> directly after the letter grid. It is dropped.
    Anything else that does not balance is left for the caller to refuse."""
    repairs = []
    diff = len(re.findall(r'<div\b', content)) - content.count('</div>')
    if diff == 1 and XL_OPEN.search(content):
        content += '</div>'
        repairs.append('language bar had no closing tag: supplied')
    elif diff == -1 and content.count('<div class="hi-letter-grid">') == 1:
        g0 = content.index('<div class="hi-letter-grid">')
        g1 = div_end(content, g0)
        if content.startswith('</div>', g1):
            content = content[:g1] + content[g1 + len('</div>'):]
            repairs.append('stray closing tag after the letter grid: dropped')
    return content, repairs


def nostyle(x):
    """inline styles go (the np- rules style every moved block); one that picks an Arabic or Urdu typeface stays"""
    return re.sub(r' style="([^"]*)"', lambda m: m.group(0) if re.search(r'Amiri|Naskh|Nastaliq', m.group(1)) else '', x)


def build(h, loc, slug):
    L = labels(loc)
    if 'asr-np' in h:
        raise Skip('already migrated')
    if f'<html lang="{loc}"' not in h:
        raise Skip('html lang is not ' + loc)
    for must in ('<article>\n<div class="hero">', '<div class="content">', '</div>\n</article>'):
        if h.count(must) != 1:
            raise Skip('page shape: expected once: ' + must.replace('\n', ' '))
    a0 = h.index('<article>')
    a1 = a0 + len('<article>')
    a2 = h.index('</article>', a1)
    pre, body, post = h[:a0], h[a1:a2], h[a2:]
    # ---- hero
    m = re.fullmatch(r'\n<div class="hero">\n<div class="arabic-name">([^<]+)</div>\n<div class="dev-name">([^<]+)</div>\n'
                     r'<div class="name-badge">([^<]+)</div>\n<h1>((?:(?!</h1>).)+)</h1>\n</div>\n(<div class="content">.*</div>)\n', body, re.S)
    if not m:
        raise Skip('hero or content wrapper not in the expected shape')
    ar_name, own_name, badge, h1, content = m.groups()
    content, repairs = repair_divs(content)
    if div_end(content, 0) != len(content):
        raise Skip('content wrapper does not close where expected')
    ns = nodes(content[len('<div class="content">'):-len('</div>')])
    # ---- sort the blocks: fixed blocks by kind, the rest under the heading that precedes them
    qf = mq = xl = correct = None
    blocks, cur = [], None          # blocks: [role, h2 text, [(kind, html), ...]]
    for kind, raw in ns:
        if kind == 'qf':
            if qf or blocks:
                raise Skip('fact box is not first or is repeated')
            qf = raw
        elif kind == 'mq':
            if mq or blocks:
                raise Skip('Islamic-name box is not before the sections or is repeated')
            mq = raw
        elif kind == 'xl':
            if xl:
                raise Skip('two language bars')
            xl = raw
        elif kind == 'correct':
            if correct:
                raise Skip('two correction notes')
            correct = raw
        elif kind == 'h2':
            t = raw[4:-5]
            role = [r for r, pat in L['h2'].items() if re.fullmatch(pat, text_of(t))]
            if len(role) != 1:
                raise Skip('heading not recognised: ' + text_of(t)[:50])
            if any(b[0] == role[0] for b in blocks):
                raise Skip('heading role twice: ' + role[0])
            cur = [role[0], t, []]
            blocks.append(cur)
        else:
            if cur is None:
                raise Skip('content before the first heading: ' + text_of(raw)[:40])
            if xl or correct:
                raise Skip('content after the closing blocks: ' + text_of(raw)[:40])
            cur[2].append((kind, raw))
    if not qf:
        raise Skip('no fact box')
    B = {b[0]: b for b in blocks}
    allowed = {'letters': ('prose', 'grid', 'list'), 'more': ('prose', 'names'), 'faq': ('faq',)}
    for role, t, items in blocks:
        ok = allowed.get(role, ('prose',))
        ks = [k for k, _ in items]
        if not ks or any(k not in ok for k in ks):
            raise Skip(f'section "{role}" holds an unexpected block: {ks}')
        if any(ks.count(k) > 1 for k in ('grid', 'list', 'names')):
            raise Skip(f'section "{role}" repeats a block')
    for need in ('meaning', 'letters', 'faq'):
        if need not in B:
            raise Skip('missing section: ' + need)
    if 'grid' not in [k for k, _ in B['letters'][2]]:
        raise Skip('no letter grid')

    def inner(role, drop_inline=True):
        x = ''.join(raw for _, raw in B[role][2])
        return nostyle(x) if drop_inline else x

    # ---- facts: cards, the strip rows, the lucky number
    rows = {}
    order = []
    for lab, attrs, val in qf_rows(qf):
        role = L['qf'].get(lab)
        if not role or role in rows:
            raise Skip('fact label not recognised or repeated: ' + lab)
        rows[role] = (lab, attrs, val)
        order.append(role)
    for need in L['cards'] + ['lucky']:
        if need not in rows:
            raise Skip('fact box lacks: ' + need)
    if qf.count('data-asr-field="lucky"') != 1 or 'data-asr-field="lucky"' not in (rows['lucky'][1] + rows['lucky'][2]):
        raise Skip('lucky field not where expected')

    def dd(role, cls=''):
        lab, attrs, val = rows[role]
        attrs = re.sub(r'\s*style="[^"]*"', '', attrs)
        sc = L['script'].get(role)
        if sc and 'lang=' not in attrs and 'lang=' not in val:
            attrs += f' lang="{sc}" dir="rtl"'      # the value is Arabic-script text: say so (no text change)
        return f'<dd{(" class=" + chr(34) + cls + chr(34)) if cls else ""}{attrs}>{val}</dd>'

    def card(role):
        lab = rows[role][0]
        if role == 'gender':
            g = L['gender'].get(text_of(rows[role][2]))
            return f'<div class="r np-card"><dt>{lab}</dt>{dd(role, ("rd-tag " + g) if g else "")}</div>'
        cls = ' np-card-sc' if role in L['script'] else ''
        return f'<div class="r np-card{cls}"><dt>{lab}</dt>{dd(role)}</div>'

    cards = ''.join(card(r) for r in L['cards'])
    strip_rows = ''.join(f'<div class="r"><dt>{rows[r][0]}</dt>{dd(r)}</div>' for r in order if r not in L['cards'] and r != 'lucky')
    pron = ''
    if 'pron' in B:
        pron = f'<h2 class="np-h2-small">{B["pron"][1]}</h2>{inner("pron")}'
    strip = ''
    if pron or strip_rows:
        strip = (f'<section class="np-pron">{pron}' + (f'<dl class="np-pron-dl">{strip_rows}</dl>' if strip_rows else '') + '</section>')
    # ---- lucky card: the published number from the page; the working is shown only when it reproduces the page's own figures
    letters_html = inner('letters')
    gl = re.findall(r'<span class="hi-letter-ar">([^<]+)</span>', letters_html)
    lucky_pub = text_of(rows['lucky'][2])
    work = ''
    parts = [(g, ABJAD[g]) for g in gl if g in ABJAD]
    if parts and len(parts) == len(gl):
        total = sum(v for _, v in parts)
        steps, x = [total], total
        while x > 9:
            x = sum(map(int, str(x)))
            steps.append(x)
        stated = set(re.findall(r'\d+', text_of(inner('lucky')))) if 'lucky' in B else set()
        if 'abjad' in rows:
            stated.add(text_of(rows['abjad'][2]))
        if str(total) in stated and str(steps[-1]) == lucky_pub:
            eq = '+'.join(str(v) for _, v in parts) + ' = ' + str(total) + ''.join(f' → {s}' for s in steps[1:])
            chips = ''.join(f'<span><i lang="ar">{g}</i>{v}</span>' for g, v in parts)
            work = f'<div class="work" dir="ltr"><div class="rd-chips">{chips}</div>{H.escape(eq)}</div>'
    lucky_card = (f'<div class="rd-lucky np-lucky"><dl class="np-lucky-dl"><div class="r"><dt>{rows["lucky"][0]}</dt>{dd("lucky")}</div></dl>{work}</div>')
    # ---- letter cards get their element as an attribute (the colour bar); the words stay as they are
    def el_attr(mm):
        e = re.search(r'<span class="hi-letter-el">([^<]*)</span>', mm.group(0))
        code = L['elements'].get(e.group(1)) if e else None
        return mm.group(0).replace('<div class="hi-letter">', f'<div class="hi-letter" data-element="{code}">', 1) if code else mm.group(0)
    letters_html = re.sub(r'<div class="hi-letter">.*?</div>', el_attr, letters_html, flags=re.S)
    letters_html = letters_html.replace('<span class="hi-letter-ar">', '<span class="hi-letter-ar" lang="ar" dir="rtl">')

    def sub(role):
        return f'<div class="np-sub"><h2 class="np-subh">{B[role][1]}</h2>{inner(role)}</div>' if role in B else ''

    # ---- sections
    secs, jumps, n = [], [], 0

    def kick(key):
        nonlocal n
        n += 1
        k = L['kicker'].get(key)
        return f'<p class="rd-kicker">{n:02d} · {k}</p>' if k else ''

    def jump(key, anchor):
        if L['jump'].get(key):
            jumps.append(f'<a href="#{anchor}">{L["jump"][key]}</a>')

    portrait = (f'<div class="np-portrait"><h2 class="np-subh">{B["reading"][1]}</h2>{inner("reading")}</div>' if 'reading' in B else '')
    secs.append(f'<section id="reading" class="np-sec np-letters">{kick("reading")}<h2 class="rd-h2">{B["letters"][1]}</h2>{letters_html}'
                f'{sub("elements")}{sub("divine")}<div class="np-portrait-row">{portrait}{lucky_card}</div>{sub("lucky")}</section>')
    jump('reading', 'reading')
    org = [r for r in ('root', 'origin', 'quran') if r in B]
    if org:
        lead = org[0]
        secs.append(f'<section id="origin" class="np-sec np-journey">{kick("origin")}<h2 class="rd-h2">{B[lead][1]}</h2>{inner(lead)}'
                    + ''.join(sub(r) for r in org[1:]) + '</section>')
        jump('origin', 'origin')
    secs.append(f'<section id="story" class="np-sec np-story">{kick("story")}<h2 class="rd-h2">{B["meaning"][1]}</h2>{inner("meaning")}</section>')
    jump('story', 'story')
    secs.append(f'<section id="faq" class="np-sec np-faq"><h2 class="rd-h2">{B["faq"][1]}</h2><div class="faq-list">{inner("faq")}</div></section>')
    jump('faq', 'faq')
    if 'more' in B:
        secs.append(f'<section id="more" class="np-sec np-more"><h2 class="rd-h2">{B["more"][1]}</h2>{inner("more")}</section>')
        jump('more', 'more')
    if correct:
        secs.append(correct)
    placed = {'letters', 'elements', 'divine', 'reading', 'lucky', 'root', 'origin', 'quran', 'meaning', 'faq', 'more', 'pron'}
    left = [b[0] for b in blocks if b[0] not in placed]
    if left:
        raise Skip('section with no place in the new layout: ' + ','.join(left))
    # ---- hero: the same four lines the old hero had, plus the page's own language links
    langs = ''
    if xl:
        langs = '<p class="asr-name-hero-langs">' + xl[len('<div class="crosslang">'):-len('</div>')].strip() + '</p>'
    hero = (f'<header class="asr-name-hero"><p class="asr-name-hero-kicker">{badge}</p>'
            f'<div class="asr-name-hero-arabic" lang="ar" dir="rtl">{ar_name}</div><h1 class="asr-name-hero-roman">{h1}</h1>'
            f'<div class="asr-name-hero-sub">{own_name}</div>{langs}</header>')
    answer = (f'<div class="asr-answer np-answer"><dl class="asr-answer-rows np-cards">{cards}</dl>{strip}{mq or ""}</div>')
    jumpbar = (f'<div class="np-jump" role="navigation" aria-label="{H.escape(L["aria"]["jump"])}"><div class="np-jump-in">{"".join(jumps)}</div></div>')
    js = L.get('js', {})
    data = f' data-l-name="{H.escape(own_name)}"' + ''.join(f' data-l-{k}="{H.escape(v)}"' for k, v in js.items())
    art = f'<article class="asr-name-article asr-np" data-np-mode="me"{data}>'
    new_body = '\n' + hero + '\n' + answer + '\n' + jumpbar + '\n<div class="np-grid">' + ''.join(secs) + '</div>\n'
    # ---- the crumb row and the page stylesheet (loaded in the body after the site header, as on the English pages)
    bc = re.search(r'<div class="breadcrumb" role="navigation" aria-label="Breadcrumb">(?:(?!</div>).)*</div>', pre, re.S)
    if not bc or pre.count('<div class="breadcrumb"') != 1:
        raise Skip('breadcrumb not in the expected shape')
    crumb = bc.group(0).replace('<div class="breadcrumb" role="navigation" aria-label="Breadcrumb">',
                                f'<div class="breadcrumb asr-breadcrumb" role="navigation" aria-label="{H.escape(L["aria"]["breadcrumb"])}">', 1)
    pre = pre.replace(bc.group(0), f'<link rel="stylesheet" href="/asr-np.css?v={VER}"><link rel="stylesheet" href="/asr-np-hitr.css?v={VER}"><div class="np-crumbrow">{crumb}</div>', 1)
    ver = lambda s: re.sub(r'(asr-redesign\.(?:css|js)\?v=)[0-9a-z]+', r'\g<1>' + VER, s)
    page = ver(pre) + art + new_body + ver(post)
    info = dict(repairs=repairs, sections=[s for s in ('reading', 'origin', 'story', 'faq', 'more') if f'id="{s}"' in new_body], letters=len(gl),
                lucky_work=bool(work), pron='pron' in B, faqs=len(B['faq'][2]), strip=[rows[r][0] for r in order if r not in L['cards'] and r != 'lucky'])
    return page, info


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args or args[0] not in LOCALES:
        sys.exit('usage: python3 redesign/np_build_hitr.py <hi|tr> slug [slug ...] [--write] [--final]')
    loc, write = args[0], '--write' in sys.argv
    for slug in args[1:]:
        p = f'{loc}/names/{slug}/index.html'
        if not os.path.exists(p):
            print(loc, slug, 'SKIP no such page')
            continue
        h = open(p, encoding='utf8').read()
        try:
            page, info = build(h, loc, slug)
        except Skip as e:
            print(loc, slug, 'SKIP', e)
            continue
        print(loc, slug, 'OK', info, len(h), '->', len(page))
        if write:
            open(p, 'w', encoding='utf8').write(page)
