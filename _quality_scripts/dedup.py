"""
CHECK 2: Convert dup loser pages to redirect stubs.
- Update canonical's spelling chip rail to include alternate forms (no-link chip)
- Replace loser /names/{slug}/index.html with redirect stub
- Update sitemap.xml: remove loser URLs
- Update names/index.html: rewrite any /names/{loser}/ link to /names/{canonical}/
- Append _redirects lines for the new loser URLs
"""
import json, re, os, sys, html
from pathlib import Path

REPO = Path("/tmp/work-quality/asrnaam")
NAMES = REPO / "names"
SITEMAP = REPO / "sitemap.xml"
INDEX = REPO / "names" / "index.html"
REDIRECTS = REPO / "_redirects"
DECISIONS = json.load(open("/tmp/work-quality/dedup-decisions.json", "r", encoding="utf-8"))

REDIRECT_STUB_TPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Redirecting to {canon_display} | AsrNaam</title>
<link rel="canonical" href="https://asrnaam.com/names/{canon}/"/>
<meta name="robots" content="noindex,follow"/>
<meta http-equiv="refresh" content="0; url=https://asrnaam.com/names/{canon}/"/>
<script>window.location.replace("https://asrnaam.com/names/{canon}/");</script>
<style>body{{font-family:sans-serif;max-width:600px;margin:4rem auto;padding:0 1rem;color:#333;}}</style>
</head>
<body>
<p>{loser_display} is also spelled <a href="https://asrnaam.com/names/{canon}/">{canon_display}</a>.</p>
</body>
</html>
"""

def write_redirect_stub(loser_slug, canon_slug):
    canon_display = canon_slug.replace('-',' ').title()
    loser_display = loser_slug.replace('-',' ').title()
    path = NAMES / loser_slug / "index.html"
    path.write_text(REDIRECT_STUB_TPL.format(
        canon=canon_slug, canon_display=canon_display, loser_display=loser_display
    ), encoding="utf-8")

def update_canonical_chip_rail(canon_slug, alt_slugs):
    """Append no-link chips for each alt spelling onto canonical's chip rail."""
    path = NAMES / canon_slug / "index.html"
    if not path.is_file(): return False
    t = path.read_text(encoding="utf-8")
    # Find spellings-grid div
    m = re.search(r'(<div class="spellings-grid">)(.*?)(</div>)', t, re.S)
    if not m: return False
    inner = m.group(2)
    chips_existing = re.findall(r'<span class="spelling-chip[^"]*"[^>]*>([^<]+?)</span>', inner)
    chips_norm = set(c.strip().rstrip('✓').strip().lower() for c in chips_existing)
    added = []
    for alt in alt_slugs:
        alt_disp = alt.replace('-',' ').title()
        if alt_disp.lower() in chips_norm: continue
        # Insert chip with link to alt URL (which is redirect stub)
        new_chip = f'<a class="spelling-chip" href="/names/{alt}/">{alt_disp}</a>'
        inner = inner + new_chip
        added.append(alt_disp)
    if not added: return False
    new_text = t[:m.start(2)] + inner + t[m.end(2):]
    path.write_text(new_text, encoding="utf-8")
    return True

def update_sitemap(loser_urls):
    """Remove <url>...<loc>https://asrnaam.com/names/{loser}/</loc>...</url> blocks."""
    t = SITEMAP.read_text(encoding="utf-8")
    removed = 0
    for u in loser_urls:
        pat = re.compile(
            r'\s*<url>\s*<loc>\s*' + re.escape(f'https://asrnaam.com/names/{u}/') + r'\s*</loc>.*?</url>',
            re.S)
        new_t, n = pat.subn('', t)
        if n: t = new_t; removed += n
    SITEMAP.write_text(t, encoding="utf-8")
    return removed

def update_names_index(rewrites):
    """rewrite href=/names/{loser}/ -> /names/{canon}/ in names/index.html. Drop the dup card."""
    t = INDEX.read_text(encoding="utf-8")
    # Strip out lines linking to losers (single line per <a> typically)
    out_lines = []
    dropped = 0
    losers = set(rewrites.keys())
    for line in t.splitlines(keepends=True):
        m = re.search(r'href="/names/([a-z0-9-]+)/"', line)
        if m and m.group(1) in losers:
            # Drop this anchor element from the list
            dropped += 1
            continue
        out_lines.append(line)
    INDEX.write_text(''.join(out_lines), encoding="utf-8")
    return dropped

def append_redirects(rewrites):
    lines = []
    for loser, canon in rewrites.items():
        lines.append(f"/names/{loser}/ /names/{canon}/ 301")
        lines.append(f"/names/{loser}/index.html /names/{canon}/ 301")
    with REDIRECTS.open("a", encoding="utf-8") as f:
        f.write("\n# Dedup pass quality round\n" + "\n".join(lines) + "\n")
    return len(lines)

def main():
    rewrites = {}
    canon_to_alts = {}
    for d in DECISIONS:
        canon = d['canonical']
        canon_to_alts.setdefault(canon, []).extend(d['redirects'])
        for r in d['redirects']:
            rewrites[r] = canon

    # Convert losers to redirect stubs
    for loser, canon in rewrites.items():
        write_redirect_stub(loser, canon)
    print(f"Wrote {len(rewrites)} redirect stubs")

    # Update each canonical's chip rail
    chip_updated = 0
    for canon, alts in canon_to_alts.items():
        if update_canonical_chip_rail(canon, alts): chip_updated += 1
    print(f"Updated chip rail on {chip_updated} canonicals")

    # Sitemap
    removed = update_sitemap(list(rewrites.keys()))
    print(f"Removed {removed} URLs from sitemap.xml")

    # names/index.html
    dropped = update_names_index(rewrites)
    print(f"Dropped {dropped} name cards from names/index.html")

    # _redirects
    n = append_redirects(rewrites)
    print(f"Appended {n} lines to _redirects")

if __name__ == "__main__":
    main()
