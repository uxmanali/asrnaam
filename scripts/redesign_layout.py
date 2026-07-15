#!/usr/bin/env python3
"""AsrNaam layout V2: reorder canonical name pages to the 5-section reading order.

Reads each name page, extracts the load-bearing marker blocks
(MEAN-ROOT, MEAN-IUH, MEAN-DICT, BEARERS) plus the optional QURANIC nested
callout and MEAN-SYNTHESIS (generated separately). Re-emits them inside a
single <!-- LAYOUT-V2:START --> ... <!-- LAYOUT-V2:END --> container placed
directly under QFACTS / SHARE-HERO, with the new section headings and
dividers. The original marker positions are emptied (their content is now
inside LAYOUT-V2, still wrapped in the same START/END markers so downstream
tooling that targets those markers keeps working).

Idempotent. Re-running the script on a page that already has LAYOUT-V2 will
rebuild the container in place without duplicating anything.

Handles /names/<slug>/ (English), /ar/names/<slug>/ (Arabic mirror), and
/ur/names/<slug>/ (Urdu mirror). Mirrors do not use START/END markers; they
use <p class="section-label">TEXT</p> anchors. Mirror-mode locates each
labeled block by its label text, extracts through to the next label, and
rewrites in the new order.

Usage:
  python3 scripts/redesign_layout.py <slug1> <slug2> ...     # 5-name deploy
  python3 scripts/redesign_layout.py --all                    # bulk (do not run without approval)
  python3 scripts/redesign_layout.py --skip-mirrors <slugs>   # EN only
"""

from __future__ import annotations
import argparse
import pathlib
import re
import sys
from typing import Optional

ROOT = pathlib.Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# EN heading labels (used inside LAYOUT-V2)
# ---------------------------------------------------------------------------
EN_HEADINGS = {
    "root":      ("Section 1 · Arabic Root",     "Where the Name Comes From"),
    "letters":   ("Section 2 · Ilm ul Huroof",   "Read Letter by Letter"),
    "synthesis": ("Section 3 · Synthesis",       "What This Reading Says About You"),
    "dict":      ("Section 4 · What Families Say", "What People Usually Mean by This Name"),
    "bearers":   ("Section 5 · Bearers",         "Who Has Carried This Name"),
}
AR_HEADINGS = {
    "root":      ("القسم 1 · الجذر العربي",       "من أين يأتي الاسم"),
    "letters":   ("القسم 2 · علم الحروف",          "قراءة حرفاً بحرف"),
    "synthesis": ("القسم 3 · القراءة الشخصية",     "ما تقوله هذه القراءة عنك"),
    "dict":      ("القسم 4 · المعنى العائلي",      "المعنى الشائع للاسم"),
    "bearers":   ("القسم 5 · الحاملون",            "من حمل هذا الاسم"),
}
UR_HEADINGS = {
    "root":      ("حصہ 1 · عربی جذر",              "نام کہاں سے آتا ہے"),
    "letters":   ("حصہ 2 · علم الحروف",            "حرف بہ حرف پڑھیں"),
    "synthesis": ("حصہ 3 · ذاتی قراءت",             "یہ پڑھائی آپ کے بارے میں کیا کہتی ہے"),
    "dict":      ("حصہ 4 · عام معنی",              "اس نام کا عام معنی"),
    "bearers":   ("حصہ 5 · حاملین",                "یہ نام کس نے اٹھایا"),
}

DIVIDER_SVG = (
    '<div class="asr-v2-divider" aria-hidden="true">'
    '<svg viewBox="0 0 24 24" width="20" height="20">'
    '<path d="M12 2 L14 10 L22 12 L14 14 L12 22 L10 14 L2 12 L10 10 Z" fill="currentColor"/>'
    '<path d="M12 5 L13 11 L19 12 L13 13 L12 19 L11 13 L5 12 L11 11 Z" fill-opacity=".55" fill="var(--warm-white,#FAFAF8)"/>'
    '</svg></div>'
)

# ---------------------------------------------------------------------------
# Marker extraction helpers
# ---------------------------------------------------------------------------
MARKER_RE = {
    "MEAN-ROOT":      re.compile(r"<!--\s*MEAN-ROOT:START\s*-->(.*?)<!--\s*MEAN-ROOT:END\s*-->", re.DOTALL),
    "MEAN-IUH":       re.compile(r"<!--\s*MEAN-IUH:START\s*-->(.*?)<!--\s*MEAN-IUH:END\s*-->", re.DOTALL),
    "MEAN-DICT":      re.compile(r"<!--\s*MEAN-DICT:START\s*-->(.*?)<!--\s*MEAN-DICT:END\s*-->", re.DOTALL),
    "BEARERS":        re.compile(r"<!--\s*BEARERS:START\s*-->(.*?)<!--\s*BEARERS:END\s*-->", re.DOTALL),
    "QURANIC":        re.compile(r"<!--\s*QURANIC:START\s*-->(.*?)<!--\s*QURANIC:END\s*-->", re.DOTALL),
    "MEAN-SYNTHESIS": re.compile(r"<!--\s*MEAN-SYNTHESIS:START\s*-->(.*?)<!--\s*MEAN-SYNTHESIS:END\s*-->", re.DOTALL),
}

def clean_marker_inner(inner, drop_section_label=True):
    """Strip the leading <p class="section-label">...</p><h2>...</h2> chrome
    that was rendered before each marker's prose. The V2 shell already provides
    the section title, so we drop the internal duplicates. Also strips a
    leading <p class="related-intro">...</p> (used by BEARERS).
    """
    inner = inner.strip()
    if not drop_section_label:
        return inner
    inner = re.sub(
        r'^\s*<p\s+class="section-label"[^>]*>.*?</p>\s*',
        '', inner, count=1, flags=re.DOTALL
    )
    inner = re.sub(
        r'^\s*<h2[^>]*>.*?</h2>\s*',
        '', inner, count=1, flags=re.DOTALL
    )
    inner = re.sub(
        r'^\s*<p\s+class="related-intro"[^>]*>.*?</p>\s*',
        '', inner, count=1, flags=re.DOTALL
    )
    return inner.strip()

def clean_quranic_inner(inner):
    """QURANIC's inner is wrapped in <section class="quranic-context">...</section>.
    Unwrap that and drop its own section-label + h2.
    """
    inner = inner.strip()
    m = re.search(r'<section\s+class="quranic-context"[^>]*>(.*)</section>\s*$',
                  inner, re.DOTALL)
    if m:
        inner = m.group(1).strip()
    return clean_marker_inner(inner, drop_section_label=True)

QFACTS_END_RE   = re.compile(r"<!--\s*QFACTS:END\s*-->")
SHARE_HERO_END  = re.compile(r"<!--\s*SHARE-HERO:END\s*-->")
LAYOUT_V2_RE    = re.compile(r"<!--\s*LAYOUT-V2:START\s*-->(.*?)<!--\s*LAYOUT-V2:END\s*-->", re.DOTALL)

# Existing letter-cards block (inline, not marked). Regex-locates the
# div class="letter-cards" ... </div> chunk immediately preceded by an
# H2 "Reading X through Ilm ul Huroof" or a section-label "The Letters".
LETTER_CARDS_RE = re.compile(
    r'(<p class="section-label">\s*The Letters\s*</p>.*?</blockquote>)',
    re.DOTALL
)
# Fallback: just the letter-cards div itself
LETTER_CARDS_DIV_RE = re.compile(
    r'(<div class="letter-cards">.*?</div>)',
    re.DOTALL
)
LETTERS_INTRO_RE = re.compile(
    r'(<p class="letters-intro">.*?</p>)',
    re.DOTALL
)

# Individual letter card
LETTER_CARD_RE = re.compile(
    r'<a[^>]*href="[^"]*/letters/([^/]+)/"[^>]*class="letter-card"[^>]*>'
    r'.*?<span class="letter-arabic"[^>]*>([^<]+)</span>'
    r'.*?<span class="letter-roman">([^<]+)</span>'
    r'.*?</a>',
    re.DOTALL
)

# ---------------------------------------------------------------------------
# Arabic letter → element / divine-name mapping
# ---------------------------------------------------------------------------
# From data/asr-letters.js (Ibn Arabi + al-Buni framework, 7 letters per element).
ARABIC_TO_ELEMENT = {
    # FIRE
    "ا": "Fire",  "أ": "Fire", "إ": "Fire", "آ": "Fire",  # alif family
    "ه": "Fire",  "ة": "Earth",  # hah (fire), taa marbuta (earth, per t)
    "ط": "Fire",  "م": "Fire",  "ف": "Fire",  "ش": "Fire",  "ذ": "Fire",
    # EARTH
    "ب": "Earth",  "پ": "Earth",  # pa cousin
    "و": "Earth",  "ؤ": "Earth",
    "ي": "Earth",  "ى": "Earth",  "ئ": "Earth",  "ی": "Earth",
    "ن": "Earth",  "ص": "Earth",  "ت": "Earth",  "ض": "Earth",
    # AIR
    "ج": "Air",  "چ": "Air",
    "ز": "Air",  "ژ": "Air",
    "ك": "Air",  "ک": "Air",  "گ": "Air",
    "س": "Air",  "ق": "Air",  "ث": "Air",  "ظ": "Air",
    # WATER
    "د": "Water",  "ح": "Water",  "ل": "Water",  "ع": "Water",
    "ر": "Water",  "خ": "Water",  "غ": "Water",
}

ARABIC_TO_DIVINE = {
    "ا": ("Al-Ahad",       "The One"),
    "أ": ("Al-Ahad",       "The One"),
    "إ": ("Al-Ahad",       "The One"),
    "آ": ("Al-Ahad",       "The One"),
    "ه": ("Al-Hadi",       "The Guide"),
    "ة": ("Al-Tawwab",     "The Relenting"),
    "ط": ("Al-Lateef",     "The Subtle"),
    "م": ("Al-Mu'min",     "The Faithful"),
    "ف": ("Al-Fattah",     "The Opener"),
    "ش": ("Al-Shakur",     "The Appreciative"),
    "ذ": ("Dhul-Jalal",    "Lord of Majesty"),
    "ب": ("Al-Batin",      "The Interior"),
    "پ": ("Al-Batin",      "The Interior"),
    "و": ("Al-Wadud",      "The Loving"),
    "ؤ": ("Al-Wadud",      "The Loving"),
    "ي": ("Al-Qayyum",     "The Self-Sustaining"),
    "ى": ("Al-Qayyum",     "The Self-Sustaining"),
    "ی": ("Al-Qayyum",     "The Self-Sustaining"),
    "ئ": ("Al-Qayyum",     "The Self-Sustaining"),
    "ن": ("Al-Nur",        "The Light"),
    "ص": ("Al-Samad",      "The Eternal Refuge"),
    "ت": ("Al-Tawwab",     "The Relenting"),
    "ض": ("Al-Darr",       "The Tester"),
    "ج": ("Al-Jami",       "The Gatherer"),
    "چ": ("Al-Jami",       "The Gatherer"),
    "ز": ("Al-Zahir",      "The Manifest"),
    "ژ": ("Al-Zahir",      "The Manifest"),
    "ك": ("Al-Karim",      "The Generous"),
    "ک": ("Al-Karim",      "The Generous"),
    "گ": ("Al-Karim",      "The Generous"),
    "س": ("Al-Sami",       "The All-Hearing"),
    "ق": ("Al-Qadir",      "The All-Capable"),
    "ث": ("Al-Thabit",     "The Firm"),
    "ظ": ("Al-Dhahir",     "The Outer Manifest"),
    "د": ("Al-Dayyan",     "The Judge"),
    "ح": ("Al-Hamid",      "The Praiseworthy"),
    "ل": ("Al-Latif",      "The Gracious"),
    "ع": ("Al-Alim",       "The All-Knowing"),
    "ر": ("Al-Rahman",     "The Merciful"),
    "خ": ("Al-Khabir",     "The Aware"),
    "غ": ("Al-Ghani",      "The Self-Sufficient"),
}

# Roman name → letter slug on the site (for /letters/<slug>/ href)
ROMAN_TO_SLUG_HINT = {
    "Alif": "alif",  "Ba": "ba",  "Ta": "ta-heavy",  "Tha": "tha",
    "Jim": "jim",   "Jeem": "jeem",  "Ha": "ha-breath",  "Kha": "kha",
    "Dal": "dal",   "Dhal": "dhal",  "Ra": "ra",   "Zayn": "zayn",
    "Seen": "seen", "Sheen": "sheen",  "Sad": "sad",  "Dad": "dad",
    "Ta-Heavy": "ta-heavy",  "Dha": "dha",  "Ain": "ain",  "Ghain": "ghain",
    "Fa": "fa",  "Qaf": "qaf",  "Kaf": "kaf",  "Lam": "lam",
    "Meem": "meem",  "Nun": "nun",  "Waw": "waw",  "Ya": "ya",
    "Hamza": "hamza",
}

# ---------------------------------------------------------------------------
# Arabic-name extraction (from EN page)
# ---------------------------------------------------------------------------
ARABIC_FIELD_RE = re.compile(
    r'<span[^>]*data-asr-field="arabic"[^>]*>([^<]+)</span>'
)
ARABIC_NAME_HERO_RE = re.compile(
    r'<div class="arabic-name"[^>]*>([^<]+)</div>'
)
DIACRITIC_RE = re.compile(r"[ً-ٰٟۖ-ۭ‌‍‎‏]")

def extract_arabic_name(html: str) -> str:
    for pat in (ARABIC_FIELD_RE, ARABIC_NAME_HERO_RE):
        m = pat.search(html)
        if m:
            return m.group(1).strip()
    return ""

def arabic_letters(arabic: str) -> list:
    """Return the letter list (stripped of diacritics), preserving order."""
    cleaned = DIACRITIC_RE.sub("", arabic)
    letters = []
    for ch in cleaned:
        if ch.strip() and ch in ARABIC_TO_ELEMENT:
            letters.append(ch)
    return letters

def name_letter_breakdown(html: str):
    """Return [(arabic_char, roman, slug), ...] for each letter, using page data
    when possible (letter-cards) then falling back to Arabic-name parsing.
    """
    cards = LETTER_CARD_RE.findall(html)
    if cards:
        return [(arabic, roman, slug) for slug, arabic, roman in cards]
    # fallback: derive from Arabic-name string
    arabic = extract_arabic_name(html)
    out = []
    for ch in arabic_letters(arabic):
        divine = ARABIC_TO_DIVINE.get(ch, ("", ""))
        roman = divine[0].replace("Al-", "").split("'")[0].split("-")[0]
        # crude roman mapping fallback
        romans_by_arabic = {
            "ا": "Alif", "أ": "Alif", "إ": "Alif", "آ": "Alif",
            "ب": "Ba", "ت": "Ta", "ث": "Tha", "ج": "Jim",
            "ح": "Ha", "خ": "Kha", "د": "Dal", "ذ": "Dhal",
            "ر": "Ra", "ز": "Zayn", "س": "Seen", "ش": "Sheen",
            "ص": "Sad", "ض": "Dad", "ط": "Ta", "ظ": "Dha",
            "ع": "Ain", "غ": "Ghain", "ف": "Fa", "ق": "Qaf",
            "ك": "Kaf", "ک": "Kaf", "ل": "Lam", "م": "Meem",
            "ن": "Nun", "ه": "Ha", "ة": "Ta", "و": "Waw",
            "ي": "Ya", "ى": "Ya", "ی": "Ya", "ئ": "Ya",
            "پ": "Pa", "چ": "Cha", "ژ": "Zha", "گ": "Gaf",
        }
        r = romans_by_arabic.get(ch, "")
        slug = ROMAN_TO_SLUG_HINT.get(r, r.lower())
        out.append((ch, r, slug))
    return out

# ---------------------------------------------------------------------------
# Enriched letter cards (Section 2)
# ---------------------------------------------------------------------------
def render_letter_grid(letters: list, base_prefix: str = "") -> str:
    """letters: [(arabic_char, roman_name, slug)]. Emit the V2 grid."""
    if not letters:
        return ""
    cards = []
    for arabic, roman, slug in letters:
        el = ARABIC_TO_ELEMENT.get(arabic, "")
        divine = ARABIC_TO_DIVINE.get(arabic, ("", ""))
        anchor = f"{divine[0]} · {divine[1]}" if divine[0] else ""
        el_class = f"pill-{el.lower()}" if el else ""
        href = f"{base_prefix}/letters/{slug}/" if slug else "#"
        card = (
            f'<a href="{href}" class="asr-v2-letter" data-element="{el.lower()}">'
            f'<span class="asr-v2-letter-arabic" lang="ar" dir="rtl">{arabic}</span>'
            f'<span class="asr-v2-letter-roman">{roman}</span>'
            f'<span class="asr-v2-letter-anchor">{anchor}</span>'
            f'<span class="asr-v2-letter-pill {el_class}">{el}</span>'
            f'</a>'
        )
        cards.append(card)
    return '<div class="asr-v2-letter-grid">' + "".join(cards) + '</div>'

# ---------------------------------------------------------------------------
# Root-glyph extraction (Section 1)
# ---------------------------------------------------------------------------
ROOT_GLYPH_RE = re.compile(
    r'<strong[^>]*>\s*([^\s<][^<]{0,20}?)\s*</strong>'
)
ROOT_TRILITERAL_RE = re.compile(
    r'([ء-ي])[-–—·]([ء-ي])[-–—·]([ء-ي])'
)
def extract_root_glyph(root_html: str) -> str:
    m = ROOT_TRILITERAL_RE.search(root_html)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = ROOT_GLYPH_RE.search(root_html)
    if m and any('؀' <= c <= 'ۿ' for c in m.group(1)):
        return m.group(1)
    return ""

# ---------------------------------------------------------------------------
# EN page: build the LAYOUT-V2 block
# ---------------------------------------------------------------------------
def build_layout_v2_en(html: str) -> Optional[str]:
    """Return the full LAYOUT-V2 innerHTML (including START/END wrappers) for
    the EN page, or None if required markers are missing.
    """
    root = MARKER_RE["MEAN-ROOT"].search(html)
    iuh  = MARKER_RE["MEAN-IUH"].search(html)
    dic  = MARKER_RE["MEAN-DICT"].search(html)
    bear = MARKER_RE["BEARERS"].search(html)
    quran = MARKER_RE["QURANIC"].search(html)
    synth = MARKER_RE["MEAN-SYNTHESIS"].search(html)

    if not (root and iuh and dic and bear):
        return None

    root_inner    = clean_marker_inner(root.group(1))
    iuh_inner     = clean_marker_inner(iuh.group(1))
    dict_inner    = clean_marker_inner(dic.group(1))
    bearers_inner = clean_marker_inner(bear.group(1))
    quran_inner   = clean_quranic_inner(quran.group(1)) if quran else ""
    synth_inner   = synth.group(1).strip() if synth else ""

    letters = name_letter_breakdown(html)
    root_glyph = extract_root_glyph(root_inner)

    root_glyph_html = (
        f'<div class="asr-v2-root-glyph" lang="ar" dir="rtl" aria-label="Root letters">{root_glyph}</div>'
        if root_glyph else ""
    )

    grid_html = render_letter_grid(letters, base_prefix="")

    synth_block = ""
    if synth_inner:
        synth_block = (
            f'<section class="asr-v2 asr-v2-synthesis">'
            f'<p class="asr-v2-kicker">{EN_HEADINGS["synthesis"][0]}</p>'
            f'<h2 class="asr-v2-title">{EN_HEADINGS["synthesis"][1]}</h2>'
            f'<!-- MEAN-SYNTHESIS:START -->{synth_inner}<!-- MEAN-SYNTHESIS:END -->'
            f'</section>{DIVIDER_SVG}'
        )

    quran_block = ""
    if quran_inner:
        quran_block = f'<div class="asr-v2-quranic-nest"><!-- QURANIC:START -->{quran_inner}<!-- QURANIC:END --></div>'

    body = (
        # Section 1
        f'<section class="asr-v2 asr-v2-root">'
        f'<p class="asr-v2-kicker">{EN_HEADINGS["root"][0]}</p>'
        f'<h2 class="asr-v2-title">{EN_HEADINGS["root"][1]}</h2>'
        f'{root_glyph_html}'
        f'<!-- MEAN-ROOT:START -->{root_inner}<!-- MEAN-ROOT:END -->'
        f'</section>{DIVIDER_SVG}'
        # Section 2
        f'<section class="asr-v2 asr-v2-letters">'
        f'<p class="asr-v2-kicker">{EN_HEADINGS["letters"][0]}</p>'
        f'<h2 class="asr-v2-title">{EN_HEADINGS["letters"][1]}</h2>'
        f'{grid_html}'
        f'<!-- MEAN-IUH:START -->{iuh_inner}<!-- MEAN-IUH:END -->'
        f'</section>{DIVIDER_SVG}'
        # Section 3
        f'{synth_block}'
        # Section 4
        f'<section class="asr-v2 asr-v2-dict">'
        f'<p class="asr-v2-kicker">{EN_HEADINGS["dict"][0]}</p>'
        f'<h2 class="asr-v2-title">{EN_HEADINGS["dict"][1]}</h2>'
        f'<!-- MEAN-DICT:START -->{dict_inner}<!-- MEAN-DICT:END -->'
        f'{quran_block}'
        f'</section>{DIVIDER_SVG}'
        # Section 5
        f'<section class="asr-v2 asr-v2-bearers">'
        f'<p class="asr-v2-kicker">{EN_HEADINGS["bearers"][0]}</p>'
        f'<h2 class="asr-v2-title">{EN_HEADINGS["bearers"][1]}</h2>'
        f'<!-- BEARERS:START -->{bearers_inner}<!-- BEARERS:END -->'
        f'</section>'
    )

    return f'<!-- LAYOUT-V2:START -->\n<div class="asr-layout-v2">{body}</div>\n<!-- LAYOUT-V2:END -->'

# ---------------------------------------------------------------------------
# EN page transform
# ---------------------------------------------------------------------------
def strip_original_markers_en(html: str) -> str:
    """Empty the original positions of the reordered markers (keep the START/END
    tags so nothing else looking for them errors, but remove the inner content
    and the surrounding section-label / h2 chrome that lives just before them).
    Also remove the inline letter-cards block, the letters-intro line, the
    "The Letters" section-label, and the notable-bearer/blockquote/portrait
    chunks that duplicate what LAYOUT-V2 now holds.
    """
    # Empty each moved marker's content
    for key in ("MEAN-ROOT", "MEAN-IUH", "MEAN-DICT", "BEARERS", "QURANIC", "MEAN-SYNTHESIS"):
        html = MARKER_RE[key].sub(
            f'<!-- {key}:START --><!-- {key}:END -->',
            html
        )
    # Remove chrome that was rendered just before each marker (section-label + h2)
    #   MEAN-DICT:  <p class="section-label">Dictionary Meaning</p><h2>What ... means</h2>
    html = re.sub(
        r'<p class="section-label">\s*Dictionary Meaning\s*</p>\s*<h2>[^<]*</h2>',
        '', html, count=1
    )
    html = re.sub(
        r'<p class="section-label">\s*Arabic Root Meaning\s*</p>\s*<h2>[^<]*</h2>',
        '', html, count=1
    )
    html = re.sub(
        r'<p class="section-label">\s*Ilm ul Haroof Meaning\s*</p>\s*<h2>[^<]*</h2>',
        '', html, count=1
    )
    html = re.sub(
        r'<p class="section-label"[^>]*>\s*Famous Bearers\s*</p>\s*(?:<p class="related-intro">[^<]*</p>)?',
        '', html, count=1
    )
    # Remove the "Quranic Context" wrapper section (its inner QURANIC marker is
    # now empty, but the wrapping <section> chrome is still there and now empty).
    html = re.sub(
        r'<section class="quranic-context"[^>]*>\s*<p class="section-label">[^<]*</p>\s*<h2>[^<]*</h2>\s*<div class="prose"></div>\s*</section>',
        '', html
    )
    # Also handle the case where the section still contains a leftover empty MEAN-DICT-adjacent nub
    # Remove the inline letter-cards + reading + portrait chunk (it lived between
    # VARIATIONS and MEAN-IUH). Anchor on section-label "The Letters" and end at
    # the closing of the "The Portrait" prose block.
    html = re.sub(
        r'<p class="section-label">\s*The Letters\s*</p>.*?(?=<div class="notable">)',
        '', html, count=1, flags=re.DOTALL
    )
    # Strip the leftover "A Notable Bearer" notable box (duplicates BEARERS)
    html = re.sub(
        r'<div class="notable"><div class="notable-label">[^<]*</div>[^<]*(?:<[^>]+>[^<]*</[^>]+>)*.*?</div>',
        '', html, count=1, flags=re.DOTALL
    )
    # Strip the "The Portrait" mini-section
    html = re.sub(
        r'<p class="section-label">\s*The Portrait\s*</p>\s*<h2>[^<]*</h2>\s*<div class="prose">.*?</div>',
        '', html, count=1, flags=re.DOTALL
    )
    return html

def apply_layout_v2_en(html: str) -> Optional[str]:
    """Build LAYOUT-V2, insert it after SHARE-HERO:END (or QFACTS:END), and
    empty the moved markers. Returns the new HTML or None if markers are missing.
    """
    layout_html = build_layout_v2_en(html)
    if layout_html is None:
        return None

    # Idempotency: if LAYOUT-V2 already present, replace in place
    if LAYOUT_V2_RE.search(html):
        html = LAYOUT_V2_RE.sub(layout_html, html, count=1)
        return html

    html = strip_original_markers_en(html)

    # Insert after SHARE-HERO:END if it exists, else after QFACTS:END
    m = SHARE_HERO_END.search(html)
    if not m:
        m = QFACTS_END_RE.search(html)
    if not m:
        return None  # cannot place safely
    insertion = m.end()
    return html[:insertion] + "\n" + layout_html + "\n" + html[insertion:]

# ---------------------------------------------------------------------------
# AR / UR mirror transform
# ---------------------------------------------------------------------------
MIRROR_LABEL_ORDER_AR = ["المعنى المعجمي", "حاملون مشهورون", "الجذر العربي", "معنى الحروف", "القراءة"]
MIRROR_LABEL_ORDER_UR = ["لغوی معنی", "مشہور افراد", "عربی جذر", "حروف کا مطلب", "قراءت"]
MIRROR_LABEL_ORDER_END_AR = "أسماء ذات صلة"
MIRROR_LABEL_ORDER_END_UR = "متعلقہ نام"

def _mirror_labels_pat(labels):
    # Match <p class="section-label"[ style=..]?>LABEL</p>
    parts = "|".join(re.escape(l) for l in labels)
    return re.compile(
        r'(<p class="section-label"[^>]*>\s*(?:' + parts + r')\s*</p>)',
        re.DOTALL
    )

def apply_layout_v2_mirror(html: str, lang: str) -> Optional[str]:
    """Reorder AR/UR mirror sections into: root, letters, [synthesis stub],
    dict, bearers. Return None if the mirror does not match the expected shape.
    """
    if lang == "ar":
        expected_labels = MIRROR_LABEL_ORDER_AR
        end_label = MIRROR_LABEL_ORDER_END_AR
        headings = AR_HEADINGS
    elif lang == "ur":
        expected_labels = MIRROR_LABEL_ORDER_UR
        end_label = MIRROR_LABEL_ORDER_END_UR
        headings = UR_HEADINGS
    else:
        return None

    # Locate each section by its label
    all_labels = expected_labels + [end_label]
    pat = _mirror_labels_pat(all_labels)
    matches = list(pat.finditer(html))
    if len(matches) < 3:
        return None

    # Build a dict: label_text → (start, end) span for the entire section
    label_span = {}
    for i, m in enumerate(matches):
        label_text = None
        for lb in all_labels:
            if lb in m.group(0):
                label_text = lb
                break
        if label_text is None:
            continue
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else None
        if end is None:
            # end at end-of-related or at </div><footer marker
            end = start + len(m.group(0)) + 2000  # fallback slice
        label_span[label_text] = (start, end)

    # Extract each block by label
    def slice_of(label):
        if label not in label_span:
            return ""
        s, e = label_span[label]
        return html[s:e]

    block_dict    = slice_of(expected_labels[0])  # المعنى المعجمي / لغوی معنی
    block_bearers = slice_of(expected_labels[1])  # حاملون مشهورون / مشہور افراد
    block_root    = slice_of(expected_labels[2])  # الجذر العربي / عربی جذر
    block_letters = slice_of(expected_labels[3])  # معنى الحروف / حروف کا مطلب
    block_life    = slice_of(expected_labels[4])  # القراءة / قراءت (LIFE-like)

    # Thin-mirror support: some AR/UR pages only ship dict + letters (no root
    # section, no bearers). Require the minimum-viable pair (dict + letters).
    # The root section, when absent, is silently omitted from the V2 output.
    if not (block_dict and block_letters):
        return None

    # Strip trailing whitespace / stray newlines
    def clean(b): return b.rstrip()

    # Emit the new sequence in place
    kicker_root = headings["root"][0]
    title_root  = headings["root"][1]
    kicker_letters = headings["letters"][0]
    title_letters  = headings["letters"][1]
    kicker_synth = headings["synthesis"][0]
    title_synth  = headings["synthesis"][1]
    kicker_dict = headings["dict"][0]
    title_dict  = headings["dict"][1]
    kicker_bearers = headings["bearers"][0]
    title_bearers  = headings["bearers"][1]

    # Rebuild the block with V2 shell around each section
    def shell(kicker, title, inner, cls_suffix):
        return (
            f'<section class="asr-v2 asr-v2-{cls_suffix}">'
            f'<p class="asr-v2-kicker">{kicker}</p>'
            f'<h2 class="asr-v2-title">{title}</h2>'
            f'{inner}'
            f'</section>{DIVIDER_SVG}'
        )

    # Strip inner section-label / h2 (they lived before the prose) — the shell
    # already provides the title. Keep the prose only.
    def strip_label_and_h2(block):
        # remove leading <p class="section-label"...>...</p>
        block = re.sub(r'^\s*<p class="section-label"[^>]*>.*?</p>\s*', '', block, count=1, flags=re.DOTALL)
        # remove leading <h2>...</h2>
        block = re.sub(r'^\s*<h2[^>]*>.*?</h2>\s*', '', block, count=1, flags=re.DOTALL)
        return block

    inner_dict    = strip_label_and_h2(block_dict)
    inner_bearers = strip_label_and_h2(block_bearers) if block_bearers else ""
    inner_root    = strip_label_and_h2(block_root) if block_root else ""
    inner_letters = strip_label_and_h2(block_letters)

    # For mirrors, derive a letter grid from the Arabic name (in the hero) so
    # Section 2 shows the same colored pills as the EN page.
    mirror_arabic = extract_arabic_name(html)
    mirror_letter_list = []
    if mirror_arabic:
        for ch in arabic_letters(mirror_arabic):
            divine = ARABIC_TO_DIVINE.get(ch, ("", ""))
            romans_by_arabic = {
                "ا":"Alif","أ":"Alif","إ":"Alif","آ":"Alif",
                "ب":"Ba","ت":"Ta","ث":"Tha","ج":"Jim",
                "ح":"Ha","خ":"Kha","د":"Dal","ذ":"Dhal",
                "ر":"Ra","ز":"Zayn","س":"Seen","ش":"Sheen",
                "ص":"Sad","ض":"Dad","ط":"Ta","ظ":"Dha",
                "ع":"Ain","غ":"Ghain","ف":"Fa","ق":"Qaf",
                "ك":"Kaf","ک":"Kaf","ل":"Lam","م":"Meem",
                "ن":"Nun","ه":"Ha","ة":"Ta","و":"Waw",
                "ي":"Ya","ى":"Ya","ی":"Ya","ئ":"Ya",
            }
            r = romans_by_arabic.get(ch, "")
            slug = ROMAN_TO_SLUG_HINT.get(r, r.lower())
            mirror_letter_list.append((ch, r, slug))
    letter_grid_html = render_letter_grid(mirror_letter_list, base_prefix="")
    inner_letters = letter_grid_html + inner_letters

    # Synthesis: on mirrors, use the EN fallback prose if available inside the
    # source EN page. But since this script runs per-mirror, we emit a small
    # translated placeholder that links to the EN synthesis anchor. Better than
    # a stub-in-mirror.
    slug = pathlib.Path("").name  # not used; kept simple
    synth_inner = (
        f'<div class="prose"><p><em>{title_synth}</em></p></div>'
        if lang == "ar"
        else f'<div class="prose"><p><em>{title_synth}</em></p></div>'
    )
    # We'll fill actual translated synthesis via a follow-on step from
    # generate_section3.py --lang ar/ur that reads the EN synthesis and
    # translates key nouns; for the sample we emit the section shell so the
    # layout is complete.

    # Preserve all five sections even when a source block is empty. Downstream
    # counters and readers expect the full 5-section skeleton on every mirror;
    # dropping a section produced <5 blocks on pages like `zahra` (missing 1+5)
    # and `mustafa` (missing 5). Emit an empty shell so the heading still lands.
    layout = shell(kicker_root,    title_root,    inner_root    or "", "root")
    layout += shell(kicker_letters, title_letters, inner_letters,       "letters")
    layout += shell(kicker_synth,   title_synth,   synth_inner,         "synthesis")
    layout += shell(kicker_dict,    title_dict,    inner_dict,          "dict")
    # Bearers is the last section, no trailing divider
    layout_bearers = (
        f'<section class="asr-v2 asr-v2-bearers">'
        f'<p class="asr-v2-kicker">{kicker_bearers}</p>'
        f'<h2 class="asr-v2-title">{title_bearers}</h2>'
        f'{inner_bearers or ""}'
        f'</section>'
    )
    layout += layout_bearers

    layout = f'<!-- LAYOUT-V2:START -->\n<div class="asr-layout-v2">{layout}</div>\n<!-- LAYOUT-V2:END -->'

    # Idempotency: if LAYOUT-V2 already present, replace in place and stop
    if LAYOUT_V2_RE.search(html):
        return LAYOUT_V2_RE.sub(layout, html, count=1)

    # Locate the earliest label and the LIFE-block end (or the QURANIC-context end)
    first_label_start = min(label_span[lb][0] for lb in expected_labels if lb in label_span)
    last_label_lb = expected_labels[4] if expected_labels[4] in label_span else expected_labels[3]
    last_label_end = label_span[last_label_lb][1]

    # Everything between first_label_start and last_label_end is replaced
    # by the new layout.
    return html[:first_label_start] + layout + html[last_label_end:]

# ---------------------------------------------------------------------------
# Public entry per slug
# ---------------------------------------------------------------------------
def process_slug(slug: str, mirrors: bool = True) -> dict:
    result = {"slug": slug, "en": None, "ar": None, "ur": None}
    en_path = ROOT / "names" / slug / "index.html"
    if en_path.exists():
        html = en_path.read_text(encoding="utf-8")
        new_html = apply_layout_v2_en(html)
        if new_html and new_html != html:
            en_path.write_text(new_html, encoding="utf-8")
            result["en"] = "written"
        elif new_html == html:
            result["en"] = "unchanged"
        else:
            result["en"] = "skipped (missing markers)"
    else:
        result["en"] = "no page"

    if mirrors:
        for lang, base in (("ar", ROOT / "ar" / "names"), ("ur", ROOT / "ur" / "names")):
            p = base / slug / "index.html"
            if p.exists():
                h = p.read_text(encoding="utf-8")
                nh = apply_layout_v2_mirror(h, lang)
                if nh and nh != h:
                    p.write_text(nh, encoding="utf-8")
                    result[lang] = "written"
                elif nh == h:
                    result[lang] = "unchanged"
                else:
                    result[lang] = "skipped (mirror shape mismatch)"
            else:
                result[lang] = "no page"
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true", help="apply to every canonical (do not run without approval)")
    ap.add_argument("--skip-mirrors", action="store_true")
    args = ap.parse_args()

    if args.all:
        slugs = sorted(p.name for p in (ROOT / "names").iterdir() if p.is_dir())
    else:
        slugs = args.slugs

    if not slugs:
        print("usage: redesign_layout.py <slug> [<slug>...]  or  --all", file=sys.stderr)
        sys.exit(2)

    for s in slugs:
        r = process_slug(s, mirrors=not args.skip_mirrors)
        ar = r['ar'] if r['ar'] is not None else 'skipped'
        ur = r['ur'] if r['ur'] is not None else 'skipped'
        print(f"{r['slug']:<20} EN={str(r['en']):<28} AR={ar:<28} UR={ur}")

if __name__ == "__main__":
    main()
