#!/usr/bin/env python3
"""
Translation layer 2 — Multi-point "Read another" CTA + dominant-letter cluster.

For every canonical name page:
 1) Insert a small "Read another" inline link right after the hero/identity
    block (before .content / SHARE-HERO begins), wrapped in HERO-RA markers.
 2) Insert a compact inline "Read another" link right after <!-- LIFE:END -->,
    wrapped in INLINE-RA markers.
 3) Insert a new section "Names sharing the [LETTER] influence" with 4-6
    cousin canonicals that share the page's dominant letter, wrapped in
    LETTERCLUSTER markers, placed after INLINE-RA (so directly after The Reading).

Dominant letter rule: most-frequent letter slug in this name's letter_breakdown;
ties broken by earliest position. If pool too small, fall back to next-ranked.

Idempotent: re-running detects existing markers and skips.
"""
import csv, json, re, hashlib
from pathlib import Path
from collections import Counter, defaultdict

REPO = Path(__file__).resolve().parent.parent
NAMES = REPO / "names"
TRACKER = REPO / "quality-tracker.csv"

NAMECARD_RE = re.compile(r'<script[^>]*id="asr-namecard"[^>]*>(.*?)</script>', re.S)
LIFE_END_RE = re.compile(r'<!--\s*LIFE:END\s*-->')
CONTENT_OPEN_RE = re.compile(r'<div class="content">')

HAS_HERO_RA = re.compile(r'<!--\s*HERO-RA:START\s*-->')
HAS_INLINE_RA = re.compile(r'<!--\s*INLINE-RA:START\s*-->')
HAS_CLUSTER = re.compile(r'<!--\s*LETTERCLUSTER:START\s*-->')


def load_canonicals():
    slugs = []
    with TRACKER.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not (row.get("is_duplicate_of") or "").strip():
                slugs.append(row["slug"])
    return slugs


def parse_namecard(text):
    m = NAMECARD_RE.search(text)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


def letter_ranking(letters):
    if not letters:
        return []
    counts = Counter(L["slug"] for L in letters)
    first_pos = {}
    for i, L in enumerate(letters):
        first_pos.setdefault(L["slug"], i)
    return sorted(counts.keys(), key=lambda s: (-counts[s], first_pos[s]))


def deterministic_sample(pool, n, seed_key):
    if not pool:
        return []
    scored = [(hashlib.md5(f"{seed_key}|{item[0]}".encode()).hexdigest(), item) for item in pool]
    scored.sort()
    return [item for (_, item) in scored[:n]]


def build_cluster_html(name_english, dominant_roman, dominant_arabic, picks):
    if not picks:
        return ""
    cards = []
    for slug, english in picks:
        cards.append(
            f'<a href="/names/{slug}/" class="lc-card" title="{english} — shares {dominant_roman}">'
            f'<span class="lc-name">{english}</span></a>'
        )
    cards_html = "".join(cards)
    return (
        '<!-- LETTERCLUSTER:START -->\n'
        f'<section class="letter-cluster" aria-label="Names sharing the {dominant_roman} influence">\n'
        f'  <p class="section-label" style="font-family:\'Cinzel\',serif;font-size:.75rem;letter-spacing:.2em;text-transform:uppercase;color:#8B6914;margin:3rem 0 .6rem;display:flex;align-items:center;gap:1rem;">Names sharing the <span lang="ar" dir="rtl" style="font-family:\'Amiri\',serif;font-size:1.1rem;color:#8B6914;letter-spacing:0;">{dominant_arabic}</span> {dominant_roman} influence<span style="flex:1;height:1px;background:#E8E2D4;display:inline-block;"></span></p>\n'
        f'  <p class="lc-intro" style="font-size:1rem;color:#6B6B6B;font-style:italic;margin-bottom:1rem;line-height:1.6;">Like <em>{name_english}</em>, these names carry {dominant_roman} ({dominant_arabic}) as their leading letter influence.</p>\n'
        f'  <div class="lc-grid" style="display:flex;flex-wrap:wrap;gap:.5rem;">{cards_html}</div>\n'
        '</section>\n'
        '<style>.letter-cluster .lc-card{display:inline-block;padding:.55rem 1.05rem;border:1px solid #E8E2D4;border-radius:4px;background:#FAFAF8;font-family:\'Cormorant Garamond\',serif;font-size:1rem;color:#2A2A2A;text-decoration:none;transition:all .18s;}.letter-cluster .lc-card:hover{background:#F2EFE8;border-color:#8B6914;color:#8B6914;}</style>\n'
        '<!-- LETTERCLUSTER:END -->\n'
    )


HERO_RA_HTML = (
    '<!-- HERO-RA:START -->\n'
    '<div class="asr-ra-hero" role="navigation" aria-label="Skip to another name" '
    'style="max-width:760px;margin:.4rem auto 1.2rem;padding:0 2rem;text-align:center;">\n'
    '  <a href="/names/" class="asr-ra-hero-link" data-asr-ra="hero" '
    'style="display:inline-flex;align-items:center;gap:.4rem;font-family:\'Cinzel\',serif;font-size:.68rem;letter-spacing:.22em;text-transform:uppercase;color:#8B6914;text-decoration:none;border-bottom:1px dotted rgba(139,105,20,.4);padding-bottom:.15rem;">'
    '<span class="asr-ra-hero-label">Or read another name</span>'
    '<span aria-hidden="true">→</span>'
    '</a>\n'
    '</div>\n'
    '<!-- HERO-RA:END -->\n'
)

INLINE_RA_HTML = (
    '<!-- INLINE-RA:START -->\n'
    '<p class="asr-ra-inline" style="max-width:760px;margin:1.2rem 0 0;font-size:1rem;color:#6B6B6B;font-style:italic;line-height:1.65;">\n'
    '  Want a different reading? '
    '<a href="/names/" data-asr-ra="inline" class="asr-ra-inline-link" '
    'style="font-style:normal;font-family:\'Cinzel\',serif;font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;color:#8B6914;text-decoration:none;border-bottom:1px solid rgba(139,105,20,.4);padding-bottom:.1rem;">'
    '<span class="asr-ra-inline-label">Read another →</span>'
    '</a>\n'
    '</p>\n'
    '<!-- INLINE-RA:END -->\n'
)


def inject_hero_ra(text):
    if HAS_HERO_RA.search(text):
        return text, False
    new = CONTENT_OPEN_RE.sub(HERO_RA_HTML + '<div class="content">', text, count=1)
    if new == text:
        return text, False
    return new, True


def inject_after_life_end(text, payload):
    m = LIFE_END_RE.search(text)
    if not m:
        return text, False
    insert_at = m.end()
    return text[:insert_at] + "\n" + payload + text[insert_at:], True


def main():
    slugs = load_canonicals()
    name_data = {}
    for slug in slugs:
        p = NAMES / slug / "index.html"
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8")
        card = parse_namecard(text)
        if not card:
            continue
        letters = card.get("letter_breakdown") or []
        if not letters:
            continue
        name_data[slug] = {
            "english": card.get("english") or slug.title(),
            "letters": letters,
            "ranking": letter_ranking(letters),
        }
    print(f"Parsed {len(name_data)} canonicals with letter data")

    by_dominant = defaultdict(list)
    by_any_letter = defaultdict(list)
    for slug, info in name_data.items():
        ranking = info["ranking"]
        if ranking:
            by_dominant[ranking[0]].append((slug, info["english"]))
        for ls in set(L["slug"] for L in info["letters"]):
            by_any_letter[ls].append((slug, info["english"]))

    print("Top dominant pools:", sorted(((k, len(v)) for k, v in by_dominant.items()), key=lambda x: -x[1])[:8])

    updated = 0
    skipped = 0
    for slug, info in name_data.items():
        p = NAMES / slug / "index.html"
        text = p.read_text(encoding="utf-8")

        ranking = info["ranking"]
        dom_slug = ranking[0]
        dom = next((L for L in info["letters"] if L["slug"] == dom_slug), None)
        if dom is None:
            continue

        def pool_for(letter_slug):
            return [(s, e) for (s, e) in by_dominant.get(letter_slug, []) if s != slug]

        pool = pool_for(dom_slug)
        if len(pool) < 4:
            seen = {s for (s, _) in pool}
            for s, e in by_any_letter.get(dom_slug, []):
                if s == slug or s in seen:
                    continue
                pool.append((s, e)); seen.add(s)
                if len(pool) >= 8:
                    break
        if len(pool) < 4:
            for fb in ranking[1:]:
                seen = {s for (s, _) in pool}
                for s, e in by_any_letter.get(fb, []):
                    if s == slug or s in seen:
                        continue
                    pool.append((s, e)); seen.add(s)
                if len(pool) >= 6:
                    break

        picks = deterministic_sample(pool, 6 if len(pool) >= 6 else max(4, min(len(pool), 5)), slug)
        if len(picks) > 6:
            picks = picks[:6]

        cluster_html = build_cluster_html(info["english"], dom["roman"], dom["arabic"], picks)

        changed = False
        if not HAS_HERO_RA.search(text):
            text2, did = inject_hero_ra(text)
            if did:
                text = text2; changed = True

        if not HAS_INLINE_RA.search(text) and not HAS_CLUSTER.search(text):
            payload = INLINE_RA_HTML + cluster_html
            text2, did = inject_after_life_end(text, payload)
            if did:
                text = text2; changed = True
        elif not HAS_INLINE_RA.search(text):
            text2, did = inject_after_life_end(text, INLINE_RA_HTML)
            if did:
                text = text2; changed = True
        elif not HAS_CLUSTER.search(text):
            text2, did = inject_after_life_end(text, cluster_html)
            if did:
                text = text2; changed = True

        if changed:
            p.write_text(text, encoding="utf-8")
            updated += 1
        else:
            skipped += 1

    print(f"Updated: {updated}  skipped (already injected): {skipped}")


if __name__ == "__main__":
    main()
