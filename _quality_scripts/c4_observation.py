#!/usr/bin/env python3
"""
Translation layer 4 — Per-name personality observation callout.

For every canonical, insert a one-sentence callout box directly above
<!-- LIFE:START --> in the form:

  People often notice {OBSERVATION} in those who carry this name.

Where OBSERVATION is grounded in the dominant-letter trait of the name's
letter_breakdown. Dominant rule mirrors C2: most-frequent letter slug;
ties broken by earliest position. For names whose dominant letter has only
one occurrence AND the name is 5+ letters with no repeats, we fall through
to a generic fallback pool.

A pool of 3-5 phrases is provided per letter; the chosen phrase is picked
deterministically by md5(slug | letter_slug) so each name gets ONE specific
line but a letter's pool produces variance across the cohort sharing that letter.

Wrapped in OBS-CALLOUT markers for idempotency.
"""
import csv, json, re, hashlib
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
NAMES = REPO / "names"
TRACKER = REPO / "quality-tracker.csv"

NAMECARD_RE = re.compile(r'<script[^>]*id="asr-namecard"[^>]*>(.*?)</script>', re.S)
LIFE_START_RE = re.compile(r'<!--\s*LIFE:START\s*-->')
HAS_CALLOUT = re.compile(r'<!--\s*OBS-CALLOUT:START\s*-->')
OLD_CALLOUT_RE = re.compile(r'<!--\s*OBS-CALLOUT:START\s*-->.*?<!--\s*OBS-CALLOUT:END\s*-->', re.S)


PHRASES = {
    'alif': [
        "an upright, standing-alone bearing",
        "a clarity at the centre, arriving whole rather than gathered",
        "a quiet refusal to be folded into the crowd",
        "an uprightness that holds without needing approval",
    ],
    'ba': [
        "a steady underneath, the kind of presence others come to rest on",
        "a grounded, supportive bearing — a foundation in the room",
        "a quiet capacity to hold things up without making a show of it",
        "a foundational reliability others build their plans around",
    ],
    'ta-light': [
        "a way of finishing things, bringing situations to a soft, complete close",
        "a quiet competence at sealing what has been opened",
        "a settled, almost feminine completeness in how they meet the world",
        "an ability to round things off, leaving situations sealed and whole",
    ],
    'ta-heavy': [
        "a firm-footedness, not easily moved off their ground",
        "a weight of conviction that doesn't bend to fashion",
        "a deliberate sturdiness in how they take a position",
        "a planted-foot certainty in how they hold space",
    ],
    'tha': [
        "a fineness of distinction, catching what others lump together",
        "a subtle perceptiveness for the small differences",
        "a quiet preference for the precise word over the easy one",
        "a refined attentiveness to texture and detail",
    ],
    'jeem': [
        "a gathering quality, bringing people and threads together",
        "a hosting presence, often becoming the meeting place",
        "an eldering instinct that others naturally orbit",
        "a binding warmth that pulls a circle into shape",
    ],
    'ha-breath': [
        "a warm vitality just under the surface, life-giving in small ways",
        "a hidden breath of mercy in how they move through difficulty",
        "a sunlit, sustaining quality that quietly feeds the people around them",
        "a life-bringing warmth that doesn't announce itself",
    ],
    'ha-light': [
        "an open, breath-like quality alive in conversation and feeling",
        "an outward aliveness that energises the rooms they enter",
        "an aspirational lightness that lifts what it touches",
        "a bright responsiveness, meeting the moment with breath",
    ],
    'kha': [
        "a discerning eye, lifting the essential out of the noise",
        "a quiet talent for sorting what belongs from what doesn't",
        "a separating intelligence that knows what to keep",
        "an instinct for cutting away the inessential",
    ],
    'dal': [
        "a door-like quality, where endings rarely close fully",
        "an instinct to leave things open, never quite closing the door",
        "a returning, forgiving softness in how they hold relationships",
        "a slow-to-close warmth that keeps the way back unlocked",
    ],
    'dha': [
        "a preserving instinct, keeping what others would discard",
        "a continuity that doesn't break easily",
        "a steady-keeping quality that holds shape over time",
        "a quiet faithfulness to what's been entrusted to them",
    ],
    'ra': [
        "a moving mercy, kindness that travels rather than waits",
        "a gentle forward-motion that carries others along",
        "a fluent warmth that bends toward softness",
        "a graceful momentum, with a tenderness underneath",
    ],
    'zayn': [
        "an instinct for adornment, making what they touch more beautiful",
        "a refined aesthetic sense in even the smallest choices",
        "a polish, an ornament-quality in how they present themselves",
        "a sense of ceremony in the ordinary",
    ],
    'seen': [
        "an orderly helpfulness, quietly arranging things in the background",
        "a supporting instinct that keeps the structure standing",
        "a sustaining capacity that keeps small details from collapsing",
        "a quiet competence with the unseen logistics of a life",
    ],
    'sheen': [
        "a spreading warmth, a presence that widens to fill the room",
        "a sun-like influence under which things tend to grow",
        "a radiating quality, with their effect felt at the edges",
        "a kind of brightness others lean into without noticing",
    ],
    'sad': [
        "a patient sincerity, where what they say tends to be what they mean",
        "an unhurried steadfastness, a long-haul faithfulness",
        "a sincere weight in their commitments",
        "a quiet uprightness in keeping their word",
    ],
    'dad': [
        "a weighty distinctness, neither blending in nor trying to",
        "an emphatic, almost gravitational presence",
        "a particularity that makes them unmistakable in a crowd",
        "a heavy-set certainty in how they take their ground",
    ],
    'ain': [
        "a deep noticing, seeing what most people walk past",
        "a perceptive stillness, watching before speaking",
        "a sourcing quality, drawing from somewhere quieter than the surface",
        "an inward eye that catches the texture of a moment",
    ],
    'ghayn': [
        "a protective quietness, shielding what's precious without performance",
        "a private depth, holding more back than offered",
        "a guarded warmth, generous once the door is opened",
        "a covering instinct, screening what doesn't yet need to be seen",
    ],
    'fa': [
        "a knack for opening with the right word, naming things cleanly",
        "an articulate instinct, quick to put shape to what was felt",
        "a fluency in finishing thoughts, sorting and naming what was true",
        "an opening-of-speech quality that gets the conversation moving",
    ],
    'qaf': [
        "a mountain-like solidity that doesn't blur in pressure",
        "a quiet command in their bearing, even without rank",
        "a weight of authority that lands without needing to be raised",
        "a settled command that doesn't have to repeat itself",
    ],
    'kaf': [
        "a self-sufficiency that doesn't need much around them to feel whole",
        "a contained completeness, nothing missing on their side",
        "an instinct for 'enough', recognised where others over-reach",
        "a quiet self-containment that doesn't ask the room for help",
    ],
    'lam': [
        "a steady attachment in love and loyalty, slow to leave anything",
        "a persistence that doesn't loosen its grip easily",
        "a turning-toward quality, fully present to whoever they're with",
        "a holding-on warmth that outlasts most weather",
    ],
    'meem': [
        "a quiet inward steadiness, the family centre even at a distance",
        "a depth of love that runs slow and doesn't dry up",
        "a sustaining, motherly warmth — even where it's never named that",
        "an inward gravitational pull that draws people back for ease",
    ],
    'nun': [
        "a hidden depth, where more is going on inside than is said out loud",
        "a quiet inward life, thinking long before speaking",
        "a reserve that holds something the conversation hasn't reached yet",
        "an underwater quality, where what surfaces is less than what's underneath",
    ],
    'waw': [
        "a joining instinct that brings two things into the same room",
        "a connective quality, tending to bridge between people",
        "an and-quality, adding rather than replacing",
        "a hinge-like presence through which many things turn",
    ],
    'ya': [
        "a quiet specificity, small and exact, never quite general",
        "an inward-turning attention that lands on one thing at a time",
        "a particularity in how they care for this person, this moment",
        "a way of taking the abstract and making it personal",
    ],
    'hamza': [
        "a decisive originating force that tends to start things",
        "an arrival quality, where their entrance shifts the room",
        "an initiating instinct, even where others wait",
        "a sharp first-cause energy, opening what was closed",
    ],
}

GENERIC = [
    "a fluid warmth and adaptiveness that shifts with the room",
    "a quietly composite quality — neither one thing nor the other",
    "a blended bearing — many threads woven, no single one dominant",
    "an evenness across registers, not over-pronounced in any direction",
]


def load_canonicals():
    out = []
    with TRACKER.open(encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if not (row.get('is_duplicate_of') or '').strip():
                out.append(row['slug'])
    return out


def parse_namecard(text):
    m = NAMECARD_RE.search(text)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


def dominant_letter(letters):
    """Return (slug, roman, max_count). If no letters, None."""
    if not letters:
        return None
    counts = Counter(L['slug'] for L in letters)
    max_c = max(counts.values())
    # Earliest-position tiebreak.
    for L in letters:
        if counts[L['slug']] == max_c:
            return (L['slug'], L['roman'], max_c)
    return None


def choose_phrase(slug, letters):
    """Return (observation_phrase, basis_label) for the slug."""
    dom = dominant_letter(letters)
    if dom is None:
        # No letter data — generic fallback
        idx = int(hashlib.md5(f"{slug}|generic".encode()).hexdigest(), 16) % len(GENERIC)
        return GENERIC[idx], 'generic'
    dom_slug, dom_roman, dom_count = dom

    # If max count is 1 and name is long with all unique letters, use generic.
    if dom_count == 1 and len(letters) >= 6:
        idx = int(hashlib.md5(f"{slug}|generic".encode()).hexdigest(), 16) % len(GENERIC)
        return GENERIC[idx], 'generic'

    pool = PHRASES.get(dom_slug)
    if not pool:
        idx = int(hashlib.md5(f"{slug}|generic".encode()).hexdigest(), 16) % len(GENERIC)
        return GENERIC[idx], 'generic'

    idx = int(hashlib.md5(f"{slug}|{dom_slug}".encode()).hexdigest(), 16) % len(pool)
    return pool[idx], dom_roman


def build_callout(observation, basis_label):
    basis_attr = f' data-letter="{basis_label}"' if basis_label != 'generic' else ' data-letter="generic"'
    sentence = f"People often notice {observation} in those who carry this name."
    return (
        '<!-- OBS-CALLOUT:START -->\n'
        f'<aside class="obs-callout"{basis_attr} role="note" aria-label="A noticing about people with this name" '
        'style="margin:1.6rem 0 1.2rem;padding:1rem 1.3rem;background:linear-gradient(180deg,rgba(139,105,20,.05),rgba(139,105,20,.02));border-left:3px solid #8B6914;border-radius:0 4px 4px 0;font-size:1.02rem;line-height:1.65;color:#2A2A2A;font-family:\'Cormorant Garamond\',Georgia,serif;font-style:italic;">\n'
        f'  {sentence}\n'
        '</aside>\n'
        '<!-- OBS-CALLOUT:END -->\n'
    )


def main():
    slugs = load_canonicals()
    updated = 0
    skipped = 0
    no_life = 0
    samples = []
    from collections import Counter as C
    letter_dist = C()
    for slug in slugs:
        p = NAMES / slug / "index.html"
        if not p.is_file():
            continue
        text = p.read_text(encoding='utf-8')
        card = parse_namecard(text)
        letters = (card or {}).get('letter_breakdown') or []
        phrase, basis = choose_phrase(slug, letters)
        letter_dist[basis] += 1

        callout = build_callout(phrase, basis)

        # Remove any pre-existing callout (idempotent re-run replaces).
        if HAS_CALLOUT.search(text):
            text = OLD_CALLOUT_RE.sub('', text)

        m = LIFE_START_RE.search(text)
        if not m:
            no_life += 1
            continue
        insert_at = m.start()
        new_text = text[:insert_at] + callout + text[insert_at:]
        if new_text != p.read_text(encoding='utf-8'):
            p.write_text(new_text, encoding='utf-8')
            updated += 1
            if len(samples) < 20:
                samples.append((slug, basis, phrase))
        else:
            skipped += 1

    print(f"Updated: {updated}  skipped: {skipped}  no LIFE marker: {no_life}")
    print("Basis distribution (top 10):", letter_dist.most_common(10))
    print("\n--- 20 spot-check samples ---")
    for slug, basis, phrase in samples:
        print(f"  {slug:20s}  [{basis}]  -> {phrase}")


if __name__ == '__main__':
    main()
