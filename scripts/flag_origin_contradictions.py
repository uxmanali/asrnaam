#!/usr/bin/env python3
"""Flag name pages whose origin field contradicts the root section.

Reads each entry in names/names-index.json, compares the quick-answer
origin field (data-asr-field="origin") with explicit origin statements in
the root section ("Latin origin", "Persian/Urdu origin", "of Hebrew origin",
and the same shapes). Prints a report. Does not modify any page.

A slash or hyphen compound such as "Persian/Urdu origin" counts as both.
"Non-Arabic origin" is not read as an Arabic origin.

Usage:
    python3 scripts/flag_origin_contradictions.py
    python3 scripts/flag_origin_contradictions.py --root /path/to/repo
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html import unescape
from pathlib import Path

# Canonical origin groups. Words in the same group do not contradict.
GROUPS = {
    "arabic": {"arabic", "arab"},
    "persian": {"persian", "farsi", "iranian"},
    "turkic": {"turkish", "turkic", "ottoman"},
    "latin": {"latin"},
    "hebrew": {"hebrew"},
    "greek": {"greek"},
    "berber": {"berber", "amazigh"},
    "sanskrit": {"sanskrit"},
    "kurdish": {"kurdish"},
    "french": {"french"},
    "german": {"german", "germanic"},
    "english": {"english"},
    "spanish": {"spanish"},
    "italian": {"italian"},
    "aramaic": {"aramaic", "syriac"},
    "pashto": {"pashto", "pashtun"},
    "urdu": {"urdu"},
    "malay": {"malay", "indonesian"},
    "kazakh": {"kazakh"},
    "somali": {"somali"},
    "amharic": {"amharic"},
    "coptic": {"coptic"},
    "swahili": {"swahili"},
    "slavic": {"slavic", "russian"},
    "kyrgyz": {"kyrgyz"},
    "circassian": {"circassian"},
    "balochi": {"balochi"},
    "filipino": {"filipino"},
    "fulani": {"fulani"},
    "bambara": {"bambara"},
    "tatar": {"tatar"},
    "sindhi": {"sindhi"},
    "bosnian": {"bosnian"},
    "hausa": {"hausa"},
    "armenian": {"armenian"},
    "avestan": {"avestan"},
    "babylonian": {"babylonian"},
}

WORD_TO_GROUP = {word: group for group, words in GROUPS.items() for word in words}
ORIGIN_WORDS = sorted(WORD_TO_GROUP, key=len, reverse=True)
_WORD = r"(?:" + "|".join(ORIGIN_WORDS) + r")"
_COMPOUND = rf"{_WORD}(?:\s*[/\-]\s*{_WORD})*"
# Explicit origin claims only. "Non-Arabic origin" must not count as Arabic.
ORIGIN_CLAIM = re.compile(
    rf"(?<![\w-])(?<!non-)(?<!non )({_COMPOUND})\s+origin\b"
    rf"|\borigin\s*[:\-]\s*({_COMPOUND})\b"
    rf"|\b({_COMPOUND})\s+in\s+origin\b"
    rf"|\bof\s+({_COMPOUND})\s+origin\b",
    re.IGNORECASE,
)
ROOT_MARKED = re.compile(
    r"<!-- MEAN-ROOT:START -->(.*?)<!-- MEAN-ROOT:END -->",
    re.DOTALL,
)
ROOT_FALLBACK = re.compile(
    r'class="asr-v2-root".*?<div class="prose">(.*?)</div>',
    re.DOTALL,
)
TAG = re.compile(r"<[^>]+>")
SPACE = re.compile(r"\s+")


def groups_in_claim(text: str) -> set[str]:
    found: set[str] = set()
    for match in ORIGIN_CLAIM.finditer(text):
        chunk = next(group for group in match.groups() if group)
        for word in re.findall(_WORD, chunk, flags=re.IGNORECASE):
            found.add(WORD_TO_GROUP[word.lower()])
    return found


def field_groups(field: str) -> set[str]:
    # "non-Arabic origin" names the origin it is not.
    cleaned = re.sub(r"non[-\s]+", "", field, flags=re.IGNORECASE)
    found: set[str] = set()
    for word, group in sorted(WORD_TO_GROUP.items(), key=lambda item: -len(item[0])):
        if re.search(r"\b" + re.escape(word) + r"\b", cleaned, flags=re.IGNORECASE):
            found.add(group)
    return found


def root_text(html: str) -> str:
    match = ROOT_MARKED.search(html) or ROOT_FALLBACK.search(html)
    if not match:
        return ""
    text = TAG.sub(" ", match.group(1))
    return unescape(SPACE.sub(" ", text)).strip()


def collect(root: Path) -> list[dict]:
    index_path = root / "names" / "names-index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    flags: list[dict] = []
    for entry in index:
        slug = entry.get("s")
        if not slug:
            continue
        page = root / "names" / slug / "index.html"
        if not page.exists():
            continue
        html = page.read_text(encoding="utf-8", errors="replace")
        field_match = re.search(r'data-asr-field="origin">([^<]+)', html)
        if not field_match:
            continue
        field = unescape(field_match.group(1)).strip()
        claimed = field_groups(field)
        prose = root_text(html)
        stated = groups_in_claim(prose)
        if not claimed or not stated or (claimed & stated):
            continue
        flags.append({
            "slug": slug,
            "field": field,
            "root_origins": sorted(stated),
            "excerpt": prose[:220],
        })
    flags.sort(key=lambda item: item["slug"])
    return flags


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root (default: .)")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    flags = collect(root)
    print(f"Origin contradictions: {len(flags)}")
    print("Compared the origin field with explicit origin claims in the root section.")
    print("No pages were modified.")
    print()
    for item in flags:
        roots = ", ".join(item["root_origins"])
        print(f"{item['slug']}\torigin field: {item['field']}\troot text says: {roots}")
        print(f"    {item['excerpt']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
