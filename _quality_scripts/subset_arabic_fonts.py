#!/usr/bin/env python3
"""
Subset the self-hosted Arabic woff2 faces to the Arabic codepoints actually
used across the site, plus the OpenType layout features required for Arabic
shaping. Reduces Amiri 400/700 from ~100KB+ each to ~48KB each, and Noto
Naskh Arabic 400 from 94KB to ~22KB.

Requires: pip install fonttools brotli
Run from the repo root: python3 _quality_scripts/subset_arabic_fonts.py
"""
import re, shutil, subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FONTS = REPO / "fonts"
ARABIC = re.compile(r'[؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-ﻼ]')


def collect_codepoints():
    cps = set()
    for p in REPO.rglob("*.html"):
        if "/.git/" in str(p) or "/_quality_scripts/" in str(p):
            continue
        t = p.read_text(encoding='utf-8', errors='ignore')
        cps.update(ARABIC.findall(t))
    return sorted(cps)


def subset_face(filename, unicodes):
    src = FONTS / filename
    if not src.is_file():
        return
    out = src.with_suffix(".subset.woff2")
    cmd = [
        "pyftsubset", str(src),
        "--unicodes=" + unicodes,
        "--layout-features=kern,liga,calt,clig,rlig,rclt,ccmp,init,medi,fina,isol,locl,mark,mkmk",
        "--flavor=woff2",
        "--output-file=" + str(out),
        "--no-hinting",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FAIL {filename}: {r.stderr[-300:]}")
        return
    old, new = src.stat().st_size, out.stat().st_size
    print(f"  {filename}: {old} -> {new} bytes ({100*new/old:.1f}%)")
    shutil.move(out, src)


def main():
    cps = collect_codepoints()
    print(f"Site uses {len(cps)} unique Arabic codepoints")
    uni = ",".join(f"U+{ord(c):04X}" for c in cps)
    # Pad with a few Latin basics for mixed-content fallback
    uni += ",U+0020,U+002E,U+002D,U+0028,U+0029"
    for f in ("amiri-400.woff2", "amiri-700.woff2",
              "noto-naskh-arabic-400.woff2"):
        subset_face(f, uni)


if __name__ == "__main__":
    main()
