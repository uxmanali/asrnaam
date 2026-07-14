#!/usr/bin/env python3
"""Generate the Section-3 "What This Reading Says About You" synthesis paragraph
for each canonical name page. Writes the result inside a
<!-- MEAN-SYNTHESIS:START --> ... <!-- MEAN-SYNTHESIS:END --> marker on the
English canonical page (does not touch AR/UR mirrors — those pull the EN
synthesis via the layout script's mirror translation stub).

Voice: reverent + accessible. 3-4 sentences. Zero em-dashes anywhere.
"""

from __future__ import annotations
import argparse
import pathlib
import re
import sys
from typing import Optional, List, Tuple

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKIP_LOG = pathlib.Path(__file__).parent / "section3-skipped.log"

# ---------------------------------------------------------------------------
# Arabic letter → element / divine-name mapping (same as redesign_layout.py)
# ---------------------------------------------------------------------------
ARABIC_TO_ELEMENT = {
    "ا": "Fire",  "أ": "Fire", "إ": "Fire", "آ": "Fire",
    "ه": "Fire",  "ط": "Fire",  "م": "Fire",  "ف": "Fire",  "ش": "Fire",  "ذ": "Fire",
    "ب": "Earth",  "پ": "Earth",  "و": "Earth",  "ؤ": "Earth",
    "ي": "Earth",  "ى": "Earth",  "ئ": "Earth",  "ی": "Earth",
    "ن": "Earth",  "ص": "Earth",  "ت": "Earth",  "ة": "Earth",  "ض": "Earth",
    "ج": "Air",  "چ": "Air",  "ز": "Air",  "ژ": "Air",
    "ك": "Air",  "ک": "Air",  "گ": "Air",
    "س": "Air",  "ق": "Air",  "ث": "Air",  "ظ": "Air",
    "د": "Water",  "ح": "Water",  "ل": "Water",  "ع": "Water",
    "ر": "Water",  "خ": "Water",  "غ": "Water",
}
ARABIC_TO_DIVINE_PHRASE = {
    "ا": "Al-Ahad, the One,",
    "أ": "Al-Ahad, the One,",
    "إ": "Al-Ahad, the One,",
    "آ": "Al-Ahad, the One,",
    "ه": "Al-Hadi, the Guide,",
    "ط": "Al-Lateef, the Subtle,",
    "م": "Al-Mu'min, the Faithful,",
    "ف": "Al-Fattah, the Opener,",
    "ش": "Al-Shakur, the Appreciative,",
    "ذ": "Dhul-Jalal, the Lord of Majesty,",
    "ب": "Al-Batin, the Interior,",
    "پ": "Al-Batin, the Interior,",
    "و": "Al-Wadud, the Loving,",
    "ؤ": "Al-Wadud, the Loving,",
    "ي": "Al-Qayyum, the Self-Sustaining,",
    "ى": "Al-Qayyum, the Self-Sustaining,",
    "ی": "Al-Qayyum, the Self-Sustaining,",
    "ئ": "Al-Qayyum, the Self-Sustaining,",
    "ن": "Al-Nur, the Light,",
    "ص": "Al-Samad, the Eternal Refuge,",
    "ت": "Al-Tawwab, the Relenting,",
    "ة": "Al-Tawwab, the Relenting,",
    "ض": "Al-Darr, the Tester,",
    "ج": "Al-Jami, the Gatherer,",
    "چ": "Al-Jami, the Gatherer,",
    "ز": "Al-Zahir, the Manifest,",
    "ژ": "Al-Zahir, the Manifest,",
    "ك": "Al-Karim, the Generous,",
    "ک": "Al-Karim, the Generous,",
    "گ": "Al-Karim, the Generous,",
    "س": "Al-Sami, the All-Hearing,",
    "ق": "Al-Qadir, the All-Capable,",
    "ث": "Al-Thabit, the Firm,",
    "ظ": "Al-Dhahir, the Outer Manifest,",
    "د": "Al-Dayyan, the Judge,",
    "ح": "Al-Hamid, the Praiseworthy,",
    "ل": "Al-Latif, the Gracious,",
    "ع": "Al-Alim, the All-Knowing,",
    "ر": "Al-Rahman, the Merciful,",
    "خ": "Al-Khabir, the Aware,",
    "غ": "Al-Ghani, the Self-Sufficient,",
}
# Short quality phrase per divine name, for the "carried as X" clause
DIVINE_TO_QUALITY = {
    "Al-Ahad":       "a singular, undivided presence",
    "Al-Hadi":       "the animating breath that guides others through",
    "Al-Lateef":     "a subtle, sun-warm attention",
    "Al-Mu'min":     "a faith others can lean on",
    "Al-Fattah":     "the will to open what was closed",
    "Al-Shakur":     "a way of noticing and honouring small kindnesses",
    "Dhul-Jalal":    "an ancient, weighty seriousness",
    "Al-Batin":      "an interior life that runs deeper than what is shown",
    "Al-Wadud":      "a steady, connective love",
    "Al-Qayyum":     "a self-holding constancy",
    "Al-Nur":        "a light that steadies the room",
    "Al-Samad":      "the eternal reliability others rest against",
    "Al-Tawwab":     "the readiness to return and be returned to",
    "Al-Darr":       "the strength to hold hard truths without flinching",
    "Al-Jami":       "the ability to gather people around what matters",
    "Al-Zahir":      "a clarity that shows itself without needing to shout",
    "Al-Karim":      "an open-handed generosity of spirit",
    "Al-Sami":       "the alertness to hear what is not being said aloud",
    "Al-Qadir":      "a capable, unruffled competence",
    "Al-Thabit":     "the firmness that outlasts weather",
    "Al-Dhahir":     "a truth that eventually surfaces",
    "Al-Dayyan":     "the fair judgment that keeps a household whole",
    "Al-Hamid":      "the trust to receive genuine praise, not flattery",
    "Al-Latif":      "an unshowy kindness that reaches the tender parts",
    "Al-Alim":       "a knowing that predates study",
    "Al-Rahman":     "mercy that keeps moving even when tested",
    "Al-Khabir":     "an aware, quietly informed presence",
    "Al-Ghani":      "an inner sufficiency that does not need external filling",
}

DIACRITIC_RE = re.compile(r"[ً-ٰٟۖ-ۭ‌‍‎‏]")

# Extract Arabic name string from a page
ARABIC_FIELD_RE = re.compile(r'<span[^>]*data-asr-field="arabic"[^>]*>([^<]+)</span>')
ARABIC_NAME_HERO_RE = re.compile(r'<div class="arabic-name"[^>]*>([^<]+)</div>')
ROMAN_NAME_TITLE_RE = re.compile(r'<h1><em>([^<]+)</em>')

# Marker regex
MEAN_SYNTHESIS_RE = re.compile(
    r"<!--\s*MEAN-SYNTHESIS:START\s*-->(.*?)<!--\s*MEAN-SYNTHESIS:END\s*-->",
    re.DOTALL
)
MEAN_IUH_END_RE = re.compile(r"<!--\s*MEAN-IUH:END\s*-->")
# Also allow insertion right after MEAN-ROOT:END if MEAN-IUH is absent
MEAN_ROOT_END_RE = re.compile(r"<!--\s*MEAN-ROOT:END\s*-->")


def extract_roman_name(html: str) -> str:
    m = ROMAN_NAME_TITLE_RE.search(html)
    if m:
        return re.sub(r'</?[^>]+>', '', m.group(1)).strip().rstrip(".,")
    return ""

def extract_arabic_letters(html: str) -> List[str]:
    for pat in (ARABIC_FIELD_RE, ARABIC_NAME_HERO_RE):
        m = pat.search(html)
        if not m:
            continue
        raw = m.group(1).strip()
        cleaned = DIACRITIC_RE.sub("", raw)
        letters = [ch for ch in cleaned if ch in ARABIC_TO_ELEMENT]
        if letters:
            return letters
    return []

def element_distribution(letters: List[str]) -> Tuple[str, dict]:
    """Return (pattern_key, counts). pattern_key is one of:
       dominant-fire, dominant-earth, dominant-air, dominant-water,
       balanced-fire-earth, balanced-fire-air, balanced-fire-water,
       balanced-earth-air, balanced-earth-water, balanced-air-water,
       mixed
    """
    counts = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    for ch in letters:
        counts[ARABIC_TO_ELEMENT[ch]] += 1
    total = sum(counts.values())
    if total == 0:
        return "mixed", counts
    ranked = sorted(counts.items(), key=lambda kv: -kv[1])
    top_el, top_ct = ranked[0]
    top_share = top_ct / total
    if top_share >= 0.6:
        return f"dominant-{top_el.lower()}", counts
    # balanced if top-two together are ≥ 80% and each ≥ 25%
    second_el, second_ct = ranked[1]
    if second_ct > 0 and (top_ct + second_ct) / total >= 0.8 and second_ct / total >= 0.25:
        pair = sorted([top_el.lower(), second_el.lower()])
        return f"balanced-{pair[0]}-{pair[1]}", counts
    return "mixed", counts


def pick_anchor_letters(letters: List[str]) -> List[str]:
    """Choose 1-2 letters whose divine names anchor the synthesis:
    the first letter, plus the most-repeated letter if different.
    """
    if not letters:
        return []
    picks = [letters[0]]
    counts = {}
    for ch in letters:
        counts[ch] = counts.get(ch, 0) + 1
    most = max(counts.items(), key=lambda kv: kv[1])[0]
    if most != letters[0]:
        picks.append(most)
    elif len(letters) >= 2 and letters[-1] != letters[0]:
        picks.append(letters[-1])
    return picks


# Template family: one per distribution pattern. Slots: {name},
# {anchor1_phrase}, {anchor1_quality}, {anchor2_phrase}, {anchor2_quality},
# {close}. The {close} sentence is chosen from a small per-name variant pool
# (deterministic by name hash) so pages with the same element distribution
# do not read identically. NO em-dashes anywhere. Only commas, semicolons,
# and periods.

CLOSE_VARIANTS = {
    "dominant-fire":     [
        "A person named {name} is likely to warm the rooms they enter and to lead by lit example.",
        "A person named {name} tends to bring warmth to a room and light to a decision.",
        "A person named {name} carries the kind of fire people gather around, not the kind that burns them.",
    ],
    "dominant-earth":    [
        "A person named {name} tends to be a settled place others return to.",
        "A person named {name} is the household others rest against without noticing they are resting.",
        "A person named {name} builds ground under other people's lives.",
    ],
    "dominant-air":      [
        "A person named {name} often catches what others miss.",
        "A person named {name} tends to name the thing everyone else was circling.",
        "A person named {name} moves through their days with a light, alert step.",
    ],
    "dominant-water":    [
        "A person named {name} carries the compassion of a river that keeps going.",
        "A person named {name} tends to be the safe place people bring their harder feelings to.",
        "A person named {name} holds others without asking them to be smaller.",
    ],
    "balanced-air-fire": [
        "A person named {name} tends to shape the direction others follow.",
        "A person named {name} is a rare mix of vision and momentum.",
        "A person named {name} tends to point at the road and take the first step.",
    ],
    "balanced-earth-water": [
        "A person named {name} holds their people through seasons.",
        "A person named {name} is the family's slow heart.",
        "A person named {name} keeps a home even in weather.",
    ],
    "balanced-fire-water": [
        "A person named {name} contains more than they show.",
        "A person named {name} runs deep water under a steady flame.",
        "A person named {name} is quieter than their fire suggests, and hotter than their calm implies.",
    ],
    "balanced-air-earth": [
        "A person named {name} is a rare kind of practical intelligence.",
        "A person named {name} builds what they have first thought all the way through.",
        "A person named {name} tends to be trusted with plans and with hands.",
    ],
    "balanced-earth-fire": [
        "A person named {name} tends to build things that outlast them.",
        "A person named {name} is the kind of person a village grows around.",
        "A person named {name} plants what their fire has cleared.",
    ],
    "balanced-air-water": [
        "A person named {name} is often the one people can be honest with.",
        "A person named {name} tends to make room for what is difficult to say.",
        "A person named {name} listens with the whole of themselves.",
    ],
    "mixed":             [
        "A person named {name} is many things at once, and gets to choose which shows up when.",
        "A person named {name} lives with more inside them than any one word can hold.",
        "A person named {name} carries a full weather system inside a single quiet chest.",
    ],
}

def _pick_close(pattern, name, letters=""):
    variants = CLOSE_VARIANTS.get(pattern, ["A person named {name} carries this reading in a way only they can."])
    # Mix name + Arabic letter sequence into a position-weighted hash so anagrams,
    # permutations, or same-pattern-but-different-name pages diverge.
    seed = 0
    src = name + "|" + "".join(letters)
    for c in src:
        seed = (seed * 131 + ord(c)) & 0xFFFFFFF
    return variants[seed % len(variants)]

TEMPLATES = {
    "dominant-fire": (
        "The letters in {name} cluster around fire, the element of will, warmth, and forward motion. "
        "This is a name that leans toward decisiveness and radiance, with the courage to begin what others hesitate to. "
        "Threaded through it is {anchor1_phrase} carried by a person as {anchor1_quality}. "
        "{close}"
    ),
    "dominant-earth": (
        "{name} is grounded in earth, the element of stability, patience, and quiet holding. "
        "The letters ask their bearer to be reliable rather than showy, to keep the household of the heart in order. "
        "Stitched through this reading is {anchor1_phrase} meaning the person carries {anchor1_quality}. "
        "{close}"
    ),
    "dominant-air": (
        "Air runs through {name}, the element of insight, breath, and swift understanding. "
        "This is a name that asks its bearer to notice quickly, speak clearly, and move light. "
        "Surfacing in the reading is {anchor1_phrase} giving the bearer {anchor1_quality}. "
        "{close}"
    ),
    "dominant-water": (
        "Water pools in {name}, the element of mercy, feeling, and receptive depth. "
        "The letters ask their bearer to hold others without hardening, to be a well and not a wall. "
        "Anchoring this reading is {anchor1_phrase} calling the person toward {anchor1_quality}. "
        "{close}"
    ),
    "balanced-air-fire": (
        "{name}'s letters bring fire and air together, the elements of will and insight, courage and clarity. "
        "A visionary drive lives inside this name, a person who both sees and moves. "
        "Written across it is {anchor1_phrase} carried by the bearer as {anchor1_quality}, joined by {anchor2_phrase} adding {anchor2_quality}. "
        "{close}"
    ),
    "balanced-earth-water": (
        "{name} weaves earth and water, the elements of steadiness and mercy, patience and feeling. "
        "The person is asked to be both root and river, a slow, sheltering presence. "
        "Running through the reading is {anchor1_phrase} meaning the bearer is trusted with {anchor1_quality}, joined by {anchor2_phrase} carried as {anchor2_quality}. "
        "{close}"
    ),
    "balanced-fire-water": (
        "{name} carries fire and water together, the two most different elements, will and mercy in one hand. "
        "This is a person of intense inner weather, capable of both flame and calm depth. "
        "Sitting inside the reading is {anchor1_phrase} giving the bearer {anchor1_quality}, softened by {anchor2_phrase} carried as {anchor2_quality}. "
        "{close}"
    ),
    "balanced-air-earth": (
        "{name} holds earth and air in even measure, grounded body and quick mind. "
        "The letters ask their bearer to think without floating away, and to build without slowing down. "
        "Weaving through the reading is {anchor1_phrase} offering the bearer {anchor1_quality}. "
        "{close}"
    ),
    "balanced-earth-fire": (
        "{name} joins fire to earth, the will that decides with the patience that lasts. "
        "This is a name that asks its bearer to burn steadily rather than in bursts, and to plant what the fire has cleared. "
        "Running through the reading is {anchor1_phrase} carried as {anchor1_quality}, and beside it {anchor2_phrase} adding {anchor2_quality}. "
        "{close}"
    ),
    "balanced-air-water": (
        "{name} brings air and water together, the elements of clear seeing and feeling deeply. "
        "The bearer is asked to name what is felt without cooling it, and to feel what is thought without losing it. "
        "Anchoring the reading is {anchor1_phrase} meaning the person carries {anchor1_quality}. "
        "{close}"
    ),
    "mixed": (
        "{name}'s letters draw from many elements at once, a full palette, not a single note. "
        "This is a name that asks its bearer to hold contradictions gracefully: warmth and steadiness, movement and depth. "
        "Running through the reading is {anchor1_phrase} carried by a person as {anchor1_quality}. "
        "{close}"
    ),
}


def divine_name_key(arabic_char: str) -> str:
    """Return the divine name key (e.g. Al-Mu'min) for a letter."""
    phrase = ARABIC_TO_DIVINE_PHRASE.get(arabic_char, "")
    if not phrase:
        return ""
    # phrase is "Al-Xxx, the Yyy," → key is the part before ,
    return phrase.split(",")[0]


def synthesize(name: str, letters: List[str]) -> Optional[str]:
    if not letters or len(letters) < 2:
        return None
    pattern, _ = element_distribution(letters)
    tpl = TEMPLATES.get(pattern)
    if tpl is None:
        return None
    anchors = pick_anchor_letters(letters)
    if not anchors:
        return None
    anchor1_char = anchors[0]
    anchor1_phrase = ARABIC_TO_DIVINE_PHRASE.get(anchor1_char, "")
    anchor1_key = divine_name_key(anchor1_char)
    anchor1_quality = DIVINE_TO_QUALITY.get(anchor1_key, "")
    if not (anchor1_phrase and anchor1_quality):
        return None
    slots = dict(
        name=name,
        anchor1_phrase=anchor1_phrase,
        anchor1_quality=anchor1_quality,
        close=_pick_close(pattern, name, letters).format(name=name),
    )
    if "{anchor2_phrase}" in tpl:
        if len(anchors) < 2:
            # collapse to a single-anchor variant by dropping the joined clause
            tpl = re.sub(r", joined by \{anchor2_phrase\} adding \{anchor2_quality\}", "", tpl)
            tpl = re.sub(r", softened by \{anchor2_phrase\} carried as \{anchor2_quality\}", "", tpl)
        else:
            anchor2_char = anchors[1]
            slots["anchor2_phrase"] = ARABIC_TO_DIVINE_PHRASE.get(anchor2_char, "")
            slots["anchor2_quality"] = DIVINE_TO_QUALITY.get(divine_name_key(anchor2_char), "")
            if not (slots["anchor2_phrase"] and slots["anchor2_quality"]):
                tpl = re.sub(r", joined by \{anchor2_phrase\} adding \{anchor2_quality\}", "", tpl)
                tpl = re.sub(r", softened by \{anchor2_phrase\} carried as \{anchor2_quality\}", "", tpl)
                slots.pop("anchor2_phrase", None)
                slots.pop("anchor2_quality", None)
    prose = tpl.format(**slots)
    # Defensive: strip any em-dashes that snuck in
    prose = prose.replace("—", ",").replace("—", ",")
    return prose


def apply_synthesis(html: str) -> Optional[str]:
    name = extract_roman_name(html)
    letters = extract_arabic_letters(html)
    if not name or not letters:
        return None
    prose = synthesize(name, letters)
    if not prose:
        return None
    block_inner = f'\n<div class="prose asr-v2-synthesis-prose"><p>{prose}</p></div>\n'
    marker = f'<!-- MEAN-SYNTHESIS:START -->{block_inner}<!-- MEAN-SYNTHESIS:END -->'

    if MEAN_SYNTHESIS_RE.search(html):
        return MEAN_SYNTHESIS_RE.sub(marker, html, count=1)

    # Insert right after MEAN-IUH:END, or after MEAN-ROOT:END as fallback
    m = MEAN_IUH_END_RE.search(html)
    if not m:
        m = MEAN_ROOT_END_RE.search(html)
    if not m:
        return None
    insertion = m.end()
    return html[:insertion] + "\n" + marker + "\n" + html[insertion:]


def process_slug(slug: str) -> str:
    en_path = ROOT / "names" / slug / "index.html"
    if not en_path.exists():
        return "no page"
    html = en_path.read_text(encoding="utf-8")
    new_html = apply_synthesis(html)
    if new_html is None:
        with SKIP_LOG.open("a", encoding="utf-8") as f:
            f.write(f"{slug}\n")
        return "skipped"
    if new_html == html:
        return "unchanged"
    en_path.write_text(new_html, encoding="utf-8")
    return "written"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if args.all:
        slugs = sorted(p.name for p in (ROOT / "names").iterdir() if p.is_dir())
    else:
        slugs = args.slugs
    if not slugs:
        print("usage: generate_section3.py <slug> [<slug>...]  or  --all", file=sys.stderr)
        sys.exit(2)
    for s in slugs:
        r = process_slug(s)
        print(f"{s:<20} {r}")


if __name__ == "__main__":
    main()
