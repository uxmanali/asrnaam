#!/usr/bin/env python3
"""Generate AR + UR pages and update English hreflang for l-r batch."""
import json, os, sys, re, importlib.util, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = json.loads((ROOT / "names" / "names-index.json").read_text(encoding="utf-8"))
IDX = {x["s"]: x for x in INDEX}

AR_LET = {
 "ا":"الألفُ قائمةٌ، صِلةٌ بين السماء والأرض",
 "آ":"الألفُ المَمدودة، نداءٌ مُمتدّ",
 "ب":"الباءُ وِعاءٌ، بَيتٌ يَأوي",
 "ت":"التاءُ ختامٌ، إثباتُ صفة",
 "ة":"التاء المربوطةُ، خِتامٌ أُنثويّ دافئ",
 "ث":"الثاءُ انتشارٌ خفيّ",
 "ج":"الجيمُ جَمعٌ واتّحاد",
 "ح":"الحاءُ حياةٌ ونَفَس",
 "خ":"الخاءُ خَفاءٌ وتنحٍّ",
 "د":"الدالُ بابٌ يَفتح",
 "ذ":"الذالُ ذِكرٌ وانتقاء",
 "ر":"الراءُ حركةٌ ونَهرٌ يَجري",
 "ز":"الزايُ زينةٌ وإشعاع",
 "س":"السينُ سَكنٌ وسِرّ",
 "ش":"الشينُ نورٌ يَنتشر",
 "ص":"الصادُ صلابةٌ وصِدق",
 "ض":"الضادُ ضِياءٌ واتّساع",
 "ط":"الطاءُ علوٌّ وثَبات",
 "ظ":"الظاءُ ظُهورٌ بعد كُمون",
 "ع":"العينُ بَصرٌ ومَنبع",
 "غ":"الغينُ غَيبٌ مَستور",
 "ف":"الفاءُ فَتحٌ وانكشاف",
 "ق":"القافُ قوّةٌ وقَرار",
 "ك":"الكافُ كَنَفٌ يَستر",
 "ل":"اللامُ لُطفٌ يَلتفّ",
 "م":"الميمُ رَحِمٌ تَحتضن",
 "ن":"النونُ نُورٌ ورَأفة",
 "ه":"الهاءُ هَويّةٌ وحياة",
 "و":"الواوُ وَصلٌ وعَطف",
 "ي":"الياءُ يَدٌ ونِسبة",
 "ى":"الألف المقصورة، انتهاءٌ مَمدود",
 "ئ":"الهمزةُ على ياء، توقّفٌ ولِين",
 "ؤ":"الهمزةُ على واو، توقّفٌ موصول",
 "أ":"الهمزةُ على ألف، ابتداءٌ حادّ",
 "إ":"الهمزة المكسورة، ابتداءٌ مَنخفض",
 "ء":"الهمزةُ، وَقفةٌ خفيفة",
}

UR_LET = {
 "ا":"الف سیدھی کھڑی، آسمان و زمین کا رابطہ",
 "آ":"الف ممدودہ، طویل پکار",
 "ب":"با گھر اور برتن کا حرف",
 "ت":"تا اثباتِ صفت کا حرف",
 "ة":"تائے مدوّرہ، نسوانی گرمی پر اختتام",
 "ث":"ثا خفیہ پھیلاؤ",
 "ج":"جیم جمع و اتحاد",
 "ح":"حا زندگی اور سانس",
 "خ":"خا چھپاؤ اور علیحدگی",
 "د":"دال دروازہ جو کھلے",
 "ذ":"ذال ذکر اور انتخاب",
 "ر":"را حرکت و روانی",
 "ز":"زا زینت اور تابانی",
 "س":"سین سکون اور راز",
 "ش":"شین پھیلتا ہوا نور",
 "ص":"صاد سچائی اور مضبوطی",
 "ض":"ضاد ضیا اور وسعت",
 "ط":"طا بلندی اور ثبات",
 "ظ":"ظا کمون کے بعد ظہور",
 "ع":"عین بصارت اور چشمہ",
 "غ":"غین پوشیدہ غیب",
 "ف":"فا کھولنے اور انکشاف کا حرف",
 "ق":"قاف قوت اور فیصلہ",
 "ك":"کاف پناہ اور گود",
 "ک":"کاف پناہ اور گود",
 "ل":"لام لطف اور لپیٹ",
 "م":"میم رحم اور محبت کی آغوش",
 "ن":"نون نور اور رحمت",
 "ه":"ہا ہویت اور زندگی",
 "ہ":"ہا ہویت اور زندگی",
 "و":"واو جوڑ اور عطف",
 "ي":"یا ہاتھ اور تعلق",
 "ی":"یا ہاتھ اور تعلق",
 "ى":"الف مقصورہ، طویل اختتام",
 "ئ":"ہمزہ یا پر، نرم وقفہ",
 "ؤ":"ہمزہ واو پر، جڑا ہوا وقفہ",
 "أ":"ہمزہ الف پر، تیز ابتدا",
 "إ":"ہمزہ مکسورہ، نچلی ابتدا",
 "ء":"ہمزہ، ہلکا وقفہ",
}

AR_DIA_RE = re.compile("[ً-ْٰـ]")

def strip_diac(s): return AR_DIA_RE.sub("", s)
def letter_list_ar(arabic):
    s = strip_diac(arabic)
    return [c for c in s if c.strip()]
def breakdown(arabic):
    return " · ".join(letter_list_ar(arabic))
def gender_ar(g): return "ذكر" if g.lower()=="male" else "أنثى"
def gender_ur(g): return "مذکر" if g.lower()=="male" else "مؤنث"
def badge_ar(g): return "اسم مسلم للذكور" if g.lower()=="male" else "اسم مسلم للإناث"
def badge_ur(g): return "مسلم لڑکوں کا نام" if g.lower()=="male" else "مسلم لڑکیوں کا نام"
def letter_prose_ar(arabic):
    chars = letter_list_ar(arabic)
    parts = [AR_LET.get(c, c) for c in chars]
    return "؛ ".join(parts) + "."
def letter_prose_ur(arabic):
    chars = letter_list_ar(arabic)
    parts = [UR_LET.get(c, c) for c in chars]
    return "؛ ".join(parts) + "۔"
def letter_short_ar(arabic):
    chars = letter_list_ar(arabic)
    descs = []
    for c in chars[:4]:
        d = AR_LET.get(c, c)
        descs.append(" ".join(d.split()[:3]))
    return "، ".join(descs)
def letter_short_ur(arabic):
    chars = letter_list_ar(arabic)
    descs = []
    for c in chars[:4]:
        d = UR_LET.get(c, c)
        descs.append(" ".join(d.split()[:3]))
    return "، ".join(descs)


AR_PAGE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="theme-color" content="#FAFAF8" media="(prefers-color-scheme: light)"/>
<meta name="theme-color" content="#1a1a1a" media="(prefers-color-scheme: dark)"/>
<title>معنى اسم __AR__ ، رسمه العربي وقراءته في علم الحروف | أَسْرَنام</title>
<meta name="description" content="__AR__: __AR_DESC__ — قراءة الحروف، الجذر العربي، ومعنى الاسم في علم الحروف على أَسْرَنام.">
<link rel="canonical" href="https://asrnaam.com/ar/names/__SLUG__/">
<link rel="alternate" hreflang="en" href="https://asrnaam.com/names/__SLUG__/"/>
<link rel="alternate" hreflang="ar" href="https://asrnaam.com/ar/names/__SLUG__/"/>
<link rel="alternate" hreflang="ur" href="https://asrnaam.com/ur/names/__SLUG__/"/>
<link rel="alternate" hreflang="x-default" href="https://asrnaam.com/names/__SLUG__/"/>
<meta property="og:type" content="article">
<meta property="og:url" content="https://asrnaam.com/ar/names/__SLUG__/">
<meta property="og:title" content="معنى اسم __AR__ ، رسمه العربي وقراءته في علم الحروف | أَسْرَنام">
<meta property="og:description" content="__AR__: __AR_DESC__ — قراءة الحروف، الجذر العربي، ومعنى الاسم في علم الحروف على أَسْرَنام.">
<meta property="og:site_name" content="أَسْرَنام">
<meta property="og:locale" content="ar_AR">
<meta property="og:locale:alternate" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="معنى اسم __AR__ ، رسمه العربي وقراءته في علم الحروف | أَسْرَنام">
<meta name="twitter:description" content="__AR__: __AR_DESC__ — قراءة الحروف، الجذر العربي، ومعنى الاسم في علم الحروف على أَسْرَنام.">

<link rel="stylesheet" href="/fonts/fonts.css">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
:root{--gold:#8B6914;--charcoal:#2A2A2A;--warm-white:#FAFAF8;--warm-mid:#F2EFE8;--text-secondary:#6B6B6B;--border:#E8E2D4;}
body{font-family:'Amiri','Noto Naskh Arabic','Scheherazade New',serif;background:var(--warm-white);color:var(--charcoal);line-height:1.85;direction:rtl;}
a{color:inherit;text-decoration:none;}
nav.asr-nav{display:flex;align-items:center;justify-content:space-between;padding:1.2rem 2.5rem;border-bottom:1px solid var(--border);background:var(--warm-white);position:sticky;top:0;z-index:100;}
.nav-brand{font-family:'Amiri',serif;font-size:1.4rem;font-weight:600;color:var(--gold);}
.nav-links{display:flex;gap:1.5rem;font-size:1rem;}
.nav-links a:hover{color:var(--gold);}
.breadcrumb{padding:1rem 2.5rem;font-size:.95rem;color:var(--text-secondary);border-bottom:1px solid var(--border);}
.breadcrumb a:hover{color:var(--gold);}
.hero{text-align:center;padding:3.5rem 2rem 2rem;max-width:760px;margin:0 auto;}
.arabic-name{font-family:'Amiri',serif;font-size:clamp(3rem,7vw,5rem);line-height:1.2;margin-bottom:1rem;color:var(--charcoal);}
.name-badge{font-size:.95rem;color:var(--text-secondary);letter-spacing:.04em;margin-bottom:1.4rem;}
h1{font-size:clamp(1.4rem,3vw,1.9rem);font-weight:600;line-height:1.55;margin-bottom:1rem;color:var(--charcoal);}
.hero-subtitle{font-size:1.1rem;color:var(--text-secondary);font-style:italic;max-width:580px;margin:0 auto;}
.content{max-width:760px;margin:0 auto;padding:0 2rem 4rem;}
.section-label{font-size:.85rem;letter-spacing:.04em;color:var(--gold);margin:3rem 0 1rem;font-weight:600;}
.section-label::after{content:"";display:block;height:1px;background:var(--border);margin-top:.6rem;}
h2{font-size:clamp(1.2rem,2.5vw,1.55rem);font-weight:600;margin-bottom:1.4rem;line-height:1.5;}
.prose p{font-size:1.12rem;line-height:1.95;margin-bottom:1.1rem;}
.quick-facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:.8rem 1.6rem;margin:1.6rem auto 2rem;padding:1.2rem 1.5rem;background:var(--warm-mid);border:1px solid var(--border);border-radius:6px;}
.qf-row{display:flex;flex-direction:column;gap:.25rem;font-size:1rem;}
.qf-label{font-size:.75rem;letter-spacing:.04em;color:var(--gold);font-weight:600;}
.qf-value{color:var(--charcoal);}
.life-note{font-size:.92rem;color:var(--text-secondary);font-style:italic;margin-top:.2rem;}
.cta-row{display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;margin:3rem 0 1.5rem;}
.cta-btn{display:inline-block;background:var(--gold);color:var(--warm-white)!important;padding:.7rem 1.6rem;border-radius:3px;font-size:.95rem;}
.cta-btn.alt{background:transparent;color:var(--gold)!important;border:1px solid var(--gold);}
footer{border-top:1px solid var(--border);padding:2.5rem 2.5rem;text-align:center;color:var(--text-secondary);}
@media (prefers-color-scheme: dark){
  body{background:#1a1a1a;color:#eae6dc;}
  .arabic-name,h1{color:#fafaf9;}
  .quick-facts{background:#242322;border-color:#3a3935;}
  nav.asr-nav, .breadcrumb, footer{background:#1a1a1a;border-color:#3a3935;}
}
</style>
</head>
<body>
<nav class="asr-nav">
  <a href="/ar/" class="nav-brand">أَسْرَنام</a>
  <div class="nav-links">
    <a href="/ar/">الرئيسية</a>
    <a href="/" lang="en">EN</a>
    <a href="/ur/">اردو</a>
  </div>
</nav>
<div class="breadcrumb">
  <a href="/ar/">الرئيسية</a> &nbsp;›&nbsp;
  <a href="/ar/">الأسماء</a> &nbsp;›&nbsp;
  <span>__AR__</span>
</div>

<main id="main-content">
<article>
<div class="hero">
  <div class="arabic-name">__AR__</div>
  <div class="name-badge">__BADGE_AR__ &nbsp;·&nbsp; قراءة في علم الحروف</div>
  <h1><em>__AR__</em> — __AR_TAG__</h1>
  <p class="hero-subtitle">__AR__ يُقرأ ثلاث قراءات — معنى الاسم، ودلالة حروفه، وما يستدعيه من حامله.</p>
</div>

<div class="content">

<aside class="quick-facts" aria-label="معلومات سريعة">
<div class="qf-row" style=""><span class="qf-label">النطق اللاتيني</span><span class="qf-value">__NAME__</span></div><div class="qf-row" style=""><span class="qf-label">الرسم العربي</span><span class="qf-value"><span lang="ar" dir="rtl" style="font-family:'Amiri',serif;font-size:1.15em;">__AR__</span></span></div><div class="qf-row" style=""><span class="qf-label">الرسم الأردي</span><span class="qf-value"><span lang="ur" dir="rtl" style="font-family:'Amiri',serif;font-size:1.15em;">__UR__</span></span></div><div class="qf-row" style=""><span class="qf-label">الجنس</span><span class="qf-value">__GEN_AR__</span></div><div class="qf-row" style=""><span class="qf-label">الأصل</span><span class="qf-value">عربي</span></div><div class="qf-row full-row" style="grid-column:1/-1;"><span class="qf-label">عدد الحروف</span><span class="qf-value">__NLET__</span></div><div class="qf-row full-row" style="grid-column:1/-1;"><span class="qf-label">تفصيل الحروف</span><span class="qf-value">__BRK__</span></div><div class="qf-row full-row" style="grid-column:1/-1;"><span class="qf-label">المعنى المعجمي</span><span class="qf-value">__AR_DICT__</span></div><div class="qf-row full-row" style="grid-column:1/-1;"><span class="qf-label">الجذر العربي</span><span class="qf-value">__AR_ROOT_QF__</span></div><div class="qf-row full-row" style="grid-column:1/-1;"><span class="qf-label">علم الحروف</span><span class="qf-value">__AR_HUROOF_SHORT__</span></div>
</aside>

<p class="section-label">المعنى المعجمي</p>
<h2>ماذا يعني اسم __AR__</h2>
<div class="prose">
<p>__AR_MEANING_PARA__</p>
</div>

<p class="section-label">الجذر العربي</p>
<h2>جذر اسم __AR__</h2>
<div class="prose">
<p>__AR_ROOT_PARA__</p>
</div>

<p class="section-label">معنى الحروف</p>
<h2>ما تكشفه حروف اسم __AR__</h2>
<div class="prose">
<p>__AR_LETTER_PARA__</p>
</div>

<p class="section-label">القراءة</p>
<h2>النمط الشخصي والعلائقي</h2>
<div class="prose">
<p>__AR_READING_PARA__</p>
<p class="life-note">اقرأ هذا كمرآة لا كحكم.</p>
</div>

<div class="cta-row">
  <a class="cta-btn" href="https://asrnaam.com/names/__SLUG__/">اقرأ الصفحة الإنجليزية</a>
  <a class="cta-btn alt" href="/ar/">الرجوع إلى فهرس الأسماء العربي</a>
</div>

</div>
</article>
</main>

<footer>
  <p style="margin-bottom:.5rem;">مكتبة مجانية لقراءة الأسماء الإسلامية بعلم الحروف.</p>
  <p style="font-size:.85rem;">© AsrNaam · <a href="/" lang="en">English</a> · <a href="/ur/">اردو</a></p>
</footer>
</body>
</html>
"""

UR_PAGE = """<!DOCTYPE html>
<html lang="ur" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="theme-color" content="#FAFAF8" media="(prefers-color-scheme: light)"/>
<meta name="theme-color" content="#1a1a1a" media="(prefers-color-scheme: dark)"/>
<title>__UR__ نام کا مطلب، عربی املا اور علم الحروف کے ذریعے قراءت | اَثَر نام</title>
<meta name="description" content="__UR__: __UR_DESC__ — حروف کی قراءت، عربی جذر، اور علم الحروف میں نام کا مطلب اَثَر نام پر۔">
<link rel="canonical" href="https://asrnaam.com/ur/names/__SLUG__/">
<link rel="alternate" hreflang="en" href="https://asrnaam.com/names/__SLUG__/"/>
<link rel="alternate" hreflang="ur" href="https://asrnaam.com/ur/names/__SLUG__/"/>
<link rel="alternate" hreflang="ar" href="https://asrnaam.com/ar/names/__SLUG__/"/>
<link rel="alternate" hreflang="x-default" href="https://asrnaam.com/names/__SLUG__/"/>
<meta property="og:type" content="article">
<meta property="og:url" content="https://asrnaam.com/ur/names/__SLUG__/">
<meta property="og:title" content="__UR__ نام کا مطلب، عربی املا اور علم الحروف کے ذریعے قراءت | اَثَر نام">
<meta property="og:description" content="__UR__: __UR_DESC__ — حروف کی قراءت، عربی جذر، اور علم الحروف میں نام کا مطلب اَثَر نام پر۔">
<meta property="og:site_name" content="اَثَر نام">
<meta property="og:locale" content="ur_PK">
<meta property="og:locale:alternate" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="__UR__ نام کا مطلب، عربی املا اور علم الحروف کے ذریعے قراءت | اَثَر نام">
<meta name="twitter:description" content="__UR__: __UR_DESC__ — حروف کی قراءت، عربی جذر، اور علم الحروف میں نام کا مطلب اَثَر نام پر۔">

<link rel="stylesheet" href="/fonts/fonts.css">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
:root{--gold:#8B6914;--charcoal:#2A2A2A;--warm-white:#FAFAF8;--warm-mid:#F2EFE8;--text-secondary:#6B6B6B;--border:#E8E2D4;}
body{font-family:'Amiri','Noto Naskh Arabic','Scheherazade New',serif;background:var(--warm-white);color:var(--charcoal);line-height:1.85;direction:rtl;}
a{color:inherit;text-decoration:none;}
nav.asr-nav{display:flex;align-items:center;justify-content:space-between;padding:1.2rem 2.5rem;border-bottom:1px solid var(--border);background:var(--warm-white);position:sticky;top:0;z-index:100;}
.nav-brand{font-family:'Amiri',serif;font-size:1.4rem;font-weight:600;color:var(--gold);}
.nav-links{display:flex;gap:1.5rem;font-size:1rem;}
.nav-links a:hover{color:var(--gold);}
.breadcrumb{padding:1rem 2.5rem;font-size:.95rem;color:var(--text-secondary);border-bottom:1px solid var(--border);}
.breadcrumb a:hover{color:var(--gold);}
.hero{text-align:center;padding:3.5rem 2rem 2rem;max-width:760px;margin:0 auto;}
.arabic-name{font-family:'Amiri',serif;font-size:clamp(3rem,7vw,5rem);line-height:1.2;margin-bottom:1rem;color:var(--charcoal);}
.name-badge{font-size:.95rem;color:var(--text-secondary);letter-spacing:.04em;margin-bottom:1.4rem;}
h1{font-size:clamp(1.4rem,3vw,1.9rem);font-weight:600;line-height:1.55;margin-bottom:1rem;color:var(--charcoal);}
.hero-subtitle{font-size:1.1rem;color:var(--text-secondary);font-style:italic;max-width:580px;margin:0 auto;}
.content{max-width:760px;margin:0 auto;padding:0 2rem 4rem;}
.section-label{font-size:.85rem;letter-spacing:.04em;color:var(--gold);margin:3rem 0 1rem;font-weight:600;}
.section-label::after{content:"";display:block;height:1px;background:var(--border);margin-top:.6rem;}
h2{font-size:clamp(1.2rem,2.5vw,1.55rem);font-weight:600;margin-bottom:1.4rem;line-height:1.5;}
.prose p{font-size:1.12rem;line-height:1.95;margin-bottom:1.1rem;}
.quick-facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:.8rem 1.6rem;margin:1.6rem auto 2rem;padding:1.2rem 1.5rem;background:var(--warm-mid);border:1px solid var(--border);border-radius:6px;}
.qf-row{display:flex;flex-direction:column;gap:.25rem;font-size:1rem;}
.qf-label{font-size:.75rem;letter-spacing:.04em;color:var(--gold);font-weight:600;}
.qf-value{color:var(--charcoal);}
.life-note{font-size:.92rem;color:var(--text-secondary);font-style:italic;margin-top:.2rem;}
.cta-row{display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;margin:3rem 0 1.5rem;}
.cta-btn{display:inline-block;background:var(--gold);color:var(--warm-white)!important;padding:.7rem 1.6rem;border-radius:3px;font-size:.95rem;}
.cta-btn.alt{background:transparent;color:var(--gold)!important;border:1px solid var(--gold);}
footer{border-top:1px solid var(--border);padding:2.5rem 2.5rem;text-align:center;color:var(--text-secondary);}
@media (prefers-color-scheme: dark){
  body{background:#1a1a1a;color:#eae6dc;}
  .arabic-name,h1{color:#fafaf9;}
  .quick-facts{background:#242322;border-color:#3a3935;}
  nav.asr-nav, .breadcrumb, footer{background:#1a1a1a;border-color:#3a3935;}
}
</style>
</head>
<body>
<nav class="asr-nav">
  <a href="/ur/" class="nav-brand">اَثَر نام</a>
  <div class="nav-links">
    <a href="/ur/">ابتدائی صفحہ</a>
    <a href="/" lang="en">EN</a>
    <a href="/ar/">العربية</a>
  </div>
</nav>
<div class="breadcrumb">
  <a href="/ur/">ابتدائی صفحہ</a> &nbsp;›&nbsp;
  <a href="/ur/">نام</a> &nbsp;›&nbsp;
  <span>__UR__</span>
</div>

<main id="main-content">
<article>
<div class="hero">
  <div class="arabic-name">__AR__</div>
  <div class="name-badge">__BADGE_UR__ &nbsp;·&nbsp; علم الحروف کی قراءت</div>
  <h1><em>__UR__</em> — __UR_TAG__</h1>
  <p class="hero-subtitle">__UR__ تین طرح پڑھیں — اس نام کا مطلب، اس کے حروف کا اشارہ، اور اس کی حامل سے کیا تقاضا۔</p>
</div>

<div class="content">

<aside class="quick-facts" aria-label="فوری حقائق">
<div class="qf-row" style=""><span class="qf-label">انگریزی تلفظ</span><span class="qf-value">__NAME__</span></div><div class="qf-row" style=""><span class="qf-label">عربی املا</span><span class="qf-value"><span lang="ar" dir="rtl" style="font-family:'Amiri',serif;font-size:1.15em;">__AR__</span></span></div><div class="qf-row" style=""><span class="qf-label">اردو املا</span><span class="qf-value"><span lang="ur" dir="rtl" style="font-family:'Amiri',serif;font-size:1.15em;">__UR__</span></span></div><div class="qf-row" style=""><span class="qf-label">صنف</span><span class="qf-value">__GEN_UR__</span></div><div class="qf-row" style=""><span class="qf-label">اصل</span><span class="qf-value">عربی</span></div><div class="qf-row full-row" style="grid-column:1/-1;"><span class="qf-label">حروف کی تعداد</span><span class="qf-value">__NLET__</span></div><div class="qf-row full-row" style="grid-column:1/-1;"><span class="qf-label">حروف کی تفصیل</span><span class="qf-value">__BRK__</span></div><div class="qf-row full-row" style="grid-column:1/-1;"><span class="qf-label">لغوی معنی</span><span class="qf-value">__UR_DICT__</span></div><div class="qf-row full-row" style="grid-column:1/-1;"><span class="qf-label">عربی جذر</span><span class="qf-value">__UR_ROOT_QF__</span></div><div class="qf-row full-row" style="grid-column:1/-1;"><span class="qf-label">علم الحروف</span><span class="qf-value">__UR_HUROOF_SHORT__</span></div>
</aside>

<p class="section-label">لغوی معنی</p>
<h2>__UR__ کا کیا مطلب ہے</h2>
<div class="prose">
<p>__UR_MEANING_PARA__</p>
</div>

<p class="section-label">عربی جذر</p>
<h2>__UR__ کا جذر</h2>
<div class="prose">
<p>__UR_ROOT_PARA__</p>
</div>

<p class="section-label">حروف کا مطلب</p>
<h2>__UR__ کے حروف کیا ظاہر کرتے ہیں</h2>
<div class="prose">
<p>__UR_LETTER_PARA__</p>
</div>

<p class="section-label">قراءت</p>
<h2>شخصیت اور تعلقات کا انداز</h2>
<div class="prose">
<p>__UR_READING_PARA__</p>
<p class="life-note">اسے فیصلہ نہیں، آئینہ سمجھ کر پڑھیں۔</p>
</div>

<div class="cta-row">
  <a class="cta-btn" href="https://asrnaam.com/names/__SLUG__/">انگریزی صفحہ پڑھیں</a>
  <a class="cta-btn alt" href="/ur/">اردو ناموں کی فہرست پر واپس جائیں</a>
</div>

</div>
</article>
</main>

<footer>
  <p style="margin-bottom:.5rem;">مسلم ناموں کو علم الحروف کے ذریعے پڑھنے کا ایک مفت ذخیرہ۔</p>
  <p style="font-size:.85rem;">© AsrNaam · <a href="/" lang="en">English</a> · <a href="/ar/">العربية</a></p>
</footer>
</body>
</html>
"""

def fill(tpl, ctx):
    out = tpl
    for k, v in ctx.items():
        out = out.replace(f"__{k}__", str(v))
    return out

def update_en_hreflang(slug):
    p = ROOT / "names" / slug / "index.html"
    if not p.exists(): return False
    t = p.read_text(encoding="utf-8")
    if f'hreflang="ar" href="https://asrnaam.com/ar/names/{slug}/"' in t:
        return False
    needle = f'<link rel="alternate" hreflang="en" href="https://asrnaam.com/names/{slug}/"/>'
    if needle not in t:
        return False
    inject = (needle
              + f'\n <link rel="alternate" hreflang="ar" href="https://asrnaam.com/ar/names/{slug}/"/>'
              + f'\n <link rel="alternate" hreflang="ur" href="https://asrnaam.com/ur/names/{slug}/"/>')
    t = t.replace(needle, inject, 1)
    p.write_text(t, encoding="utf-8")
    return True

def render(slug, data):
    e = IDX[slug]
    ar = e["a"]; ur = e["u"]; g = e["g"]; name = e["n"]
    chars = letter_list_ar(ar)
    nlet = len(chars)
    brk = breakdown(ar)
    base = {
        "SLUG": slug, "NAME": name, "AR": ar, "UR": ur,
        "GEN_AR": gender_ar(g), "GEN_UR": gender_ur(g),
        "BADGE_AR": badge_ar(g), "BADGE_UR": badge_ur(g),
        "NLET": str(nlet), "BRK": brk,
    }
    base["AR_TAG"] = data["ar_tag"]
    base["AR_DESC"] = data["ar_desc"]
    base["AR_DICT"] = data["ar_dict"]
    base["AR_ROOT_QF"] = data["ar_root_qf"]
    base["AR_HUROOF_SHORT"] = data.get("ar_huroof_short") or letter_short_ar(ar)
    base["AR_MEANING_PARA"] = data["ar_meaning"]
    base["AR_ROOT_PARA"] = data["ar_root"]
    base["AR_LETTER_PARA"] = data.get("ar_letter") or letter_prose_ar(ar)
    base["AR_READING_PARA"] = data["ar_reading"]
    base["UR_TAG"] = data["ur_tag"]
    base["UR_DESC"] = data["ur_desc"]
    base["UR_DICT"] = data["ur_dict"]
    base["UR_ROOT_QF"] = data["ur_root_qf"]
    base["UR_HUROOF_SHORT"] = data.get("ur_huroof_short") or letter_short_ur(ar)
    base["UR_MEANING_PARA"] = data["ur_meaning"]
    base["UR_ROOT_PARA"] = data["ur_root"]
    base["UR_LETTER_PARA"] = data.get("ur_letter") or letter_prose_ur(ar)
    base["UR_READING_PARA"] = data["ur_reading"]

    ar_dir = ROOT / "ar" / "names" / slug
    ur_dir = ROOT / "ur" / "names" / slug
    ar_dir.mkdir(parents=True, exist_ok=True)
    ur_dir.mkdir(parents=True, exist_ok=True)
    (ar_dir / "index.html").write_text(fill(AR_PAGE, base), encoding="utf-8")
    (ur_dir / "index.html").write_text(fill(UR_PAGE, base), encoding="utf-8")
    update_en_hreflang(slug)

def run(names_file):
    spec = importlib.util.spec_from_file_location("d", names_file)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    n = 0
    for slug, data in m.NAMES.items():
        if slug not in IDX:
            print("MISSING_IDX:", slug); continue
        render(slug, data); n += 1
    print(f"wrote {n} names")

if __name__ == "__main__":
    run(sys.argv[1])
