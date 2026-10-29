#!/usr/bin/env python3
"""
AsrNaam Phase 2A audit scanner (A-04).

Runs 12 quality checks (C1-C12) across every canonical page in the repo
and writes outputs/audit-2a-<DATE>.md plus outputs/audit-2a.json.

Dependencies: Python 3 stdlib + beautifulsoup4.
Idempotent. Rerunnable. Zero em-dashes (U+2014) in this file or its output.

Usage:
    python3 scripts/audit_2a.py            # scan repo root
    python3 scripts/audit_2a.py --root .   # explicit root
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup, Comment
except Exception as e:
    print("ERROR: beautifulsoup4 is required (pip install beautifulsoup4):", e, file=sys.stderr)
    sys.exit(2)

# ---------------- configuration ----------------

CRITICAL_CHECKS = {"C3", "C4", "C5", "C6"}
CHECK_SEVERITY = {
    "C1": "High", "C2": "High", "C3": "Critical", "C4": "Critical",
    "C5": "Critical", "C6": "Critical", "C7": "High", "C8": "High",
    "C9": "High", "C10": "High", "C11": "Medium", "C12": "Medium",
}
CHECK_TITLES = {
    "C1": "Five weapons present",
    "C2": "Opening depth",
    "C3": "Truncated fields",
    "C4": "Internal IDs leaking",
    "C5": "Repeated sentences",
    "C6": "Letter consistency",
    "C7": "Implausible variants",
    "C8": "Unique metadata",
    "C9": "Boilerplate share",
    "C10": "Valid schema",
    "C11": "House style (em-dash)",
    "C12": "Consistent facts",
}

SCHEMA_ALLOWLIST = {"FAQPage", "BreadcrumbList", "Article", "WebPage",
                    "WebSite", "Organization", "Person", "ItemList",
                    "Question", "Answer", "ListItem", "ImageObject",
                    "BlogPosting", "Blog", "Thing",
                    "CollectionPage", "DefinedTerm", "SpeakableSpecification"}

EM_DASH = chr(0x2014)  # Build the character programmatically so this file contains zero literal em-dashes.

# Regex helpers
RE_TRUNC_END = re.compile(r"(?:…|\.\.\.)\s*$")
# Internal-ID pattern: lowercase word followed by -digits, or _<8+ alnum>.
# Exclude common hyphenated English + year patterns (post-1980, top-5, etc.).
RE_SLUG_ID1 = re.compile(r"\b[a-z]{2,}-\d{1,3}\b")
RE_SLUG_ID2 = re.compile(r"\b_[a-z0-9]{8,}\b")
_SLUG_PREFIX_STOP = {
    "top", "bottom", "step", "year", "chapter", "section", "part",
    "pre", "post", "mid", "sub", "no", "page", "lesson", "level",
    "day", "week", "month", "era", "age", "age-group", "class",
}
RE_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
RE_LIBSIZE = re.compile(r"\b2[, ]?45\d\+?\b")
RE_PH = re.compile(r"\bPh", re.IGNORECASE)  # per spec, "Ph" where "F" expected
RE_DOUBLE_VOWEL = re.compile(r"(ii|uu|oo)", re.IGNORECASE)
RE_NON_LATIN = re.compile(r"[^A-Za-z\s\-’'À-ɏ]")  # tolerate accented latin

# ---------------- discovery ----------------

def discover_pages(root: Path) -> list[Path]:
    """Return the list of canonical page paths to scan."""
    pages: list[Path] = []

    # Names from names-index.json (authoritative)
    idx_path = root / "names" / "names-index.json"
    if idx_path.exists():
        try:
            idx = json.loads(idx_path.read_text(encoding="utf-8"))
            for entry in idx:
                slug = entry.get("s") if isinstance(entry, dict) else None
                if not slug:
                    continue
                p = root / "names" / slug / "index.html"
                if p.exists():
                    pages.append(p)
        except Exception as e:
            print(f"WARN: could not parse names-index.json: {e}", file=sys.stderr)

    # Letters, aathaar, basaair, blog (filter out hub index pages at the section root)
    for section in ("letters", "aathaar", "basaair", "blog"):
        sec_dir = root / section
        if not sec_dir.exists():
            continue
        for sub in sorted(sec_dir.iterdir()):
            if not sub.is_dir():
                continue
            p = sub / "index.html"
            if p.exists():
                pages.append(p)

    return pages


# ---------------- parsing ----------------

def strip_scripts_styles(soup: BeautifulSoup) -> None:
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()


def extract_main_text(soup: BeautifulSoup) -> str:
    main = soup.find("main") or soup.find("article") or soup.body
    if main is None:
        return ""
    return main.get_text(" ", strip=True)


def extract_meta(soup: BeautifulSoup) -> tuple[str, str]:
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    md_tag = soup.find("meta", attrs={"name": "description"})
    md = (md_tag.get("content") or "").strip() if md_tag else ""
    return title, md


# ---------------- per-page checks ----------------

def check_page(path: Path, root: Path, meta_dupe: dict, lib_counter: collections.Counter,
                shingle_corpus: dict) -> dict:
    """Run all checks on one page. meta_dupe / lib_counter / shingle_corpus are
    accumulators updated here and finalised in a second pass."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    # Parse with the stdlib parser to keep dependencies at bs4 only.
    try:
        soup = BeautifulSoup(raw, "html.parser")
    except Exception as e:
        # Treat as C10 failure plus total scan failure
        return {
            "path": str(path.relative_to(root)),
            "parse_error": f"html.parser: {e}",
            "checks": {cid: False for cid in CHECK_TITLES},
            "details": {},
            "title": "", "meta_description": "",
        }

    is_name = "/names/" in path.as_posix()

    # Collect JSON-LD scripts BEFORE stripping scripts
    jsonld_scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    jsonld_blobs: list[dict | list] = []
    jsonld_parse_errors: list[str] = []
    for s in jsonld_scripts:
        txt = s.string or s.get_text() or ""
        if not txt.strip():
            jsonld_parse_errors.append("empty JSON-LD block")
            continue
        try:
            jsonld_blobs.append(json.loads(txt))
        except Exception as e:
            jsonld_parse_errors.append(str(e))

    title, meta_desc = extract_meta(soup)

    # Pre-grab variant-chip tokens before stripping scripts (chip classes are in body)
    variant_chip_tokens = [t.get_text(" ", strip=True)
                            for t in soup.select(".spelling-chip")]

    # Pre-grab related-name cards
    related_cards = soup.select(".related-card")

    # Pre-grab urdu section signal
    has_urdu = bool(
        soup.find(attrs={"data-asr-field": "urdu"}) or
        soup.find(class_="urdu-section") or
        soup.find(attrs={"lang": "ar", "dir": "rtl"})
    )

    # Pre-grab letter chip romans + letter-reading prose for C6
    letter_chip_romans = [el.get_text(" ", strip=True)
                           for el in soup.select(".asr-v2-letter .asr-v2-letter-roman")]
    iuh_prose = ""
    # MEAN-IUH:START ... :END block
    m = re.search(r"MEAN-IUH:START(.*?)MEAN-IUH:END", raw, re.DOTALL)
    if m:
        iuh_prose = BeautifulSoup(m.group(1), "html.parser").get_text(" ", strip=True)

    # First-paragraph for C2: within main content
    first_p = ""
    main_el = soup.find("main") or soup.find("article") or soup.body
    if main_el is not None:
        p = main_el.find("p")
        if p is not None:
            first_p = p.get_text(" ", strip=True)

    # Capture visible content fields for truncation check (C3)
    truncation_candidates: dict[str, str] = {}
    truncation_candidates["title"] = title
    truncation_candidates["meta_description"] = meta_desc
    for el in soup.find_all(attrs={"data-asr-field": True}):
        truncation_candidates[f"field:{el['data-asr-field']}"] = el.get_text(" ", strip=True)

    # Grab href values for C4 href-exclusion
    href_values = {a.get("href", "") for a in soup.find_all("a")}

    # Now strip scripts and styles to compute visible text
    strip_scripts_styles(soup)
    visible_text = extract_main_text(soup)
    full_visible_text = soup.get_text(" ", strip=True) if soup.body else visible_text

    # ---------- C1: five weapons ----------
    schema_types = set()
    def collect_types(obj):
        if isinstance(obj, dict):
            t = obj.get("@type")
            if isinstance(t, str):
                schema_types.add(t)
            elif isinstance(t, list):
                schema_types.update(x for x in t if isinstance(x, str))
            for v in obj.values():
                collect_types(v)
        elif isinstance(obj, list):
            for v in obj:
                collect_types(v)
    for b in jsonld_blobs:
        collect_types(b)

    # Count FAQ Q&A: look in FAQPage mainEntity
    faq_qcount = 0
    def count_faq(obj):
        nonlocal faq_qcount
        if isinstance(obj, dict):
            if obj.get("@type") == "FAQPage":
                me = obj.get("mainEntity") or []
                if isinstance(me, list):
                    faq_qcount = max(faq_qcount, len(me))
            for v in obj.values():
                count_faq(v)
        elif isinstance(obj, list):
            for v in obj:
                count_faq(v)
    for b in jsonld_blobs:
        count_faq(b)

    weapons_missing = []
    if is_name:
        if not ({"FAQPage", "BreadcrumbList", "Article"} <= schema_types):
            missing = {"FAQPage", "BreadcrumbList", "Article"} - schema_types
            weapons_missing.append(f"schema({','.join(sorted(missing))})")
        if faq_qcount < 6:
            weapons_missing.append(f"faq-q-count({faq_qcount})")
        if not variant_chip_tokens:
            weapons_missing.append("variant-chips")
        if not has_urdu:
            weapons_missing.append("urdu-section")
        if not related_cards:
            weapons_missing.append("related-cards")
    c1_fail = bool(weapons_missing) if is_name else False

    # ---------- C2: opening depth ----------
    c2_fail = is_name and (len(first_p) <= 200)

    # ---------- C3: truncated fields ----------
    c3_hits = []
    for key, val in truncation_candidates.items():
        if not val:
            continue
        if RE_TRUNC_END.search(val):
            c3_hits.append(key)
    c3_fail = bool(c3_hits)

    # ---------- C4: internal IDs leaking ----------
    c4_hits = []
    # Visible text: strip href values that happen to appear verbatim
    scan_text = visible_text
    for m1 in RE_SLUG_ID1.finditer(scan_text):
        tok = m1.group(0)
        prefix, _, numpart = tok.rpartition("-")
        # Skip 4+ digit tails (years) and common English hyphenated phrases
        if len(numpart) >= 4:
            continue
        if prefix in _SLUG_PREFIX_STOP:
            continue
        # If this exact token appears in any href attribute, treat as non-leak
        if any(tok in h for h in href_values):
            continue
        c4_hits.append(tok)
    for m2 in RE_SLUG_ID2.finditer(scan_text):
        tok = m2.group(0)
        if any(tok in h for h in href_values):
            continue
        c4_hits.append(tok)
    c4_fail = bool(c4_hits)

    # ---------- C5: repeated sentences ----------
    sentences = [s.strip() for s in RE_SENT_SPLIT.split(visible_text) if len(s.strip()) >= 30]
    sc = collections.Counter(sentences)
    c5_dupes = [s for s, n in sc.items() if n >= 2]
    c5_fail = bool(c5_dupes)

    # ---------- C6: letter consistency ----------
    c6_fail = False
    c6_detail = None
    if is_name and letter_chip_romans:
        chip_set = {r.strip() for r in letter_chip_romans if r.strip()}
        # Check which chip tokens appear in the IUH prose
        if iuh_prose:
            missing_in_prose = {r for r in chip_set
                                 if not re.search(r"\b" + re.escape(r) + r"\b", iuh_prose, re.IGNORECASE)}
            if missing_in_prose:
                c6_fail = True
                c6_detail = sorted(missing_in_prose)
        else:
            # No IUH prose yet chips exist: letter-reading content is missing
            c6_fail = True
            c6_detail = ["no-iuh-prose"]

    # ---------- C7: implausible variants ----------
    c7_hits = []
    for tok in variant_chip_tokens:
        # Strip chip-state glyphs the UI appends (checkmark on the current chip, etc.)
        t = re.sub(r"[✓✔☑•\*]", "", tok).strip()
        if not t:
            continue
        # Non-standard Latin: any char outside allowed set
        if RE_NON_LATIN.search(t):
            c7_hits.append(f"{t}:nonlatin")
            continue
        if RE_PH.search(t):
            c7_hits.append(f"{t}:Ph")
            continue
        if RE_DOUBLE_VOWEL.search(t):
            c7_hits.append(f"{t}:doubled-vowel")
    c7_fail = bool(c7_hits)

    # ---------- C8: unique metadata (accumulator) ----------
    key_title = title.strip().lower()
    key_md = meta_desc.strip().lower()
    meta_dupe["title"][key_title].append(str(path.relative_to(root)))
    meta_dupe["md"][key_md].append(str(path.relative_to(root)))
    # Resolved in second pass

    # ---------- C9: boilerplate share (accumulator) ----------
    # Compute 7-gram shingles from visible_text
    words = re.findall(r"[A-Za-z0-9]+", visible_text.lower())
    shingles = set()
    N = 7
    for i in range(len(words) - N + 1):
        shingles.add(" ".join(words[i:i+N]))
    shingle_corpus["per_page"][str(path.relative_to(root))] = shingles
    for sh in shingles:
        shingle_corpus["df"][sh] = shingle_corpus["df"].get(sh, 0) + 1

    # ---------- C10: valid schema ----------
    c10_hits = list(jsonld_parse_errors)
    unknown_types = schema_types - SCHEMA_ALLOWLIST
    if unknown_types:
        c10_hits.append(f"unknown-types:{','.join(sorted(unknown_types))}")
    c10_fail = bool(c10_hits)

    # ---------- C11: em-dash ----------
    c11_count = full_visible_text.count(EM_DASH)
    c11_fail = c11_count > 0

    # ---------- C12: consistent facts (accumulator) ----------
    lib_hits = RE_LIBSIZE.findall(full_visible_text)
    for v in lib_hits:
        lib_counter[v.replace(" ", ",")] += 1

    return {
        "path": str(path.relative_to(root)),
        "parse_error": None,
        "title": title,
        "meta_description": meta_desc,
        "is_name": is_name,
        "checks": {
            "C1": c1_fail, "C2": c2_fail, "C3": c3_fail, "C4": c4_fail,
            "C5": c5_fail, "C6": c6_fail, "C7": c7_fail,
            "C8": False, "C9": False,  # resolved in second pass
            "C10": c10_fail, "C11": c11_fail,
            "C12": False,  # resolved in second pass
        },
        "details": {
            "C1": weapons_missing,
            "C2": {"first_p_len": len(first_p)} if c2_fail else None,
            "C3": c3_hits,
            "C4": c4_hits[:10],
            "C5": [s[:120] for s in c5_dupes[:5]],
            "C6": c6_detail,
            "C7": c7_hits[:10],
            "C10": c10_hits,
            "C11": c11_count if c11_fail else 0,
            "_lib_hits": lib_hits,
        },
    }


# ---------------- second pass (cross-page) ----------------

def finalise(results: list[dict], meta_dupe: dict, lib_counter: collections.Counter,
              shingle_corpus: dict, total: int) -> None:
    # C8: duplicate titles / meta descriptions
    dup_titles = {k: v for k, v in meta_dupe["title"].items() if k and len(v) > 1}
    dup_mds = {k: v for k, v in meta_dupe["md"].items() if k and len(v) > 1}
    dup_title_paths = {p for paths in dup_titles.values() for p in paths}
    dup_md_paths = {p for paths in dup_mds.values() for p in paths}

    # C9: boilerplate share -> flag pages where >=50% of shingles appear in >=50% of pages
    half = max(2, total // 2)
    boilerplate = {sh for sh, df in shingle_corpus["df"].items() if df >= half}
    for r in results:
        if r.get("parse_error"):
            continue
        shingles = shingle_corpus["per_page"].get(r["path"], set())
        if not shingles:
            r["checks"]["C9"] = False
            continue
        unique = shingles - boilerplate
        ratio = len(unique) / len(shingles) if shingles else 1.0
        r["details"]["C9"] = round(ratio, 3)
        r["checks"]["C9"] = ratio < 0.5

    # C12: consistent facts - most common library-size token
    most_common = lib_counter.most_common(1)
    canonical_lib = most_common[0][0] if most_common else None
    for r in results:
        hits = r["details"].get("_lib_hits") or []
        if not hits:
            continue
        bad = [h for h in hits if h.replace(" ", ",") != canonical_lib]
        if bad:
            r["checks"]["C12"] = True
            r["details"]["C12"] = {"found": sorted(set(hits)), "canonical": canonical_lib}

    # C8 attach
    for r in results:
        if r["path"] in dup_title_paths or r["path"] in dup_md_paths:
            r["checks"]["C8"] = True
            r["details"]["C8"] = {
                "title_dup": r["path"] in dup_title_paths,
                "md_dup": r["path"] in dup_md_paths,
            }

    # Clean the internal field
    for r in results:
        r["details"].pop("_lib_hits", None)


# ---------------- reporting ----------------

def build_reports(results: list[dict], out_md: Path, out_json: Path, date_str: str) -> dict:
    total = len(results)
    per_check = {cid: 0 for cid in CHECK_TITLES}
    critical_pages = []
    all_fail_counts = []
    for r in results:
        fails_critical = False
        fail_count = 0
        for cid, failed in r["checks"].items():
            if failed:
                per_check[cid] += 1
                fail_count += 1
                if cid in CRITICAL_CHECKS:
                    fails_critical = True
        if r.get("parse_error"):
            # Count parse errors as C10
            per_check["C10"] += 0  # already counted inside check
        all_fail_counts.append((r["path"], fail_count,
                                 sum(1 for c in CRITICAL_CHECKS if r["checks"].get(c))))
        if fails_critical:
            critical_pages.append(r)

    crit_count = len(critical_pages)
    crit_rate = (crit_count / total * 100.0) if total else 0.0

    # Top-20 offending pages
    all_fail_counts.sort(key=lambda t: (-t[2], -t[1], t[0]))
    top20 = all_fail_counts[:20]

    summary = {
        "generated_at": dt.datetime.utcnow().isoformat() + "Z",
        "date": date_str,
        "total_pages": total,
        "critical_failures": crit_count,
        "critical_defect_rate_pct": round(crit_rate, 2),
        "per_check": per_check,
        "top_20_offending": [
            {"path": p, "total_fails": tf, "critical_fails": cf}
            for p, tf, cf in top20
        ],
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(
        {"summary": summary, "results": results}, indent=2, ensure_ascii=False
    ), encoding="utf-8")

    # Markdown report (no em-dashes anywhere)
    lines: list[str] = []
    lines.append(f"# AsrNaam Phase 2A Audit, {date_str}")
    lines.append("")
    lines.append("Scanner: `scripts/audit_2a.py` (A-04). 12 automated quality checks (C1-C12).")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total canonical pages scanned: **{total}**")
    lines.append(f"- Pages failing at least one Critical check (C3, C4, C5, C6): **{crit_count}**")
    lines.append(f"- Critical defect rate: **{crit_rate:.2f}%**")
    lines.append("")
    lines.append("## Per-check tally")
    lines.append("")
    lines.append("| ID | Check | Severity | Failing pages |")
    lines.append("|----|-------|----------|---------------|")
    for cid in sorted(CHECK_TITLES.keys(), key=lambda s: int(s[1:])):
        lines.append(f"| {cid} | {CHECK_TITLES[cid]} | {CHECK_SEVERITY[cid]} | {per_check[cid]} |")
    lines.append("")
    lines.append("## Top 20 offending pages")
    lines.append("")
    lines.append("| Rank | Path | Critical fails | Total fails |")
    lines.append("|------|------|----------------|-------------|")
    for i, (p, tf, cf) in enumerate(top20, 1):
        lines.append(f"| {i} | `{p}` | {cf} | {tf} |")
    lines.append("")
    lines.append("## Critical defects: pending for user")
    lines.append("")
    if not critical_pages:
        lines.append("No pages failed any Critical check.")
    else:
        lines.append(f"Top {min(10, len(critical_pages))} of {len(critical_pages)} pages failing one or more Critical checks:")
        lines.append("")
        for r in critical_pages[:10]:
            lines.append(f"### `{r['path']}`")
            for cid in sorted(CRITICAL_CHECKS):
                if r["checks"].get(cid):
                    detail = r["details"].get(cid)
                    lines.append(f"- **{cid} {CHECK_TITLES[cid]}**: {detail}")
            lines.append("")
    lines.append("## Quality gate rule")
    lines.append("")
    lines.append("No batch of pages ships with open Critical defects (C3, C4, C5, C6). Rerun this scanner before every batch upload.")
    lines.append("")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines), encoding="utf-8")
    # Belt-and-braces: fail hard if an em-dash leaked into the report.
    if EM_DASH in out_md.read_text(encoding="utf-8"):
        raise RuntimeError("em-dash found in report output; aborting")
    return summary


# ---------------- main ----------------

def main() -> int:
    ap = argparse.ArgumentParser(description="AsrNaam Phase 2A audit scanner (A-04)")
    ap.add_argument("--root", default=".", help="Repo root (default: cwd)")
    ap.add_argument("--date", default=None, help="Date tag for the report filename (YYYY-MM-DD)")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    date_str = args.date or dt.date.today().isoformat()

    pages = discover_pages(root)
    if not pages:
        print("No pages discovered. Is --root correct?", file=sys.stderr)
        return 1

    print(f"Scanning {len(pages)} pages...", file=sys.stderr)
    results: list[dict] = []
    meta_dupe = {"title": collections.defaultdict(list), "md": collections.defaultdict(list)}
    lib_counter: collections.Counter = collections.Counter()
    shingle_corpus = {"per_page": {}, "df": {}}

    for i, p in enumerate(pages, 1):
        try:
            r = check_page(p, root, meta_dupe, lib_counter, shingle_corpus)
        except Exception as e:
            r = {
                "path": str(p.relative_to(root)),
                "parse_error": f"scan-exception: {e}",
                "checks": {cid: (cid == "C10") for cid in CHECK_TITLES},
                "details": {"C10": [f"scan-exception: {e}"]},
                "title": "", "meta_description": "",
            }
        results.append(r)
        if i % 250 == 0:
            print(f"  ... {i}/{len(pages)}", file=sys.stderr)

    finalise(results, meta_dupe, lib_counter, shingle_corpus, len(pages))

    out_md = root / "outputs" / f"audit-2a-{date_str}.md"
    out_json = root / "outputs" / "audit-2a.json"
    summary = build_reports(results, out_md, out_json, date_str)

    print(f"Wrote {out_md}", file=sys.stderr)
    print(f"Wrote {out_json}", file=sys.stderr)
    print(json.dumps({
        "total": summary["total_pages"],
        "critical_failures": summary["critical_failures"],
        "critical_defect_rate_pct": summary["critical_defect_rate_pct"],
        "per_check": summary["per_check"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
