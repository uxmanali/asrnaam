#!/usr/bin/env python3
"""
Translation layer 3 — Per-page section ordering by content strength.

For every canonical, decide an archetype based on signals from the page itself,
then reorder these movable sections inside .content:

   QFACTS  SHARE-HERO  [MEAN-DICT  MEAN-ROOT  MEAN-IUH  LIFE+INLINE-RA+LETTERCLUSTER
                        PRON]  ...

Movable group = MEAN-DICT, MEAN-ROOT, MEAN-IUH, LIFE-trio, PRON.
The LIFE/INLINE-RA/LETTERCLUSTER trio always moves together (they're a single
narrative unit). BEARERS is also moved in the bearer-led/light archetypes.

Archetypes (priority order — first match wins):
  bearer-led : bearers_count_visible >= 2  → BEARERS lifted up between
               MEAN-DICT and MEAN-ROOT; meaning group otherwise default order.
  iuh-led    : meaning_iuh chars >= 200    → LIFE-trio + MEAN-IUH promoted to top.
  root-led   : meaning_root chars >= 150   → MEAN-ROOT promoted before MEAN-DICT.
  bearer-light : bearers_count_visible == 0  → BEARERS dropped below FAQ; PRON
               promoted up to right after MEAN-DICT.
  default    : current order.

Idempotent — reading the markers and rewriting in archetype order produces
identical text on a second run.
"""
import csv, re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
NAMES = REPO / "names"
TRACKER = REPO / "quality-tracker.csv"

MOVABLE = ['MEAN-DICT', 'MEAN-ROOT', 'MEAN-IUH', 'LIFE', 'INLINE-RA', 'LETTERCLUSTER', 'PRON']
TRIO = ['LIFE', 'INLINE-RA', 'LETTERCLUSTER']

ORDER_MARKER = re.compile(r'<!--\s*SECTION-ORDER:archetype=([\w-]+)\s*-->')


def block_pattern(name):
    return re.compile(rf'<!--\s*{re.escape(name)}:START\s*-->.*?<!--\s*{re.escape(name)}:END\s*-->', re.S)


def extract_block(text, name):
    p = block_pattern(name)
    m = p.search(text)
    if not m:
        return None, None, None
    return m.group(0), m.start(), m.end()


def remove_block(text, name):
    p = block_pattern(name)
    return p.sub('', text, count=1)


def archetype_for(row):
    bearers = int(row.get('bearers_count_visible') or '0' or 0)
    iuh_len = len(row.get('meaning_iuh') or '')
    root_len = len(row.get('meaning_root') or '')
    if bearers >= 2:
        return 'bearer-led'
    if iuh_len >= 200:
        return 'iuh-led'
    if root_len >= 150:
        return 'root-led'
    if bearers == 0:
        return 'bearer-light'
    return 'default'


def desired_meaning_order(archetype):
    """Return the order (list of marker names) for the meaning movable group.
    LIFE-trio is represented as 'LIFE-TRIO'."""
    if archetype == 'bearer-led':
        return ['MEAN-DICT', 'BEARERS', 'MEAN-ROOT', 'MEAN-IUH', 'LIFE-TRIO', 'PRON']
    if archetype == 'iuh-led':
        return ['MEAN-IUH', 'LIFE-TRIO', 'MEAN-DICT', 'MEAN-ROOT', 'PRON']
    if archetype == 'root-led':
        return ['MEAN-ROOT', 'MEAN-DICT', 'MEAN-IUH', 'LIFE-TRIO', 'PRON']
    if archetype == 'bearer-light':
        return ['MEAN-DICT', 'PRON', 'MEAN-IUH', 'LIFE-TRIO', 'MEAN-ROOT']
    return ['MEAN-DICT', 'MEAN-ROOT', 'MEAN-IUH', 'LIFE-TRIO', 'PRON']


def reorder_page(text, archetype):
    # Extract all movable blocks.
    blocks = {}
    spans = {}
    for name in MOVABLE:
        blk, s, e = extract_block(text, name)
        if blk:
            blocks[name] = blk
            spans[name] = (s, e)
    # Build LIFE-TRIO as concatenation in current page order of LIFE, INLINE-RA, LETTERCLUSTER.
    trio_parts = [blocks[n] for n in TRIO if n in blocks]
    trio_text = '\n'.join(trio_parts) if trio_parts else ''

    # Determine the region covered by the meaning movable group (MEAN-DICT through PRON).
    region_names = ['MEAN-DICT', 'MEAN-ROOT', 'MEAN-IUH', 'LIFE', 'INLINE-RA', 'LETTERCLUSTER', 'PRON']
    starts = [spans[n][0] for n in region_names if n in spans]
    ends = [spans[n][1] for n in region_names if n in spans]
    if not starts:
        return text, False
    region_start = min(starts)
    region_end = max(ends)

    # Determine BEARERS state if archetype needs it.
    bearers_blk = None
    bearers_span = None
    if archetype in ('bearer-led', 'bearer-light'):
        bearers_blk, bs, be = extract_block(text, 'BEARERS')
        if bearers_blk:
            bearers_span = (bs, be)

    order = desired_meaning_order(archetype)

    # Build new region text.
    parts = []
    for name in order:
        if name == 'LIFE-TRIO':
            if trio_text:
                parts.append(trio_text)
        elif name == 'BEARERS':
            if bearers_blk:
                parts.append(bearers_blk)
        else:
            if name in blocks:
                parts.append(blocks[name])
    new_region = '\n'.join(parts)

    # Detect existing SECTION-ORDER comment and remove (we'll add a fresh one).
    text = ORDER_MARKER.sub('', text)
    # Re-extract region positions after marker removal.
    starts = []
    ends = []
    for n in region_names:
        m = block_pattern(n).search(text)
        if m:
            starts.append(m.start())
            ends.append(m.end())
    region_start = min(starts)
    region_end = max(ends)

    # If we lifted BEARERS into the region, also strip BEARERS from its later position
    # and (in bearer-led) the new BEARERS is part of new_region.
    if archetype == 'bearer-led' and bearers_blk:
        # Remove ALL existing BEARERS occurrences in the rest of the text (but they're outside region).
        text_pre = text[:region_start]
        text_post = text[region_end:]
        text_post = block_pattern('BEARERS').sub('', text_post, count=1)
        new_text = text_pre + new_region + text_post
    elif archetype == 'bearer-light' and bearers_blk:
        # Remove BEARERS from current position and append it just before </div></div></body> region.
        text_pre = text[:region_start]
        text_post = text[region_end:]
        text_post = block_pattern('BEARERS').sub('', text_post, count=1)
        # Append BEARERS near the bottom of .content — before the closing </div> of .content.
        # Strategy: insert before the next </div> followed by <!-- TRUST or <!-- ASR:FOOTER. We'll
        # look for the last </div> in .content. Simplest: insert right before any </div>\s*<!-- TRUST
        # or </div>\s*<!-- ASR:FOOTER.
        m_trust = re.search(r'(\s*</div>\s*)(<!--\s*TRUST:START)', text_post)
        m_foot  = re.search(r'(\s*</div>\s*)(<!--\s*ASR:FOOTER:START)', text_post)
        if m_trust:
            insert_at = m_trust.start(1)
            text_post = text_post[:insert_at] + '\n' + bearers_blk + '\n' + text_post[insert_at:]
        elif m_foot:
            insert_at = m_foot.start(1)
            text_post = text_post[:insert_at] + '\n' + bearers_blk + '\n' + text_post[insert_at:]
        else:
            # Fallback: append at end of text_post.
            text_post = bearers_blk + '\n' + text_post
        new_text = text_pre + new_region + text_post
    else:
        new_text = text[:region_start] + new_region + text[region_end:]

    # Stamp archetype marker just inside .content (after the opening <div class="content">).
    stamp = f'<!-- SECTION-ORDER:archetype={archetype} -->\n'
    new_text = re.sub(r'(<div class="content">)', r'\1' + stamp, new_text, count=1)

    return new_text, True


def main():
    rows = []
    with TRACKER.open(encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if not (row.get("is_duplicate_of") or "").strip():
                rows.append(row)
    print(f"Canonicals: {len(rows)}")

    from collections import Counter
    arch_count = Counter()
    updated = 0
    skipped = 0
    for row in rows:
        slug = row['slug']
        p = NAMES / slug / "index.html"
        if not p.is_file():
            continue
        text = p.read_text(encoding='utf-8')

        # Detect existing archetype stamp.
        m = ORDER_MARKER.search(text)
        archetype = archetype_for(row)
        arch_count[archetype] += 1
        if m and m.group(1) == archetype:
            skipped += 1
            continue

        new_text, changed = reorder_page(text, archetype)
        if changed and new_text != text:
            p.write_text(new_text, encoding='utf-8')
            updated += 1
        else:
            skipped += 1

    print("Archetype distribution:", dict(arch_count))
    print(f"Updated: {updated}  skipped: {skipped}")


if __name__ == '__main__':
    main()
