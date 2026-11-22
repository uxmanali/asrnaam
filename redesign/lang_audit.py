#!/usr/bin/env python3
"""Language audit for AsrNaam: every page under ur/ ar/ hi/ tr/ measured against the English page of the same name.

READ-ONLY. It never edits a page. It reads the site as it is on production (git ref origin/main) so that
half-finished work in the working tree is not counted.

  python3 redesign/lang_audit.py                 # audit origin/main, write redesign/lang/audit.json and audit.md
  python3 redesign/lang_audit.py --ref HEAD      # audit another commit or branch
  python3 redesign/lang_audit.py --tree          # audit the files on disk instead (preview work)
  python3 redesign/lang_audit.py --discover      # print label and string tables (used to maintain the maps below)

Defect classes used in the report:
  A  safe mechanical fix by script
  B  needs translation written and reviewed
  C  needs a native reader's judgement
  D  needs Usman's decision
"""
import atexit
import collections
import html
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unicodedata
from html.parser import HTMLParser

LANGS = ['ur', 'ar', 'hi', 'tr']
SITE = 'https://asrnaam.com'
DIR = {'ur': 'rtl', 'ar': 'rtl', 'hi': 'ltr', 'tr': 'ltr'}
OGLOC = {'ur': {'ur_PK'}, 'ar': {'ar_AR', 'ar_SA', 'ar'}, 'hi': {'hi_IN'}, 'tr': {'tr_TR'}}
LANGNAME = {'ur': 'Urdu', 'ar': 'Arabic', 'hi': 'Hindi', 'tr': 'Turkish', 'en': 'English'}
OUT_DIR = 'redesign/lang'

# ----------------------------------------------------------------------------- characters
HARAKAT = '\u064b-\u0652\u0670\u0653-\u0655\u0640'
RE_HARAKAT = re.compile('[' + HARAKAT + '\u06d6-\u06ed]')
RE_ARAB = re.compile('[؀-ۿݐ-ݿﭐ-﷿ﹰ-\ufeff]')
RE_ARAB_LETTER = re.compile('[ء-يٮ-ۓۺ-ۿ]')
RE_DEVA = re.compile('[ऀ-ॿ]')
RE_LATIN_LETTER = re.compile('[A-Za-zÀ-ɏḀ-ỿ]')
RE_LATIN_RUN = re.compile(r"[A-Za-zÀ-ɏḀ-ỿʻ-ʿ'’][A-Za-zÀ-ɏḀ-ỿʻ-ʿ'’.\-]*(?:[ \u00a0][A-Za-zÀ-ɏḀ-ỿʻ-ʿ'’][A-Za-zÀ-ɏḀ-ỿʻ-ʿ'’.\-]*)*")
WEST = '0123456789'
ARIN = '٠١٢٣٤٥٦٧٨٩'   # ٠-٩ Arabic-Indic (Arabic)
EXIN = '۰۱۲۳۴۵۶۷۸۹'   # ۰-۹ Extended (Urdu, Persian)
DEVD = '०१२३४५६७८९'
DIG = str.maketrans(ARIN + EXIN + DEVD, WEST * 3)
# letters that have a different code point in Urdu and in Arabic
AR_FORMS_IN_UR = {'ي': 'ي Arabic ya (Urdu uses ی)', 'ى': 'ى alef maksura (Urdu uses ی)', 'ك': 'ك Arabic kaf (Urdu uses ک)',
                  'ه': 'ه Arabic ha (Urdu uses ہ or ھ)', 'ة': 'ة ta marbuta (Urdu uses ہ or ۃ)'}
UR_FORMS_IN_AR = {'ی': 'ی Farsi/Urdu ya (Arabic uses ي or ى)', 'ک': 'ک Urdu kaf (Arabic uses ك)', 'ہ': 'ہ Urdu he (Arabic uses ه)',
                  'ے': 'ے Urdu bari ye', 'ھ': 'ھ Urdu do-chashmi he', 'ں': 'ں Urdu noon ghunna', 'ۃ': 'ۃ Urdu ta marbuta'}
UR_ONLY = set('ٹڈڑںےہھپچگژکیۃ')     # letters used in Urdu and not in Arabic
AR_ONLY = set('يكةىإأؤئ')            # letters or forms used in Arabic and not in Urdu spelling of the same sound
HALF = set('the of or and to from same root forth with for is at by as that this his her who was were son daughter wife martyred born died meaning form variant spelling also one see '
           'means name names not on it its'.split())
ZW = {'\u200b': 'zero-width space', '\u200d': 'zero-width joiner', '\ufeff': 'BOM', '\u200e': 'LRM', '\u200f': 'RLM', '\u00ad': 'soft hyphen',
      '\u202a': 'LRE', '\u202b': 'RLE', '\u202c': 'PDF', '\u2066': 'LRI', '\u2067': 'RLI', '\u2069': 'PDI'}
JUNK = re.compile(r'\ufffd|\{\{|\}\}|\{%|\$\{|\bundefined\b|\bNaN\b|\bNone\b|\bnull\b|\bTODO\b|\bFIXME\b|\bTBD\b|[Ll]orem ipsum|\[object|&amp;|&#x?[0-9a-fA-F]+;|&[a-z]{2,8};')
ENGLISH_WORDS = set('''the and of is are was with for this that from by on at to as it its not be or an which who what when where how why
meaning meanings name names origin gender boy girl lucky number letters letter pronunciation pronounced share save copy read more home search
breadcrumb related similar about contact privacy terms policy menu close open next previous back view all see list loading error click here
arabic urdu english turkish hindi spelling root quran verse section famous bearers faq frequently asked questions answer main navigation skip content'''.split())
TR_ALSO = {'on', 'at', 'an', 'be', 'it', 'as', 'of', 'not', 'bu', 'name', 'by', 'to', 'or', 'error'}   # real Turkish words or too ambiguous: never used for the Turkish check
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
STRUCT = {'html', 'body', 'main', 'article', 'section', 'div', 'nav', 'header', 'footer', 'aside', 'ul', 'ol', 'details', 'dl', 'table', 'form'}
SKIP = {'script', 'style', 'svg', 'noscript', 'template'}
IMPLIED = {'p', 'li', 'dt', 'dd', 'option', 'tr', 'td', 'th', 'thead', 'tbody'}


def nd(s):
    """digits of any script as Western digits"""
    return s.translate(DIG)


def strip_h(s):
    return RE_HARAKAT.sub('', s)


def norm_ar(s):
    """Arabic or Urdu spelling reduced to one comparable skeleton"""
    s = strip_h(unicodedata.normalize('NFC', s))
    for a, b in [('أ', 'ا'), ('إ', 'ا'), ('آ', 'ا'), ('ٱ', 'ا'), ('ى', 'ي'), ('ی', 'ي'), ('ئ', 'ي'), ('ؤ', 'و'), ('ة', 'ه'), ('ۃ', 'ه'), ('ہ', 'ه'),
                 ('ھ', 'ه'), ('ک', 'ك'), ('ۀ', 'ه'), ('ے', 'ي')]:
        s = s.replace(a, b)
    return ''.join(c for c in s if RE_ARAB_LETTER.match(c))


def fold(s):
    s = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in s if not unicodedata.combining(c)).lower().replace('ʿ', '').replace('ʾ', '').replace("'", '').replace('’', '').replace('-', ' ').strip()


def txt(h):
    h = re.sub(r'<(script|style|svg|noscript|template)\b.*?</\1>', ' ', h, flags=re.S)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', h))).strip()


def words(t):
    return len(re.findall(r'\S+', t))


# ----------------------------------------------------------------------------- site access
class Site:
    def __init__(self, ref=None):
        self.ref = ref
        if ref:
            self.tmp = tempfile.mkdtemp(prefix='langaudit-')
            atexit.register(shutil.rmtree, self.tmp, True)
            self.files = set(subprocess.run(['git', 'ls-tree', '-r', '--name-only', ref], capture_output=True, text=True, check=True).stdout.split('\n'))
            keep = [p for p in ['ur', 'ar', 'hi', 'tr', 'names', '_redirects', 'index.html'] + sorted(f for f in self.files if re.fullmatch(r'sitemap[^/]*\.xml|asr-[^/]*\.js', f))
                    if p in self.files or any(f.startswith(p + '/') for f in self.files)]
            p = subprocess.Popen(['git', 'archive', ref] + keep, stdout=subprocess.PIPE)
            with tarfile.open(fileobj=io.BytesIO(p.stdout.read())) as tar:
                tar.extractall(self.tmp, filter='data')
            self.root = self.tmp
            self.sha = subprocess.run(['git', 'rev-parse', '--short', ref], capture_output=True, text=True).stdout.strip()
        else:
            self.root = '.'
            self.files = set(subprocess.run(['git', 'ls-files', '-co', '--exclude-standard'], capture_output=True, text=True).stdout.split('\n'))
            self.sha = 'working tree'
        self.dirs = {f[:-len('index.html')] for f in self.files if f.endswith('/index.html')} | {''}

    def read(self, path):
        try:
            return open(os.path.join(self.root, path), encoding='utf8').read()
        except OSError:
            return None

    def exists_url(self, path):
        """does a site-relative URL path resolve to a file"""
        p = path.split('#')[0].split('?')[0].lstrip('/')
        if p == '' or p in self.files or p in self.dirs or (p + '/') in self.dirs or (p.rstrip('/') + '.html') in self.files:
            return True
        return False


# ----------------------------------------------------------------------------- page parser
class Page(HTMLParser):
    """visible text nodes with their context, attribute texts, links, quick facts, structure"""

    def __init__(self, src):
        super().__init__(convert_charrefs=True)
        self.stack = []          # (tag, attrs)
        self.nodes = []          # (text, ctx dict)
        self.attrs_text = []     # (attr, value, tag)
        self.links = []          # dict(href, text, lang, hreflang, zone, cls)
        self.qf = []             # (label, value)
        self.kickers = []
        self.h = collections.defaultdict(list)
        self.ids = collections.Counter()
        self.unclosed, self.stray = [], []
        self.empty = []
        self.details = 0
        self.faq = []            # (question, answer)
        self._skip = 0
        self._a = None
        self._cap = []           # capture buffers [tag_depth, kind, parts]
        self._last_text_len = {}
        self.in_body = False
        self.feed(src)
        self.close()
        for t, a in self.stack:
            if t in STRUCT and t not in ('html', 'body'):
                self.unclosed.append(t)

    def ctx(self):
        lang, cls, zone, tags = None, [], 'body', []
        for t, a in self.stack:
            if a.get('lang'):
                lang = a['lang'].lower()
            c = a.get('class')
            if c:
                cls.append(c)
            if t in ('nav', 'footer', 'header', 'main', 'article', 'aside'):
                zone = t
            if 'breadcrumb' in (c or ''):
                zone = 'breadcrumb'
            tags.append(t)
        hidden = any('hidden' in a or a.get('aria-hidden') == 'true' for _, a in self.stack)
        return {'lang': lang, 'cls': ' '.join(cls), 'zone': zone, 'tag': tags[-1] if tags else '', 'tags': tags, 'hidden': hidden}

    def handle_starttag(self, tag, attrs):
        a = {k: (v or '') for k, v in attrs}
        if tag == 'body':
            self.in_body = True
        if tag in SKIP:
            self._skip += 1
        if tag in IMPLIED:      # an open <p>/<li> is closed by the next one
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == tag:
                    if not any(s[0] in STRUCT for s in self.stack[i + 1:]):
                        self._close_to(i)
                    break
                if self.stack[i][0] in STRUCT and tag != 'li':
                    break
        if a.get('id'):
            self.ids[a['id']] += 1
        if self.in_body and not self._skip:
            for k in ('aria-label', 'alt', 'title', 'placeholder', 'value'):
                if a.get(k) and not (k == 'value' and tag not in ('input', 'button')):
                    self.attrs_text.append((k, a[k], tag))
        if tag in VOID:
            return
        self.stack.append((tag, a))
        c = a.get('class', '')
        if tag == 'a':
            cx = self.ctx()
            self._a = {'href': a.get('href', ''), 'text': '', 'lang': a.get('lang', ''), 'hreflang': a.get('hreflang', ''), 'zone': cx['zone'], 'cls': cx['cls']}
        for kind, test in (('qfl', 'qf-label' in c), ('qfv', 'qf-value' in c), ('kick', 'asr-v2-kicker' in c), ('h', tag in ('h1', 'h2', 'h3')), ('sum', tag == 'summary'),
                           ('det', tag == 'details'), ('emp', tag in ('p', 'li', 'h2', 'h3', 'td', 'dd', 'summary') or False)):
            if test:
                self._cap.append([len(self.stack), kind, [], tag])
        if tag == 'details':
            self.details += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def _close_to(self, i):
        while len(self.stack) > i:
            depth = len(self.stack)
            tag, a = self.stack.pop()
            if tag in SKIP:
                self._skip -= 1
            for cap in [c for c in self._cap if c[0] == depth]:
                self._cap.remove(cap)
                val = re.sub(r'\s+', ' ', ''.join(cap[2])).strip()
                k = cap[1]
                if k == 'qfl':
                    self.qf.append([val, None])
                elif k == 'qfv':
                    if self.qf and self.qf[-1][1] is None:
                        self.qf[-1][1] = val
                    else:
                        self.qf.append(['', val])
                elif k == 'kick':
                    self.kickers.append(val)
                elif k == 'h':
                    self.h[cap[3]].append(val)
                elif k == 'sum':
                    self.faq.append([val, None])
                elif k == 'det':
                    if self.faq and self.faq[-1][1] is None:
                        q = self.faq[-1][0]
                        self.faq[-1][1] = val[len(q):].strip() if val.startswith(q) else val
                elif k == 'emp' and not val and self.in_body and not self._skip:
                    self.empty.append(cap[3] + ('.' + a.get('class') if a.get('class') else ''))
            if tag == 'a' and self._a is not None:
                self._a['text'] = re.sub(r'\s+', ' ', self._a['text']).strip()
                self.links.append(self._a)
                self._a = None

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                for t, _ in self.stack[i + 1:]:
                    if t in STRUCT:
                        self.unclosed.append(t)
                self._close_to(i)
                return
        if tag in STRUCT:
            self.stray.append(tag)

    def handle_data(self, data):
        if self._skip or not self.in_body:
            return
        for cap in self._cap:
            cap[2].append(data)
        if self._a is not None:
            self._a['text'] += data
        if data.strip():
            self.nodes.append((data, self.ctx()))


# ----------------------------------------------------------------------------- head
def head_info(h):
    head = h[:h.find('</head>')] if '</head>' in h else h[:20000]
    d = {}
    m = re.search(r'<html\b([^>]*)>', h)
    ha = dict(re.findall(r'([a-z-]+)="([^"]*)"', m.group(1))) if m else {}
    d['lang'], d['dir'] = ha.get('lang'), ha.get('dir')
    m = re.search(r'<title>(.*?)</title>', head, re.S)
    d['title'] = html.unescape(m.group(1)).strip() if m else None

    def meta(key, attr='name'):
        m = re.search(r'<meta\s+[^>]*%s="%s"[^>]*>' % (attr, re.escape(key)), head)
        if not m:
            return None
        c = re.search(r'content="([^"]*)"', m.group(0))
        return html.unescape(c.group(1)) if c else None
    d['desc'] = meta('description')
    d['ogloc'] = meta('og:locale', 'property')
    d['ogalt'] = re.findall(r'property="og:locale:alternate"\s+content="([^"]*)"', head)
    d['ogtitle'], d['ogdesc'], d['ogimage'], d['ogurl'] = meta('og:title', 'property'), meta('og:description', 'property'), meta('og:image', 'property'), meta('og:url', 'property')
    d['twtitle'], d['twdesc'] = meta('twitter:title'), meta('twitter:description')
    d['modified'] = meta('article:modified_time', 'property')
    m = re.search(r'<link[^>]*rel="canonical"[^>]*>', head)
    d['canonical'] = re.search(r'href="([^"]*)"', m.group(0)).group(1) if m else None
    d['hreflang'] = {}
    d['hreflang_dupe'] = []
    for m in re.finditer(r'<link[^>]*rel="alternate"[^>]*>', head):
        hl, hr = re.search(r'hreflang="([^"]*)"', m.group(0)), re.search(r'href="([^"]*)"', m.group(0))
        if hl and hr:
            if hl.group(1) in d['hreflang']:
                d['hreflang_dupe'].append(hl.group(1))
            d['hreflang'][hl.group(1)] = hr.group(1)
    d['robots'] = meta('robots')
    d['jsonld'], d['jsonld_err'] = [], []
    for b in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', h, re.S):
        try:
            j = json.loads(b)
        except ValueError as e:
            d['jsonld_err'].append(str(e)[:80])
            continue
        for x in (j.get('@graph', [j]) if isinstance(j, dict) else j):
            if isinstance(x, dict):
                d['jsonld'].append(x)
    m = re.search(r'<time[^>]*datetime="([^"]*)"[^>]*itemprop="dateModified"', h)
    d['time_tag'] = m.group(1)[:10] if m else None
    d['scripts'] = re.findall(r'<script[^>]*src="(/[^"?]+)', h)
    return d


def rel(u):
    return u[len(SITE):] if u and u.startswith(SITE) else u


# ----------------------------------------------------------------------------- facts
def first(t, pats):
    for p in pats:
        m = re.search(p, t, re.S)
        if m:
            return m.group(1).strip()
    return None


GENDER = {'boy': 'M', 'male': 'M', 'girl': 'F', 'female': 'F', 'unisex': 'U', 'both': 'U',
          'مذکر': 'M', 'مؤنث': 'F', 'مونث': 'F', 'دونوں': 'U', 'مشترک': 'U', 'للذكور والإناث': 'U', 'مذکر و مؤنث': 'U', 'ذكر': 'M', 'أنثى': 'F', 'مؤنّث': 'F', 'مذكر': 'M', 'للجنسين': 'U', 'مشترك': 'U',
          'लड़कों का नाम': 'M', 'लड़कियों का नाम': 'F', 'erkek ismi': 'M', 'kız ismi': 'F', 'üniseks': 'U', 'unisex isim': 'U'}
LABELS = {
    'ur': {'gender': ['صنف'], 'origin': ['اصل'], 'root': ['عربی جذر'], 'urdu': ['اردو املا'], 'arabic': ['عربی املا'], 'pron': ['تلفظ'], 'nletters': ['حروف کی تعداد'],
           'abjad': ['ابجد / خوش نصیب عدد'], 'meaning': ['لغوی معنی'], 'letters': ['حروف', 'حروف کی تفصیل']},
    'ar': {'gender': ['الجنس'], 'origin': ['الأصل'], 'root': ['الجذر العربي'], 'urdu': ['الرسم الأردي'], 'arabic': ['الرسم العربي'], 'roman': ['النطق اللاتيني'],
           'nletters': ['عدد الحروف'], 'meaning': ['المعنى المعجمي'], 'letters': ['تفصيل الحروف']},
    'hi': {'gender': ['लिंग'], 'origin': ['मूल', 'उत्पत्ति'], 'lucky': ['शुभ अंक'], 'arabic': ['अरबी'], 'urdu': ['उर्दू'], 'nletters': ['अरबी अक्षर'], 'meaning': ['मतलब'], 'roman': ['अंग्रेज़ी']},
    'tr': {'gender': ['Cinsiyet'], 'origin': ['Köken'], 'arabic': ['Arapça yazılış'], 'urdu': ['Urduca yazılış'], 'total': ['Ebced değeri'], 'lucky': ['Ebced rakamı'],
           'nletters': ['Harf sayısı'], 'meaning': ['Anlamı']},
}


def gender_code(v):
    if not v:
        return None
    v = v.strip().lower()
    if v in GENDER:
        return GENDER[v]
    for k, c in GENDER.items():
        if v.startswith(k):
            return c
    return '?' + v


def verse_refs(t):
    return set(re.findall(r'(?<![\d:])(\d{1,3}):(\d{1,3})(?![\d:])', nd(t or '')))


def facts_en(h):
    f = {}
    for k, v in re.findall(r'data-asr-field="([^"]+)"[^>]*>(.*?)</(?:dd|span|div|p)>', h, re.S):
        f.setdefault(k, html.unescape(re.sub(r'<[^>]+>', '', v)).strip())
    o = {'gender': gender_code(f.get('gender')), 'origin': f.get('origin'), 'lucky': f.get('lucky'), 'urdu': f.get('urdu')}
    p = f.get('pronunciation')
    o['pron'] = re.sub(r'\s*/.*$', '', p).strip() if p else None
    m = re.search(r'class="asr-name-hero-arabic"[^>]*>([^<]+)<', h) or re.search(r'class="asr-answer-script"[^>]*>([^<]+)<', h)
    o['arabic'] = html.unescape(m.group(1)).strip() if m else None
    m = re.search(r'Arabic root</(?:dt|span)>\s*<[^>]*>(.*?)</', h, re.S)
    o['root'] = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip() if m else None
    m = re.search(r'>\s*(\d+) syllables?\s*<', h)
    o['syll'] = m.group(1) if m else None
    o['letters'] = ''.join(re.findall(r'asr-v2-letter-arabic[^>]*>([^<]+)', h))
    q = None
    for b in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', h, re.S):
        if 'FAQPage' in b:
            try:
                j = json.loads(b)
            except ValueError:
                continue
            for x in (j.get('@graph', [j]) if isinstance(j, dict) else j):
                if isinstance(x, dict) and x.get('@type') == 'FAQPage':
                    for e in x.get('mainEntity', []):
                        if re.search(r'Qur', e.get('name', '')) and re.search(r'mention|in the Qur|appear', e.get('name', ''), re.I):
                            q = e['acceptedAnswer']['text']
    o['quran_answer'] = q
    first_s = re.split(r'(?<=[.!?])\s', q)[0] if q else ''
    o['quran_yes'] = None if q is None else ('Y' if re.match(r'\s*Yes\b', q) else 'N' if re.match(r'\s*(No\b|Not\b)', q) or re.search(
        r"\bnot\b[^.]*\b(Quran|Quranic|mentioned|named|appear|appears|directly|found)\b|\bis not\b|isn't|does not", first_s) else None)
    o['verses'] = verse_refs(q) if q else set()
    return o


def facts_loc(lang, pg, body_text, slug):
    qf = {}
    for l, v in pg.qf:
        qf.setdefault(l.strip(), v)
    o = {'_labels': list(qf)}

    def g(key):
        for l in LABELS[lang].get(key, []):
            if l in qf and qf[l]:
                return qf[l]
        return None
    o['gender'] = gender_code(g('gender'))
    o['origin'] = g('origin')
    o['arabic'], o['urdu'], o['meaning'] = g('arabic'), g('urdu'), g('meaning')
    o['nletters'] = nd(g('nletters') or '') or None
    o['root'] = g('root')
    o['pron'] = g('pron')
    t = nd(body_text)
    if lang == 'ur':
        a = nd(g('abjad') or '')
        o['total'] = first(a, [r'مجموعہ\s*(\d+)']) or first(t, [r'حروف کا مجموعہ\s*(\d+)'])
        o['lucky'] = first(a, [r'مختصر\s*(\d+)']) or first(t, [r'مختصر عدد\s*(\d+)'])
    elif lang == 'ar':
        o['total'] = first(t, [r'بحساب الجُمَّل هو\s*(\d+)', r'الجُمَّل\s*(?:هو|:)?\s*(\d+)'])
        o['lucky'] = first(t, [r'ورقمه المختزل\s*(\d+)'])
    elif lang == 'hi':
        o['lucky'] = nd(g('lucky') or '') or None
        o['total'] = first(t, [r'अक्षरों का योग\s*(\d+)'])
        o['root'] = first(body_text, [r'अरबी जड़\s*([ء-يکی][ء-يکی\-\s·]*?)\s+है'])
        o['pron'] = first(body_text, [r'इस नाम को\s*(.+?)\s*बोला जाता है'])
    elif lang == 'tr':
        o['lucky'] = nd(g('lucky') or '') or None
        o['total'] = nd(g('total') or '') or None
        o['root'] = first(body_text, [r'([ء-ي](?:-[ء-ي]){1,4})\s*(?:\([^)]*\)\s*)?kökünden'])
    return o


# ----------------------------------------------------------------------------- one locale page
def expected_script_share(lang, s):
    """share of the letters of s that are in the page language's script"""
    lat = len(RE_LATIN_LETTER.findall(s))
    ar = len(RE_ARAB_LETTER.findall(s))
    dv = len(re.findall('[ऄ-हक़-ॡ]', s))
    tot = lat + ar + dv
    if not tot:
        return 1.0
    return {'ur': ar, 'ar': ar, 'hi': dv, 'tr': lat}[lang] / tot


RE_SOURCES = re.compile(r'Behind the Name|Wikipedia|Wiktionary|Encyclopaedia of Islam|Encyclopaedia Iranica|Nişanyan Sözlük|Lisan al-Arab|Oxford Dictionary of [A-Z]\w+')
RE_IPA = re.compile(r'/[^/\s<>]{1,40}/|\[[^\]\s]{1,40}\]')


def latin_phrases(text):
    text = RE_IPA.sub(lambda m: ' ' if re.search(r'[\u0250-\u02ff.]', m.group(0)) else m.group(0), text)
    return [m.group(0).strip(" .'’-") for m in RE_LATIN_RUN.finditer(text) if RE_LATIN_LETTER.search(m.group(0))]


SWITCH = {'english', 'en', 'türkçe', 'turkce', 'tr', 'hi', 'ur', 'ar'}
BRAND = {'asrnaam', 'asrnaam.com', 'asr naam'}


def classify_latin(ph, cx, own_names, all_names, en_pron):
    """-> (bucket, legit?)  buckets: brand, switcher, own-name, other-name, pronunciation, ipa, url, alphabet, person, ui"""
    f = fold(ph)
    c = cx.get('cls', '')
    if not f:
        return 'symbol', True
    if f in BRAND or 'asrnaam' in f:
        return 'brand', True
    if re.search(r'@|\.com|https?:|www\.', ph):
        return 'url', True
    if f in SWITCH and (cx.get('zone') in ('nav', 'footer') or 'crosslang' in c or cx.get('tag') == 'a'):
        return 'switcher', True
    if 'code' in cx.get('tags', []) or ph.startswith('/'):
        return 'ipa', True
    bear = 'bearers' in c or 'life-note' in c
    if f in own_names and not bear:
        return 'own-name', True
    if (en_pron and f == fold(en_pron)) or 'pron' in c:
        return 'pronunciation', False
    if len(f) == 1 and cx.get('zone') != 'nav':
        return ('alphabet', False) if cx.get('kind') != 'name' else ('abbr', False)
    if f in ('ce', 'ah', 'bce', 'ad', 'ra', 'as', 'saw', 'pbuh', 'd. c', 'b. c', 'c', 'ca'):
        return 'abbr', False
    if re.fullmatch(r'[a-z]( [a-z]){1,4}', f) and '-' in ph:
        return 'root-latin', False
    if bear or re.search(r"\b(ibn|bint|bin|binti|abu|abi|umm|abd)\b|\bal-|\bel-", ph, re.I):
        return 'person', False
    if f in all_names:
        return ('other-name', False) if cx.get('kind') == 'name' else ('own-name', True)
    return 'ui', False


def audit_page(site, lang, path, src, en, idx, ctxd):
    """returns dict(metrics, findings{check:[examples]})"""
    F = collections.defaultdict(list)

    def add(k, ex=''):
        if len(F[k]) < 4:
            F[k].append(ex if isinstance(ex, str) else str(ex))
        else:
            F[k].append('')
    url = '/' + path[:-len('index.html')]
    slug = path.split('/')[2] if path.count('/') >= 3 else None
    kind = 'name' if slug else ('home' if path == lang + '/index.html' else 'hub')
    hd = head_info(src)
    pg = Page(src)
    body_text = re.sub(r'\s+', ' ', ' '.join(t for t, c in pg.nodes if not c['hidden']))
    M = {'kind': kind, 'slug': slug, 'words': words(body_text), 'bytes': len(src)}

    # ---- 1 plumbing
    if hd['lang'] != lang:
        add('P1 html lang wrong or missing', f"lang={hd['lang']!r}")
    if hd['dir'] != DIR[lang]:
        add('P2 html dir wrong or missing', f"dir={hd['dir']!r}, expected {DIR[lang]}")
    if rel(hd['canonical']) != url:
        add('P3 canonical is not the page itself', f"canonical={hd['canonical']}")
    hl = {k: rel(v) for k, v in hd['hreflang'].items()}
    if hl.get(lang) != url:
        add('H1 hreflang: no entry for the page itself', f"hreflang {lang} = {hl.get(lang)}")
    if 'x-default' not in hl:
        add('H2 hreflang: x-default missing')
    if 'en' not in hl:
        add('H3 hreflang: English missing')
    for k, v in hl.items():
        if v and v.startswith('/') and not site.exists_url(v):
            add('H4 hreflang points at a page that does not exist', f'{k} -> {v}')
    # which languages actually have this page
    def sibling(l2):
        if kind == 'name':
            return ('' if l2 == 'en' else l2 + '/') + f'names/{slug}/'
        if kind == 'hub':
            return ('' if l2 == 'en' else l2 + '/') + path[len(lang) + 1:-len('index.html')]
        return '' if l2 == 'en' else l2 + '/'
    have = [l2 for l2 in ['en'] + LANGS if sibling(l2) in site.dirs]
    M['siblings'] = have
    miss = [l2 for l2 in have if l2 not in hl]
    if miss:
        add('H5 hreflang set incomplete (a translation exists but is not listed)', 'missing: ' + ','.join(miss))
    for l2 in have:
        if l2 == lang or l2 not in hl:
            continue
        other = ctxd['head'](sibling(l2) + 'index.html')
        if other is not None and rel(other['hreflang'].get(lang)) != url:
            add('H6 hreflang not returned by the other page', f'{l2} page {("/" + sibling(l2))} does not list {lang}')
    if hd['hreflang_dupe']:
        add('H7 hreflang listed twice', ','.join(hd['hreflang_dupe']))
    if not hd['ogloc']:
        add('P4 og:locale missing')
    elif hd['ogloc'] not in OGLOC[lang]:
        add('P4 og:locale wrong', hd['ogloc'])
    if hd['jsonld_err']:
        add('P5 JSON-LD does not parse', hd['jsonld_err'][0])
    types = collections.Counter(x.get('@type') if isinstance(x.get('@type'), str) else str(x.get('@type')) for x in hd['jsonld'])
    for x in hd['jsonld']:
        t = x.get('@type')
        if t in ('Article', 'FAQPage', 'WebPage', 'CollectionPage', 'WebSite', 'DefinedTerm'):
            il = x.get('inLanguage')
            if not il:
                add('P6 JSON-LD inLanguage missing', f'{t}')
            elif str(il).split('-')[0].lower() != lang:
                add('P6 JSON-LD inLanguage wrong', f'{t}: {il}')
        if t == 'BreadcrumbList':
            items = x.get('itemListElement', [])
            urls = [rel(i.get('item')) for i in items if isinstance(i.get('item'), str)]
            if len(urls) >= 2 and urls[0] == urls[1]:
                add('P7 breadcrumb data: "home" and "names" are the same URL', f'{urls[0]}')
            for u in urls:
                if u and u.startswith('/') and not site.exists_url(u):
                    add('P7 breadcrumb data points at a page that does not exist', u)
    if kind == 'name' and not types.get('Article'):
        add('P8 JSON-LD Article missing')
    for nm, val in (('title', hd['title']), ('meta description', hd['desc'])):
        if not val:
            add(f'T1 {nm} missing')
            continue
        if lang != 'tr':
            sh = expected_script_share(lang, val)
            if sh < 0.5:
                add(f'T2 {nm} is mostly not in {LANGNAME[lang]} script', f'{round(sh * 100)}% {LANGNAME[lang]} letters: {val[:110]}')
        eng = [w for w in re.findall(r'(?<![\w-])[A-Za-z]+(?![\w-])', val) if w.lower() in ENGLISH_WORDS - TR_ALSO and (lang != 'tr' or w.lower() not in TR_ALSO)]
        if eng and lang != 'tr' or len(eng) >= 2:
            add(f'T3 English words in the {nm}', f'{eng[:5]}: {val[:110]}')
        if '—' in val:
            add(f'T4 em dash in the {nm}', val[:110])
    if hd['title'] and len(hd['title']) > 65:
        M['title_len'] = len(hd['title'])
    if hd['desc'] and len(hd['desc']) > 165:
        M['desc_len'] = len(hd['desc'])
    if hd['title'] and hd['ogtitle'] and hd['ogtitle'] != hd['title']:
        add('T5 og:title differs from the title', hd['ogtitle'][:90])
    if not hd['ogtitle'] or not hd['ogdesc']:
        add('T6 og:title or og:description missing')
    if not hd['twtitle']:
        add('T7 twitter:title missing')
    if hd['ogimage'] and not site.exists_url(rel(hd['ogimage'])):
        add('P9 og:image file does not exist', hd['ogimage'])
    if not hd['ogimage']:
        add('P9 og:image missing')
    dm = [x.get('dateModified') for x in hd['jsonld'] if x.get('dateModified')]
    dates = {k: v[:10] for k, v in (('meta', hd['modified']), ('time tag', hd['time_tag']), ('JSON-LD', dm[0] if dm else None)) if v}
    if kind == 'name':
        if len(set(dates.values())) > 1:
            add('P10 the page states two different "last modified" dates', str(dates))
        if not dates:
            add('P11 no "last modified" date anywhere')
        elif 'JSON-LD' not in dates:
            add('P12 JSON-LD dateModified missing')
    if url not in ctxd['sitemap']:
        add('P13 page is not in any sitemap', url)
    if hd['robots'] and 'noindex' in hd['robots']:
        add('P14 page is set to noindex', hd['robots'])

    # ---- structure
    if pg.unclosed:
        add('X1 HTML: block element never closed', ','.join(sorted(set(pg.unclosed))))
    if pg.stray:
        add('X2 HTML: closing tag without an opening tag', ','.join(sorted(set(pg.stray))))
    for i, n in pg.ids.items():
        if n > 1:
            add('X3 HTML: same id used twice', i)
    for e in pg.empty:
        add('X4 empty element (blank paragraph, list item or value)', e)
    for lb, v in pg.qf:
        if lb and v == '':
            add('X4b fact row with an empty value', f'label "{lb}"')
    if len(pg.h['h1']) != 1:
        add('X5 page does not have exactly one H1', f"{len(pg.h['h1'])} H1")
    ks = [int(m.group(1)) for k in pg.kickers for m in [re.search(r'(\d+)', nd(k))] if m]
    if ks and ks != list(range(1, len(ks) + 1)):
        add('X6 section numbers skip or run out of order', ' '.join(map(str, ks)) + '  (' + ' | '.join(pg.kickers)[:120] + ')')

    # ---- 2 + 3 text
    own = set()
    d = idx.get(slug) if slug else None
    if d:
        own = {fold(d['n'])} | {fold(v) for v in d.get('v', [])} | {fold(w) for w in re.split(r'[ -]', d['n'])}
    en_pron = en.get('pron') if en else None
    lat = collections.Counter()
    lat_ex = {}
    digs = collections.Counter()
    forms = collections.Counter()
    form_ex, form_ex_mixed = [], []
    own_ar = {strip_h(w) for w in re.split(r'\s+', (d or {}).get('a', '')) if w}
    own_ur = {strip_h(w) for w in re.split(r'\s+', (d or {}).get('u', '')) if w}
    para = []
    cur_label = ''
    for text, cx in pg.nodes:
        if cx['hidden']:
            continue
        c = cx['cls']
        if 'qf-label' in c:
            cur_label = text.strip()
        nlang = cx['lang']
        # Latin strings
        ltext = RE_SOURCES.sub(' ', text)
        if lang != 'tr':
            for ph in latin_phrases(ltext):
                if nlang == 'en' and cx['tag'] == 'a':
                    b, ok = 'switcher', True
                else:
                    cx['kind'] = kind
                    b, ok = classify_latin(ph, cx, own, ctxd['names'], en_pron)
                    if b == 'ui' and 'qf-value' in c and cur_label in LABELS[lang].get('roman', []) + LABELS[lang].get('pron', []):
                        b, ok = ('pronunciation', False) if cur_label in LABELS[lang].get('pron', []) else ('own-name', True)
                lat[(b, ph)] += 1
                lat_ex.setdefault((b, ph), text.strip()[:140])
        else:
            for w in re.findall(r'[A-Za-z]+', ltext):
                if w.lower() in ENGLISH_WORDS - TR_ALSO and not (nlang == 'en'):
                    if not (cx['tag'] == 'a' and w.lower() == 'english'):
                        lat[('ui', w)] += 1
                        lat_ex.setdefault(('ui', w), text.strip()[:140])
        # digits
        if nlang != 'en':
            digs['west'] += sum(ch in WEST for ch in text)
            digs['arin'] += sum(ch in ARIN for ch in text)
            digs['exin'] += sum(ch in EXIN for ch in text)
            digs['deva'] += sum(ch in DEVD for ch in text)
        # letter forms
        if lang in ('ur', 'ar') and nlang not in ('en',) and cx['zone'] not in ('nav', 'footer') and 'crosslang' not in c:
            table = AR_FORMS_IN_UR if lang == 'ur' else UR_FORMS_IN_AR
            other_tab = UR_ONLY if lang == 'ur' else AR_ONLY
            other = 'ar' if lang == 'ur' else 'ur'
            excl_cls = ('arabic-name', 'root-glyph', 'letter-arabic', 'hi-letter-ar')
            excl_lab = (LABELS[lang].get('arabic', []) + LABELS[lang].get('root', []) + LABELS[lang].get('letters', [])) if lang == 'ur' else LABELS[lang].get('urdu', [])
            if nlang == other or any(e in c for e in excl_cls) or ('qf-value' in c and cur_label in excl_lab):
                pass
            else:
                t2 = re.sub(r'«[^»]*»|﴿[^﴾]*﴾|"[^"]*"|“[^”]*”', ' ', text)      # quoted Arabic (Quran, hadith, cited words)
                if lang == 'ar':
                    t2 = re.sub(r'(?:بالأردية|بالأردو|الأردية|الأردي)[^.،؛]{0,40}', ' ', t2)   # a sentence that quotes the Urdu spelling
                for tok in re.findall(r'[\u0621-\u065f\u066e-\u06d3\u06fa-\u06ff\u0670]+', t2):
                    if RE_HARAKAT.search(tok) and lang == 'ur':
                        continue                                   # vocalised: an Arabic citation
                    bare = strip_h(tok)
                    if len(bare) < 2 or bare in (own_ar if lang == 'ur' else own_ur):
                        continue
                    hit = [ch for ch in bare if ch in table]
                    if hit:
                        mixed = any(ch in other_tab for ch in bare)
                        for ch in set(hit):
                            forms[('mixed ' if mixed else 'whole ') + ch] += 1
                        ex = form_ex_mixed if mixed else form_ex
                        if len(ex) < 4:
                            ex.append(f'{tok}  in: {text.strip()[:90]}  [{c[-40:]}]')
        # half-translated sentences
        if lang != 'tr' and nlang != 'en' and (RE_ARAB_LETTER.search(text) or RE_DEVA.search(text)):
            hw = [w for w in re.findall(r"(?<![\w\-.'’])[A-Za-z]+(?![\w\-'’])", re.sub(r'Behind the Name|Encyclopaedia of Islam|Dictionary of [A-Z]\w+', ' ', text)) if w.lower() in HALF]
            if hw:
                add('U8 half-translated sentence (English words inside a ' + LANGNAME[lang] + ' sentence)', f'{hw[:4]} in: {text.strip()[:150]}')
        # punctuation
        if lang in ('ur', 'ar'):
            for m in re.finditer(r'[ء-ۓ][,;?](?=\s|$)', text):
                add('S5 Latin comma, semicolon or question mark after ' + LANGNAME[lang] + ' text (should be ، ؛ ؟)', text.strip()[max(0, m.start() - 40):m.start() + 20])
        for m in re.finditer(r'\S\s,\s', text):
            add('S6 space before a comma (left over where a dash was removed)', text.strip()[max(0, m.start() - 40):m.start() + 30])
        if '—' in text:
            add('S7 em dash in visible text (house rule: none)', text.strip()[:110])
        for m in JUNK.finditer(text):
            g = m.group(0)
            if g in ('None', 'null', 'none') and lang == 'tr':
                continue
            add('S8 placeholder, template token or broken character in visible text', f'{g!r} in: {text.strip()[max(0, m.start() - 40):m.start() + 40]}')
        for ch in ZW:
            if ch in text:
                add('S9 invisible control character in visible text', f'{ZW[ch]} (U+{ord(ch):04X}) in: {text.strip()[:70]}')
        if cx['tag'] == 'p' and len(text.strip()) >= 60 and cx['zone'] not in ('nav', 'footer'):
            para.append(text.strip())
    for k, v, tag in pg.attrs_text:
        if lang != 'tr':
            if RE_LATIN_LETTER.search(v) and expected_script_share(lang, v) < 0.5 and fold(v) not in BRAND and fold(v) not in own:
                add('U2 English in a screen-reader label or alt text', f'{k}="{v}" on <{tag}>')
        elif any(w.lower() in ENGLISH_WORDS - TR_ALSO for w in re.findall(r'[A-Za-z]+', v)):
            add('U2 English in a screen-reader label or alt text', f'{k}="{v}" on <{tag}>')
    M['latin'] = {f'{b}|{ph}': n for (b, ph), n in lat.items()}
    for (b, ph), n in lat.items():
        if b == 'ui':
            M.setdefault('ui_ex', {})[ph] = lat_ex[(b, ph)]
        elif b == 'person':
            add('S1 name of a person or place left in Latin letters', f'"{ph}" in: {lat_ex[(b, ph)]}')
        elif b == 'pronunciation':
            add('S2 pronunciation given only in Latin letters', f'"{ph}" in: {lat_ex[(b, ph)]}')
        elif b == 'alphabet':
            add('U3 Latin A to Z used as index letters', f'"{ph}" in: {lat_ex[(b, ph)]}')
        elif b == 'abbr':
            add('U6 English abbreviation left in (c., b., d., CE, AH)', f'"{ph}" in: {lat_ex[(b, ph)]}')
        elif b == 'root-latin':
            add('U7 Arabic root written in Latin letters', f'"{ph}" in: {lat_ex[(b, ph)]}')
        elif b == 'other-name':
            add('S1b another name written in Latin letters inside the text', f'"{ph}" in: {lat_ex[(b, ph)]}')
    if forms:
        if form_ex_mixed:
            nm = 'S3a one word mixes Urdu and Arabic letter forms' if lang == 'ur' else 'S3a one word mixes Arabic and Urdu letter forms'
            for e in form_ex_mixed:
                add(nm, e)
            for _ in range(sum(n for k, n in forms.items() if k.startswith('mixed')) - len(form_ex_mixed)):
                F[nm].append('')
        if form_ex:
            nm = 'S3b whole word in Arabic letter forms inside Urdu text' if lang == 'ur' else 'S3b whole word in Urdu letter forms inside Arabic text'
            for e in form_ex:
                add(nm, e)
        M['forms'] = {k: n for k, n in forms.items()}
    M['digits'] = dict(digs)
    native = {'ur': 'exin', 'ar': 'arin', 'hi': 'deva'}.get(lang)
    if lang in ('ur', 'ar'):
        wrong = 'arin' if lang == 'ur' else 'exin'
        if digs[wrong]:
            add('S4b digits of the wrong family (' + ('Arabic ٤٥٦ on an Urdu page' if lang == 'ur' else 'Urdu ۴۵۶ on an Arabic page') + ')', f'{digs[wrong]} digits')
        if digs['west'] and digs[native]:
            add('S4a Western and ' + LANGNAME[lang] + ' digits mixed on one page', f"{digs['west']} Western, {digs[native]} {LANGNAME[lang]}")
    if lang == 'hi' and digs['west'] and digs['deva']:
        add('S4a Western and Hindi digits mixed on one page', f"{digs['west']} Western, {digs['deva']} Devanagari")
    # Arabic-script leftovers on Hindi / Turkish pages are expected (the name in Arabic); nothing to flag.

    # brand
    brands = collections.Counter()
    full = body_text + ' ' + (hd['title'] or '') + ' ' + (hd['desc'] or '')
    for b in ctxd['brand_re'].findall(full):
        brands[strip_h(b)] += 1
    M['brand'] = dict(brands)

    # ---- 4 coverage / links
    seen_sw = set()
    for a in pg.links:
        h = a['href']
        if not h or h.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
            continue
        if h.startswith(SITE):
            h = h[len(SITE):]
        if not h.startswith('/'):
            if h.startswith('http'):
                M['ext_links'] = M.get('ext_links', 0) + 1
            continue
        M['int_links'] = M.get('int_links', 0) + 1
        if not site.exists_url(h) and h.split('#')[0].split('?')[0] not in ctxd['redirects']:
            add('L1 link to a page that does not exist (404)', f'{h}  "{a["text"][:40]}"')
            continue
        m = re.match(r'/(?:(ur|ar|hi|tr)/)?(.*)$', h.split('#')[0].split('?')[0])
        tl, rest = m.group(1) or 'en', m.group(2)
        is_switch = bool(a['hreflang']) or a['lang'] == 'en' or fold(a['text']) in SWITCH or a['text'].strip() in ('العربية', 'اردو', 'हिन्दी', 'हिंदी', 'Türkçe', 'English', 'EN') \
            or 'crosslang' in a['cls']
        if is_switch:
            seen_sw.add(tl)
            continue
        if tl == 'en':
            same = lang + '/' + rest
            if re.search(r'الإنجليزية|انگریزی|अंग्रेज़ी|İngilizce|English', a['text']):
                add('C13 page sends the reader to the English page for the rest', f'{h}  "{a["text"][:40]}"')
            elif same in site.dirs or same.rstrip('/') + '/' in site.dirs:
                add('L2 link goes to the English page although a ' + LANGNAME[lang] + ' page exists', f'{h}  "{a["text"][:40]}"  ({"/" + same} exists)')
            else:
                sec = rest.split('/')[0] or 'home'
                M.setdefault('en_only', collections.Counter())[sec] += 1
                if RE_ARAB.search(a['text']) or RE_DEVA.search(a['text']) or lang == 'tr':
                    add('L3 translated link label leads to an English-only page', f'{h}  "{a["text"][:40]}"')
        elif tl != lang:
            add('L4 link goes to another language (not a language switcher)', f'{h}  "{a["text"][:40]}"')
    if 'en_only' in M:
        M['en_only'] = dict(M['en_only'])
    if kind == 'name':
        cross = {m.group(1) or 'en' for a in pg.links if 'crosslang' in a['cls'] or a['hreflang'] for m in [re.match(r'/(?:(ur|ar|hi|tr)/)?names/', a['href'].replace(SITE, ''))] if m}
        want = set(have) - {lang}
        if want - cross:
            add('C3 "this name in other languages" misses a language that has the page', 'missing: ' + ','.join(sorted(want - cross)))
        if not d and 'en' not in have:
            add('C2 name page has no English page', url)
        # visible breadcrumb
        bc = [a for a in pg.links if a['zone'] == 'breadcrumb']
        hrefs = [a['href'] for a in bc]
        if len(hrefs) >= 2 and len(set(hrefs)) < len(hrefs):
            add('L5 breadcrumb: two steps go to the same page', ' , '.join(f'"{a["text"]}" -> {a["href"]}' for a in bc))
        jb = [rel(i.get('item')) for x in hd['jsonld'] if x.get('@type') == 'BreadcrumbList' for i in x.get('itemListElement', []) if isinstance(i.get('item'), str)]
        if hrefs and jb and hrefs != jb[:len(hrefs)]:
            add('L6 breadcrumb on the page and breadcrumb in the data disagree', f'page {hrefs} vs data {jb}')

    if kind == 'name':
        bn = [i.get('name') for x in hd['jsonld'] if x.get('@type') == 'BreadcrumbList' for i in x.get('itemListElement', [])]
        bt = [a['text'] for a in pg.links if a['zone'] == 'breadcrumb']
        if bn and bt and bn[0] != bt[0]:
            add('L7 breadcrumb wording differs between the page and the data', f'page "{bt[0]}" vs data "{bn[0]}"')
    noads = {'ur': r'بغیر اشتہار|نہ اشتہار|اشتہار نہیں|اشتہارات کے بغیر', 'ar': r'بلا إعلانات|لا إعلانات|بدون إعلانات', 'hi': r'विज्ञापन नहीं|बिना विज्ञापन|विज्ञापन-मुक्त|विज्ञापन मुक्त', 'tr': r'reklamsız|reklam yok'}[lang]
    m = re.search(noads, body_text)
    if m and 'adsbygoogle' in src:
        add('Z1 page says the site has no advertising, and the same page loads the ad code', body_text[max(0, m.start() - 60):m.end() + 40])
    m = re.search(r'انگریزی ماخذ کے مطابق|انگریزی صفحہ|الصفحة الإنجليزية|المصدر الإنجليزي|अंग्रेज़ी पृष्ठ|İngilizce sayfa', body_text)
    if m and kind == 'name':
        add('C14 text leans on the English page ("according to the English source", "see the English page")', body_text[max(0, m.start() - 50):m.end() + 60])
    if kind != 'name':
        nums = sorted({int(x) for x in re.findall(r'(?<![\d,.:])(\d{3,4})(?![\d,.:])', nd(body_text)) if 150 <= int(x) <= 3000})
        M['counts_stated'] = nums

    # ---- FAQ parity (visible vs JSON-LD)
    vis = [(q, a or '') for q, a in pg.faq]
    jf = [(e.get('name', ''), (e.get('acceptedAnswer') or {}).get('text', '')) for x in hd['jsonld'] if x.get('@type') == 'FAQPage' for e in x.get('mainEntity', [])]
    M['faq_visible'], M['faq_data'] = len(vis), len(jf)
    if kind == 'name':
        if len(vis) != len(jf):
            add('Q1 FAQ: number of questions on the page and in the data differ', f'{len(vis)} on page, {len(jf)} in data')
        sq = lambda s: re.sub(r'[\s.,;:،۔।]+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()
        vd = {sq(q): sq(a) for q, a in vis}
        for q, a in jf:
            if sq(q) not in vd:
                add('Q2 FAQ: question in the data is not on the page', q[:90])
            elif sq(a) != vd[sq(q)] and sq(a) not in vd[sq(q)]:
                add('Q3 FAQ: answer in the data differs from the answer on the page', f'{q[:50]} | data: {a[:70]} | page: {vd[sq(q)][:70]}')

    # ---- 5 parity + facts
    if kind == 'name':
        fl = facts_loc(lang, pg, body_text, slug)
        cls_all = ' '.join(c['cls'] for _, c in pg.nodes)
        M['has'] = {'bearers': 'bearers' in src, 'pron': bool(fl.get('pron')) or 'asr-pron' in src or bool(re.search(r'उच्चारण|telaffuz|okunuş', body_text, re.I)),
                    'letters': 'letter-grid' in src, 'verse': bool(verse_refs(body_text)), 'related': len([a for a in pg.links if 'related-card' in a['cls'] or 'name-list' in a['cls']])}
        M['facts'] = {k: v for k, v in fl.items() if not k.startswith('_') and v}
        M['labels'] = fl['_labels']
        hero = None
        m = re.search(r'class="arabic-name"[^>]*>([^<]+)<', src)
        if m:
            hero = html.unescape(m.group(1)).strip()
        M['facts']['hero'] = hero
        ql = None
        for q, a in vis:
            if re.search(r'قرآن|القرآن|क़ुरआन|कुरआन|Kur', q):
                ql = a
                break
        M['facts']['quran_answer'] = ql
        if 'asr-pron' not in src and not fl.get('pron') and lang in ('ur',):
            pass
    M['paras'] = para
    return M, {k: v for k, v in F.items()}


# ----------------------------------------------------------------------------- english side metrics
def en_metrics(h):
    b = h[h.find('<body'):]
    t = txt(b)
    faq = 0
    for x in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', h, re.S):
        if 'FAQPage' in x:
            try:
                j = json.loads(x)
                for y in (j.get('@graph', [j]) if isinstance(j, dict) else j):
                    if isinstance(y, dict) and y.get('@type') == 'FAQPage':
                        faq = len(y.get('mainEntity', []))
            except ValueError:
                pass
    return {'words': words(t), 'faq': faq, 'bearers': bool(re.search(r'bearers-list|np-bearers|id="famous"', h)), 'pron': 'data-asr-field="pronunciation"' in h,
            'letters': 'asr-v2-letter-arabic' in h, 'verse': bool(verse_refs(t)), 'int_links': len(re.findall(r'<a\s[^>]*href="/(?!/)', b)),
            'name_links': len(set(re.findall(r'href="/names/([a-z0-9-]+)/"', b)))}


# ----------------------------------------------------------------------------- run
def main():
    args = sys.argv[1:]
    ref = None if '--tree' in args else (args[args.index('--ref') + 1] if '--ref' in args else 'origin/main')
    site = Site(ref)
    idx_list = json.loads(site.read('names/names-index.json'))
    idx = {d['s']: d for d in idx_list}
    all_names = {fold(d['n']) for d in idx_list}
    redirects = set()
    for line in (site.read('_redirects') or '').split('\n'):
        p = line.split()
        if len(p) >= 2 and p[0].startswith('/'):
            redirects.add(p[0])
    sitemap = set()
    sm_files = sorted(f for f in site.files if re.fullmatch(r'sitemap[^/]*\.xml', f))
    for f in sm_files:
        sitemap |= {rel(u) for u in re.findall(r'<loc>([^<]+)</loc>', site.read(f) or '')}
    head_cache = {}

    def head_of(path):
        if path not in head_cache:
            s = site.read(path)
            head_cache[path] = head_info(s) if s else None
        return head_cache[path]
    brand_re = re.compile(r'(?<![\u0600-\u06ff\u0900-\u097fA-Za-z])(?:' + '|'.join(['ا[\u064b-\u0652]?ث[\u064b-\u0652]?ر ?نام', 'ا[\u064b-\u0652]?سر ?نام', 'أثر ?نام', 'असर ?नाम', 'अस्र ?नाम', 'AsrNaam', 'Asr Naam', 'Asrnaam', 'ASRNAAM'])
                          + r')(?![\u0600-\u06ff\u0900-\u097fA-Za-z])')
    ctxd = {'head': head_of, 'sitemap': sitemap, 'redirects': redirects, 'names': all_names, 'brand_re': brand_re}

    pages = {l: sorted(f for f in site.files if f.startswith(l + '/') and f.endswith('index.html')) for l in LANGS}
    en_slugs = sorted(s for s in idx if f'names/{s}/index.html' in site.files)
    EN = {}
    for s in en_slugs:
        h = site.read(f'names/{s}/index.html')
        EN[s] = dict(facts_en(h), **{'m': en_metrics(h)}, **{'head': head_info(h)})
        head_cache[f'names/{s}/index.html'] = EN[s]['head']

    R = {}          # path -> {m, f}
    for l in LANGS:
        for p in pages[l]:
            src = site.read(p)
            slug = p.split('/')[2] if p.count('/') >= 3 else None
            try:
                M, F = audit_page(site, l, p, src, EN.get(slug), idx, ctxd)
            except Exception as e:   # one bad page must not stop the audit; it is itself a finding
                M, F = {'kind': 'name' if slug else 'hub', 'slug': slug, 'words': 0}, {'X0 page could not be parsed by the audit': [repr(e)[:160]]}
            R[p] = {'lang': l, 'm': M, 'f': F}

    if '--discover' in args:
        discover(R, EN)
        return

    post(site, R, EN, idx, pages, sitemap, sm_files)
    write(site, R, EN, idx, pages)


def discover(R, EN):
    for l in LANGS:
        lab, lat, org, gen = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
        for p, r in R.items():
            if r['lang'] != l or r['m'].get('kind') != 'name':
                continue
            for x in r['m'].get('labels', []):
                lab[x] += 1
            for k, n in r['m'].get('latin', {}).items():
                lat[k] += 1
            e = EN.get(r['m']['slug']) or {}
            org[(e.get('origin'), r['m'].get('facts', {}).get('origin'))] += 1
            gen[(e.get('gender'), r['m'].get('facts', {}).get('gender'))] += 1
        print('=====', l)
        print(' labels', lab.most_common(30))
        print(' gender pairs', gen.most_common(12))
        print(' origin pairs', org.most_common(40))
        for b in ('ui', 'person', 'pronunciation', 'alphabet', 'other-name', 'switcher', 'brand'):
            print(' latin', b, [(k.split('|', 1)[1], n) for k, n in lat.most_common(4000) if k.startswith(b + '|')][:40])


# ----------------------------------------------------------------------------- cross-page checks
def post(site, R, EN, idx, pages, sitemap, sm_files):
    def add(p, k, ex=''):
        R[p]['f'].setdefault(k, [])
        R[p]['f'][k].append(ex)

    # sitemap entries without a page
    R['_site'] = {'lang': 'site', 'm': {}, 'f': {}}
    for u in sorted(sitemap):
        m = re.match(r'/(ur|ar|hi|tr)/', u or '')
        if m and not site.exists_url(u):
            R['_site']['f'].setdefault('P15 sitemap lists a URL that does not exist', []).append(u)
    R['_site']['m']['sitemaps'] = sm_files
    for l in LANGS:
        if f'{l}/index.html' not in site.files:
            R['_site']['f'].setdefault('P16 language has no home page', []).append(f'/{l}/')
        for sec in ('letters', 'about', 'contact', 'privacy', 'terms'):
            if not any(f.startswith(f'{l}/{sec}/') for f in site.files):
                R['_site']['f'].setdefault('C1 section exists only in English', []).append(f'/{l}/{sec}/')

    # origin / gender maps learnt from the data: the usual pairing is the translation, the unusual pairing is a disagreement
    for l in LANGS:
        pair = collections.Counter()
        for p in pages[l]:
            r = R[p]
            s = r['m'].get('slug')
            if s in EN and r['m'].get('facts', {}).get('origin') and EN[s].get('origin'):
                pair[(EN[s]['origin'], r['m']['facts']['origin'])] += 1
        by_en = collections.defaultdict(collections.Counter)
        by_loc = collections.defaultdict(collections.Counter)
        for (e, o), n in pair.items():
            by_en[e][o] += n
            by_loc[o][e] += n
        R['_site']['m'].setdefault('origin_map', {})[l] = {e: c.most_common(3) for e, c in by_en.items()}
        for p in pages[l]:
            r = R[p]
            s = r['m'].get('slug')
            if r['m'].get('kind') != 'name':
                continue
            f = r['m'].get('facts', {})
            e = EN.get(s)
            if not e:
                continue
            # gender
            if f.get('gender') and e.get('gender') and f['gender'] != e['gender']:
                add(p, 'F1 FACT gender differs from the English page', f"English {e['gender']}, {LANGNAME[l]} {f['gender']}")
            if f.get('gender', '').startswith('?'):
                add(p, 'F1b gender value not recognised by the audit', f['gender'])
            # origin
            if f.get('origin') and e.get('origin'):
                top_for_en = by_en[e['origin']].most_common(1)[0]
                top_for_loc = by_loc[f['origin']].most_common(1)[0]
                # disagreement when this English origin is usually translated otherwise AND this local label usually stands for another English origin
                if top_for_en[0] != f['origin'] and top_for_loc[0] != e['origin'] and top_for_en[1] >= 3:
                    add(p, 'F2 FACT origin differs from the English page', f"English \"{e['origin']}\", {LANGNAME[l]} \"{f['origin']}\" (elsewhere \"{e['origin']}\" is \"{top_for_en[0]}\")")
            elif e.get('origin') and not f.get('origin') and l in ('ur', 'ar', 'tr'):
                add(p, 'F2b origin stated in English but absent here', e['origin'])
            elif f.get('origin') and not e.get('origin') and not re.search(r'درج نہیں|غير مذكور|غير معروف', f['origin']):
                add(p, 'F2c FACT origin stated here although the English page states none', f"{LANGNAME[l]} \"{f['origin']}\"")
            # numbers
            if f.get('lucky') and e.get('lucky') and nd(f['lucky']) != nd(e['lucky']):
                add(p, 'F3 FACT lucky number differs from the English page', f"English {e['lucky']}, {LANGNAME[l]} {f['lucky']}")
            # arabic spelling
            ia = idx.get(s, {}).get('a')
            for nm, val in (('name in Arabic in the page header', f.get('hero')), ('"Arabic spelling" fact', f.get('arabic'))):
                if val and ia and unicodedata.normalize('NFC', val) != unicodedata.normalize('NFC', ia):
                    if norm_ar(val) != norm_ar(ia):
                        add(p, 'F4 FACT Arabic spelling of the name differs from the site index', f'{nm}: {val} vs index {ia}')
                    else:
                        add(p, 'F4b Arabic spelling: same letters as the index, vowel marks differ or are missing on one side', f'{nm}: {val} vs index {ia}')
            if e.get('arabic') and f.get('hero') and norm_ar(e['arabic']) != norm_ar(f['hero']):
                add(p, 'F4 FACT Arabic spelling of the name differs from the English page', f"English {e['arabic']}, {LANGNAME[l]} {f['hero']}")
            # urdu spelling
            iu = idx.get(s, {}).get('u')
            if f.get('urdu') and iu and strip_h(f['urdu']) != strip_h(iu):
                if norm_ar(f['urdu']) != norm_ar(iu):
                    add(p, 'F5 FACT Urdu spelling of the name differs from the site index (which the English page shows)', f"{LANGNAME[l]} page {f['urdu']} vs index {iu}")
                else:
                    add(p, 'F5b Urdu spelling: same word as the index, but Arabic versus Urdu letter forms, hamza or spacing differ', f"{LANGNAME[l]} page {f['urdu']} vs index {iu}")
            if f.get('urdu') and len(RE_HARAKAT.findall(f['urdu'])) >= 2 and f.get('hero') and unicodedata.normalize('NFC', f['urdu']) == unicodedata.normalize('NFC', f['hero']):
                add(p, 'F15 "Urdu spelling" is a copy of the vowelled Arabic spelling', f"{f['urdu']}")
            cards = len(re.findall(r'class="(?:asr-v2-letter-arabic|hi-letter-ar)"', site.read(p) or ''))
            if f.get('nletters') and f['nletters'].isdigit() and cards and int(f['nletters']) != cards:
                add(p, 'F14 FACT number of letters stated differs from the letters shown on the same page', f"states {f['nletters']}, shows {cards} letter cards")
            if f.get('urdu') and RE_HARAKAT.search(f['urdu']) and l != 'ur':
                pass
            # root
            if f.get('root') and e.get('root'):
                ra = lambda v: (lambda m: norm_ar(m.group(0)) if m else '')(re.search(r'[\u0621-\u064a\u06a9\u06cc](?:\s*[-\u2011]\s*[\u0621-\u064a\u06a9\u06cc]){1,4}', strip_h(v)))
                a, b = ra(f['root']), ra(e['root'])
                if a and b and a != b:
                    add(p, 'F6 FACT Arabic root differs from the English page', f"English {e['root'][:30]}, {LANGNAME[l]} {f['root'][:30]}")
            # letters count
            if f.get('nletters') and e.get('letters'):
                n_en = len(norm_ar(e['letters']))
                if f['nletters'].isdigit() and int(f['nletters']) != n_en:
                    add(p, 'F7 FACT number of letters differs from the letters read on the English page', f"{LANGNAME[l]} says {f['nletters']}, English reads {n_en} ({e['letters']})")
            # pronunciation
            if f.get('pron') and e.get('pron') and l in ('ur', 'hi'):
                a, b = fold(re.sub(r'\s*/.*$', '', f['pron'])), fold(e['pron'])
                if a != b and b not in a and a not in b:
                    add(p, 'F8 FACT pronunciation differs from the English page', f"English {e['pron']}, {LANGNAME[l]} {f['pron'][:40]}")
            # quran
            qa = f.get('quran_answer')
            if qa is not None and e.get('quran_answer'):
                lv, ev = verse_refs(qa), e['verses']
                if lv and ev and not (lv & ev):
                    add(p, 'F9 FACT Quran reference differs from the English page', f"English {sorted(':'.join(v) for v in ev)[:3]}, {LANGNAME[l]} {sorted(':'.join(v) for v in lv)[:3]}")
                neg = re.match(r'\s*(Hayır|नहीं|لا[،\s]|نہیں|جی نہیں)', qa) is not None or re.search(r'نہیں آیا|ذکر نہیں|لم يرد|لم يُذكر|geçmez', qa[:120]) is not None
                pos = re.match(r'\s*(Evet|हाँ|نعم|جی ہاں)', qa) is not None or bool(lv)
                if e.get('quran_yes') == 'Y' and neg and not pos:
                    add(p, 'F10 FACT English says the name is in the Quran, this page says it is not', qa[:110])
                if e.get('quran_yes') == 'N' and pos and not neg:
                    add(p, 'F10 FACT English says the name is not in the Quran, this page says it is', f"{qa[:100]} | English: {e['quran_answer'][:110]}")
                if e.get('quran_yes') is None and l == 'ur' and 'قرآن میں یہاں ہے' in qa:
                    add(p, 'F10b FACT this page says the name or its word is mentioned in the Quran at a verse; the English answer does not say yes (it cites a root, an attribute or a theme)',
                        f"{qa[:90]} | English: {e['quran_answer'][:120]}")
            # cross-check locale total vs lucky (own page arithmetic)
            if f.get('total') and f.get('lucky') and f['total'].isdigit() and f['lucky'].isdigit():
                n = int(f['total'])
                while n > 9:
                    n = sum(map(int, str(n)))
                if n != int(f['lucky']):
                    add(p, 'F11 FACT abjad total and its reduced number do not agree on this page', f"total {f['total']} reduces to {n}, page says {f['lucky']}")
            # parity
            em, m = e['m'], r['m']
            m['ratio'] = round(m['words'] / em['words'], 2) if em['words'] else None
            m['en_words'], m['en_faq'] = em['words'], em['faq']
            if m['ratio'] is not None and m['ratio'] < 0.5:
                add(p, 'C4 content: fewer than half the words of the English page', f"{m['words']} words vs {em['words']} ({m['ratio']})")
            if m['faq_visible'] < em['faq']:
                add(p, 'C5 content: fewer FAQ questions than the English page', f"{m['faq_visible']} vs {em['faq']}")
            if em['bearers'] and not m['has']['bearers']:
                add(p, 'C6 content: English lists famous bearers, this page lists none')
            if em['pron'] and not m['has']['pron']:
                add(p, 'C7 content: English gives a pronunciation, this page gives none')
            if em['letters'] and not m['has']['letters']:
                add(p, 'C8 content: no letter-by-letter reading')
            if em['verse'] and not m['has']['verse']:
                add(p, 'C9 content: English cites a Quran verse, this page cites none')
            if m['has']['related'] == 0:
                add(p, 'C10 content: no related names')
            if m['words'] < 250:
                add(p, 'C11 thin page: under 250 words', f"{m['words']} words")

    # cross-language facts between the translations themselves (total, letters, hero spelling)
    by_slug = collections.defaultdict(dict)
    for l in LANGS:
        for p in pages[l]:
            if R[p]['m'].get('kind') == 'name':
                by_slug[R[p]['m']['slug']][l] = p
    for s, d in by_slug.items():
        for key, name in (('total', 'abjad total'), ('lucky', 'lucky number'), ('nletters', 'number of letters')):
            vals = {l: nd(R[p]['m'].get('facts', {}).get(key) or '') for l, p in d.items()}
            vals = {l: v for l, v in vals.items() if v}
            if len(set(vals.values())) > 1:
                for l, p in d.items():
                    if l in vals:
                        add(p, f'F12 FACT {name} differs between the translations', ' '.join(f'{k}={v}' for k, v in sorted(vals.items())))
        ur = {l: strip_h(R[p]['m'].get('facts', {}).get('urdu') or '') for l, p in d.items()}
        ur = {l: v for l, v in ur.items() if v}
        if len(set(ur.values())) > 1:
            real = len({norm_ar(v) for v in ur.values()}) > 1
            for l, p in d.items():
                if l in ur:
                    add(p, 'F13 FACT Urdu spelling of the name differs between the translations' if real else
                        'F13b Urdu spelling between the translations: same word, letter forms, hamza or spacing differ', ' '.join(f'{k}={v}' for k, v in sorted(ur.items())))

    # coverage
    cov = {l: sorted(set(idx) - {R[p]['m']['slug'] for p in pages[l] if R[p]['m'].get('kind') == 'name'}) for l in LANGS}
    R['_site']['m']['missing'] = cov
    R['_site']['m']['english_names'] = len([s for s in idx if s in EN])
    # English page not linking / not listing the translation
    for s, d in by_slug.items():
        e = EN.get(s)
        if not e:
            continue
        for l, p in d.items():
            if rel(e['head']['hreflang'].get(l)) != '/' + p[:-len('index.html')]:
                add(p, 'H8 the English page does not list this translation in hreflang', f'/names/{s}/')

    # English words in running text: template leftovers (many pages) versus one-off words
    for l in LANGS:
        c = collections.Counter()
        for p in pages[l]:
            for ph in R[p]['m'].get('ui_ex', {}):
                c[ph] += 1
        for p in pages[l]:
            for ph, ex in R[p]['m'].pop('ui_ex', {}).items():
                if c[ph] >= 5 or fold(ph) in ENGLISH_WORDS:
                    add(p, 'U1a English word left in the template (same string on many pages)', f'"{ph}" ({c[ph]} pages) in: {ex}')
                else:
                    add(p, 'U1b Latin-letter word inside the text (leftover or a deliberate gloss)', f'"{ph}" in: {ex}')
    # counts stated on home and hub pages
    for l in LANGS:
        n_pages = sum(1 for p in pages[l] if R[p]['m'].get('kind') == 'name')
        for p in pages[l]:
            cs = R[p]['m'].get('counts_stated')
            cs = [c for c in (cs or []) if abs(c - n_pages) <= 80]
            if cs and n_pages not in cs:
                add(p, 'Z2 number of names stated on the page differs from the name pages that exist', f'page states {cs}, {LANGNAME[l]} name pages on the site: {n_pages}, names in the index: {len(idx)}')

    # boilerplate
    for l in LANGS:
        cnt = collections.Counter()
        norm = {}
        for p in pages[l]:
            r = R[p]
            s = r['m'].get('slug')
            d = idx.get(s, {})
            reps = [x for x in {d.get('n'), d.get('a'), d.get('u'), strip_h(d.get('a') or ''), strip_h(d.get('u') or '')} if x]
            h1 = None
            out = []
            for t in r['m'].pop('paras', []):
                k = t
                for x in sorted(reps, key=len, reverse=True):
                    k = k.replace(x, '◌')
                k = re.sub(r'[\d' + ARIN + EXIN + DEVD + ']+', '#', k)
                out.append((k, words(t)))
            norm[p] = out
            for k in {k for k, _ in out}:
                cnt[k] += 1
        thr = max(20, int(len(pages[l]) * 0.02))
        tot_w = tot_b = 0
        for p in pages[l]:
            w = sum(n for _, n in norm[p])
            b = sum(n for k, n in norm[p] if cnt[k] >= thr)
            R[p]['m']['para_words'], R[p]['m']['boiler_words'] = w, b
            tot_w += w
            tot_b += b
            if R[p]['m'].get('kind') == 'name':
                uniq = R[p]['m']['words'] and (w - b)
                if w and b / w >= 0.6:
                    add(p, 'C12 most of the running text is wording shared with many other pages', f'{b} of {w} paragraph words are shared')
        R['_site']['m'].setdefault('boiler', {})[l] = {'share': round(tot_b / tot_w, 3) if tot_w else 0, 'threshold_pages': thr,
                                                         'top': [(k[:200], n) for k, n in cnt.most_common(6)]}

    # brand variants
    for l in LANGS:
        c = collections.Counter()
        for p in pages[l]:
            for b, n in R[p]['m'].get('brand', {}).items():
                c[b] += 1
        R['_site']['m'].setdefault('brand', {})[l] = c.most_common()
        native = [b for b, _ in c.most_common() if not re.match('[A-Za-z]', b)]
        main_b = native[0] if native else None
        for p in pages[l]:
            odd = [b for b in R[p]['m'].get('brand', {}) if not re.match('[A-Za-z]', b) and b != main_b]
            if odd:
                add(p, 'U4 site name spelled differently from the rest of the language', f'{odd} (usual: {main_b})')

    # runtime scripts
    js = collections.Counter()
    for l in LANGS:
        for p in pages[l][:50]:
            for s in head_info(site.read(p))['scripts']:
                js[(l, s)] += 1
    R['_site']['m']['scripts'] = sorted({s for (l, s), n in js.items()})
    eng_js = {}
    for s in R['_site']['m']['scripts']:
        code = site.read(s.lstrip('/')) or ''
        strs = set(re.findall(r"""(?:textContent|innerHTML|innerText|aria-label'\s*,|title\s*=|placeholder\s*=)\s*[=,(]?\s*['"`]([A-Z][A-Za-z ,.'!?]{3,60})['"`]""", code))
        loc = bool(re.search(r"documentElement\.lang|getAttribute\(['\"]lang|\bI18N\b|i18n|translations|STR\[|L10N", code))
        if strs:
            eng_js[s] = {'english_strings': sorted(strs)[:25], 'reads_page_language': loc}
    R['_site']['m']['js_english'] = eng_js


# ----------------------------------------------------------------------------- report
CLASS = [
    (r'^F4b|^F5b|^F13b|^F15', 'D'),
    (r'^F1b|^F14|^F11', 'A'),
    (r'^F\d', 'C'),
    (r'^P3 |^P9 |^P14|^P5 |^C2 |^T1 |^T2 |^T3 |^T4 |^X5 |^X0|^S2 |^S1b|^U3 |^U4 |^L4 |^Z1 ', 'D'),
    (r'^S3a', 'A*'),
    (r'^S3b|^U1b', 'C'),
    (r'^U1a|^U6 |^U7 |^U8 |^S1 |^C4 |^C5 |^C6 |^C7 |^C8 |^C9 |^C10|^C11|^C12|^C13|^C14|^L3 |^F2b|^X4b', 'B'),
    (r'^P|^H|^X|^L|^Q|^S|^T|^U2 |^C3 |^Z2 ', 'A'),
]
SERIOUS = [   # (check prefix, what it means in plain words)
    (r'^F10 |^F10b', 'Urdu pages say the name, or its word, "is mentioned in the Quran here" and give a verse, where the English answer says it is not in the Quran, or only cites a root, an attribute of God or a theme. A religious claim stated more strongly in Urdu than in the source.'),
    (r'^F3 |^F12 FACT (abjad|lucky)|^F11', 'The abjad total and the lucky number differ between languages for the same name. The odd one out is Hindi on 19 names and Turkish on 1. In 11 of the 19 the Hindi total is short by exactly 10, the value of the letter ya: those names are written with the Urdu form ی, which the Hindi calculation did not count.'),
    (r'^F4 ', 'The Arabic spelling of the name in the page header is a different word from the one on the English page and in the site index (not a vowel-mark difference).'),
    (r'^F13 |^F5 ', 'The Urdu spelling of the name is a different word in different languages of the same name, or differs from the index that the English page shows.'),
    (r'^F2 |^F2c', 'The origin of the name (Arabic, Persian, Turkish, Hebrew and so on) differs from the English page, or is stated where English states none.'),
    (r'^F14|^F7 |^F12 FACT number', 'The number of letters stated does not match the letters shown. On Arabic pages the count includes vowel marks (for example 13 for an 8-letter name).'),
    (r'^F6 |^F1 |^F9 ', 'Arabic root, gender or Quran reference differs from the English page.'),
    (r'^Z1 ', 'The Urdu and Arabic home pages say the site is "without advertising", and the same pages load the ad code.'),
    (r'^U8 |^U1a|^U6 |^U7 ', 'Half-translated text: English words inside Urdu or Arabic sentences, element and letter names left as "Earth", "Fire", "Air", "Dhal", dates as "c.", "b.", "CE", "AH", roots in Latin letters.'),
    (r'^S1 ', 'Famous bearers named in Latin letters on Urdu and Arabic pages.'),
    (r'^S3a', 'A name or word that mixes Arabic and Urdu letter forms inside one word (for example Arabic ه with Urdu ی). It can display wrongly and does not match a search typed on an Urdu or Arabic keyboard.'),
    (r'^L3 |^C13|^C14', 'Every translated page links to English-only pages under translated labels (the 28 letter pages, About, Contact, Privacy, Terms), and Arabic and Hindi pages send the reader to the English page for the full reading.'),
    (r'^C4 |^C5 |^C6 |^C7 |^C9 ', 'Content gap with English: fewer than half the words, fewer questions, no bearers, no pronunciation, no verse.'),
]
FIX = [
    (r'^U2 ', 'translate the fixed labels (aria-label "Breadcrumb", "Summary") from a label table'),
    (r'^L5 |^L6 |^L7 |^P7 ', 'point the second breadcrumb step at the names list and use one wording on the page and in the data'),
    (r'^P6 |^P8 |^P12|^P11|^P10', 'write inLanguage, Article and one modified date into the page data from values already on the page'),
    (r'^X1 |^X2 ', 'close the unclosed <article>, remove the stray closing tag'),
    (r'^X6 ', 'renumber the section labels 1..n in page order'),
    (r'^S4a|^S4b', 'use one digit family per page (decide first: Western, or the language\'s own)'),
    (r'^S5|^S6 ', 'replace Latin comma, semicolon and question mark after Arabic-script text with ، ؛ ؟ and remove the space before a comma'),
    (r'^T7 |^T6 |^P4 |^T5 ', 'copy title and description into the missing social tags'),
    (r'^C3 |^H\d', 'rebuild the hreflang set and the "other languages" line from the pages that exist'),
    (r'^F14|^F11', 'recount letters from the letter cards on the same page; recompute the reduced number from the total'),
    (r'^P13|^Z2 |^Q3 |^S9 |^L2 ', 'single pages: sitemap entry, stated count, one FAQ answer, one stray control character, home link'),
]
SEVERITY = [r'^F(1|2|3|4|5|6|7|8|9|10|11|12|13) ', r'^L1 |^H4 |^P5 |^X0|^P15|^P7 .*not exist', r'^U1 |^S1 |^S3 |^U4 ', r'^C', r'.']


def klass(k):
    for pat, c in CLASS:
        if re.search(pat, k):
            return c
    return '?'


def write(site, R, EN, idx, pages):
    os.makedirs(OUT_DIR, exist_ok=True)
    siteM = R['_site']['m']
    out = {'ref': site.ref or 'working tree', 'commit': site.sha, 'pages': {l: len(pages[l]) for l in LANGS}, 'classes': {'A': 'safe mechanical fix by script', 'A*': 'mechanical fix, but the word list must be approved first (spelling of words changes)',
           'B': 'needs translation written and reviewed', 'C': 'needs a native reader or the source checked', 'D': "needs Usman's decision"},
           'site': siteM, 'site_findings': R['_site']['f'], 'page': {}}
    code = {}
    used = collections.Counter()
    for k in sorted({k for p, r in R.items() for k in r['f']}):
        if k in code:
            continue
        c0 = k.split(' ')[0]
        used[c0] += 1
        code[k] = c0 if used[c0] == 1 else f'{c0}.{used[c0]}'
    out['checks'] = {c: {'title': k, 'class': klass(k)} for k, c in code.items()}
    out['site_findings'] = {code[k]: v for k, v in R['_site']['f'].items()}
    table = collections.defaultdict(lambda: collections.Counter())
    hits = collections.defaultdict(lambda: collections.Counter())
    examples = collections.defaultdict(lambda: collections.defaultdict(list))
    for p, r in R.items():
        if p == '_site':
            continue
        m = {k: v for k, v in r['m'].items() if k not in ('latin', 'labels', 'paras', 'en_only', 'brand', 'bytes')}
        if 'facts' in m:
            m['facts'] = {k: v for k, v in m['facts'].items() if k not in ('meaning', 'quran_answer')}
        out['page'][p] = {'m': m, 'f': {code[k]: [e[:170] for e in v if e][:2] + ([f'... {len(v)} in all'] if len(v) > 2 else []) for k, v in r['f'].items()}}
        for k, v in r['f'].items():
            table[k][r['lang']] += 1
            hits[k][r['lang']] += len(v)
            for e in v:
                if e and len(examples[k][r['lang']]) < 400:
                    examples[k][r['lang']].append((p, e))
    out['summary'] = {code[k]: {'title': k, 'class': klass(k), 'pages': dict(table[k]), 'occurrences': dict(hits[k])} for k in sorted(table)}
    json.dump(out, open(os.path.join(OUT_DIR, 'audit.json'), 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'), default=list)

    # Latin string tables
    lat = {l: collections.defaultdict(collections.Counter) for l in LANGS}
    for p, r in R.items():
        if p == '_site':
            continue
        for k, n in r['m'].get('latin', {}).items():
            b, ph = k.split('|', 1)
            lat[r['lang']][b][ph] += 1

    L = []
    w = L.append
    npages = sum(len(pages[l]) for l in LANGS)
    w('# Language audit: Urdu, Arabic, Hindi and Turkish pages')
    w('')
    w(f'Built by `redesign/lang_audit.py` from production (`{site.ref or "working tree"}`, commit `{site.sha}`). {npages} pages read: '
      + ', '.join(f'{LANGNAME[l]} {len(pages[l])}' for l in LANGS) + f'. English name pages compared against: {siteM["english_names"]}.')
    w('')
    w('Nothing on the site was changed. Every number below is a count of pages on which the check fails. The full list per page is in `redesign/lang/audit.json`.')
    w('')
    w('**Classes.** A = a script can fix it safely on every page. A* = a script can fix it, but the list of words it changes must be approved first. '
      'B = text has to be written or translated, then reviewed. C = a native reader or the source has to decide. D = Usman has to decide.')
    w('')

    def row(k):
        return f'| {k} | {klass(k)} | ' + ' | '.join(str(table[k][l] or '') for l in LANGS) + f' | {sum(table[k].values())} |'

    groups = [('Facts that disagree between languages (most serious)', r'^F'), ('Claims on the page that are not true of the site', r'^Z'), ('Language plumbing: lang, hreflang, canonical, social and search data', r'^[PHT]\d'),
              ('Untranslated interface text', r'^U'), ('Script and typography', r'^S'), ('Coverage and content parity with English', r'^C'),
              ('Links', r'^L'), ('FAQ on the page against FAQ in the search data', r'^Q'), ('Page structure', r'^X')]
    w('## Headline: pages affected, by class')
    w('')
    w('| Class | ' + ' | '.join(LANGNAME[l] for l in LANGS) + ' | Defect types |')
    w('|---|---|---|---|---|---|')
    for c in ('A', 'A*', 'B', 'C', 'D'):
        ks = [k for k in table if klass(k) == c]
        per = []
        for l in LANGS:
            s = {p for p, r in R.items() if p != '_site' and r['lang'] == l and any(klass(k) == c for k in r['f'])}
            per.append(str(len(s)))
        w(f'| {c} | ' + ' | '.join(per) + f' | {len(ks)} |')
    clean = {l: sum(1 for p in pages[l] if not R[p]['f']) for l in LANGS}
    w('| Pages with no finding at all | ' + ' | '.join(str(clean[l]) for l in LANGS) + ' | |')
    w('')
    w('## Coverage')
    w('')
    w('| | ' + ' | '.join(LANGNAME[l] for l in LANGS) + ' |')
    w('|---|---|---|---|---|')
    w('| Name pages | ' + ' | '.join(str(sum(1 for p in pages[l] if R[p]['m'].get('kind') == 'name')) for l in LANGS) + ' |')
    w(f'| English names with no page in this language (of {len(idx)}) | ' + ' | '.join(str(len(siteM['missing'][l])) for l in LANGS) + ' |')
    w('| Home page exists | ' + ' | '.join('yes' if f'{l}/index.html' in site.files else '**no**' for l in LANGS) + ' |')
    for sec in ('letters', 'about', 'contact', 'privacy', 'terms', 'blog', 'ilm-ul-huroof', 'reader'):
        w(f'| /{sec}/ translated | ' + ' | '.join('yes' if any(f.startswith(f'{l}/{sec}/') for f in site.files) else 'no' for l in LANGS) + ' |')
    avg = lambda l, key: (lambda v: round(sum(v) / len(v), 1) if v else 0)([R[p]['m'].get(key) or 0 for p in pages[l] if R[p]['m'].get('kind') == 'name'])
    w('| Average words per name page | ' + ' | '.join(str(avg(l, 'words')) for l in LANGS) + ' |')
    w('| Average words on the English page of the same names | ' + ' | '.join(str(avg(l, 'en_words')) for l in LANGS) + ' |')
    w('| Average FAQ questions (English same names) | ' + ' | '.join(f"{avg(l, 'faq_visible')} ({avg(l, 'en_faq')})" for l in LANGS) + ' |')
    w('| Share of running text that is wording shared across many pages | ' + ' | '.join(f"{round(siteM['boiler'][l]['share'] * 100)}%" for l in LANGS) + ' |')
    w('')
    w('## The most serious findings')
    w('')
    for pat, why in SERIOUS:
        ks = [k for k in table if re.search(pat, k)]
        if not ks:
            continue
        per = {l: len({p for p, r in R.items() if p != '_site' and r['lang'] == l and any(k in r['f'] for k in ks)}) for l in LANGS}
        w(f'- **{sum(per.values())} pages** (' + ', '.join(f'{LANGNAME[l]} {n}' for l, n in per.items() if n) + f'). {why}')
        ex = [(p, e) for k in ks for l in LANGS for (p, e) in examples[k][l][:1]][:2]
        for p, e in ex:
            w(f'  - `{p}`: {e[:260]}')
    w('')
    w('## What a script can fix on every page at once (class A)')
    w('')
    w('| Fix | Pages | ' + ' | '.join(LANGNAME[l] for l in LANGS) + ' |')
    w('|---|---|---|---|---|---|')
    for pat, what in FIX:
        ks = [k for k in table if re.search(pat, k) and klass(k) == 'A']
        if not ks:
            continue
        per = {l: len({p for p, r in R.items() if p != '_site' and r['lang'] == l and any(k in r['f'] for k in ks)}) for l in LANGS}
        w(f'| {what} ({", ".join(sorted({k.split(" ")[0] for k in ks}))}) | {sum(per.values())} | ' + ' | '.join(str(per[l] or '') for l in LANGS) + ' |')
    w('')
    w('None of these touches the spelling of a name. Fixes that do (S3a, class A*) need the word list approved first.')
    w('')
    w('## What this audit cannot judge')
    w('')
    w('- Whether the Urdu, Arabic, Hindi or Turkish reads naturally, and whether a meaning is translated correctly. No check here reads meaning.')
    w('- Which side is right when two languages disagree on a fact (origin, spelling, root, verse). The audit proves the disagreement, not the answer; the source decides.')
    w('- Whether a Latin-letter word inside a sentence is a leftover or a deliberate gloss (U1b), and whether a word in the other script\'s letter forms is a quotation (S3b).')
    w('- Whether Hindi and Turkish transliterations of names (Devanagari and Turkish spellings) are the forms readers use.')
    w('- Religious wording: honorifics, how verses and hadith are cited, and whether a claim is stated more strongly than the source.')
    w('')
    for title, pat in groups:
        ks = sorted((k for k in table if re.search(pat, k)), key=lambda k: -sum(table[k].values()))
        if not ks:
            continue
        w(f'## {title}')
        w('')
        w('| Check | Class | ' + ' | '.join(LANGNAME[l] for l in LANGS) + ' | Pages |')
        w('|---|---|---|---|---|---|---|')
        for k in ks:
            w(row(k))
        w('')
        for k in ks:
            w(f'**{k}** (class {klass(k)})')
            w('')
            shown = 0
            seen_txt = set()
            # spread examples over languages
            pool = []
            for i in range(400):
                for l in LANGS:
                    if i < len(examples[k][l]):
                        pool.append(examples[k][l][i])
            for p, e in pool:
                key = re.sub(r'[\d' + ARIN + EXIN + ']+', '#', e)[:60]
                if key in seen_txt:
                    continue
                seen_txt.add(key)
                w(f'- `{p}`: {e}' if e else f'- `{p}`')
                shown += 1
                if shown >= 5:
                    break
            if not shown:
                for l in LANGS:
                    ps = [p for p, r in R.items() if p != '_site' and r['lang'] == l and k in r['f']][:2]
                    for p in ps:
                        w(f'- `{p}`')
            w('')
    w('## Latin-letter strings found in Urdu, Arabic and Hindi pages')
    w('')
    w('Number of pages on which each string appears. "Leftover" strings are the untranslated ones; names of the page itself, the brand, web addresses and the language switch are counted as legitimate.')
    w('')
    for l in ('ur', 'ar', 'hi'):
        w(f'### {LANGNAME[l]}')
        w('')
        w('| Kind | Distinct strings | Pages x strings | Most frequent |')
        w('|---|---|---|---|')
        for b, nm in (('ui', 'LEFTOVER interface or English words'), ('person', 'LEFTOVER person or place names'), ('pronunciation', 'Pronunciation in Latin letters (decision)'),
                      ('alphabet', 'A to Z index letters (decision)'), ('abbr', 'LEFTOVER English abbreviations'), ('root-latin', 'LEFTOVER roots in Latin letters'),
                      ('other-name', 'LEFTOVER another name in Latin letters'), ('own-name', 'legitimate: the name itself, romanised'),
                      ('brand', 'legitimate: brand'), ('switcher', 'legitimate: language switch'), ('url', 'legitimate: address'), ('ipa', 'legitimate: phonetic notation')):
            c = lat[l][b]
            if c:
                w(f'| {nm} | {len(c)} | {sum(c.values())} | ' + '; '.join(f'{ph} ({n})' for ph, n in c.most_common(12)).replace('|', '/') + ' |')
        w('')
    w('### Turkish: English words found')
    w('')
    c = lat['tr']['ui']
    w('; '.join(f'{ph} ({n})' for ph, n in c.most_common(30)) or 'none')
    w('')
    w('## Site name: spellings in use')
    w('')
    for l in LANGS:
        w(f'- {LANGNAME[l]}: ' + '; '.join(f'{b} on {n} pages' for b, n in siteM['brand'][l]))
    w('')
    w('## Letter forms')
    w('')
    for l, table_ in (('ur', AR_FORMS_IN_UR), ('ar', UR_FORMS_IN_AR)):
        for kind_, nm in (('mixed', 'inside a word that also has ' + ('Urdu' if l == 'ur' else 'Arabic') + '-only letters (certain error)'), ('whole', 'in a word written wholly in the other form (may be a cited word)')):
            c = collections.Counter()
            pg_c = collections.Counter()
            for p in pages[l]:
                for k, n in R[p]['m'].get('forms', {}).items():
                    if k.startswith(kind_):
                        c[k[-1]] += n
                        pg_c[k[-1]] += 1
            if c:
                w(f'- {LANGNAME[l]} pages, {nm}: ' + '; '.join(f'{table_[ch]}: {c[ch]} words on {pg_c[ch]} pages' for ch in table_ if c[ch]))
    w('')
    w('Counted outside the name\'s own Arabic spelling, the root, the letter cards, quoted Arabic in « », and fully vowelled Arabic words.')
    w('')
    w('## Wording shared across many pages')
    w('')
    for l in LANGS:
        b = siteM['boiler'][l]
        w(f'**{LANGNAME[l]}**: {round(b["share"] * 100)}% of paragraph words sit in paragraphs that are identical on {b["threshold_pages"]} or more pages once the name and numbers are blanked. Most repeated:')
        w('')
        for k, n in b['top'][:4]:
            w(f'- {n} pages: {k[:170]}')
        w('')
    w('## English text added by scripts after the page loads')
    w('')
    w('A static read of the HTML cannot see this text. These script files are loaded by the translated pages and contain English strings that they write into the page:')
    w('')
    for s, d in siteM['js_english'].items():
        w(f'- `{s}` (reads the page language: {"yes" if d["reads_page_language"] else "no"}): ' + '; '.join(d['english_strings'][:10]))
    rt = os.path.join(OUT_DIR, 'runtime.json')
    if os.path.exists(rt):
        w('')
        w('Measured in a real browser (`redesign/lang/runtime.json`): strings present after scripts ran that are not in the HTML file.')
        w('')
        for pth, strs in json.load(open(rt, encoding='utf8')).items():
            w(f'- `{pth}`: ' + '; '.join(strs[:25]))
    w('')
    w('## Site-level')
    w('')
    for k, v in R['_site']['f'].items():
        w(f'- {k}: {len(v)} ({", ".join(v[:5])})')
    w(f'- Sitemaps read: {", ".join(siteM["sitemaps"])}')
    w('')
    open(os.path.join(OUT_DIR, 'audit.md'), 'w', encoding='utf8').write('\n'.join(L) + '\n')
    print('pages', {l: len(pages[l]) for l in LANGS}, '-> redesign/lang/audit.json, redesign/lang/audit.md')
    for k in sorted(table, key=lambda k: -sum(table[k].values()))[:60]:
        print(f'  {klass(k):2} {sum(table[k].values()):5}  {dict(table[k])}  {k}')


if __name__ == '__main__':
    main()
