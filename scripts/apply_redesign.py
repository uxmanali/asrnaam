#!/usr/bin/env python3
"""Apply the redesign across generated pages.

The site publishes static HTML. This script is the generator step: it
computes the name count from names-index.json, rebuilds the homepage hero
from that index, corrects Hilal's Arabic heh and Inaya's Urdu spelling,
and attaches the shared redesign stylesheet and script to every real page.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "names" / "names-index.json"
FILTERS_PATH = ROOT / "names" / "filters.json"

LINK = '<link rel="stylesheet" href="/asr-redesign.css?v=20261112">'
SCRIPT = '<script src="/asr-redesign.js?v=20261112" defer></script>'
AD_OPT = (
    '<script>window.adsbygoogle=window.adsbygoogle||[];'
    'adsbygoogle.push({google_ad_client:"ca-pub-4856363287006906",'
    'enable_page_level_ads:false,overlays:{bottom:false},vignettes:{enable:false}});'
    '</script>'
)
AD_SRC = (
    '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
    '?client=ca-pub-4856363287006906" crossorigin="anonymous"></script>'
)

POPULAR = ["aisha", "muhammad", "maryam", "yusuf", "fatima", "hamza", "ibrahim", "noor"]
RAMADAN = ["hilal", "qamar", "huda", "badr"]
QURAN = ["maryam", "yusuf", "musa", "ibrahim", "ayat"]
MEANINGS = [
    ("/names/by-meaning/light/", "Light", "Noor, Zahra"),
    ("/names/by-meaning/strength/", "Strength", "Hamza"),
    ("/names/by-meaning/mercy/", "Peace", "Rahma"),
    ("/names/by-meaning/wisdom/", "Knowledge", "Hakim"),
]
ILM_LETTERS = [("ع", "Ain"), ("ا", "Alif"), ("ئ", "Ya"), ("ش", "Sheen"), ("ة", "Ta")]


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def short(meaning: str, n: int = 42) -> str:
    meaning = meaning.split(". ")[0].strip().rstrip(".")
    if len(meaning) <= n:
        return meaning
    cut = meaning[:n].rsplit(" ", 1)[0]
    return cut + "…"


def load_index() -> list[dict]:
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def fix_data(index: list[dict]) -> None:
    raw = INDEX_PATH.read_text(encoding="utf-8")
    raw2 = raw.replace(
        '"s":"inaya","n":"Inaya","a":"عناية","u":"عنایت"',
        '"s":"inaya","n":"Inaya","a":"عناية","u":"عنایہ"',
    ).replace(
        '"s":"hilal","n":"Hilal","a":"ہلال"',
        '"s":"hilal","n":"Hilal","a":"هلال"',
    )
    if raw2 != raw:
        INDEX_PATH.write_text(raw2, encoding="utf-8")
        for row in index:
            if row["s"] == "inaya":
                row["u"] = "عنایہ"
            if row["s"] == "hilal":
                row["a"] = "هلال"
    filters = FILTERS_PATH.read_text(encoding="utf-8")
    filters2 = filters.replace(
        '["inaya","Inaya","عناية","عنایت"',
        '["inaya","Inaya","عناية","عنایہ"',
    ).replace(
        '["hilal","Hilal","ہلال","ہلال"',
        '["hilal","Hilal","هلال","ہلال"',
    )
    if filters2 != filters:
        FILTERS_PATH.write_text(filters2, encoding="utf-8")


def fix_hilal_and_inaya() -> None:
    # Arabic-script headings marked lang=ar must use Arabic heh, not Urdu heh.
    for path in ROOT.rglob("index.html"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        orig = text
        if "ہلال" in text:
            text = text.replace('lang="ar" dir="rtl">ہلال', 'lang="ar" dir="rtl">هلال')
            text = text.replace('lang="ar">ہلال', 'lang="ar">هلال')
            text = text.replace('"arabic": "ہلال"', '"arabic": "هلال"')
            text = text.replace(
                'lang="ar" dir="rtl">ہ</span><span class="asr-v2-letter-roman">Ha',
                'lang="ar" dir="rtl">ه</span><span class="asr-v2-letter-roman">Ha',
            )
            text = text.replace('"arabic": "ہ", "roman": "Ha"', '"arabic": "ه", "roman": "Ha"')
        if (
            path.parent.name == "hilal"
            and path.parent.parent.name == "names"
            and path.parent.parent.parent.name == "ar"
        ):
            # The Arabic page is in Arabic. Keep only the labelled Urdu spelling.
            text = text.replace("ہلال", "هلال")
            text = re.sub(r'(lang="ur"[^>]*>)هلال', r"\1ہلال", text)
        if path.parent.name == "inaya" and path.name == "index.html":
            text = text.replace("عنایت", "عنایہ")
        if text != orig:
            path.write_text(text, encoding="utf-8")


def hero_html(index: list[dict], rotation: str) -> str:
    by = {row["s"]: row for row in index}
    count = f"{len(index):,}"
    girls = sum(1 for row in index if row.get("g") == "Female")
    boys = sum(1 for row in index if row.get("g") == "Male")
    letters = "".join(
        f'<a class="rd-lchip" href="/names/by-letter/{c}/" data-f="letter" data-v="{c}" aria-pressed="false">{c}</a>'
        for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )
    nums = "".join(
        f'<button type="button" class="rd-num" data-f="lucky" data-v="{i}" aria-pressed="false" aria-label="Lucky number {i}">{i}</button>'
        for i in range(1, 10)
    )
    pops = []
    for slug in POPULAR:
        row = by[slug]
        g = "girl" if row["g"] == "Female" else "boy"
        pops.append(
            f'<a class="rd-pop" href="/names/{slug}/"><span class="ar" lang="ar" dir="rtl">{esc(row["a"])}</span>'
            f'<span><b>{esc(row["n"])}</b><small>{esc(short(row["m"]))}</small></span>'
            f'<span class="rd-tag {g}">{esc(row["g"])}</span></a>'
        )
    rams = []
    for slug in RAMADAN:
        row = by[slug]
        rams.append(
            f'<a class="rd-rn" href="/names/{slug}/"><span><b>{esc(row["n"])}</b>'
            f'<small>{esc(short(row["m"], 36))}</small></span>'
            f'<span class="ar" lang="ar" dir="rtl">{esc(row["a"])}</span></a>'
        )
    pills = []
    for slug in QURAN:
        row = by[slug]
        pills.append(
            f'<span class="rd-pill">{esc(row["n"])} <span class="ar" lang="ar" dir="rtl">{esc(row["a"])}</span></span>'
        )
    meaning = "".join(
        f'<a class="rd-chip" href="{href}">{esc(label)}</a>' for href, label, _ex in MEANINGS
    )
    # The four meaning chips above are the ones that exist as collection pages.
    extra_meanings = (
        '<a class="rd-chip" href="/names/by-meaning/beautiful/">Beauty</a>'
        '<a class="rd-chip" href="/names/by-meaning/faithful/">Faith</a>'
        '<a class="rd-chip" href="/names/by-meaning/flower/">Nature</a>'
    )
    ilm = "".join(
        f'<span class="rd-lt"><span class="ar" lang="ar">{g}</span><small>{name}</small></span>'
        for g, name in ILM_LETTERS
    )
    return f'''<section class="rd-hero">
  <div class="rd-wrap">
    <p class="rd-hk"><b data-name-count>{count}</b> Muslim names · <span lang="ur" dir="rtl">اردو</span> · <span lang="ar" dir="rtl">العربية</span> · हिन्दी · Türkçe</p>
    <h1>Find a name your child will <em>love to carry</em></h1>
    <p class="rd-sub">Real meanings from classical sources, Arabic and Urdu script, pronunciation, an abjad lucky number and a letter-by-letter Ilm ul Huroof reading.</p>
    <form class="rd-search" action="/reader/" method="get" role="search" autocomplete="off">
      <div class="rd-search-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3-3"/></svg>
        <label class="rd-sr" for="rd-q">Search names</label>
        <input id="rd-q" name="name" type="search" placeholder="Search names, meanings, or Arabic script" aria-autocomplete="list" aria-controls="rd-ac" aria-expanded="false" enterkeyhint="search">
        <button class="rd-btn rd-btn-primary" type="submit"><span>Search</span></button>
      </div>
      <div id="rd-ac" class="rd-ac" role="listbox" hidden></div>
    </form>
    <div class="rd-gb">
      <a class="g" href="/names/girls/"><span class="ic" aria-hidden="true">♀</span>Girl names <small>{girls:,}</small></a>
      <a class="b" href="/names/boys/"><span class="ic" aria-hidden="true">♂</span>Boy names <small>{boys:,}</small></a>
    </div>
    <p class="rd-stats"><span><b>Free</b> · no sign-up</span><span><b>5</b> languages</span><span>Checked against <b>classical lexicons</b></span></p>
  </div>
</section>
<section class="rd-filters"><div class="rd-wrap"><div class="rd-card">
  <div class="rd-frow"><span class="rd-flabel">First letter</span><div class="rd-letters">{letters}</div></div>
  <div class="rd-frow"><span class="rd-flabel">Meaning</span>{meaning}{extra_meanings}</div>
  <div class="rd-frow"><span class="rd-flabel">Origin</span>
    <a class="rd-chip" href="/names/by-region/arabic/">Arabic</a>
    <a class="rd-chip" href="/names/by-region/persian/">Persian</a>
    <a class="rd-chip" href="/names/by-region/turkish/">Turkish</a>
    <a class="rd-chip" href="/names/by-region/south-asian/">Urdu</a>
    <a class="rd-chip" href="/names/quranic/">Quranic</a>
    <span class="rd-flabel">Length</span>
    <button type="button" class="rd-chip" data-f="length" data-v="short" aria-pressed="false">Short · 3–4</button>
    <button type="button" class="rd-chip" data-f="length" data-v="medium" aria-pressed="false">Medium</button>
    <button type="button" class="rd-chip" data-f="length" data-v="long" aria-pressed="false">Long</button>
  </div>
  <div class="rd-frow"><span class="rd-flabel">Lucky number</span>{nums}</div>
  <div id="rd-filter-results" class="rd-results" hidden>
    <p class="rd-results-meta"></p>
    <div class="rd-results-grid"></div>
  </div>
</div></div></section>
<section><div class="rd-wrap rd-duo">
  <!-- google_ad_section_start(weight=ignore) -->
  <article class="rd-notd" id="nameOfTheDay" aria-label="Name of the day">
    <div class="rd-top"><span class="rd-kicker">Name of the day</span><span class="date" id="notdDate">Today</span></div>
    <span class="rd-ar" lang="ar" dir="rtl" id="notdArabic">مُحَمَّد</span>
    <h2><a id="notdLink" href="/names/muhammad/"><span id="notdName">Muhammad</span></a></h2>
    <p class="mean" id="notdMeaning">The most praised; the praiseworthy one</p>
    <a class="rd-btn rd-btn-primary" id="notdCta" href="/names/muhammad/">Read the full meaning</a>
  </article>
  <!-- google_ad_section_end -->
  <div class="rd-popular">
    <h2>Popular names</h2>
    <p class="note">A curated list of names parents ask for. Not a live ranking.</p>
    {''.join(pops)}
  </div>
</div></section>
{rotation}
<section class="rd-section"><div class="rd-wrap">
  <div class="rd-ramadan">
    <div>
      <p class="rd-kicker">Ramadan names</p>
      <h2>Names for a Ramadan and Eid baby</h2>
      <p>Crescent, moon and guidance. Each of these names is on the site, with its reading.</p>
      <a class="rd-btn rd-btn-gold" href="/names/by-meaning/light/">Explore names of light</a>
    </div>
    <div class="rd-rnames">{''.join(rams)}</div>
  </div>
</div></section>
<section class="rd-section"><div class="rd-wrap rd-lists">
  <a class="rd-list q" href="/names/quranic/">
    <p class="rd-kicker">Collection</p>
    <h2>Names from the Quran</h2>
    <p>Prophets, the righteous and Quranic words, each with its own page.</p>
    <div class="rd-pills">{''.join(pills)}</div>
    <span class="go">Browse Quranic names</span>
  </a>
  <a class="rd-list m" href="/names/by-meaning/">
    <p class="rd-kicker">Collection</p>
    <h2>Names by meaning</h2>
    <p>Start from the quality you hope for, then find the name.</p>
    <div class="rd-pills">
      <span class="rd-pill">Light</span><span class="rd-pill">Strength</span><span class="rd-pill">Mercy</span><span class="rd-pill">Wisdom</span>
    </div>
    <span class="go">Browse by meaning</span>
  </a>
</div></section>
<section class="rd-section"><div class="rd-wrap"><div class="rd-ilm">
  <div>
    <p class="rd-kicker">Ilm ul Huroof</p>
    <h2>What do the letters of a name say?</h2>
    <p>Read any name, including one that is not in the list. The letters of Aisha are one example.</p>
  </div>
  <div class="rd-lts" aria-hidden="true">{ilm}</div>
  <a class="rd-btn rd-btn-primary" href="/reader/">Read your name</a>
</div></div></section>
'''


def rebuild_home(index: list[dict]) -> None:
    path = ROOT / "index.html"
    html = path.read_text(encoding="utf-8")
    start = html.find('<div class="hero">')
    end = html.find('<div class="how">')
    if start < 0 or end < 0:
        raise SystemExit("homepage markers missing")
    block = html[start:end]
    rotation = re.search(
        r'<script type="application/json" id="notd-rotation">.*?</script>\s*<script>.*?</script>',
        block,
        re.S,
    )
    if not rotation:
        raise SystemExit("name-of-the-day script missing")
    count = f"{len(index):,}"
    html = html[:start] + hero_html(index, rotation.group(0)) + html[end:]
    html = html.replace("2,445", count)
    # Keep the count tied to the index in structured data that used a bare figure.
    html = html.replace(
        "Letter-by-letter spiritual readings for 2,445 Muslim names",
        f"Letter-by-letter spiritual readings for {count} Muslim names",
    )
    if "<!-- name-count:" not in html:
        html = html.replace(
            "<title>",
            f"<!-- name-count:{len(index)} computed from names/names-index.json -->\n<title>",
            1,
        )
    path.write_text(html, encoding="utf-8")


def attach(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if 'http-equiv="refresh"' in text or "window.location.replace" in text:
        return
    orig = text
    if "asr-redesign.css" not in text and "</head>" in text:
        text = text.replace("</head>", LINK + "\n</head>", 1)
    if "asr-redesign.js" not in text and "</body>" in text:
        text = text.replace("</body>", SCRIPT + "\n</body>", 1)
    if AD_SRC in text and "enable_page_level_ads:false" not in text:
        text = text.replace(AD_SRC, AD_OPT + "\n" + AD_SRC, 1)
    if text != orig:
        path.write_text(text, encoding="utf-8")


def main() -> None:
    index = load_index()
    fix_data(index)
    index = load_index()
    missing = [slug for slug in POPULAR + RAMADAN + QURAN if slug not in {r["s"] for r in index}]
    if missing:
        raise SystemExit("curated names missing from the index: " + ", ".join(missing))
    rebuild_home(index)
    fix_hilal_and_inaya()
    n = 0
    for path in ROOT.rglob("index.html"):
        if ".git" in path.parts:
            continue
        attach(path)
        n += 1
    print(f"names {len(index)} pages-seen {n}")


if __name__ == "__main__":
    main()
