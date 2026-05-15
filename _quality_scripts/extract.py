"""
Extract per-canonical fields into /tmp/work-quality/quality-tracker.csv.
"""
import os, re, json, csv, html
from pathlib import Path

REPO = Path("/tmp/work-quality/asrnaam")
NAMES_DIR = REPO / "names"
OUT_CSV = Path("/tmp/work-quality/quality-tracker.csv")

PILLARS = {"boys","girls","by-letter","by-meaning","by-region","quranic"}

ASR_FIELD = re.compile(r'data-asr-field="([^"]+)">([^<]*)<')
ASR_NAMECARD_RE = re.compile(r'<script[^>]*id="asr-namecard"[^>]*>(.*?)</script>', re.S)
PERSON_LD_RE = re.compile(
    r'<script type="application/ld\+json">(\{[^<]*?"@type"\s*:\s*"Person"[^<]*?\})</script>', re.S)
FAQ_LD_RE = re.compile(
    r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', re.S)
MARKER_RE = lambda name: re.compile(
    rf'<!--\s*{name}:START\s*-->(.*?)<!--\s*{name}:END\s*-->', re.S)
PLACEHOLDER_RE = re.compile(r'asr-placeholder|coming soon|placeholder', re.I)
WORDS_RE = re.compile(r"[A-Za-z][A-Za-z'-]+")
PRONOUN_HIM_HER = re.compile(r"\b(him|his|her|himself|herself)\b", re.I)

REDIRECT_MARKER = '<meta http-equiv="refresh"'

def is_redirect(t):
    return REDIRECT_MARKER in t[:1500]

def extract(slug, t):
    f = {"slug": slug}
    for m in ASR_FIELD.finditer(t):
        k = m.group(1).strip(); v = html.unescape(m.group(2)).strip()
        km = {"english":"english","arabic":"arabic","urdu":"urdu","gender":"gender",
              "origin":"origin","letters":"letters","letter-breakdown":"letter_breakdown",
              "meaning-dict":"meaning_dict","meaning-root":"meaning_root","meaning-iuh":"meaning_iuh"}
        if k in km: f[km[k]] = v
    qf = re.search(r'qfacts-key[^>]*>Gender</span>[^<]*<span[^>]*>([^<]+)</span>', t)
    f["qfacts_gender"] = html.unescape(qf.group(1)).strip() if qf else ""
    nm = ASR_NAMECARD_RE.search(t)
    bearers_count = 0; namecard_gender = ""
    if nm:
        try:
            d = json.loads(nm.group(1))
            namecard_gender = str(d.get("gender","")).strip()
            bearers_count = len(d.get("bearers") or [])
        except Exception: pass
    f["namecard_gender"] = namecard_gender
    f["bearers_count_json"] = str(bearers_count)
    pld = PERSON_LD_RE.search(t)
    f["person_ld_gender"] = ""
    if pld:
        try:
            d = json.loads(pld.group(1))
            f["person_ld_gender"] = str(d.get("gender","")).strip()
        except Exception: pass
    # FAQ: try all <script type="application/ld+json"> blocks for "boy or girl"
    f["faq_gender_answer"] = ""
    for m in re.finditer(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', t, re.S):
        block = m.group(1)
        if '"FAQPage"' not in block: continue
        try:
            d = json.loads(block)
            for q in d.get("mainEntity",[]):
                if "boy or girl" in q.get("name","").lower():
                    f["faq_gender_answer"] = q.get("acceptedAnswer",{}).get("text","").strip()
                    break
            if f["faq_gender_answer"]: break
        except Exception: pass
    # Marker content
    for marker_name, key in [("MEAN-DICT","mean_dict_marker"),
                              ("MEAN-ROOT","mean_root_marker"),
                              ("MEAN-IUH","mean_iuh_marker")]:
        mm = MARKER_RE(marker_name).search(t)
        body = mm.group(1) if mm else ""
        body_clean = re.sub(r'<[^>]+>', ' ', body).strip()
        f[key+"_placeholder"] = "1" if (PLACEHOLDER_RE.search(body) or len(body_clean) < 40) else "0"
    # No widely-attested marker
    f["is_widely_attested_negative"] = "1" if re.search(r'[Nn]o widely-attested', t) else "0"
    # Pronouns in prose (rough sentinel for prose gender)
    cleaned = re.sub(r'<script.*?</script>', ' ', t, flags=re.S)
    cleaned = re.sub(r'<style.*?</style>', ' ', cleaned, flags=re.S)
    cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
    words = WORDS_RE.findall(cleaned)
    f["word_count_prose"] = str(len(words))
    pcounts = {"him":0,"her":0,"his":0,"hers":0,"himself":0,"herself":0}
    for m in PRONOUN_HIM_HER.finditer(cleaned):
        w = m.group(1).lower()
        if w in pcounts: pcounts[w] += 1
    male_p = pcounts["him"]+pcounts["his"]+pcounts["himself"]
    fem_p = pcounts["her"]+pcounts["hers"]+pcounts["herself"]
    # Note: 'her' can be possessive (her name) so over-counts female; we use ratio
    f["prose_male_pronouns"] = str(male_p)
    f["prose_female_pronouns"] = str(fem_p)
    return f

def main():
    rows = []
    for d in sorted(os.listdir(NAMES_DIR)):
        if d in PILLARS: continue
        p = NAMES_DIR / d / "index.html"
        if not p.is_file(): continue
        t = p.read_text(encoding="utf-8", errors="replace")
        if is_redirect(t): continue
        rows.append(extract(d, t))
    cols = ["slug","english","arabic","urdu","gender","qfacts_gender","person_ld_gender",
            "namecard_gender","faq_gender_answer","origin","letters","letter_breakdown",
            "meaning_dict","meaning_root","meaning_iuh",
            "mean_dict_marker_placeholder","mean_root_marker_placeholder","mean_iuh_marker_placeholder",
            "bearers_count_json","is_widely_attested_negative","word_count_prose",
            "prose_male_pronouns","prose_female_pronouns"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for r in rows: w.writerow({c: r.get(c,"") for c in cols})
    print(f"WROTE {len(rows)} canonicals to {OUT_CSV}")
if __name__=="__main__": main()
