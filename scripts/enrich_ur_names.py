#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild Urdu name pages so they carry the same sections as the English pages.

Reads each full /ur/names/<slug>/ page and its English counterpart. Reuses the
Urdu gloss already stored on the English page (or a checked gloss in
ur_glosses.py). Does not invent a lexical meaning when the English source says
the meaning is not established. Leaves spelling-variant redirect stubs alone,
and does not edit English pages.
"""

from __future__ import annotations

import json
import re
import sys
from html import escape as html_escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ur_glosses import GLOSS, REVIEW  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TODAY = "2026-11-12"
SITE = "https://asrnaam.com"

UNESTABLISHED = (
    "دستیاب ماخذ میں اس نام کا لغوی مطلب طے نہیں ہوا۔ "
    "یہ صفحہ املا، حروف اور ابجد دیتا ہے، اور کوئی مفہوم نہیں گھڑتا۔"
)

DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

ABJAD = {
    "ا": 1, "آ": 1, "أ": 1, "إ": 1, "ٱ": 1,
    "ب": 2, "پ": 2,
    "ج": 3, "چ": 3,
    "د": 4,
    "ه": 5, "ة": 5, "ہ": 5, "ھ": 5, "ۃ": 5,
    "و": 6, "ؤ": 6,
    "ز": 7, "ژ": 7,
    "ح": 8,
    "ط": 9,
    "ی": 10, "ي": 10, "ى": 10, "ئ": 10, "ے": 10,
    "ک": 20, "ك": 20, "گ": 20,
    "ل": 30, "م": 40, "ن": 50, "ں": 50, "س": 60, "ع": 70, "ف": 80, "ص": 90,
    "ق": 100, "ر": 200, "ش": 300, "ت": 400, "ث": 500, "خ": 600, "ذ": 700,
    "ض": 800, "ظ": 900, "غ": 1000,
}

DIV = (
    '<div class="asr-v2-divider" aria-hidden="true"><svg viewBox="0 0 24 24" width="20" height="20">'
    '<path d="M12 2 L14 10 L22 12 L14 14 L12 22 L10 14 L2 12 L10 10 Z" fill="currentColor"/>'
    '<path d="M12 5 L13 11 L19 12 L13 13 L12 19 L11 13 L5 12 L11 11 Z" fill-opacity=".55" '
    'fill="var(--warm-white,#FAFAF8)"/></svg></div>'
)

TYPE_CSS = """<style id="ur-type">
body{line-height:2.05;}
h1,h2,.asr-v2-title,.prose p,.qf-value{letter-spacing:0;}
.asr-v2-kicker,.asr-v2-letter-roman,.asr-v2-letter-pill,.asr-v2-letter-anchor{
  font-family:'Amiri','Noto Naskh Arabic',serif;letter-spacing:0;text-transform:none;
}
.asr-v2-kicker{font-size:.95rem;}
.asr-v2-letter-roman{font-size:1.02rem;}
.asr-v2-letter-anchor{font-size:1rem;line-height:1.6;}
.asr-v2-letter-pill{font-size:.92rem;}
.asr-faq-item{border-bottom:1px solid var(--border,#E8E2D4);padding:.85rem 0;}
.asr-faq-item summary{cursor:pointer;font-weight:700;font-size:1.08rem;line-height:1.75;}
.asr-faq-item .prose{margin-top:.4rem;}
.related-grid{display:flex;flex-wrap:wrap;gap:.55rem;margin-top:.8rem;}
.related-card{display:inline-flex;flex-direction:column;gap:.15rem;padding:.5rem .9rem;border:1px solid var(--border,#E8E2D4);border-radius:4px;background:var(--warm-mid,#F2EFE8);min-width:7.2rem;line-height:1.45;}
.related-teaser{font-size:.88rem;color:var(--text-secondary,#6B6B6B);}
.asr-pron{margin:.4rem 0 1rem;padding:.9rem 1.1rem;background:var(--warm-mid,#F2EFE8);border-inline-start:3px solid var(--gold,#7A570E);border-radius:4px;}
@media(prefers-color-scheme:dark){
  .related-card,.asr-pron{background:#242322;border-color:#3a3935;}
  .related-teaser{color:#c8c2b4;}
}
</style>"""

DIVINE_AR = {
    "Al-Ahad": "الأحد",
    "Al-Alim": "العلیم",
    "Al-Nur": "النور",
    "Al-Mu'min": "المؤمن",
    "Al-Rahman": "الرحمن",
    "Al-Tawwab": "التواب",
    "Al-Batin": "الباطن",
    "Al-Sami": "السمیع",
    "Al-Fattah": "الفتاح",
    "Al-Dayyan": "الدیان",
    "Al-Hamid": "الحمید",
    "Al-Zahir": "الظاہر",
    "Al-Shakur": "الشکور",
    "Al-Latif": "اللطیف",
    "Al-Lateef": "اللطیف",
    "Al-Jami": "الجامع",
    "Al-Qayyum": "القیوم",
    "Al-Karim": "الکریم",
    "Al-Wadud": "الودود",
    "Al-Samad": "الصمد",
    "Al-Hadi": "الہادی",
    "Al-Khabir": "الخبیر",
    "Al-Ghani": "الغنی",
    "Al-Qadir": "القادر",
    "Al-Darr": "الضار",
    "Al-Thabit": "الثابت",
    "Al-Dhahir": "الظاہر",
    "Al-Adil": "العادل",
    "Dhul-Jalal": "ذوالجلال",
}

EPITHET_UR = {
    "the One": "یکتا",
    "the All-Knowing": "سب جاننے والا",
    "the Light": "نور",
    "the Faithful": "ایمان والا",
    "the Merciful": "رحم کرنے والا",
    "the Relenting": "توبہ قبول کرنے والا",
    "the Interior": "باطن",
    "the All-Hearing": "سب سننے والا",
    "the Opener": "کھولنے والا",
    "the Judge": "منصف",
    "the Praiseworthy": "قابلِ تعریف",
    "the Manifest": "ظاہر",
    "the Appreciative": "قدر دان",
    "the Gracious": "لطیف، کریم",
    "the Gatherer": "جمع کرنے والا",
    "the Self-Sustaining": "قائم رکھنے والا",
    "the Generous": "سخی",
    "the Loving": "محبت کرنے والا",
    "the Eternal Refuge": "بے نیاز پناہ",
    "the Guide": "ہدایت دینے والا",
    "the Aware": "باخبر",
    "the Self-Sufficient": "بے نیاز",
    "the All-Capable": "قدرت والا",
    "the Subtle": "باریک بین",
    "the Tester": "آزمانے والا",
    "the Firm": "مضبوط",
    "the Outer Manifest": "ظاہر",
    "the Lord of Majesty": "ربِّ جلال",
}

QUALITY_UR = {
    "a singular, undivided presence": "ایک اکیلی، نہ بٹنے والی موجودگی",
    "a knowing that predates study": "ایسا علم جو پڑھائی سے پہلے کا ہے",
    "a faith others can lean on": "ایمان جس پر دوسرے ٹیک لگا سکیں",
    "mercy that keeps moving even when tested": "رحمت جو آزمائش میں بھی جاری رہے",
    "the alertness to hear what is not being said aloud": "وہ کان جو وہ سنے جو زبان پر نہیں آیا",
    "the will to open what was closed": "بند کو کھول دینے کا ارادہ",
    "a light that steadies the room": "روشنی جو کمرے کو تھام لے",
    "the readiness to return and be returned to": "لوٹ آنے، اور لوٹا لیے جانے کی تیاری",
    "a way of noticing and honouring small kindnesses": "چھوٹی مہربانی کو دیکھنا اور قدر کرنا",
    "the fair judgment that keeps a household whole": "انصاف جو گھر کو جوڑے رکھے",
    "an interior life that runs deeper than what is shown": "اندر کی زندگی، جو باہر سے گہری ہو",
    "the ability to gather people around what matters": "لوگوں کو اصل بات کے گرد جمع کرنا",
    "the trust to receive genuine praise, not flattery": "سچی تعریف سننا، خوشامد نہیں",
    "an open-handed generosity of spirit": "کھلے ہاتھ کی سخاوت",
    "a clarity that shows itself without needing to shout": "صفائی جو چیخے بغیر سامنے آئے",
    "an unshowy kindness that reaches the tender parts": "بے نمائش مہربانی، جو نرم جگہ تک پہنچے",
    "a self-holding constancy": "اپنے آپ کو تھامے رہنے والا ثبات",
    "a steady, connective love": "جڑی ہوئی، ٹھہری محبت",
    "the animating breath that guides others through": "سانس جو دوسروں کو راستہ دکھائے",
    "the eternal reliability others rest against": "وہ بھروسا جس سے دوسرے ٹیک لگائیں",
    "an inner sufficiency that does not need external filling": "اندر کی بے نیازی، جو باہر سے نہ بھری جائے",
    "a subtle, sun-warm attention": "باریک، دھوپ جیسی توجہ",
    "a capable, unruffled competence": "قابل، بے اضطراب صلاحیت",
    "an aware, quietly informed presence": "باخبر، خاموش موجودگی",
    "an ancient, weighty seriousness": "پرانا، بھاری وقار",
    "the firmness that outlasts weather": "مضبوطی جو موسم سے آگے رہے",
    "the strength to hold hard truths without flinching": "کڑی سچائی کو سنبھالنے کی طاقت",
    "a truth that eventually surfaces": "سچ جو آخر سامنے آ ہی جاتا ہے",
    "a depth that does not show all of itself at once": "گہرائی جو ایک دم ساری نہیں کھلتی",
}

ENDING_UR = {
    "carries a full weather system inside a single quiet chest.": "ایک خاموش سینے میں پورا موسم لیے ہوئے ہے۔",
    "lives with more inside them than any one word can hold.": "اندر اتنا لیے ہوئے ہے جتنا ایک لفظ نہیں سنبھال سکتا۔",
    "is many things at once, and gets to choose which shows up when.": "ایک ساتھ کئی رخ رکھتا ہے، اور یہ چنتا ہے کہ کون سا سامنے آئے۔",
    "tends to be a settled place others return to.": "اکثر وہ ٹھہرا ٹھکانا بنتا ہے جہاں لوگ لوٹ کر آتے ہیں۔",
    "is the household others rest against without noticing they are resting.": "وہ گھر ہے جس سے لوگ ٹیک لگاتے ہیں، اور انہیں پتا نہیں چلتا۔",
    "is the kind of person a village grows around.": "ایسا شخص ہے جس کے گرد بستی بس جاتی ہے۔",
    "tends to build things that outlast them.": "ایسی چیزیں بناتا ہے جو اس کے بعد بھی رہیں۔",
    "carries the kind of fire people gather around, not the kind that burns them.": "وہ آگ لیے ہے جس کے گرد لوگ بیٹھتے ہیں، جو انہیں جلائے نہیں۔",
    "tends to bring warmth to a room and light to a decision.": "کمرے میں گرمی اور فیصلے میں روشنی لاتا ہے۔",
    "is likely to warm the rooms they enter and to lead by lit example.": "جس کمرے میں جائے اسے گرم کرتا ہے، اور روشن مثال سے آگے چلتا ہے۔",
    "holds their people through seasons.": "اپنے لوگوں کو موسموں کے پار تھامے رکھتا ہے۔",
    "keeps a home even in weather.": "موسم میں بھی گھر کو سنبھالے رکھتا ہے۔",
    "is the family's slow heart.": "خاندان کا آہستہ دل ہے۔",
    "contains more than they show.": "اندر اس سے زیادہ ہے جتنا باہر دکھتا ہے۔",
    "carries the compassion of a river that keeps going.": "ایسی شفقت لیے ہے جو دریا کی طرح چلتی رہے۔",
    "is quieter than their fire suggests, and hotter than their calm implies.": "آگ سے زیادہ خاموش ہے، اور سکون سے زیادہ گرم۔",
    "tends to be the safe place people bring their harder feelings to.": "وہ محفوظ جگہ بنتا ہے جہاں لوگ اپنا بھاری احساس لے آئیں۔",
    "holds others without asking them to be smaller.": "دوسروں کو تھامتا ہے، یہ کہے بغیر کہ وہ چھوٹے ہو جائیں۔",
    "is a rare kind of practical intelligence.": "عملی سمجھ کی ایک کم یاب صورت ہے۔",
    "tends to be trusted with plans and with hands.": "منصوبے بھی اس کے سپرد ہوتے ہیں، اور ہاتھ کا کام بھی۔",
    "tends to name the thing everyone else was circling.": "اس بات کا نام لے لیتا ہے جس کے گرد باقی چکر لگا رہے ہوتے ہیں۔",
    "is a rare mix of vision and momentum.": "نظر اور رفتار کا کم یاب ملاپ ہے۔",
    "tends to make room for what is difficult to say.": "اس بات کے لیے جگہ بناتا ہے جو کہنا مشکل ہو۔",
    "tends to shape the direction others follow.": "وہ سمت بناتا ہے جس پر باقی چلتے ہیں۔",
    "tends to point at the road and take the first step.": "راستہ دکھاتا ہے، اور پہلا قدم خود اٹھاتا ہے۔",
    "tends to keep watch for others before thinking of themselves.": "اپنے خیال سے پہلے دوسروں کی نگہبانی کرتا ہے۔",
    "is often the one people can be honest with.": "اکثر وہ شخص ہوتا ہے جس سے لوگ سچ بول سکیں۔",
        "tends to be gentler than they look and harder to tear than people expect.": "دکھائی سے زیادہ نرم ہے، اور لوگوں کے گمان سے زیادہ مشکل سے پھٹتا ہے۔",
        "builds what they have first thought all the way through.": "جو پہلے سوچے، اسے آخر تک بنا ڈالتا ہے۔",
        "plants what their fire has cleared.": "آگ نے جو جگہ صاف کی ہو، وہاں بو دیتا ہے۔",
}

MIDDLE_UR = {
    "This is a name that asks its bearer to hold contradictions gracefully: warmth and steadiness, movement and depth.": "یہ نام اپنے حامل سے چاہتا ہے کہ وہ تضاد کو نرمی سے تھامے: گرمی اور ثبات، چلنے اور گہرائی۔",
    "The letters ask their bearer to be reliable rather than showy, to keep the household of the heart in order.": "حروف حامل سے چاہتے ہیں کہ وہ دکھاوے کے بجائے بھروسے کے لائق رہے، اور دل کے گھر کو سنبھالے۔",
    "This is a name that asks its bearer to burn steadily rather than in bursts, and to plant what the fire has cleared.": "یہ نام چاہتا ہے کہ حامل جھٹکوں میں نہیں، برابر جلے، اور آگ نے جو جگہ صاف کی ہو وہاں بو دے۔",
    "This is a name that leans toward decisiveness and radiance, with the courage to begin what others hesitate to.": "یہ نام فیصلے اور چمک کی طرف جھکتا ہے، اور اس بات کی ہمت دیتا ہے جس سے دوسرے ہچکچائیں۔",
    "The person is asked to be both root and river, a slow, sheltering presence.": "حامل سے کہا جاتا ہے کہ وہ جڑ بھی ہو اور دریا بھی: آہستہ، سایہ کرنے والی موجودگی۔",
    "This is a person of intense inner weather, capable of both flame and calm depth.": "یہ اندر کے شدید موسم والا شخص ہے: شعلہ بھی، اور خاموش گہرائی بھی۔",
    "The letters ask their bearer to hold others without hardening, to be a well and not a wall.": "حروف چاہتے ہیں کہ حامل دوسروں کو تھامے اور سخت نہ پڑے: کنواں ہو، دیوار نہیں۔",
    "The letters ask their bearer to think without floating away, and to build without slowing down.": "حروف چاہتے ہیں کہ حامل سوچے اور اڑ نہ جائے، اور بنائے اور رک نہ جائے۔",
    "This is a name that asks its bearer to notice quickly, speak clearly, and move light.": "یہ نام چاہتا ہے کہ حامل جلدی دیکھے، صاف بولے، اور ہلکا چلے۔",
    "A visionary drive lives inside this name, a person who both sees and moves.": "اس نام میں ایک دیکھنے والی رفتار ہے: شخص جو دیکھے بھی اور چلے بھی۔",
    "The bearer is asked to name what is felt without cooling it, and to feel what is thought without losing it.": "حامل سے کہا جاتا ہے کہ محسوس کو ٹھنڈا کیے بغیر نام دے، اور سوچے ہوئے کو گنواے بغیر محسوس کرے۔",
    "The letters ask their bearer to hold a line without hardening, as a frontier holds without becoming a wall.": "حروف چاہتے ہیں کہ حامل ایک لکیر تھامے اور سخت نہ پڑے، جیسے سرحد دیوار بنے بغیر ٹھہرتی ہے۔",
    "The letters ask their bearer to be soft to the touch and strong in the weave, as silk is.": "حروف چاہتے ہیں کہ حامل چھوت میں نرم ہو اور بناوٹ میں مضبوط، جیسے ریشم۔",
}

OPENING_PATTERNS = [
    (re.compile(r"^(?P<name>.+?)['’]s letters draw from many elements at once, a full palette, not a single note\.$"),
     "{n} کے حروف ایک ساتھ کئی عناصر سے کھینچتے ہیں: یہ پورا رنگ ہے، ایک ہی سر نہیں۔"),
    (re.compile(r"^(?P<name>.+?) is grounded in earth, the element of stability, patience, and quiet holding\.$"),
     "{n} مٹی پر ٹکا ہے: ثبات، صبر، اور خاموش سنبھال۔"),
    (re.compile(r"^(?P<name>.+?) joins fire to earth, the will that decides with the patience that lasts\.$"),
     "{n} آگ کو مٹی سے جوڑتا ہے: فیصلہ کرنے والا ارادہ، اور ٹھہر جانے والا صبر۔"),
    (re.compile(r"^The letters in (?P<name>.+?) cluster around fire, the element of will, warmth, and forward motion\.$"),
     "{n} کے حروف آگ کے گرد جمع ہیں: ارادہ، گرمی، اور آگے بڑھنا۔"),
    (re.compile(r"^(?P<name>.+?) weaves earth and water, the elements of steadiness and mercy, patience and feeling\.$"),
     "{n} مٹی اور پانی کو گوندتا ہے: ثبات اور رحمت، صبر اور احساس۔"),
    (re.compile(r"^(?P<name>.+?) carries fire and water together, the two most different elements, will and mercy in one hand\.$"),
     "{n} آگ اور پانی کو ساتھ اٹھاتا ہے: ارادہ اور رحمت، ایک ہی ہاتھ میں۔"),
    (re.compile(r"^(?P<name>.+?) holds earth and air in even measure, grounded body and quick mind\.$"),
     "{n} مٹی اور ہوا کو برابر رکھتا ہے: جما ہوا بدن، چست ذہن۔"),
    (re.compile(r"^(?P<name>.+?)['’]s letters bring fire and air together, the elements of will and insight, courage and clarity\.$"),
     "{n} کے حروف آگ اور ہوا کو ملاتے ہیں: ارادہ اور بصیرت، ہمت اور صفائی۔"),
    (re.compile(r"^(?P<name>.+?) brings air and water together, the elements of clear seeing and feeling deeply\.$"),
     "{n} ہوا اور پانی کو ساتھ لاتا ہے: صاف دیکھنا، اور گہرا محسوس کرنا۔"),
    (re.compile(r"^Water pools in (?P<name>.+?), the element of mercy, feeling, and receptive depth\.$"),
     "{n} میں پانی ٹھہرتا ہے: رحمت، احساس، اور قبول کرنے والی گہرائی۔"),
    (re.compile(r"^Air runs through (?P<name>.+?), the element of insight, breath, and swift understanding\.$"),
     "{n} میں ہوا دوڑتی ہے: بصیرت، سانس، اور تیز سمجھ۔"),
    (re.compile(r"^(?P<name>.+?) letters bring fire and air together, the elements of will and insight, courage and clarity\.$"),
     "{n} کے حروف آگ اور ہوا کو ملاتے ہیں: ارادہ اور بصیرت، ہمت اور صفائی۔"),
]

ORIGIN_UR = {
    "Arabic": "عربی",
    "Persian": "فارسی",
    "Turkish": "ترکی",
    "Kurdish": "کرد",
    "Kazakh": "قازق",
    "Berber": "بربر",
    "Urdu": "اردو",
    "Pashto": "پشتو",
    "Malay": "مالے",
    "Turkic": "ترک",
    "Sindhi": "سندھی",
    "Balochi": "بلوچی",
    "Filipino": "فلپائنی",
    "Somali": "صومالی",
    "Fulani": "فولا",
    "Kyrgyz": "کرغز",
    "Bambara": "بمبارا",
    "Tatar": "تاتاری",
    "Spanish": "ہسپانوی",
    "Indonesian": "انڈونیشیائی",
    "South Asian": "جنوبی ایشیائی",
    "Circassian": "چرکس",
    "Hebrew (preserved in Quranic Arabic)": "عبرانی (قرآنی عربی میں محفوظ)",
    "Hebrew → Arabic": "عبرانی سے عربی",
    "Hebrew/Aramaic (preserved in Quranic Arabic)": "عبرانی/آرامی (قرآنی عربی میں محفوظ)",
    "Hebrew, South Asian Muslim use": "عبرانی، جنوبی ایشیا کے مسلمانوں میں مستعمل",
    "Indonesian / Arabic": "انڈونیشیائی / عربی",
    "Swahili / Arabic": "سواحلی / عربی",
    "Bosnian / Arabic": "بوسنیائی / عربی",
    "Syriac → Arabic": "سریانی سے عربی",
    "Arabic (Quranic prophet)": "عربی (قرآنی نبی)",
    "Arabicized Latin": "عربی قالب میں لاطینی",
    "Latin, international use": "لاطینی، بین الاقوامی استعمال",
    "non-Arabic origin (Babylonian / Avestan)": "غیر عربی (بابلی / اوستائی)",
    "non-Arabic origin (debated)": "غیر عربی (ماخذ میں اختلاف)",
    "Uncertain": "غیر یقینی",
    "Uncertain (English usage reported)": "غیر یقینی (انگریزی استعمال درج ہے)",
    "Uncertain (English and Arabic usage reported)": "غیر یقینی (انگریزی اور عربی استعمال درج ہے)",
    "Uncertain (Pakistani usage reported)": "غیر یقینی (پاکستانی استعمال درج ہے)",
    "Slavic / Bosnian Muslim usage": "سلاوی / بوسنیائی مسلمان استعمال",
}

ORIGIN_TOKEN = [
    ("Quranic Arabic", "قرآنی عربی"),
    ("Arabic", "عربی"),
    ("Persian", "فارسی"),
    ("Turkish", "ترکی"),
    ("Hebrew", "عبرانی"),
    ("Aramaic", "آرامی"),
    ("Urdu", "اردو"),
    ("Kurdish", "کرد"),
    ("Pashto", "پشتو"),
    ("Sindhi", "سندھی"),
    ("Berber", "بربر"),
    ("Swahili", "سواحلی"),
    ("Malay", "مالے"),
    ("Indonesian", "انڈونیشیائی"),
    ("Bosnian", "بوسنیائی"),
    ("Hausa", "ہاؤسا"),
    ("Fulani", "فولا"),
    ("Wolof", "وولوف"),
    ("French", "فرانسیسی"),
    ("English", "انگریزی"),
    ("South Asian", "جنوبی ایشیائی"),
    ("North African", "شمالی افریقی"),
    ("West African", "مغربی افریقی"),
    ("Uncertain", "غیر یقینی"),
    ("preserved", "محفوظ"),
    ("reported", "درج"),
    ("usage", "استعمال"),
    ("origin", "اصل"),
]

GENDER = {
    "Girl": ("مؤنث", "لڑکیوں"),
    "Female": ("مؤنث", "لڑکیوں"),
    "Boy": ("مذکر", "لڑکوں"),
    "Male": ("مذکر", "لڑکوں"),
    "Boy or girl": ("مشترک", "لڑکوں اور لڑکیوں"),
}

COMMUNITY_UR = {
    "Arabic · Classical": "عربی · کلاسیکی",
    "South Asian · Pakistan": "جنوبی ایشیا · پاکستان",
    "Malay · Indonesia": "مالے · انڈونیشیا",
    "Turkish": "ترکی",
    "Persian": "فارسی",
    "Urdu": "اردو",
    "Arab world": "عرب دنیا",
}

ROLE_PHRASES = [
    ("Final Prophet of Islam", "اسلام کے آخری نبی ﷺ"),
    ("Mother of the Believers", "اُمّ المؤمنین"),
    ("Mother of the Prophet", "نبی ﷺ کی والدہ"),
    ("wife of the Prophet", "نبی ﷺ کی زوجہ"),
    ("Wife of the Prophet", "نبی ﷺ کی زوجہ"),
    ("daughter of the Prophet", "نبی ﷺ کی بیٹی"),
    ("Daughter of the Prophet", "نبی ﷺ کی بیٹی"),
    ("grandson of the Prophet", "نبی ﷺ کے نواسے"),
    ("Grandson of the Prophet", "نبی ﷺ کے نواسے"),
    ("Companion of the Prophet", "نبی ﷺ کے صحابی"),
    ("companion of the Prophet", "نبی ﷺ کے صحابی"),
    ("Cousin and son-in-law of the Prophet", "نبی ﷺ کے چچا زاد اور داماد"),
    ("fourth Caliph", "چوتھے خلیفہ"),
    ("Fourth caliph", "چوتھے خلیفہ"),
    ("third Caliph", "تیسرے خلیفہ"),
    ("Third caliph", "تیسرے خلیفہ"),
    ("Second caliph of Islam", "اسلام کے دوسرے خلیفہ"),
    ("second caliph", "دوسرے خلیفہ"),
    ("first Caliph", "پہلے خلیفہ"),
    ("Wife of Pharaoh", "فرعون کی بیوی"),
    ("Queen of Sheba", "ملکۂ سبا"),
    ("Prophet mentioned in the Qur'an", "قرآن میں مذکور نبی"),
    ("Prophet mentioned in the Quran", "قرآن میں مذکور نبی"),
    ("Quranic prophet", "قرآنی نبی"),
    ("Wet-nurse of the Prophet", "نبی ﷺ کی دایہ"),
    ("one of the ten promised paradise", "عشرۂ مبشرہ میں سے"),
    ("Compiler of Ṣaḥīḥ al-Bukhārī", "صحیح بخاری کے جامع"),
    ("Hadith scholar", "محدث"),
    ("Islamic scholar", "اسلامی عالم"),
    ("Poet-philosopher", "شاعر اور فلسفی"),
    ("spiritual father of Pakistan", "پاکستان کے روحانی باپ"),
    ("First human and first prophet in Islamic tradition", "اسلامی روایت میں پہلا انسان اور پہلا نبی"),
    ("King and prophet", "بادشاہ اور نبی"),
    ("martyr at Karbala", "کربلا کے شہید"),
    ("third Shia Imam", "تیسرے شیعہ امام"),
]
ROLE_PHRASES.sort(key=lambda kv: len(kv[0]), reverse=True)

PLACE_UR = {
    "Arabia": "جزیرہ عرب",
    "Mecca": "مکہ",
    "Medina": "مدینہ",
    "Makkah": "مکہ",
    "Madinah": "مدینہ",
    "British India / Pakistan": "برطانوی ہند / پاکستان",
    "British India": "برطانوی ہند",
    "Pakistan": "پاکستان",
    "India": "ہندوستان",
    "United States": "ریاستہائے متحدہ",
    "Baghdad": "بغداد",
    "Khurasan": "خراسان",
    "Egypt": "مصر",
    "Syria": "شام",
    "Andalusia": "اندلس",
    "Persia": "ایران",
    "Iran": "ایران",
    "Turkey": "ترکی",
    "Ottoman": "عثمانی",
    "Gaza": "غزہ",
    "Tehran": "تہران",
    "Cordoba": "قرطبہ",
    "Damascus": "دمشق",
    "Kufa": "کوفہ",
    "Basra": "بصرہ",
    "Yemen": "یمن",
    "Morocco": "مراکش",
    "Tunisia": "تیونس",
    "Algeria": "الجزائر",
}


def esc(text: str) -> str:
    return html_escape(text or "", quote=True)


def ur_num(n) -> str:
    return str(n).translate(DIGITS)


def unescape(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    for a, b in (
        ("&#x27;", "'"), ("&#39;", "'"), ("&amp;", "&"), ("&nbsp;", " "),
        ("&ldquo;", "“"), ("&rdquo;", "”"), ("&rsquo;", "’"), ("&quot;", '"'),
        ("&mdash;", "—"), ("&ndash;", "–"), ("&apos;", "'"),
    ):
        text = text.replace(a, b)
    return re.sub(r"\s+", " ", text).strip()


def norm_ar(text: str) -> str:
    text = re.sub(r"[\u064B-\u065F\u0670\u0640]", "", text or "")
    text = text.replace("ي", "ی").replace("ك", "ک").replace("ة", "ہ")
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    return re.sub(r"\s+", "", text)


def is_stub(html: str) -> bool:
    head = html[:2500]
    return 'http-equiv="refresh"' in head or "window.location.replace" in head


def field(html: str, name: str) -> str:
    m = re.search(rf'data-asr-field="{re.escape(name)}">(.*?)</dd>', html, re.S)
    return unescape(m.group(1)) if m else ""


def clean_spelling(text: str) -> str:
    text = unescape(text).strip().strip("«»\"'“”")
    text = text.strip(" .۔")
    return text


def is_lexical(text: str, spelling: str) -> bool:
    if not text:
        return False
    if "Not recorded" in text or "not recorded" in text.lower():
        return False
    if "املا" in text and ("«" in text or "»" in text or '"' in text):
        return False
    if not re.search(r"[\u0600-\u06FF]", text):
        return False
    if spelling and norm_ar(text) == norm_ar(spelling):
        return False
    return True


def meaning_unestablished(en_meaning: str) -> bool:
    low = (en_meaning or "").lower()
    return "not established" in low or "no definition" in low


def short_meaning(text: str, limit: int = 42) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    bit = re.split(r"[۔.]", text)[0].strip()
    if ":" in bit:
        head = bit.split(":", 1)[0].strip()
        if len(head) >= 8:
            bit = head
    if len(bit) > limit:
        cut = bit[:limit]
        if "،" in cut:
            cut = cut.rsplit("،", 1)[0]
        bit = cut.rstrip()
    return bit


def feminize(text: str) -> str:
    swaps = (
        ("ٹکا ہے", "ٹکی ہے"),
        ("جوڑتا ہے", "جوڑتی ہے"),
        ("گوندتا ہے", "گوندتی ہے"),
        ("اٹھاتا ہے", "اٹھاتی ہے"),
        ("رکھتا ہے", "رکھتی ہے"),
        ("لاتا ہے", "لاتی ہے"),
        ("بناتا ہے", "بناتی ہے"),
        ("لیتا ہے", "لیتی ہے"),
        ("دکھاتا ہے", "دکھاتی ہے"),
        ("کرتا ہے", "کرتی ہے"),
        ("تھامتا ہے", "تھامتی ہے"),
        ("چنتا ہے", "چنتی ہے"),
        ("رہتا ہے", "رہتی ہے"),
        ("حامل", "حاملہ"),
    )
    for a, b in swaps:
        text = text.replace(a, b)
    return text


def ur_origin(origin: str) -> str:
    origin = (origin or "").strip()
    if not origin:
        return "ماخذ میں اصل درج نہیں"
    if origin in ORIGIN_UR:
        return ORIGIN_UR[origin]
    out = origin
    for src, dst in ORIGIN_TOKEN:
        out = re.sub(rf"\b{re.escape(src)}\b", dst, out)
    # If Latin words remain, keep the Urdu we could make and drop leftover English clauses.
    if re.search(r"[A-Za-z]{3,}", out):
        mapped = ORIGIN_UR.get(origin.split("(")[0].strip())
        if mapped:
            return mapped
        return "ماخذ کے مطابق: " + origin
    return out.replace("→", "سے").replace("/", " / ")


def gender_pair(gender: str):
    return GENDER.get((gender or "").strip(), ("", ""))


def digital_root(n: int) -> int:
    while n > 9:
        n = sum(int(c) for c in str(n))
    return n


def abjad_sum(glyphs: list[str]) -> int | None:
    total = 0
    seen = 0
    for g in glyphs:
        for ch in g:
            if ch in ABJAD:
                total += ABJAD[ch]
                seen += 1
            elif "\u0600" <= ch <= "\u06FF" and ch not in "ءًٌٍَُِّْٰ":
                return None
    return total if seen else None


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def translate_opening(sentence: str, name: str) -> str:
    for cre, tmpl in OPENING_PATTERNS:
        if cre.match(sentence):
            return tmpl.format(n=name)
    return ""


def translate_quality(fragment: str) -> str:
    fragment = re.sub(r"\s+", " ", fragment).strip(" ,.")
    if fragment in QUALITY_UR:
        return QUALITY_UR[fragment]
    for src in sorted(QUALITY_UR, key=len, reverse=True):
        if src in fragment or fragment in src:
            return QUALITY_UR[src]
    return ""


def epithet_ur(ep: str) -> str:
    ep = ep.strip()
    return EPITHET_UR.get(ep, "")


def _name_bit(dn: str, ep: str, quality: str) -> tuple[str, bool]:
    ar = DIVINE_AR.get(dn, "")
    ep_u = epithet_ur(ep)
    q_u = translate_quality(quality)
    fell = not ar or not q_u
    if not ar:
        ar = dn
    if ep_u and q_u:
        return f"{ar}، {ep_u}، یعنی {q_u}", fell
    if ep_u:
        return f"{ar}، {ep_u}", True
    return ar, True


def translate_synthesis(text: str, name: str, feminine: bool = False) -> tuple[str, bool]:
    """Return Urdu synthesis and whether a clause fell back."""
    if not text:
        return "", True
    sents = sentences(text)
    opening = translate_opening(sents[0], name) if sents else ""
    middle = MIDDLE_UR.get(sents[1], "") if len(sents) > 1 else ""
    fell = not opening
    divine = ""
    pair_res = [
        re.compile(
            r"((?:Al|Dhul)-[A-Za-z']+), (the [^,]+), carried (?:by (?:a person|the bearer) )?as (.+?), "
            r"(?:and beside it|joined by) "
            r"((?:Al|Dhul)-[A-Za-z']+), (the [^,]+), adding (.+?)(?:\.|$)"
        ),
        re.compile(
            r"((?:Al|Dhul)-[A-Za-z']+), (the [^,]+), giving the bearer (.+?), softened by "
            r"((?:Al|Dhul)-[A-Za-z']+), (the [^,]+), carried as (.+?)(?:\.|$)"
        ),
        re.compile(
            r"((?:Al|Dhul)-[A-Za-z']+), (the [^,]+), meaning the (?:person|bearer) (?:carries|is trusted with) (.+?), "
            r"(?:joined by|softened by) ((?:Al|Dhul)-[A-Za-z']+), (the [^,]+), carried as (.+?)(?:\.|$)"
        ),
    ]
    single_res = [
        re.compile(
            r"((?:Al|Dhul)-[A-Za-z']+), (the [^,]+), calling the person toward (.+?)(?:\.|$)"
        ),
        re.compile(
            r"((?:Al|Dhul)-[A-Za-z']+), (the [^,]+), offering the bearer (.+?)(?:\.|$)"
        ),
        re.compile(
            r"((?:Al|Dhul)-[A-Za-z']+), (the [^,]+), (?:carried (?:by a person )?as|giving the bearer|"
            r"meaning the (?:person|bearer) (?:carries|is trusted with)) (.+?)(?:\.|$)"
        ),
    ]
    matched = False
    for cre in pair_res:
        m = cre.search(text)
        if not m:
            continue
        a, f1 = _name_bit(m.group(1), m.group(2), m.group(3))
        b, f2 = _name_bit(m.group(4), m.group(5), m.group(6))
        divine = f"اس قراءت میں {a} شامل ہے، اور اس کے ساتھ {b}۔"
        fell = fell or f1 or f2
        matched = True
        break
    if not matched:
        for cre in single_res:
            m = cre.search(text)
            if not m:
                continue
            a, f1 = _name_bit(m.group(1), m.group(2), m.group(3))
            divine = f"اس قراءت میں {a} شامل ہے۔"
            fell = fell or f1
            matched = True
            break
    if not matched and ("Al-" in text or "Dhul-" in text):
        fell = True
    ending = ""
    em = re.search(
        r"A person named .+? ((?:is|lives|tends|carries|contains|walks|keeps|holds|comes|meets) .+)$",
        text,
    )
    if em:
        ending = ENDING_UR.get(em.group(1), "")
        if not ending:
            fell = True
    parts = [p for p in (opening, middle, divine, ending) if p]
    if not parts:
        line = (
            f"{name} کی حرفی قراءت ان حروف کے عناصر کو جوڑ کر پڑھی جاتی ہے۔ "
            "یہ علم الحروف کی تعبیر ہے، غور کے لیے، نہ کوئی حکم۔"
        )
        return feminize(line) if feminine else line, True
    parts.append("یہ علم الحروف کی تعبیری قراءت ہے، غور کے لیے، نہ کوئی حکم اور نہ کوئی پیشین گوئی۔")
    line = " ".join(parts)
    if feminine:
        line = feminize(line)
    return line, fell


def quran_answer(ans: str, root: str, name: str) -> str:
    if not ans:
        return ""
    low = ans.lower()
    verses = re.findall(r"\b(\d{1,3}:\d{1,3}(?:\s*[–-]\s*\d{1,3})?)\b", ans)
    verse_txt = ""
    if verses:
        bits = []
        for v in verses[:6]:
            bits.append(ur_num(v.replace(" ", "")))
        verse_txt = "، ".join(bits)
    not_direct = (
        "does not appear" in low
        or "not directly mentioned" in low
        or low.startswith("no.")
        or low.startswith("no ")
    )
    if not_direct:
        line = f"{name} قرآن میں براہِ راست نام لے کر نہیں آیا۔"
        if root and "root" in low and "appear" in low:
            line += f" جذر {root}، جس سے یہ نام بنا ہے، قرآن کی لغت میں آتا ہے؛ نام خود کوئی آیت نہیں۔"
        elif "no established" in low and "root" in low:
            line += " انگریزی ماخذ اس نام کا کوئی مستند قرآنی جذر بھی نہیں دیتا۔"
        elif verse_txt:
            line += f" ماخذ ان آیتوں کا حوالہ دیتا ہے: {verse_txt}۔"
        return line
    if verse_txt and any(w in low for w in ("appear", "names", "named", "mentioned")):
        return f"انگریزی ماخذ کے مطابق اس نام یا اس کے لفظ کا ذکر قرآن میں یہاں ہے: {verse_txt}۔"
    return ""


def translate_role(blurb: str) -> str:
    if not blurb:
        return ""
    out = blurb
    for src, dst in ROLE_PHRASES:
        out = out.replace(src, dst)
    # Drop leftover English sentences rather than guess them.
    latin_words = re.findall(r"[A-Za-z]{3,}", out)
    # Allow a few proper-name leftovers.
    if len(latin_words) > 2:
        return ""
    out = re.sub(r"\s+", " ", out).strip(" ;.")
    if not re.search(r"[\u0600-\u06FF]", out):
        return ""
    return out


def translate_place(place: str) -> str:
    place = place.strip()
    if place in PLACE_UR:
        return PLACE_UR[place]
    out = place
    for src, dst in sorted(PLACE_UR.items(), key=lambda kv: len(kv[0]), reverse=True):
        out = out.replace(src, dst)
    return out


def parse_bearers(html: str) -> list[dict]:
    m = re.search(r"BEARERS:START -->(.*?)<!-- BEARERS:END", html, re.S)
    if not m:
        m = re.search(r'<ul class="bearers-list".*?</ul>', html, re.S)
        block = m.group(0) if m else ""
    else:
        block = m.group(1)
    people = []
    for li in re.findall(r"<li\b.*?</li>", block, re.S):
        strong = re.search(r"<strong[^>]*>(.*?)</strong>", li, re.S)
        name = unescape(strong.group(1)) if strong else ""
        spans = [unescape(s) for s in re.findall(r"<span[^>]*>(.*?)</span>", li, re.S)]
        spans = [s for s in spans if s and s != "·"]
        dates = spans[0] if spans else ""
        place = spans[1] if len(spans) > 1 else ""
        divs = [unescape(d) for d in re.findall(r"<div[^>]*>(.*?)</div>", li, re.S)]
        blurb = ""
        for d in reversed(divs):
            if d and d != dates and d != place and not re.fullmatch(r"[\d–\-\sCEAH]+", d):
                blurb = d
                break
        if name:
            people.append({"name": name, "dates": dates, "place": place, "blurb": blurb})
    return people


def ur_bearer_html(html: str) -> str:
    m = re.search(r'<ul class="bearers-list".*?</ul>', html, re.S)
    if not m:
        return ""
    block = m.group(0)
    if len(re.findall(r"[\u0600-\u06FF]", block)) < 12:
        return ""
    return block


def parse_related(html: str) -> list[str]:
    rel = []
    for m in re.finditer(
        r'href="(?:https://asrnaam.com)?/names/([a-z0-9-]+)/"[^>]*class="related-(?:card|name)',
        html,
    ):
        rel.append(m.group(1))
    for m in re.finditer(
        r'class="related-card[^"]*"[^>]*href="(?:https://asrnaam.com)?/names/([a-z0-9-]+)/"',
        html,
    ):
        rel.append(m.group(1))
    out = []
    for s in rel:
        if s not in out:
            out.append(s)
    return out


def parse_variants(html: str) -> list[tuple[str, str]]:
    """Return (slug, community label) from spelling chips."""
    out = []
    for m in re.finditer(r'href="/names/([a-z0-9-]+)/"[^>]*class="spelling-chip[^"]*"[^>]*>(.*?)</a>', html, re.S):
        slug, inner = m.group(1), m.group(2)
        comm = ""
        cm = re.search(r"chip-community[^>]*>(.*?)<", inner, re.S)
        if cm:
            comm = unescape(cm.group(1))
        out.append((slug, comm))
    return out


def letter_glyphs(html: str) -> list[str]:
    glyphs = re.findall(
        r'class="asr-v2-letter-arabic"[^>]*>(.*?)</span>',
        html,
        re.S,
    )
    return [unescape(g) for g in glyphs]


def section_inner(html: str, cls: str) -> str:
    m = re.search(rf'<section class="asr-v2 {cls}"[^>]*>(.*?)</section>', html, re.S)
    return m.group(1) if m else ""


def paras_of(fragment: str) -> list[str]:
    return [unescape(p) for p in re.findall(r"<p>(.*?)</p>", fragment, re.S)]


GENERIC_MARKERS = (
    "ایک عربی الاصل نام ہے",
    "مختلف مسلم خطوں میں رائج رہا ہے",
    "لطیف مفہوم کو زمانوں تک",
    "اس نام کی لغوی اصل ہے",
    "کے ساتھ اس کا تعلق واضح ہوتا ہے",
    "اندرونی آہنگ کی ایک مختصر تصویر",
)


def legacy_bios(html: str) -> str:
    """Keep hand-written biography blocks on the scholar pages."""
    kept = re.findall(r'<section class="asr-v2 asr-v2-bio">.*?</section>', html, re.S)
    if kept:
        return "".join(kept)
    parts = []
    for m in re.finditer(
        r"<h2(?![^>]*class=\"asr-v2-title\")[^>]*>(.*?)</h2>\s*<div class=\"prose\">(.*?)</div>",
        html,
        re.S,
    ):
        title = unescape(m.group(1))
        if not title or not re.search(r"[\u0600-\u06FF]", title):
            continue
        body = m.group(2).strip()
        if not re.search(r"[\u0600-\u06FF]", body):
            continue
        parts.append(
            f'<section class="asr-v2 asr-v2-bio"><h2 class="asr-v2-title">{esc(title)}</h2>'
            f'<div class="prose">{body}</div></section>'
        )
    return "".join(parts)


QURAN_NOTE_MARKERS = (
    "قرآن میں براہِ راست نام لے کر نہیں آیا",
    "انگریزی ماخذ کے مطابق اس نام یا اس کے لفظ کا ذکر قرآن میں",
)


def is_quran_note(text: str) -> bool:
    return any(marker in (text or "") for marker in QURAN_NOTE_MARKERS)


def usable_paras(paras: list[str]) -> list[str]:
    kept = []
    for p in paras:
        if len(p) < 25:
            continue
        if any(g in p for g in GENERIC_MARKERS):
            continue
        if not re.search(r"[\u0600-\u06FF]", p):
            continue
        kept.append(p)
    return kept


def faq_answers(html: str) -> dict[str, str]:
    out = {}
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if data.get("@type") != "FAQPage":
            continue
        for q in data.get("mainEntity") or []:
            name = q.get("name") or ""
            text = ((q.get("acceptedAnswer") or {}).get("text")) or ""
            out[name] = unescape(text)
    return out


def has_hadith(faq: dict[str, str]) -> bool:
    blob = " ".join(faq.values()).lower()
    return "abu dawud" in blob or "abu dawūd" in blob or "resurrection" in blob


def page_exists(lang: str, slug: str) -> bool:
    if lang == "en":
        path = ROOT / "names" / slug / "index.html"
    else:
        path = ROOT / lang / "names" / slug / "index.html"
    if not path.exists():
        return False
    html = path.read_text(errors="replace")
    return not is_stub(html)


def hreflang_links(slug: str) -> str:
    pairs = [("en", f"{SITE}/names/{slug}/")]
    if page_exists("ur", slug):
        pairs.append(("ur", f"{SITE}/ur/names/{slug}/"))
    for lang in ("ar", "hi", "tr"):
        if page_exists(lang, slug):
            pairs.append((lang, f"{SITE}/{lang}/names/{slug}/"))
    lines = [f'<link rel="alternate" hreflang="{lang}" href="{href}"/>' for lang, href in pairs]
    lines.append(f'<link rel="alternate" hreflang="x-default" href="{SITE}/names/{slug}/"/>')
    return "\n".join(lines)


def build_faq(name, roman, meaning, origin, gender_word, pron, ipa, syllables, total, reduced, lucky, root, quran, letter_line, hadith) -> list[dict]:
    faqs = []
    faqs.append((
        f"{name} نام کا مطلب کیا ہے؟",
        f"{name} کا مطلب ہے: {meaning}",
    ))
    if quran:
        faqs.append((f"کیا {name} قرآن میں آیا ہے؟", quran))
    gline = f"{name} {gender_word} نام ہے۔" if gender_word else f"{name} کی صنف ماخذ میں صاف درج نہیں۔"
    faqs.append((
        f"{name} کا اصل کیا ہے، اور یہ لڑکوں کا نام ہے یا لڑکیوں کا؟",
        f"اصل {origin} ہے۔ {gline}",
    ))
    pron_bits = f"انگریزی قرات میں اسے {pron} لکھا جاتا ہے" if pron else "انگریزی قرات اوپر درج نہیں"
    if syllables:
        pron_bits += f"، {ur_num(syllables)} ہجے"
    if ipa:
        pron_bits += f"۔ آوازی لکھائی {ipa} ہے"
    faqs.append((f"{name} کا تلفظ کیسے ہے؟", pron_bits + "۔"))
    if total is not None:
        ab = f"حسابِ جُمل کے مطابق دکھائے ہوئے حروف کا مجموعہ {ur_num(total)} ہے، اور اس کا مختصر عدد {ur_num(reduced)} ہے۔"
        if lucky and str(lucky) != str(reduced):
            ab += f" انگریزی صفحے پر خوش نصیب عدد {ur_num(lucky)} درج ہے۔"
        else:
            ab += " یہی اس نام کا ابجد خوش نصیب عدد ہے۔"
        faqs.append((f"علم الحروف میں {name} کی عددی قیمت کیا ہے؟", ab))
    elif lucky:
        faqs.append((
            f"علم الحروف میں {name} کا خوش نصیب عدد کیا ہے؟",
            f"انگریزی صفحے پر خوش نصیب عدد {ur_num(lucky)} درج ہے۔",
        ))
    if meaning == UNESTABLISHED:
        editorial = (
            f"اَثَر نام کی ادارتی رائے میں (یہ فتویٰ نہیں): {name} کا لغوی مطلب طے نہیں ہوا، "
            "اس لیے یہ سائٹ یہ نہیں کہہ سکتی کہ اس کا کوئی قائم شدہ اسلامی معنی ہے۔"
        )
    else:
        editorial = (
            f"اَثَر نام کی ادارتی رائے میں جی ہاں (یہ فتویٰ نہیں): {name} مسلم روایت میں قدر والا نام ہے"
            + (f"، مطلب: {short_meaning(meaning, 80)}" if meaning else "")
            + "۔"
        )
    if hadith:
        editorial += " نبی ﷺ نے فرمایا: «تم قیامت کے دن اپنے ناموں سے پکارے جاؤ گے، پس اپنے نام اچھے رکھو» (ابو داؤد)۔"
    editorial += " حرفی قراءت غور کے لیے ہے، قائم شدہ حکم نہیں۔"
    faqs.append((f"کیا {name} اچھا اسلامی نام ہے؟", editorial))
    if letter_line:
        faqs.append((
            f"علم الحروف میں {name} کی قراءت کیا کہتی ہے؟",
            letter_line + " یہ ابن عربی کی علم الحروف روایت کی تعبیر ہے، غور کے لیے، نہ کوئی حکم۔",
        ))
    faqs.append((
        f"{name} کے ساتھ کون سے نام جڑتے ہیں؟",
        f"بہن بھائی کے نام خاندان کا ذوق ہے۔ نیچے متعلقہ نام {name} سے حرف، جذر، یا روایت میں ملتے ہیں۔ یہ جوڑ کوئی قاعدہ نہیں۔",
    ))
    root_bit = f" جذر {root} ہے۔" if root else ""
    faqs.append((
        f"{roman} اردو میں کیسے لکھا جاتا ہے؟",
        f"{roman} اردو میں {name} لکھا جاتا ہے۔{root_bit}",
    ))
    return [{"q": q, "a": a} for q, a in faqs]


def render_faq_html(faqs: list[dict]) -> str:
    bits = []
    for item in faqs:
        bits.append(
            f'<details class="asr-faq-item"><summary>{esc(item["q"])}</summary>'
            f'<div class="prose"><p>{esc(item["a"])}</p></div></details>'
        )
    return "".join(bits)


def faq_json(faqs: list[dict]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "inLanguage": "ur",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["q"],
                "acceptedAnswer": {"@type": "Answer", "text": item["a"]},
            }
            for item in faqs
        ],
    }


def cross_links(slug: str) -> str:
    bits = []
    bits.append(f'<a href="/names/{slug}/" hreflang="en" lang="en">English</a>')
    if page_exists("ar", slug):
        bits.append(f'<a href="/ar/names/{slug}/" hreflang="ar" lang="ar" dir="rtl">العربية</a>')
    if page_exists("hi", slug):
        bits.append(f'<a href="/hi/names/{slug}/" hreflang="hi" lang="hi">हिन्दी</a>')
    if page_exists("tr", slug):
        bits.append(f'<a href="/tr/names/{slug}/" hreflang="tr" lang="tr">Türkçe</a>')
    return " · ".join(bits)


def syllable_count(pron: str, pron_html: str) -> str:
    m = re.search(r"(\d+)\s+syllables", pron_html)
    if m:
        return m.group(1)
    if pron:
        chunks = re.split(r"[-·.\s]+", pron.split("/")[0].strip())
        chunks = [c for c in chunks if c]
        if 1 < len(chunks) <= 8:
            return str(len(chunks))
    return ""


def extract_ipa(pron: str, pron_html: str) -> str:
    m = re.search(r"(/(?:[^/<]{1,40})/)", pron + " " + unescape(pron_html))
    return m.group(1) if m else ""


def pron_plain(pron: str) -> str:
    pron = pron.split("/")[0].strip()
    return pron


def update_head(html: str, slug: str, title: str, desc: str, faqs: list[dict], og_image: str) -> str:
    html = re.sub(r"<title>.*?</title>", f"<title>{esc(title)}</title>", html, count=1, flags=re.S)
    html = re.sub(
        r'<meta name="description" content="[^"]*"',
        f'<meta name="description" content="{esc(desc)}"',
        html,
        count=1,
    )
    for prop in ("og:title", "twitter:title"):
        html = re.sub(
            rf'<meta property="{prop}" content="[^"]*"',
            f'<meta property="{prop}" content="{esc(title)}"',
            html,
            count=1,
        )
        html = re.sub(
            rf'<meta name="{prop}" content="[^"]*"',
            f'<meta name="{prop}" content="{esc(title)}"',
            html,
            count=1,
        )
    for prop in ("og:description", "twitter:description"):
        html = re.sub(
            rf'<meta property="{prop}" content="[^"]*"',
            f'<meta property="{prop}" content="{esc(desc)}"',
            html,
            count=1,
        )
        html = re.sub(
            rf'<meta name="{prop}" content="[^"]*"',
            f'<meta name="{prop}" content="{esc(desc)}"',
            html,
            count=1,
        )
    html = re.sub(
        r'<meta property="article:modified_time" content="[^"]*"\s*/?>',
        f'<meta property="article:modified_time" content="{TODAY}"/>',
        html,
        count=1,
    )

    def _touch_modified(m):
        tag = m.group(0)
        if "dateModified" not in tag:
            return tag
        if "datetime=" not in tag:
            return tag
        return re.sub(r'datetime="[^"]*"', f'datetime="{TODAY}T00:00:00+00:00"', tag, count=1)

    html = re.sub(r"<time\b[^>]*>", _touch_modified, html)
    block = hreflang_links(slug)
    head, sep, tail = html.partition("</head>")
    if sep:
        head = re.sub(r'<link rel="alternate" hreflang="[^"]+" href="[^"]+"\s*/>\s*', "", head)
        if 'hreflang="x-default"' not in head:
            head = head.replace("</title>", "</title>\n" + block + "\n", 1)
        html = head + sep + tail
    if 'rel="canonical"' not in html:
        html = html.replace("</title>", f"</title>\n<link rel=\"canonical\" href=\"{SITE}/ur/names/{slug}/\">", 1)

    faq_payload = json.dumps(faq_json(faqs), ensure_ascii=False)
    saw_faq = False

    def _ld(m):
        nonlocal saw_faq
        raw = m.group(1)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return m.group(0)
        if data.get("@type") == "FAQPage":
            saw_faq = True
            return f'<script type="application/ld+json">{faq_payload}</script>'
        if data.get("@type") == "Article":
            data["headline"] = title
            data["inLanguage"] = "ur"
            data["mainEntityOfPage"] = f"{SITE}/ur/names/{slug}/"
            if og_image:
                data["image"] = og_image
                pub = data.get("publisher") or {}
                logo = pub.get("logo") if isinstance(pub, dict) else None
                if isinstance(logo, dict):
                    logo["url"] = og_image
            return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'
        if data.get("@type") == "BreadcrumbList":
            try:
                data["itemListElement"][-1]["name"] = title.split(" نام")[0]
            except (KeyError, IndexError, TypeError):
                pass
            return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'
        return m.group(0)

    html = re.sub(r"<script type=\"application/ld\+json\">(.*?)</script>", _ld, html, flags=re.S)
    if not saw_faq:
        html = html.replace(
            "</head>",
            f'<script type="application/ld+json">{faq_payload}</script>\n</head>',
            1,
        )
    if "asr-enhance.css" not in html:
        html = html.replace(
            "</head>",
            '<link rel="stylesheet" href="/asr-enhance.css?v=20260901">\n</head>',
            1,
        )
    if 'id="ur-type"' not in html:
        html = html.replace("</head>", TYPE_CSS + "\n</head>", 1)
    if 'lang="ur"' not in html[:200]:
        html = html.replace("<html", '<html lang="ur" dir="rtl"', 1)
    elif 'dir="rtl"' not in html[:250]:
        html = html.replace('lang="ur"', 'lang="ur" dir="rtl"', 1)
    return html


def og_image_of(html: str, slug: str) -> str:
    m = re.search(r'<meta property="og:image" content="([^"]+)"', html)
    if m:
        return m.group(1)
    return f"{SITE}/og/{slug}.png"


def render_main(ctx: dict) -> str:
    name = ctx["name"]
    arabic = ctx["arabic"]
    meaning = ctx["meaning"]
    origin = ctx["origin_ur"]
    gender_word, gender_pl = ctx["gender_word"], ctx["gender_pl"]
    badge = f"مسلم {gender_pl} کا نام" if gender_pl else "مسلم نام"
    badge += " &nbsp;·&nbsp; علم الحروف کی قراءت"
    root = ctx["root"]
    pron = ctx["pron"]
    ipa = ctx["ipa"]
    syllables = ctx["syllables"]
    total, reduced, lucky = ctx["total"], ctx["reduced"], ctx["lucky"]

    facts = []
    facts.append(("لغوی معنی", meaning, True))
    facts.append(("اصل", origin, False))
    if gender_word:
        facts.append(("صنف", gender_word, False))
    if root:
        facts.append(("عربی جذر", root, True))
    facts.append(("اردو املا", name, False))
    if arabic:
        facts.append(("عربی املا", arabic, False))
    if pron:
        facts.append(("تلفظ", pron + (f" · {ipa}" if ipa else ""), False))
    if ctx["glyphs"]:
        facts.append(("حروف کی تعداد", ur_num(len(ctx["glyphs"])), True))
        facts.append(("حروف", " · ".join(ctx["glyphs"]), True))
    if total is not None:
        lucky_show = ur_num(reduced if not lucky or str(lucky) == str(reduced) else lucky)
        facts.append(("ابجد / خوش نصیب عدد", f"مجموعہ {ur_num(total)} · مختصر {lucky_show}", True))
    elif lucky:
        facts.append(("خوش نصیب عدد", ur_num(lucky), False))

    fact_html = []
    for label, value, wide in facts:
        cls = ' class="qf-row full-row" style="grid-column:1/-1;"' if wide else ' class="qf-row"'
        # Pronunciation value may contain Latin; keep the value as text.
        fact_html.append(
            f"<div{cls}><span class=\"qf-label\">{esc(label)}</span>"
            f"<span class=\"qf-value\">{esc(value)}</span></div>"
        )

    parts = []
    parts.append("<article>")
    parts.append(
        f'<div class="hero"><div class="arabic-name" lang="ar" dir="rtl">{esc(arabic or name)}</div>'
        f'<div class="name-badge">{badge}</div>'
        f"<h1>{esc(name)} نام کا مطلب</h1>"
        f'<p class="hero-subtitle">{esc(short_meaning(meaning, 90))}</p></div>'
    )
    parts.append('<div class="content">')
    parts.append(f'<aside class="quick-facts" aria-label="فوری حقائق">{"".join(fact_html)}</aside>')
    parts.append('<div class="asr-layout-v2">')

    # 1 root
    kept_root = [p for p in ctx["root_paras"] if not is_quran_note(p)]
    if meaning == UNESTABLISHED:
        kept_root = [p for p in kept_root if "جی ہاں" not in p and "قدر والا نام" not in p]
    root_paras = "".join(f"<p>{esc(p)}</p>" for p in kept_root)
    if not root_paras:
        if meaning == UNESTABLISHED:
            root_paras = (
                f"<p>{esc(name)} کا کوئی قائم شدہ لغوی مطلب ماخذ میں نہیں۔ "
                "حروف اوپر دکھائی گئی املا کے مطابق پڑھے گئے ہیں۔</p>"
            )
        elif root:
            root_paras = f"<p>جذر <strong>{esc(root)}</strong> اس نام کی لغوی اصل ہے۔ مطلب: {esc(meaning)}</p>"
        else:
            root_paras = f"<p>{esc(name)} کا مطلب ہے: {esc(meaning)} اصل {esc(origin)} ہے۔</p>"
    parts.append(
        '<section class="asr-v2 asr-v2-root"><p class="asr-v2-kicker">حصہ ۱ · عربی جذر</p>'
        f'<h2 class="asr-v2-title">نام کہاں سے آتا ہے</h2>'
        + (f'<div class="asr-v2-root-glyph" lang="ar" dir="rtl">{esc(root)}</div>' if root else "")
        + f'<div class="prose">{root_paras}</div>'
    )
    if meaning == UNESTABLISHED:
        mq = (
            f"یہ کوئی دینی فتویٰ نہیں۔ {esc(name)} کا لغوی مطلب ماخذ میں طے نہیں ہوا، "
            "اس لیے یہ سائٹ یہ نہیں کہہ سکتی کہ اس کا کوئی قائم شدہ اسلامی معنی ہے۔ "
            f"اصل {esc(origin)} درج ہے، مگر یہ قائم شدہ لغوی مطلب نہیں۔"
        )
    else:
        mq = (
            f"سائٹ کی ادارتی رائے میں جی ہاں (یہ کوئی دینی فتویٰ نہیں)، {esc(name)} "
            f"مسلمانوں میں رائج نام ہے، اصل {esc(origin)} ہے۔ "
            f"رائج مطلب: {esc(short_meaning(meaning, 110))}۔ "
            "اسلامی روایت نام میں اچھا معنی چاہتی ہے، اور یہ کہ وہ اللہ کے مخصوص ناموں میں سے نہ ہو۔"
        )
    parts.append(
        f'<div class="asr-mq"><span class="asr-mq-q">کیا {esc(name)} اسلامی نام ہے؟</span>'
        f'<p class="asr-mq-a">{mq}</p></div>'
    )
    parts.append("</section>")
    parts.append(DIV)

    # 2 letters
    grid = ctx["grid"] or "<p>حرفی خانے اس صفحے کے موجودہ مواد میں نہیں ملے۔</p>"
    letter_paras = "".join(f"<p>{esc(p)}</p>" for p in ctx["letter_paras"])
    if not letter_paras and ctx["glyphs"]:
        letter_paras = f"<p>نام کے حروف: {'، '.join(esc(g) for g in ctx['glyphs'])}۔ ہر حرف اوپر اپنے عنصر اور اسم کے ساتھ پڑھا گیا ہے۔</p>"
    parts.append(
        '<section class="asr-v2 asr-v2-letters"><p class="asr-v2-kicker">حصہ ۲ · علم الحروف</p>'
        '<h2 class="asr-v2-title">حرف بہ حرف پڑھیں</h2>'
        f'{grid}<div class="prose">{letter_paras}</div></section>'
    )
    parts.append(DIV)

    # 3 synthesis
    if ctx["synthesis"]:
        parts.append(
            '<section class="asr-v2 asr-v2-synthesis"><p class="asr-v2-kicker">حصہ ۳ · قراءت کا خلاصہ</p>'
            '<h2 class="asr-v2-title">یہ قراءت حامل سے کیا کہتی ہے</h2>'
            f'<div class="prose"><p>{esc(ctx["synthesis"])}</p></div></section>'
        )
        parts.append(DIV)

    # 4 common meaning
    dict_bits = [f"<p>{esc(name)} کا عام مطلب ہے: {esc(meaning)}</p>"]
    seen_paras = set()
    for p in ctx["dict_paras"]:
        if is_quran_note(p):
            continue
        if meaning[:24] and meaning[:24] in p:
            continue
        key = re.sub(r"\s+", " ", p).strip()
        if key in seen_paras:
            continue
        seen_paras.add(key)
        dict_bits.append(f"<p>{esc(p)}</p>")
    quran = ctx["quran"]
    if quran and not any(quran in unescape(bit) or is_quran_note(unescape(bit)) for bit in dict_bits):
        dict_bits.append(f"<p>{esc(quran)}</p>")
    parts.append(
        '<section class="asr-v2 asr-v2-dict"><p class="asr-v2-kicker">حصہ ۴ · عام معنی</p>'
        '<h2 class="asr-v2-title">اس نام کا عام معنی</h2>'
        f'<div class="prose">{"".join(dict_bits)}</div></section>'
    )
    parts.append(DIV)

    # 5 bearers
    if ctx["bearers_html"]:
        parts.append(
            '<section class="asr-v2 asr-v2-bearers"><p class="asr-v2-kicker">حصہ ۵ · حاملین</p>'
            '<h2 class="asr-v2-title">یہ نام کس نے اٹھایا</h2>'
            f'{ctx["bearers_html"]}</section>'
        )
        parts.append(DIV)

    # 6 pronunciation
    pron_inner = ""
    if pron or ipa:
        syl = f" · {ur_num(syllables)} ہجے" if syllables else ""
        ipa_html = f'<div style="margin-top:.35rem;">آوازی لکھائی <code dir="ltr">{esc(ipa)}</code></div>' if ipa else ""
        pron_inner = (
            f'<div class="asr-pron" role="note"><span class="qf-label">تلفظ</span>'
            f'<div dir="ltr" lang="en" style="font-size:1.15rem;margin-top:.25rem;"><strong>{esc(pron)}</strong></div>'
            f'<p style="margin:.45rem 0 0;">انگریزی قرات: <span dir="ltr" lang="en">{esc(pron)}</span>'
            + (f"، {ur_num(syllables)} ہجے۔" if syllables else "۔")
            + "</p>"
            + ipa_html
            + "</div>"
        )
    else:
        pron_inner = "<p>اس نام کی الگ آوازی لکھائی ماخذ میں درج نہیں۔</p>"
    parts.append(
        '<section class="asr-v2 asr-v2-pron"><p class="asr-v2-kicker">حصہ ۶ · تلفظ</p>'
        f'<h2 class="asr-v2-title">{esc(name)} کا تلفظ</h2>{pron_inner}</section>'
    )

    # variants
    if ctx["variants_html"]:
        parts.append(DIV)
        parts.append(
            '<section class="asr-v2 asr-v2-variants"><p class="asr-v2-kicker">حصہ ۷ · املائیں</p>'
            f'<h2 class="asr-v2-title">{esc(name)} مسلم دنیا میں</h2>'
            '<div class="prose"><p>وہی عربی نام مختلف خطوں میں مختلف رومن املا لیتا ہے۔ حروف اور جذر وہی رہتے ہیں۔</p></div>'
            f'{ctx["variants_html"]}</section>'
        )

    if ctx.get("bio_html"):
        parts.append(DIV)
        parts.append(ctx["bio_html"])
    # FAQ
    parts.append(DIV)
    parts.append(
        '<section class="asr-v2 asr-faq"><h2 class="asr-v2-title">اکثر پوچھے گئے سوالات</h2>'
        f'{ctx["faq_html"]}</section>'
    )
    parts.append(
        f'<section class="asr-v2 asr-crosslang"><p class="prose">یہ نام دیگر زبانوں میں: {ctx["cross"]}</p></section>'
    )
    parts.append("</div>")  # layout

    if ctx["related_html"]:
        parts.append(
            '<div class="related-section" dir="rtl"><p class="section-label" style="margin:3rem 0 1rem;">متعلقہ نام</p>'
            f'{ctx["related_html"]}'
            '<p style="margin-top:1rem;"><a href="/ur/names/">تمام نام دیکھیں (الف–ے)</a></p></div>'
        )
    parts.append("</div></article>")
    # fix the stray syllable line I left as a no-op above; pronunciation block is already complete.
    return "\n".join(parts)


def bearer_block(en_people: list[dict], ur_html: str, spellings: dict) -> str:
    existing = ur_bearer_html(ur_html)
    items = []
    if existing:
        items.append(existing)
    west = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
    seen_dates = set(re.findall(r"\d{3,4}", existing.translate(west)))
    lis = []
    for person in en_people:
        years = re.findall(r"\d{3,4}", person["dates"])
        if years and any(y in seen_dates for y in years):
            continue
        role = translate_role(person["blurb"])
        place = translate_place(person["place"]) if person["place"] else ""
        dates = person["dates"].replace("CE", "عیسوی").replace("AH", "ہجری")
        dates = ur_num(dates) if dates else ""
        meta = " · ".join(x for x in (dates, place) if x)
        # Prefer an Urdu spelling when the bearer is exactly this name's roman form.
        name = person["name"]
        body = f"<strong>{esc(name)}</strong>"
        if meta:
            body += f'<div class="life-note">{esc(meta)}</div>'
        if role:
            body += f"<div>{esc(role)}</div>"
        lis.append(f'<li style="padding:.85rem 0;border-bottom:1px solid var(--border);list-style:none;">{body}</li>')
    if lis:
        items.append('<ul class="bearers-list" style="list-style:none;padding:0;margin:1rem 0 .5rem;">' + "".join(lis) + "</ul>")
    return "".join(items)


def related_block(slug: str, related: list[str], names: dict, ur_full: set[str]) -> str:
    cards = []
    for rel in related:
        if rel == slug or rel not in ur_full:
            continue
        info = names.get(rel) or {}
        label = clean_spelling(info.get("ur") or info.get("u") or rel)
        teaser = info.get("meaning") or ""
        teaser = short_meaning(teaser, 36) if teaser and teaser != UNESTABLISHED else ""
        teaser_html = f'<span class="related-teaser">{esc(teaser)}</span>' if teaser else ""
        cards.append(
            f'<a href="/ur/names/{rel}/" class="related-card"><span class="related-name">{esc(label)}</span>{teaser_html}</a>'
        )
        if len(cards) >= 8:
            break
    if not cards:
        return ""
    return f'<div class="related-grid">{"".join(cards)}</div>'


def variants_block(slug: str, variants: list[tuple[str, str]], names: dict, ur_full: set[str]) -> str:
    chips = []
    for rel, comm in variants:
        if rel == slug or rel not in ur_full:
            continue
        info = names.get(rel) or {}
        label = clean_spelling(info.get("ur") or info.get("u") or rel)
        comm_u = COMMUNITY_UR.get(comm, "")
        extra = f'<span class="life-note">{esc(comm_u)}</span>' if comm_u else ""
        chips.append(f'<a href="/ur/names/{rel}/" class="related-card">{esc(label)}{extra}</a>')
        if len(chips) >= 8:
            break
    if not chips:
        return ""
    return f'<div class="related-grid">{"".join(chips)}</div>'


def resolve_meaning(slug: str, en_html: str, ur_html: str) -> tuple[str, str]:
    """Return (meaning, flag). flag is '' or a short reason."""
    en_meaning = field(en_html, "meaning-dict")
    spelling = clean_spelling(field(en_html, "urdu"))
    stored = field(en_html, "urdu-meaning")
    if meaning_unestablished(en_meaning):
        return UNESTABLISHED, "source-unestablished"
    if is_lexical(stored, spelling):
        return stored, ""
    if slug in REVIEW:
        return REVIEW[slug], "thin-source"
    # Urdu page quick-fact, if it is more than the spelling.
    m = re.search(r'لغوی معنی</span><span class="qf-value">(.*?)</span>', ur_html, re.S)
    page_meaning = unescape(m.group(1)) if m else ""
    if is_lexical(page_meaning, spelling) and (len(norm_ar(page_meaning)) > len(norm_ar(spelling)) + 3 or "،" in page_meaning or ":" in page_meaning):
        return page_meaning, ""
    if slug in GLOSS:
        return GLOSS[slug], ""
    return "", "no-confident-urdu"


def load_name_index() -> dict:
    data = json.loads((ROOT / "names" / "names-index.json").read_text())
    return {row["s"]: row for row in data}


def full_ur_slugs() -> list[str]:
    slugs = []
    for path in sorted((ROOT / "ur" / "names").glob("*/index.html")):
        html = path.read_text(errors="replace")
        if is_stub(html):
            continue
        slugs.append(path.parent.name)
    return slugs


def process(slug: str, names: dict, ur_full: set[str]) -> dict:
    ur_path = ROOT / "ur" / "names" / slug / "index.html"
    en_path = ROOT / "names" / slug / "index.html"
    ur_html = ur_path.read_text(errors="replace")
    en_html = en_path.read_text(errors="replace") if en_path.exists() else ""
    meaning, flag = resolve_meaning(slug, en_html, ur_html)
    spelling = clean_spelling(field(en_html, "urdu")) or clean_spelling((names.get(slug) or {}).get("u") or "")
    if not spelling:
        hm = re.search(r"<h1[^>]*>(.*?)</h1>", ur_html, re.S)
        spelling = clean_spelling(unescape(hm.group(1))) if hm else slug
    if not meaning:
        meaning = f"{spelling} کا پختہ اردو مفہوم موجودہ مواد سے اعتماد کے ساتھ نہیں نکلا۔ انگریزی صفحہ ماخذ ہے۔"
    arabic = ""
    am = re.search(r'<div class="arabic-name"[^>]*>(.*?)</div>', ur_html, re.S)
    if am:
        arabic = unescape(am.group(1))
    if not arabic:
        am = re.search(r'class="asr-name-hero-arabic"[^>]*>(.*?)</div>', en_html, re.S)
        arabic = unescape(am.group(1)) if am else (names.get(slug) or {}).get("a") or ""
    origin = field(en_html, "origin")
    gender = field(en_html, "gender")
    g_word, g_pl = gender_pair(gender)
    root_m = re.search(r'<dd dir="rtl" lang="ar">(.*?)</dd>', en_html, re.S)
    root = unescape(root_m.group(1)) if root_m else ""
    pron = pron_plain(field(en_html, "pronunciation"))
    pron_html = ""
    pm = re.search(r'class="asr-pronunciation".*?</div>\s*</div>|class="asr-pronunciation".*?</div>', en_html, re.S)
    if pm:
        pron_html = pm.group(0)
    ipa = extract_ipa(field(en_html, "pronunciation"), pron_html)
    syllables = syllable_count(pron, en_html)
    lucky = field(en_html, "lucky")
    lucky = re.sub(r"\D", "", lucky)

    grid_m = re.search(r'<div class="asr-v2-letter-grid">.*?</div>', ur_html, re.S)
    if not grid_m:
        grid_m = re.search(r'<div class="asr-v2-letter-grid">.*?</div>', en_html, re.S)
    grid = grid_m.group(0) if grid_m else ""
    glyphs = letter_glyphs(grid or ur_html)
    total = abjad_sum(glyphs)
    reduced = digital_root(total) if total is not None else None

    root_paras = usable_paras(paras_of(section_inner(ur_html, "asr-v2-root")))
    letter_paras = usable_paras(paras_of(section_inner(ur_html, "asr-v2-letters")))
    dict_paras = usable_paras(paras_of(section_inner(ur_html, "asr-v2-dict")))

    syn_m = re.search(r"MEAN-SYNTHESIS:START -->(.*?)<!-- MEAN-SYNTHESIS:END", en_html, re.S)
    syn_text = unescape(syn_m.group(1)) if syn_m else ""
    synthesis, syn_fell = translate_synthesis(syn_text, spelling, feminine=(g_word == "مؤنث"))

    faqs_en = faq_answers(en_html)
    quran = ""
    for q, a in faqs_en.items():
        if "quran" in q.lower() or "qur'an" in q.lower():
            quran = quran_answer(a, root, spelling)
            break

    letter_line = letter_paras[0] if letter_paras else ""
    if not letter_line and glyphs:
        letter_line = "حروف اوپر اپنے عنصر اور اسمِ الٰہی کے ساتھ پڑھے گئے ہیں: " + "، ".join(glyphs) + "۔"
    faqs = build_faq(
        spelling, field(en_html, "meaning-dict") and (names.get(slug) or {}).get("n") or slug,
        meaning, ur_origin(origin), g_word, pron, ipa, syllables,
        total, reduced, lucky, root, quran, letter_line, has_hadith(faqs_en),
    )
    # The roman name argument above is messy. Fix display roman from index.
    roman = (names.get(slug) or {}).get("n") or slug
    faqs = build_faq(
        spelling, roman, meaning, ur_origin(origin), g_word, pron, ipa, syllables,
        total, reduced, lucky, root, quran, letter_line, has_hadith(faqs_en),
    )

    bearers = bearer_block(parse_bearers(en_html), ur_html, names)
    related = related_block(slug, parse_related(en_html), names, ur_full)
    variants = variants_block(slug, parse_variants(en_html), names, ur_full)

    ctx = {
        "name": spelling,
        "arabic": arabic,
        "meaning": meaning,
        "origin_ur": ur_origin(origin),
        "gender_word": g_word,
        "gender_pl": g_pl,
        "root": root,
        "pron": pron,
        "ipa": ipa,
        "syllables": syllables,
        "total": total,
        "reduced": reduced,
        "lucky": lucky,
        "glyphs": glyphs,
        "grid": grid,
        "root_paras": root_paras,
        "letter_paras": letter_paras,
        "dict_paras": dict_paras,
        "synthesis": synthesis,
        "quran": quran,
        "bearers_html": bearers,
        "related_html": related,
        "variants_html": variants,
        "faq_html": render_faq_html(faqs),
        "cross": cross_links(slug),
        "bio_html": legacy_bios(ur_html),
    }
    main = render_main(ctx)
    title_bit = short_meaning(meaning, 36)
    if flag == "source-unestablished":
        title = f"{spelling} نام کا مطلب | اَثَر نام"
    else:
        title = f"{spelling} نام کا مطلب: {title_bit} | اَثَر نام"
    desc_pron = f" تلفظ {pron}۔" if pron else ""
    desc_num = ""
    if total is not None:
        show = lucky or str(reduced)
        desc_num = f" ابجد کا مختصر عدد {ur_num(show)}۔"
    desc = (
        f"{spelling} نام کا مطلب: {short_meaning(meaning, 70)}۔ "
        f"اصل {ur_origin(origin)}"
        + (f"، {g_word} نام۔" if g_word else "۔")
        + desc_pron + desc_num
        + " علم الحروف کی حرف بہ حرف قراءت اَثَر نام پر۔"
    )
    # Keep description from getting huge.
    if len(desc) > 220:
        desc = desc[:217].rstrip() + "…"
    image = og_image_of(ur_html, slug)
    new_html = update_head(ur_html, slug, title, desc, faqs, image)
    new_html, nsubs = re.subn(
        r"<main(?:\s[^>]*)?>.*?</main>",
        '<main id="main-content">\n' + main + "\n</main>",
        new_html,
        count=1,
        flags=re.S,
    )
    if nsubs != 1:
        raise SystemExit(f"did not replace <main> on {slug}")
    # Breadcrumb current name.
    new_html = re.sub(
        r'(<a href="/ur/">نام</a>\s*&nbsp;›&nbsp;\s*<span>)(.*?)(</span>)',
        rf"\1{esc(spelling)}\3",
        new_html,
        count=1,
        flags=re.S,
    )
    ur_path.write_text(new_html)
    return {
        "slug": slug,
        "flag": flag,
        "meaning": meaning,
        "en_meaning": field(en_html, "meaning-dict"),
        "syn_fell": syn_fell,
        "quran": bool(quran),
        "bytes": ur_path.stat().st_size,
    }


def update_sitemap(slugs: list[str]) -> int:
    path = ROOT / "sitemap-ur.xml"
    text = path.read_text()
    added = 0
    for slug in slugs:
        loc = f"{SITE}/ur/names/{slug}/"
        if loc not in text:
            entry = (
                f"  <url><loc>{loc}</loc><lastmod>{TODAY}</lastmod>"
                f"<changefreq>monthly</changefreq><priority>0.7</priority></url>\n"
            )
            text = text.replace("</urlset>", entry + "</urlset>")
            added += 1
        else:
            text = re.sub(
                rf"(<loc>{re.escape(loc)}</loc><lastmod>)[^<]+(</lastmod>)",
                rf"\g<1>{TODAY}\2",
                text,
                count=1,
            )
    path.write_text(text)
    return added


def write_review(rows: list[dict]) -> None:
    flagged = [r for r in rows if r["flag"]]
    lines = [
        "# Urdu meaning review",
        "",
        "Names where a confident lexical Urdu meaning was not taken from existing data.",
        "Pages state only what the English source supports, or say outright that the source does not settle a meaning.",
        "",
        f"Flagged: {len(flagged)}",
        "",
    ]
    for r in flagged:
        lines.append(f"- `{r['slug']}` ({r['flag']}): EN: {r['en_meaning'][:180]}")
        lines.append(f"  - UR used: {r['meaning'][:180]}")
    out = ROOT / "outputs" / "ur-meaning-review.md"
    out.write_text("\n".join(lines) + "\n")


def main(argv: list[str]) -> None:
    only = set()
    if "--only" in argv:
        only = set(argv[argv.index("--only") + 1].split(","))
    names = load_name_index()
    slugs = full_ur_slugs()
    ur_full = set(slugs)
    # First pass: meanings, so related teasers can use them.
    # process() resolves meaning itself; prefill names[slug]['meaning'] and ['ur'].
    for slug in slugs:
        en_path = ROOT / "names" / slug / "index.html"
        ur_path = ROOT / "ur" / "names" / slug / "index.html"
        en_html = en_path.read_text(errors="replace") if en_path.exists() else ""
        ur_html = ur_path.read_text(errors="replace")
        meaning, _flag = resolve_meaning(slug, en_html, ur_html)
        spelling = clean_spelling(field(en_html, "urdu")) or clean_spelling((names.get(slug) or {}).get("u") or "")
        row = names.setdefault(slug, {"s": slug, "n": slug, "u": spelling, "a": ""})
        row["ur"] = spelling or row.get("u") or ""
        row["meaning"] = meaning
    targets = [s for s in slugs if not only or s in only]
    rows = []
    for i, slug in enumerate(targets, 1):
        rows.append(process(slug, names, ur_full))
        if i % 400 == 0:
            print(f"wrote {i}/{len(targets)}", flush=True)
    if not only:
        added = update_sitemap(slugs)
        write_review(rows)
        print("sitemap urls added", added)
    flags = {}
    for r in rows:
        if r["flag"]:
            flags[r["flag"]] = flags.get(r["flag"], 0) + 1
    fell = sum(1 for r in rows if r["syn_fell"])
    quran = sum(1 for r in rows if r["quran"])
    print(f"pages {len(rows)} flags {flags} synthesis_fallback {fell} quran_faq {quran}")
    if rows:
        print("sample", rows[0]["slug"], rows[0]["bytes"])


if __name__ == "__main__":
    main(sys.argv[1:])
