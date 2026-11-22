# Language audit: Urdu, Arabic, Hindi and Turkish pages

Built by `redesign/lang_audit.py` from production (`origin/main`, commit `f91c8d4d1`). 5571 pages read: Urdu 2450, Arabic 2450, Hindi 502, Turkish 169. English name pages compared against: 2446.

Nothing on the site was changed. Every number below is a count of pages on which the check fails. The full list per page is in `redesign/lang/audit.json`.

**Classes.** A = a script can fix it safely on every page. A* = a script can fix it, but the list of words it changes must be approved first. B = text has to be written or translated, then reviewed. C = a native reader or the source has to decide. D = Usman has to decide.

## Headline: pages affected, by class

| Class | Urdu | Arabic | Hindi | Turkish | Defect types |
|---|---|---|---|---|---|
| A | 2450 | 2450 | 502 | 169 | 37 |
| A* | 135 | 43 | 0 | 0 | 2 |
| B | 2450 | 2450 | 502 | 169 | 17 |
| C | 494 | 1152 | 57 | 55 | 19 |
| D | 2322 | 820 | 484 | 31 | 15 |
| Pages with no finding at all | 0 | 0 | 0 | 0 | |

## Coverage

| | Urdu | Arabic | Hindi | Turkish |
|---|---|---|---|---|
| Name pages | 2448 | 2448 | 500 | 168 |
| English names with no page in this language (of 2446) | 1 | 1 | 1946 | 2287 |
| Home page exists | yes | yes | yes | **no** |
| /letters/ translated | no | no | no | no |
| /about/ translated | no | no | no | no |
| /contact/ translated | no | no | no | no |
| /privacy/ translated | no | no | no | no |
| /terms/ translated | no | no | no | no |
| /blog/ translated | no | no | no | no |
| /ilm-ul-huroof/ translated | no | no | no | no |
| /reader/ translated | no | no | no | no |
| Average words per name page | 735.9 | 343.1 | 598.9 | 545.9 |
| Average words on the English page of the same names | 1272.5 | 1272.5 | 1355.2 | 1231.7 |
| Average FAQ questions (English same names) | 8.7 (6.8) | 3.3 (6.8) | 4.0 (7.2) | 5.0 (6.6) |
| Share of running text that is wording shared across many pages | 19% | 29% | 27% | 21% |

## The most serious findings

- **90 pages** (Urdu 90). Urdu pages say the name, or its word, "is mentioned in the Quran here" and give a verse, where the English answer says it is not in the Quran, or only cites a root, an attribute of God or a theme. A religious claim stated more strongly in Urdu than in the source.
  - `ur/names/aahil/index.html`: انگریزی ماخذ کے مطابق اس نام یا اس کے لفظ کا ذکر قرآن میں یہاں ہے: ۳:۲۶۔ | English: The concept of divinely-granted sovereignty runs throughout the Quran: 'Say: O Allah, Owner of Sovereignty. You give sov
  - `ur/names/laiba/index.html`: انگریزی ماخذ کے مطابق اس نام یا اس کے لفظ کا ذکر قرآن میں یہاں ہے: ۴۴:۵۴، ۵۲:۲۰، ۵۵:۷۲۔ | English: Laiba is not directly from a Quranic verse but is connected to the Quranic concept of the hur al-ayn (celestia
- **60 pages** (Urdu 20, Arabic 20, Hindi 19, Turkish 1). The abjad total and the lucky number differ between languages for the same name. The odd one out is Hindi on 19 names and Turkish on 1. In 11 of the 19 the Hindi total is short by exactly 10, the value of the letter ya: those names are written with the Urdu form ی, which the Hindi calculation did not count.
  - `ur/names/aiyana/index.html`: ar=63 hi=136 ur=63
  - `ar/names/aiyana/index.html`: ar=63 hi=136 ur=63
- **123 pages** (Urdu 72, Arabic 51). The Arabic spelling of the name in the page header is a different word from the one on the English page and in the site index (not a vowel-mark difference).
  - `ur/names/abdelali/index.html`: name in Arabic in the page header: عَبْد الْعَلِيّ vs index عَبْد الْعَالِي
  - `ar/names/abdelali/index.html`: name in Arabic in the page header: عَبْد الْعَلِيّ vs index عَبْد الْعَالِي
- **211 pages** (Urdu 94, Arabic 94, Hindi 15, Turkish 8). The Urdu spelling of the name is a different word in different languages of the same name, or differs from the index that the English page shows.
  - `ur/names/abdelali/index.html`: ar=عبد العلی ur=عبد العالی
  - `ar/names/abdelali/index.html`: ar=عبد العلی ur=عبد العالی
- **287 pages** (Arabic 240, Turkish 47). The origin of the name (Arabic, Persian, Turkish, Hebrew and so on) differs from the English page, or is stated where English states none.
  - `ar/names/aayat/index.html`: Arabic "عربي"
  - `tr/names/alp-arslan/index.html`: Turkish "Türkçe"
- **252 pages** (Urdu 102, Arabic 102, Hindi 44, Turkish 4). The number of letters stated does not match the letters shown. On Arabic pages the count includes vowel marks (for example 13 for an 8-letter name).
  - `ur/names/abd-ar-rahman/index.html`: ar=10 hi=9 ur=9
  - `ar/names/abd-ar-rahman/index.html`: ar=10 hi=9 ur=9
- **109 pages** (Urdu 2, Arabic 105, Turkish 2). Arabic root, gender or Quran reference differs from the English page.
  - `ur/names/khursheed/index.html`: English M, Urdu U
  - `ar/names/khursheed/index.html`: English M, Arabic U
- **2 pages** (Urdu 1, Arabic 1). The Urdu and Arabic home pages say the site is "without advertising", and the same pages load the ad code.
  - `ur/index.html`: لدین کے ناموں کے حروف بھی پڑھائی کا حصہ بنتے ہیں۔ مفت، نجی، بغیر اشتہار , نہ اکاؤنٹ، نہ پے وال، نہ اشتہار۔ آپ ک
  - `ar/index.html`: لأخير، ويربطها بحروف الوالدَين في قراءة موسّعة. مجاني وخاص وبلا إعلانات , لا حساب، لا اشتراك، لا إعلانات. لا يُ
- **646 pages** (Urdu 197, Arabic 446, Turkish 3). Half-translated text: English words inside Urdu or Arabic sentences, element and letter names left as "Earth", "Fire", "Air", "Dhal", dates as "c.", "b.", "CE", "AH", roots in Latin letters.
  - `ur/names/aamir/index.html`: "b" in: b. ۱۹۶۵ · ہندوستان
  - `ar/names/abu-bakr-al-razi/index.html`: "c" in: طَبيبُ الرَّيّ · c. 854 – c. 925 CE
- **1066 pages** (Urdu 993, Arabic 71, Hindi 2). Famous bearers named in Latin letters on Urdu and Arabic pages.
  - `ur/names/aabid/index.html`: "Aabid Surti" in: Aabid Surti
  - `ar/names/abu-bakr-al-razi/index.html`: "Abū Bakr Muḥammad ibn Zakariyyāʾ al-Rāzī" in: Abū Bakr Muḥammad ibn Zakariyyāʾ al-Rāzī · الرَّيّ / بغداد
- **178 pages** (Urdu 135, Arabic 43). A name or word that mixes Arabic and Urdu letter forms inside one word (for example Arabic ه with Urdu ی). It can display wrongly and does not match a search typed on an Urdu or Arabic keyboard.
  - `ur/names/abdul-muhaymin/index.html`: المهیمن  in: عبد المهیمن  [breadcrumb]
  - `ar/names/azhar/index.html`: أزہار  in: ما معنى اسم أزہار؟  [sr-layout-v2 asr-v2 asr-faq asr-faq-item]
- **5571 pages** (Urdu 2450, Arabic 2450, Hindi 502, Turkish 169). Every translated page links to English-only pages under translated labels (the 28 letter pages, About, Contact, Privacy, Terms), and Arabic and Hindi pages send the reader to the English page for the full reading.
  - `ur/index.html`: /letters/  "اٹھائیس حروف"
  - `ar/index.html`: /letters/  "الحروف الثمانية والعشرين"
- **4019 pages** (Urdu 917, Arabic 2445, Hindi 500, Turkish 157). Content gap with English: fewer than half the words, fewer questions, no bearers, no pronunciation, no verse.
  - `ur/names/aabid/index.html`: 766 words vs 1711 (0.45)
  - `ar/names/aabid/index.html`: 317 words vs 1711 (0.19)

## What a script can fix on every page at once (class A)

| Fix | Pages | Urdu | Arabic | Hindi | Turkish |
|---|---|---|---|---|---|
| translate the fixed labels (aria-label "Breadcrumb", "Summary") from a label table (U2) | 5496 | 2413 | 2413 | 502 | 168 |
| point the second breadcrumb step at the names list and use one wording on the page and in the data (L5, L6, L7, P7) | 5490 | 2411 | 2411 | 500 | 168 |
| write inLanguage, Article and one modified date into the page data from values already on the page (P10, P11, P12, P6, P8) | 5565 | 2448 | 2448 | 500 | 169 |
| close the unclosed <article>, remove the stray closing tag (X1, X2) | 2024 |  | 1994 | 30 |  |
| renumber the section labels 1..n in page order (X6) | 1989 | 1364 | 625 |  |  |
| use one digit family per page (decide first: Western, or the language's own) (S4a, S4b) | 2357 | 363 | 1994 |  |  |
| replace Latin comma, semicolon and question mark after Arabic-script text with ، ؛ ؟ and remove the space before a comma (S5, S6) | 2049 | 347 | 1702 |  |  |
| copy title and description into the missing social tags (P4, T5, T6, T7) | 674 | 1 | 2 | 502 | 169 |
| rebuild the hreflang set and the "other languages" line from the pages that exist (C3, H1, H2, H3, H5, H6) | 140 | 4 | 129 | 6 | 1 |
| recount letters from the letter cards on the same page; recompute the reduced number from the total (F11, F14) | 99 |  | 86 | 13 |  |
| single pages: sitemap entry, stated count, one FAQ answer, one stray control character, home link (L2, P13, Q3, S9, Z2) | 15 | 6 | 8 | 1 |  |

None of these touches the spelling of a name. Fixes that do (S3a, class A*) need the word list approved first.

## What this audit cannot judge

- Whether the Urdu, Arabic, Hindi or Turkish reads naturally, and whether a meaning is translated correctly. No check here reads meaning.
- Which side is right when two languages disagree on a fact (origin, spelling, root, verse). The audit proves the disagreement, not the answer; the source decides.
- Whether a Latin-letter word inside a sentence is a leftover or a deliberate gloss (U1b), and whether a word in the other script's letter forms is a quotation (S3b).
- Whether Hindi and Turkish transliterations of names (Devanagari and Turkish spellings) are the forms readers use.
- Religious wording: honorifics, how verses and hadith are cited, and whether a claim is stated more strongly than the source.

## Facts that disagree between languages (most serious)

| Check | Class | Urdu | Arabic | Hindi | Turkish | Pages |
|---|---|---|---|---|---|---|
| F4b Arabic spelling: same letters as the index, vowel marks differ or are missing on one side | D | 691 | 467 | 5 |  | 1163 |
| F13b Urdu spelling between the translations: same word, letter forms, hamza or spacing differ | D | 279 | 279 | 26 | 14 | 598 |
| F5b Urdu spelling: same word as the index, but Arabic versus Urdu letter forms, hamza or spacing differ | D | 275 | 78 |  | 13 | 366 |
| F12 FACT number of letters differs between the translations | C | 102 | 102 | 41 | 4 | 249 |
| F13 FACT Urdu spelling of the name differs between the translations | C | 94 | 94 | 15 | 8 | 211 |
| F15 "Urdu spelling" is a copy of the vowelled Arabic spelling | D | 79 | 77 | 19 | 7 | 182 |
| F2 FACT origin differs from the English page | C |  | 120 |  | 43 | 163 |
| F2c FACT origin stated here although the English page states none | C |  | 120 |  | 4 | 124 |
| F4 FACT Arabic spelling of the name differs from the site index | C | 72 | 51 |  |  | 123 |
| F4 FACT Arabic spelling of the name differs from the English page | C | 72 | 51 |  |  | 123 |
| F6 FACT Arabic root differs from the English page | C |  | 103 |  |  | 103 |
| F7 FACT number of letters differs from the letters read on the English page | C |  | 86 | 15 | 1 | 102 |
| F14 FACT number of letters stated differs from the letters shown on the same page | A |  | 86 | 12 |  | 98 |
| F5 FACT Urdu spelling of the name differs from the site index (which the English page shows) | C |  | 94 | 1 |  | 95 |
| F10b FACT this page says the name or its word is mentioned in the Quran at a verse; the English answer does not say yes (it cites a root, an attribute or a theme) | C | 82 |  |  |  | 82 |
| F12 FACT lucky number differs between the translations | C | 20 | 20 | 19 | 1 | 60 |
| F12 FACT abjad total differs between the translations | C | 19 | 19 | 18 | 1 | 57 |
| F3 FACT lucky number differs from the English page | C |  |  | 19 | 1 | 20 |
| F10 FACT English says the name is not in the Quran, this page says it is | C | 8 |  |  |  | 8 |
| F1 FACT gender differs from the English page | C | 2 | 2 |  |  | 4 |
| F9 FACT Quran reference differs from the English page | C |  |  |  | 2 | 2 |
| F11 FACT abjad total and its reduced number do not agree on this page | A |  |  | 1 |  | 1 |

**F4b Arabic spelling: same letters as the index, vowel marks differ or are missing on one side** (class D)

- `ur/names/aabid/index.html`: name in Arabic in the page header: عَابِد vs index عابد
- `hi/names/alizeh/index.html`: name in Arabic in the page header: اليزه vs index الیزہ
- `ur/names/aabid/index.html`: "Arabic spelling" fact: عَابِد vs index عابد
- `hi/names/alizeh/index.html`: "Arabic spelling" fact: اليزه vs index الیزہ
- `ur/names/aabida/index.html`: name in Arabic in the page header: عَابِدَة vs index عابدة

**F13b Urdu spelling between the translations: same word, letter forms, hamza or spacing differ** (class D)

- `ur/names/aayat/index.html`: ar=آيات ur=آیات
- `hi/names/abd-al-mumin/index.html`: ar=عبد المؤمن hi=عبد المؤمن ur=عبد المومن
- `tr/names/araz/index.html`: ar=اراز tr=آراز ur=آراز
- `hi/names/abdul-malik/index.html`: ar=عبد الملک hi=عبد الملك ur=عبد الملک
- `tr/names/aylin/index.html`: ar=ايلين tr=ایلین ur=ایلین

**F5b Urdu spelling: same word as the index, but Arabic versus Urdu letter forms, hamza or spacing differ** (class D)

- `ur/names/aayat/index.html`: Urdu page آیَات vs index آيَات
- `ar/names/abdelaziz/index.html`: Arabic page عبد العزیز vs index عبدالعزیز
- `tr/names/ahmet/index.html`: Turkish page اَحْمَد vs index أَحْمَد
- `ur/names/abd-al-mumin/index.html`: Urdu page عبد المومن vs index عبد المؤمن
- `ar/names/abdelhafid/index.html`: Arabic page عبد الحفیظ vs index عبدالحفیظ

**F12 FACT number of letters differs between the translations** (class C)

- `ur/names/abd-ar-rahman/index.html`: ar=10 hi=9 ur=9
- `tr/names/berat/index.html`: ar=4 tr=5 ur=4
- `ur/names/abdelilah/index.html`: ar=13 ur=8

**F13 FACT Urdu spelling of the name differs between the translations** (class C)

- `ur/names/abdelali/index.html`: ar=عبد العلی ur=عبد العالی
- `hi/names/abdoulaye/index.html`: ar=عبد اللاہی hi=عبداللہ ur=عبداللہ
- `tr/names/asel/index.html`: ar=اصیلہ tr=اصیل ur=اصیل
- `ur/names/abdelwafi/index.html`: ar=عبد الوفی ur=عبد الوافی
- `hi/names/ainul/index.html`: ar=عین hi=عینل ur=عینل

**F15 "Urdu spelling" is a copy of the vowelled Arabic spelling** (class D)

- `ur/names/abbas/index.html`: عَبَّاس
- `hi/names/abd-ar-rahman/index.html`: عَبْد الرَّحْمَن
- `tr/names/hasan/index.html`: حَسَن
- `ur/names/abdelfattah/index.html`: عَبْد الْفَتَّاح
- `ar/names/ahmar/index.html`: أَحْمَر

**F2 FACT origin differs from the English page** (class C)

- `ar/names/ablikim/index.html`: English "Arabic", Arabic "تركي (آسيا الوسطى)" (elsewhere "Arabic" is "عربي")
- `tr/names/ahmet/index.html`: English "Turkish", Turkish "Arapça" (elsewhere "Turkish" is "Türkçe")
- `tr/names/arslan/index.html`: English "Arabic", Turkish "Türkçe" (elsewhere "Arabic" is "Arapça")
- `ar/names/afiqah/index.html`: English "Arabic", Arabic "ماليزي/إندونيسي" (elsewhere "Arabic" is "عربي")
- `ar/names/afreen/index.html`: English "Persian", Arabic "عربي" (elsewhere "Persian" is "فارسي")

**F2c FACT origin stated here although the English page states none** (class C)

- `ar/names/aayat/index.html`: Arabic "عربي"
- `tr/names/alp-arslan/index.html`: Turkish "Türkçe"
- `tr/names/leyla/index.html`: Turkish "Arapça"
- `ar/names/aigul/index.html`: Arabic "تركي (آسيا الوسطى)"
- `ar/names/anmol/index.html`: Arabic "هندي/جنوب آسيوي"

**F4 FACT Arabic spelling of the name differs from the site index** (class C)

- `ur/names/abdelali/index.html`: name in Arabic in the page header: عَبْد الْعَلِيّ vs index عَبْد الْعَالِي
- `ur/names/abdelali/index.html`: "Arabic spelling" fact: عَبْد الْعَلِيّ vs index عَبْد الْعَالِي
- `ur/names/abdelwafi/index.html`: name in Arabic in the page header: عَبْد الْوَفِيّ vs index عبد الوافي
- `ur/names/abdelwafi/index.html`: "Arabic spelling" fact: عَبْد الْوَفِيّ vs index عبد الوافي
- `ur/names/abdoulaye/index.html`: name in Arabic in the page header: عَبْدُ اللَّاهي vs index عَبْد الله

**F4 FACT Arabic spelling of the name differs from the English page** (class C)

- `ur/names/abdelali/index.html`: English عَبْد الْعَالِي, Urdu عَبْد الْعَلِيّ
- `ar/names/abdelali/index.html`: English عَبْد الْعَالِي, Arabic عَبْد الْعَلِيّ
- `ur/names/abdelwafi/index.html`: English عبد الوافي, Urdu عَبْد الْوَفِيّ
- `ar/names/abdelwafi/index.html`: English عبد الوافي, Arabic عَبْد الْوَفِيّ
- `ur/names/abdoulaye/index.html`: English عَبْد الله, Urdu عَبْدُ اللَّاهي

**F6 FACT Arabic root differs from the English page** (class C)

- `ar/names/aatika/index.html`: English ع-ت-ق, Arabic الجذر ع-ت-ك: الطِّيب الصَّافي 
- `ar/names/aayat/index.html`: English ا-ي-ة, Arabic أ-ي-ي
- `ar/names/abd-ar-rahman/index.html`: English ر-ح-م, Arabic ع-ب-د + ر-ح-م, العبودية المضاف
- `ar/names/abdelali/index.html`: English ع-ل-و, Arabic الجذر ع-ب-د + ع-ل-و: عَبدُ الم
- `ar/names/abdelaziz/index.html`: English ع-ز-ز, Arabic الجذر ع-ب-د + ع-ز-ز: عَبدُ الم

**F7 FACT number of letters differs from the letters read on the English page** (class C)

- `ar/names/abd-ar-rahman/index.html`: Arabic says 10, English reads 9 (عبدالرحمن)
- `hi/names/alizeh/index.html`: Hindi says 4, English reads 5 (اليزه)
- `tr/names/berat/index.html`: Turkish says 5, English reads 4 (برات)
- `ar/names/abdelilah/index.html`: Arabic says 13, English reads 8 (عبدالإله)
- `hi/names/bouchaib/index.html`: Hindi says 4, English reads 6 (بوشعيب)

**F14 FACT number of letters stated differs from the letters shown on the same page** (class A)

- `ar/names/abd-ar-rahman/index.html`: states 10, shows 9 letter cards

**F5 FACT Urdu spelling of the name differs from the site index (which the English page shows)** (class C)

- `ar/names/abdelali/index.html`: Arabic page عبد العلی vs index عبد العالی
- `hi/names/zavian/index.html`: Hindi page زفیان vs index زاویان
- `ar/names/abdelwafi/index.html`: Arabic page عبد الوفی vs index عبد الوافی
- `ar/names/abdoulaye/index.html`: Arabic page عبد اللاہی vs index عبداللہ
- `ar/names/aboubakry/index.html`: Arabic page ابو بکر vs index ابوبکری

**F10b FACT this page says the name or its word is mentioned in the Quran at a verse; the English answer does not say yes (it cites a root, an attribute or a theme)** (class C)

- `ur/names/aahil/index.html`: انگریزی ماخذ کے مطابق اس نام یا اس کے لفظ کا ذکر قرآن میں یہاں ہے: ۳:۲۶۔ | English: The concept of divinely-granted sovereignty runs throughout the Quran: 'Say: O Allah, Owner of Sovereignty. You give sov

**F12 FACT lucky number differs between the translations** (class C)

- `ur/names/aiyana/index.html`: ar=9 hi=1 ur=9
- `tr/names/berat/index.html`: ar=9 tr=2 ur=9

**F12 FACT abjad total differs between the translations** (class C)

- `ur/names/aiyana/index.html`: ar=63 hi=136 ur=63
- `tr/names/berat/index.html`: ar=603 tr=209 ur=603

**F3 FACT lucky number differs from the English page** (class C)

- `hi/names/aiyana/index.html`: English 9, Hindi 1
- `tr/names/berat/index.html`: English 9, Turkish 2

**F10 FACT English says the name is not in the Quran, this page says it is** (class C)

- `ur/names/laiba/index.html`: انگریزی ماخذ کے مطابق اس نام یا اس کے لفظ کا ذکر قرآن میں یہاں ہے: ۴۴:۵۴، ۵۲:۲۰، ۵۵:۷۲۔ | English: Laiba is not directly from a Quranic verse but is connected to the Quranic concept of the hur al-ayn (celestia

**F1 FACT gender differs from the English page** (class C)

- `ur/names/khursheed/index.html`: English M, Urdu U
- `ar/names/khursheed/index.html`: English M, Arabic U

**F9 FACT Quran reference differs from the English page** (class C)

- `tr/names/nura/index.html`: English ['25:61'], Turkish ['24:35']

**F11 FACT abjad total and its reduced number do not agree on this page** (class A)

- `hi/names/zavian/index.html`: total 75 reduces to 3, page says 4

## Claims on the page that are not true of the site

| Check | Class | Urdu | Arabic | Hindi | Turkish | Pages |
|---|---|---|---|---|---|---|
| Z2 number of names stated on the page differs from the name pages that exist | A | 2 | 2 |  |  | 4 |
| Z1 page says the site has no advertising, and the same page loads the ad code | D | 1 | 1 |  |  | 2 |

**Z2 number of names stated on the page differs from the name pages that exist** (class A)

- `ur/index.html`: page states [2445], Urdu name pages on the site: 2448, names in the index: 2446
- `ar/index.html`: page states [2445], Arabic name pages on the site: 2448, names in the index: 2446

**Z1 page says the site has no advertising, and the same page loads the ad code** (class D)

- `ur/index.html`: لدین کے ناموں کے حروف بھی پڑھائی کا حصہ بنتے ہیں۔ مفت، نجی، بغیر اشتہار , نہ اکاؤنٹ، نہ پے وال، نہ اشتہار۔ آپ ک
- `ar/index.html`: لأخير، ويربطها بحروف الوالدَين في قراءة موسّعة. مجاني وخاص وبلا إعلانات , لا حساب، لا اشتراك، لا إعلانات. لا يُ

## Language plumbing: lang, hreflang, canonical, social and search data

| Check | Class | Urdu | Arabic | Hindi | Turkish | Pages |
|---|---|---|---|---|---|---|
| P12 JSON-LD dateModified missing | A | 2448 | 2448 |  |  | 4896 |
| P6 JSON-LD inLanguage missing | A |  | 1994 | 500 | 169 | 2663 |
| P10 the page states two different "last modified" dates | A | 50 | 2044 |  |  | 2094 |
| P8 JSON-LD Article missing | A | 454 | 454 |  |  | 908 |
| T7 twitter:title missing | A | 1 | 1 | 502 | 169 | 673 |
| P7 breadcrumb data: "home" and "names" are the same URL | A |  |  | 500 | 168 | 668 |
| P11 no "last modified" date anywhere | A |  |  | 500 |  | 500 |
| T2 title is mostly not in Hindi script | D |  |  | 259 |  | 259 |
| T3 English words in the title | D |  |  | 247 |  | 247 |
| P3 canonical is not the page itself | D | 4 | 4 | 1 |  | 9 |
| P13 page is not in any sitemap | A | 4 | 4 | 1 |  | 9 |
| H5 hreflang set incomplete (a translation exists but is not listed) | A | 1 | 4 | 1 | 1 | 7 |
| H1 hreflang: no entry for the page itself | A | 3 | 3 |  |  | 6 |
| P4 og:locale missing | A | 1 | 1 | 2 |  | 4 |
| T6 og:title or og:description missing | A | 1 | 1 | 2 |  | 4 |
| P9 og:image missing | D | 1 | 1 | 2 |  | 4 |
| H6 hreflang not returned by the other page | A | 3 |  |  |  | 3 |
| H2 hreflang: x-default missing | A |  | 3 |  |  | 3 |
| H3 hreflang: English missing | A |  | 3 |  |  | 3 |
| T3 English words in the meta description | D |  | 3 |  |  | 3 |
| T5 og:title differs from the title | A |  | 1 |  |  | 1 |

**P12 JSON-LD dateModified missing** (class A)

- `ur/names/aabid/index.html`
- `ur/names/aabida/index.html`
- `ar/names/aabid/index.html`
- `ar/names/aabida/index.html`

**P6 JSON-LD inLanguage missing** (class A)

- `ar/names/aabid/index.html`: FAQPage

**P10 the page states two different "last modified" dates** (class A)

- `ur/names/ahyan/index.html`: {'meta': '2026-11-13', 'time tag': '2026-11-12'}

**P8 JSON-LD Article missing** (class A)

- `ur/names/aaliyah-d/index.html`
- `ur/names/aayat/index.html`
- `ar/names/aaliyah-d/index.html`
- `ar/names/aayat/index.html`

**T7 twitter:title missing** (class A)

- `ur/names/index.html`
- `ar/names/index.html`
- `hi/index.html`
- `hi/names/aairah/index.html`
- `tr/names/ada/index.html`
- `tr/names/ahmet/index.html`

**P7 breadcrumb data: "home" and "names" are the same URL** (class A)

- `hi/names/aairah/index.html`: /hi/names/
- `tr/names/ada/index.html`: /tr/names/

**P11 no "last modified" date anywhere** (class A)

- `hi/names/aairah/index.html`
- `hi/names/aamira/index.html`

**T2 title is mostly not in Hindi script** (class D)

- `hi/names/aairah/index.html`: 24% Hindi letters: Aairah Name Meaning in Hindi: आइरा नाम का मतलब | AsrNaam
- `hi/names/aariz/index.html`: 25% Hindi letters: Aariz Name Meaning in Hindi: आरिज़ नाम का मतलब | AsrNaam
- `hi/names/abd-ar-rahman/index.html`: 29% Hindi letters: Abd ar Rahman Name Meaning in Hindi: अब्दुर्रहमान नाम का मतलब | AsrNaam
- `hi/names/abdoulaye/index.html`: 26% Hindi letters: Abdoulaye Name Meaning in Hindi: अब्दुलाय नाम का मतलब | AsrNaam
- `hi/names/abdulaziz/index.html`: 29% Hindi letters: Abdulaziz Name Meaning in Hindi: अब्दुल अज़ीज़ नाम का मतलब | AsrNaam

**T3 English words in the title** (class D)

- `hi/names/aairah/index.html`: ['Meaning', 'Hindi']: Aairah Name Meaning in Hindi: आइरा नाम का मतलब | AsrNaam
- `hi/names/aariz/index.html`: ['Meaning', 'Hindi']: Aariz Name Meaning in Hindi: आरिज़ नाम का मतलब | AsrNaam
- `hi/names/abd-ar-rahman/index.html`: ['Meaning', 'Hindi']: Abd ar Rahman Name Meaning in Hindi: अब्दुर्रहमान नाम का मतलब | AsrNaam
- `hi/names/abdoulaye/index.html`: ['Meaning', 'Hindi']: Abdoulaye Name Meaning in Hindi: अब्दुलाय नाम का मतलब | AsrNaam
- `hi/names/abdulaziz/index.html`: ['Meaning', 'Hindi']: Abdulaziz Name Meaning in Hindi: अब्दुल अज़ीज़ नाम का मतलब | AsrNaam

**P3 canonical is not the page itself** (class D)

- `ur/names/musa-modern/index.html`: canonical=https://asrnaam.com/ur/names/moosa/
- `ar/names/musa-modern/index.html`: canonical=https://asrnaam.com/ar/names/moosa/
- `hi/names/yakub/index.html`: canonical=https://asrnaam.com/hi/names/yaqub/
- `ur/names/rasul-t/index.html`: canonical=https://asrnaam.com/ur/names/rasul-f/
- `ar/names/rasul-t/index.html`: canonical=https://asrnaam.com/ar/names/rasul-f/

**P13 page is not in any sitemap** (class A)

- `ur/names/musa-modern/index.html`: /ur/names/musa-modern/
- `ar/names/musa-modern/index.html`: /ar/names/musa-modern/
- `hi/names/yakub/index.html`: /hi/names/yakub/
- `ur/names/rasul-t/index.html`: /ur/names/rasul-t/
- `ar/names/rasul-t/index.html`: /ar/names/rasul-t/

**H5 hreflang set incomplete (a translation exists but is not listed)** (class A)

- `ur/index.html`: missing: ar
- `ar/index.html`: missing: ur
- `hi/names/index.html`: missing: tr
- `tr/names/index.html`: missing: hi
- `ar/names/musa-modern/index.html`: missing: en,ur,ar

**H1 hreflang: no entry for the page itself** (class A)

- `ur/names/musa-modern/index.html`: hreflang ur = /ur/names/moosa/
- `ar/names/musa-modern/index.html`: hreflang ar = None
- `ur/names/rasul-t/index.html`: hreflang ur = /ur/names/rasul-f/
- `ur/names/zaydn/index.html`: hreflang ur = /ur/names/zaydan/

**P4 og:locale missing** (class A)

- `ur/names/index.html`
- `ar/names/index.html`
- `hi/index.html`
- `hi/names/index.html`

**T6 og:title or og:description missing** (class A)

- `ur/names/index.html`
- `ar/names/index.html`
- `hi/index.html`
- `hi/names/index.html`

**P9 og:image missing** (class D)

- `ur/names/index.html`
- `ar/names/index.html`
- `hi/index.html`
- `hi/names/index.html`

**H6 hreflang not returned by the other page** (class A)

- `ur/names/musa-modern/index.html`: en page /names/musa-modern/ does not list ur
- `ur/names/musa-modern/index.html`: ar page /ar/names/musa-modern/ does not list ur
- `ur/names/rasul-t/index.html`: en page /names/rasul-t/ does not list ur
- `ur/names/rasul-t/index.html`: ar page /ar/names/rasul-t/ does not list ur
- `ur/names/zaydn/index.html`: en page /names/zaydn/ does not list ur

**H2 hreflang: x-default missing** (class A)

- `ar/names/musa-modern/index.html`
- `ar/names/rasul-t/index.html`

**H3 hreflang: English missing** (class A)

- `ar/names/musa-modern/index.html`
- `ar/names/rasul-t/index.html`

**T3 English words in the meta description** (class D)

- `ar/names/parviz/index.html`: ['lucky']: پرویز (Parviz): مَنصور, lucky. الأصل: فارسي. وقراءة كل حرف في علم الحروف على أثر نام.
- `ar/names/sehrish/index.html`: ['Urdu']: سحرش (Sehrish): فارسيّ / Urdu. الأصل: عربي. وقراءة كل حرف في علم الحروف على أثر نام.
- `ar/names/shahira/index.html`: ['Famous']: شهيرة (Shahira): Famous. الأصل: عربي. وقراءة كل حرف في علم الحروف على أثر نام.

**T5 og:title differs from the title** (class A)

- `ar/names/safiyyah-bint-abd/index.html`: معنى اسم صَفِيَّة (Safiyyah): الجذر وقراءة الحروف | أثر نام

## Untranslated interface text

| Check | Class | Urdu | Arabic | Hindi | Turkish | Pages |
|---|---|---|---|---|---|---|
| U2 English in a screen-reader label or alt text | A | 2413 | 2413 | 502 | 168 | 5496 |
| U1b Latin-letter word inside the text (leftover or a deliberate gloss) | C | 147 | 608 | 2 |  | 757 |
| U1a English word left in the template (same string on many pages) | B | 91 | 223 |  | 3 | 317 |
| U8 half-translated sentence (English words inside a Arabic sentence) | B |  | 187 |  |  | 187 |
| U6 English abbreviation left in (c., b., d., CE, AH) | B | 95 | 70 |  |  | 165 |
| U7 Arabic root written in Latin letters | B | 9 | 41 |  |  | 50 |
| U8 half-translated sentence (English words inside a Urdu sentence) | B | 11 |  |  |  | 11 |
| U4 site name spelled differently from the rest of the language | D | 1 | 1 | 1 |  | 3 |
| U3 Latin A to Z used as index letters | D | 1 | 1 |  |  | 2 |

**U2 English in a screen-reader label or alt text** (class A)

- `ur/index.html`: aria-label="Summary" on <div>
- `tr/names/ada/index.html`: aria-label="Breadcrumb" on <div>

**U1b Latin-letter word inside the text (leftover or a deliberate gloss)** (class C)

- `ur/names/abu-bakr-al-razi/index.html`: "Liber Continens" in: ابو بکر الرازی نے ری اور بغداد کے ہسپتالوں کی نگرانی کی۔ ان کی «کتاب الحاوی» (Liber Continens) ایک وسیع کلینیکل مجموعہ ہے جو ان کے ذاتی نوٹس
- `ar/names/abu-bakr-al-razi/index.html`: "Liber Continens" in: أَدارَ أَبو بكر الرَّازي مَشافي الرَّيّ وبغداد. كتابُه «الحاوي» (Liber Continens) تَجميعٌ سَريريٌّ واسِع لمُلاحَظاته الخاصَّة مع المَصادِر ا
- `hi/names/aynur/index.html`: "ay" in: ay
- `ur/names/admir/index.html`: "admirari" in: Admir بوسنیائی مسلم نام ہے، جو لاتینی admirari (تحسین کرنا) سے ماخوذ ہے۔ بلقانیوں نے بیسویں صدی کے بعد یورپ کے فصیح زبان سے لیا، اور آج بوسن
- `ar/names/abu-hanifa/index.html`: "Kufa" in: Abū Ḥanīfa al-Nuʿmān ibn Thābit ibn Zūṭā ibn Marzubān · Kufa (Iraq) / Baghdad

**U1a English word left in the template (same string on many pages)** (class B)

- `ur/names/abd-al-mumin/index.html`: "Earth" (40 pages) in: Earth
- `tr/names/aylin/index.html`: "and" (2 pages) in: Aylin, “ay halesi” anlamıyla bilinen Türkçe bir kız ismidir. Ay sözcüğüyle kurulmuştur ve ayın çevresinde görülen ışık halkasını andırır. Tü
- `tr/names/dilara/index.html`: "Urdu" (1 pages) in: Dilara, gönül süsleyen, gönlü huzura erdiren sevgili anlamına gelir. Bu birleşik kelime Fars, Osmanlı ve Urdu şiirinde, varlığıyla gönlü din
- `tr/names/esra/index.html`: "and" (2 pages) in: Arapça “geceleyin yürütmek” anlamındaki س-ر-ي (s-r-y) kökünden gelir. İsrâ, Hz. Peygamber'in (s.a.v.) Mekke'den Kudüs'e yaptığı gece yolculu
- `ur/names/abu-dharr/index.html`: "Dhal" (29 pages) in: Dhal

**U8 half-translated sentence (English words inside a Arabic sentence)** (class B)

- `ar/names/ghazala/index.html`: ['form'] in: غزالة (Ghazala). Gazelle, feminine form.
- `ar/names/ghizlan/index.html`: ['name'] in: غزلان (Ghizlan). Gazelles. North African girls name.
- `ar/names/ghofrane/index.html`: ['name'] in: غفران (Ghofrane). Forgiveness. Tunisian girls name.
- `ar/names/habib/index.html`: ['of', 'the'] in: حبيب (Habib). Beloved. Al-Habib title of the Prophet.
- `ar/names/habibah/index.html`: ['form'] in: حبيبة (Habibah). Beloved. Malay -ah form.

**U6 English abbreviation left in (c., b., d., CE, AH)** (class B)

- `ur/names/aamir/index.html`: "b" in: b. ۱۹۶۵ · ہندوستان
- `ar/names/abu-bakr-al-razi/index.html`: "c" in: طَبيبُ الرَّيّ · c. 854 – c. 925 CE
- `ur/names/aaqib/index.html`: "b" in: b. ۱۹۷۲ · پاکستان
- `ar/names/abu-bakr-al-razi/index.html`: "CE" in: طَبيبُ الرَّيّ · c. 854 – c. 925 CE
- `ur/names/aatika/index.html`: "d. c" in: d. c. ۶۶۰ عیسوی · جزیرہ عرب

**U7 Arabic root written in Latin letters** (class B)

- `ur/names/eva/index.html`: "ḥ-w-h" in: عبرانی «حَوَّاء» جذر ḥ-w-h سے، یعنی زندگی: «ہر زندہ کی ماں»۔ عربی میں بعض نے «حَیَّ یَحیا» سے، اور بعض نے «حَوَیٰ» (جمع کیا) سے کہا، چونکہ پ
- `ar/names/eva/index.html`: "ḥ-w-h" in: «حَوَّاء» في العِبريَّة من جذر ḥ-w-h يَعني الحَياة، فَهيَ «أُمُّ كُلِّ حَيٍّ». وَفي العَربيَّة قال البَعض إنَّ الاسم من «حَيَّ» يَحيا، وَقال
- `ur/names/mouhamad/index.html`: "ḥ-m-d" in: جذر ح-م-د : Same root بطور محمّد ﷺ: ḥ-m-d , کی طرف حمد .
- `ar/names/imane/index.html`: "a-m-n" in: a-m-n
- `ur/names/nida/index.html`: "n-d-w" in: جذر ن-د-و : سے n-d-w , کی طرف پکار .

**U8 half-translated sentence (English words inside a Urdu sentence)** (class B)

- `ur/names/al-husain/index.html`: ['martyred', 'at'] in: نبی ﷺ کے نواسے; martyred at Karbala
- `ur/names/asim/index.html`: ['martyred', 'at'] in: نبی ﷺ کے صحابی, martyred at al-Rajiʿ
- `ur/names/fadl/index.html`: ['of'] in: نبی ﷺ کے صحابی, cousin of Muhammad
- `ur/names/mahira/index.html`: ['Same', 'root'] in: جذر م-ه-ر : مؤنث کا Māhir : ماہر ایک. Same root m-h-r .
- `ur/names/mouhamad/index.html`: ['Same', 'root'] in: جذر ح-م-د : Same root بطور محمّد ﷺ: ḥ-m-d , کی طرف حمد .

**U4 site name spelled differently from the rest of the language** (class D)

- `ur/names/index.html`: ['اسرنام'] (usual: اثر نام)
- `ar/index.html`: ['اثر نام'] (usual: أثر نام)
- `hi/index.html`: ['अस्रनाम'] (usual: असर नाम)

**U3 Latin A to Z used as index letters** (class D)

- `ur/names/index.html`: "A" in: A
- `ur/names/index.html`: "B" in: B
- `ur/names/index.html`: "C" in: C
- `ur/names/index.html`: "D" in: D

## Script and typography

| Check | Class | Urdu | Arabic | Hindi | Turkish | Pages |
|---|---|---|---|---|---|---|
| S2 pronunciation given only in Latin letters | D | 2181 |  | 456 |  | 2637 |
| S4a Western and Arabic digits mixed on one page | A |  | 1994 |  |  | 1994 |
| S5 Latin comma, semicolon or question mark after Arabic text (should be ، ؛ ؟) | A |  | 1302 |  |  | 1302 |
| S1 name of a person or place left in Latin letters | B | 993 | 71 | 2 |  | 1066 |
| S6 space before a comma (left over where a dash was removed) | A | 54 | 403 |  |  | 457 |
| S4a Western and Urdu digits mixed on one page | A | 362 |  |  |  | 362 |
| S5 Latin comma, semicolon or question mark after Urdu text (should be ، ؛ ؟) | A | 318 |  |  |  | 318 |
| S3b whole word in Urdu letter forms inside Arabic text | C |  | 292 |  |  | 292 |
| S1b another name written in Latin letters inside the text | D | 90 | 61 | 1 |  | 152 |
| S3a one word mixes Urdu and Arabic letter forms | A* | 135 |  |  |  | 135 |
| S3b whole word in Arabic letter forms inside Urdu text | C | 83 |  |  |  | 83 |
| S3a one word mixes Arabic and Urdu letter forms | A* |  | 43 |  |  | 43 |
| S4b digits of the wrong family (Arabic ٤٥٦ on an Urdu page) | A | 7 |  |  |  | 7 |
| S9 invisible control character in visible text | A |  | 1 |  |  | 1 |

**S2 pronunciation given only in Latin letters** (class D)

- `ur/names/aabid/index.html`: "AA-bid" in: AA-bid
- `hi/names/aairah/index.html`: "aa-I-rah" in: aa-I-rah
- `ur/names/aabida/index.html`: "aa-BI-da" in: aa-BI-da
- `hi/names/aamira/index.html`: "aa-MI-ra" in: aa-MI-ra
- `ur/names/aahil/index.html`: "AA-hil" in: AA-hil

**S4a Western and Arabic digits mixed on one page** (class A)

- `ar/names/aabid/index.html`: 7 Western, 3 Arabic

**S5 Latin comma, semicolon or question mark after Arabic text (should be ، ؛ ؟)** (class A)

- `ar/index.html`: ي، والمعنى المعجمي، وعلم الحروف الكلاسيكي, التراث الذي وضع أ
- `ar/names/aabid/index.html`: عَابِد يُقرأ ثلاث قراءات, معنى الاسم، ودلال
- `ar/names/aabid/index.html`: العابِد, المُتعبِّد لله بإ
- `ar/names/aabid/index.html`: ن، وأصلُه عربي. ومعناه المتداوَل: العابِد, المُتعبِّد لله بإ
- `ar/names/aabida/index.html`: عَابِدَة يُقرأ ثلاث قراءات, معنى الاسم، ودلال

**S1 name of a person or place left in Latin letters** (class B)

- `ur/names/aabid/index.html`: "Aabid Surti" in: Aabid Surti
- `ar/names/abu-bakr-al-razi/index.html`: "Abū Bakr Muḥammad ibn Zakariyyāʾ al-Rāzī" in: Abū Bakr Muḥammad ibn Zakariyyāʾ al-Rāzī · الرَّيّ / بغداد
- `hi/index.html`: "Abu Bakr al-Razi" in: (Abu Bakr al-Razi)
- `ur/names/aabid/index.html`: "Aabid Hussain" in: Aabid Hussain
- `ar/names/abu-hanifa/index.html`: "Abū Ḥanīfa al-Nuʿmān ibn Thābit ibn Zūṭā ibn Marzubān" in: Abū Ḥanīfa al-Nuʿmān ibn Thābit ibn Zūṭā ibn Marzubān · Kufa (Iraq) / Baghdad

**S6 space before a comma (left over where a dash was removed)** (class A)

- `ur/names/mohsen/index.html`: ب: کرنے والا کا اچھائی : سے Arabic muhsin , ایران میں عام نام نام۔
- `ar/names/aaliyah-d/index.html`: عالية يُقرأ ثلاث قراءات , معنى الاسم، ودلالة حروفه، 
- `ur/names/mouhamad/index.html`: جذر ح-م-د : Same root بطور محمّد ﷺ: ḥ-m-d , کی طرف حمد .
- `ar/names/aayat/index.html`: آيَات يُقرأ ثلاث قراءات , معنى الاسم، ودلالة حروفه، 
- `ur/names/musaddiq/index.html`: ربی الاصل ہے۔ اس کا مطلب: تصدیق کرنے والا , تصدیق کرنے والا : وہ ایک ج

**S4a Western and Urdu digits mixed on one page** (class A)

- `ur/names/aaliya/index.html`: 2 Western, 30 Urdu

**S5 Latin comma, semicolon or question mark after Urdu text (should be ، ؛ ؟)** (class A)

- `ur/index.html`: ا ہے: عربی جذر، لغوی معنی، اور علم الحروف, وہ کلاسیکی روایت 
- `ur/index.html`: , پہلا حرف، اندرونی حروف، آخری حرف, اور والدین کے نام
- `ur/index.html`:  باطن اور گہرائی کا، راء رحمت اور حرکت کا, اور اسی ترتیب پر 
- `ur/index.html`: کیا، اگرچہ اس کی جڑیں اس سے بھی پرانی ہیں, جعفر الصادق، سہل 
- `ur/names/al-husain/index.html`: نبی ﷺ کے نواسے; martyred at Karba

**S3b whole word in Urdu letter forms inside Arabic text** (class C)

- `ar/names/abdelwahed/index.html`: وحید  in: وحید  [content related-grid related-card]
- `ar/names/abdul-malik/index.html`: ملک  in: ملک  [content related-grid related-card]
- `ar/names/abeer/index.html`: آفرین  in: آفرین  [content related-grid related-card]
- `ar/names/aigerim/index.html`: بینش  in: بینش  [content related-grid related-card]
- `ar/names/aigerim/index.html`: فطریہ  in: فطریہ  [content related-grid related-card]

**S1b another name written in Latin letters inside the text** (class D)

- `ur/names/abir/index.html`: "Abeer" in: «عبیر» نام Abeer کا متبادل املا ہے: پھیلنے والی خوشبو۔ شام اور مغرب میں مقبول۔
- `ar/names/abir/index.html`: "Abeer" in: «عبير» إملاء بَديل لاسم «Abeer» نفسه: ضَربٌ من الطِّيب الفَوَّاح. شائع في الشَّام والمَغرب.
- `hi/names/aynur/index.html`: "nur" in: nur
- `ur/names/ahmad/index.html`: "Ahmed" in: جذر ح-م-د : وہی جذر، وہی نام، صرف املا کا فرق (Ahmad / Ahmed)۔
- `ar/names/ahmad/index.html`: "Ahmed" in: : نفس الجذر، نفس الاسم, اختلاف الإملاء فحسب (Ahmad / Ahmed).

**S3a one word mixes Urdu and Arabic letter forms** (class A*)

- `ur/names/abdul-muhaymin/index.html`: المهیمن  in: عبد المهیمن  [breadcrumb]
- `ur/names/abdul-muhaymin/index.html`: المهیمن  in: عبد المهیمن نام کا مطلب  [hero]
- `ur/names/abdul-muhaymin/index.html`: المهیمن  in: عبد المهیمن  [content quick-facts qf-row qf-value]
- `ur/names/abdul-muhaymin/index.html`: المهیمن  in: کیا عبد المهیمن اسلامی نام ہے؟  [ut-v2 asr-v2 asr-v2-root asr-mq asr-mq-q]
- `ur/names/abdulhadi/index.html`: عبدالهادی  in: عبدالهادی  [breadcrumb]

**S3b whole word in Arabic letter forms inside Urdu text** (class C)

- `ur/index.html`: عائشة  in: عائشة  [page examples examples-list]
- `ur/index.html`: فاطمة  in: فاطمة  [page examples examples-list]
- `ur/index.html`: مريم  in: مريم  [page examples examples-list]
- `ur/index.html`: يوسف  in: يوسف  [page examples examples-list]
- `ur/names/abdelali/index.html`: عبدالاله  in: عبدالاله  [n related-grid related-card related-name]

**S3a one word mixes Arabic and Urdu letter forms** (class A*)

- `ar/names/azhar/index.html`: أزہار  in: ما معنى اسم أزہار؟  [sr-layout-v2 asr-v2 asr-faq asr-faq-item]
- `ar/names/azhar/index.html`: أزہار  in: يُكتب الاسم بالعربية: أزہار، وبالإنجليزية: Azhar. وبالأردية يُكتب: ازہار.  [out-v2 asr-v2 asr-faq asr-faq-item prose]
- `ar/names/azhar/index.html`: أزہار  in: ما القيمة العددية لاسم أزہار في علم الحروف؟  [sr-layout-v2 asr-v2 asr-faq asr-faq-item]
- `ar/names/azhar/index.html`: أزہار  in: هل أزہار اسم مذكر أم مؤنث؟  [sr-layout-v2 asr-v2 asr-faq asr-faq-item]
- `ar/names/dalia/index.html`: ديمۃ  in: ديمۃ  [content related-grid related-card]

**S4b digits of the wrong family (Arabic ٤٥٦ on an Urdu page)** (class A)

- `ur/names/abdirahman/index.html`: 1 digits

**S9 invisible control character in visible text** (class A)

- `ar/names/mouhamadou/index.html`: LRM (U+200E) in: مُحَمَّد (Mouhamadou). محمد. الصيغة الفولانية بلاحقة ‎-adou.

## Coverage and content parity with English

| Check | Class | Urdu | Arabic | Hindi | Turkish | Pages |
|---|---|---|---|---|---|---|
| C4 content: fewer than half the words of the English page | B | 306 | 2441 | 360 | 123 | 3230 |
| C5 content: fewer FAQ questions than the English page | B | 3 | 2445 | 500 | 143 | 3091 |
| C7 content: English gives a pronunciation, this page gives none | B |  | 2336 | 10 | 153 | 2499 |
| C9 content: English cites a Quran verse, this page cites none | B | 722 | 1048 | 247 | 5 | 2022 |
| C14 text leans on the English page ("according to the English source", "see the English page") | B | 318 | 417 | 500 |  | 1235 |
| C6 content: English lists famous bearers, this page lists none | B |  | 870 | 262 | 80 | 1212 |
| C10 content: no related names | B | 500 | 437 | 4 |  | 941 |
| C13 page sends the reader to the English page for the rest | B |  | 417 | 500 |  | 917 |
| C3 "this name in other languages" misses a language that has the page | A |  | 125 | 5 |  | 130 |
| C12 most of the running text is wording shared with many other pages | B |  | 74 |  |  | 74 |
| C2 name page has no English page | D |  |  |  | 9 | 9 |

**C4 content: fewer than half the words of the English page** (class B)

- `ur/names/aabid/index.html`: 766 words vs 1711 (0.45)

**C5 content: fewer FAQ questions than the English page** (class B)

- `ur/names/ammar/index.html`: 9 vs 10

**C7 content: English gives a pronunciation, this page gives none** (class B)

- `ar/names/aabid/index.html`
- `ar/names/aabida/index.html`
- `hi/names/ayaana/index.html`
- `hi/names/dilan-k/index.html`
- `tr/names/ada/index.html`
- `tr/names/ahmet/index.html`

**C9 content: English cites a Quran verse, this page cites none** (class B)

- `ur/names/aabid/index.html`
- `ur/names/aairah/index.html`
- `ar/names/aabid/index.html`
- `ar/names/aahil/index.html`
- `hi/names/aairah/index.html`
- `hi/names/aamira/index.html`
- `tr/names/fatih/index.html`
- `tr/names/hamza/index.html`

**C14 text leans on the English page ("according to the English source", "see the English page")** (class B)

- `ur/names/aahil/index.html`:  یہ ہے کہ حامل بلند اخلاق کے تقاضوں کا اہل ٹھہرے۔ انگریزی ماخذ کے مطابق اس نام یا اس کے لفظ کا ذکر قرآن میں یہاں ہے: ۳:۲۶۔ حصہ ۶ · 
- `ar/names/aaliyah-d/index.html`: يعةُ السامية القَدر. اقرأ هذا كمرآة لا كحكم. اقرأ الصفحة الإنجليزية الرجوع إلى فهرس الأسماء العربي هذا الاسم بلغات أخرى: Englis
- `hi/names/aairah/index.html`: म-उल-हुरूफ़) की सदियों पुरानी पद्धति से की गई है: अंग्रेज़ी पृष्ठ पर अक्षर-दर-अक्षर विवरण उपलब्ध है। आइरा के अक्षर, एक-एक करक
- `ur/names/abdul-malik/index.html`: لَّهُ ... الْمَلِكُ الْقُدُّوسُ» (الحشر: 23) آیا۔ انگریزی ماخذ کے مطابق اس نام یا اس کے لفظ کا ذکر قرآن میں یہاں ہے: ۵۹:۲۳، ۶۲:۱، ۵
- `ar/names/aayat/index.html`: ُه في الكون والقرآن. اقرأ هذا كمرآة لا كحكم. اقرأ الصفحة الإنجليزية الرجوع إلى فهرس الأسماء العربي هذا الاسم بلغات أخرى: Englis

**C6 content: English lists famous bearers, this page lists none** (class B)

- `ar/names/aabid/index.html`
- `ar/names/aabida/index.html`
- `hi/names/abd-al-mumin/index.html`
- `hi/names/abd-ar-rahman/index.html`
- `tr/names/ahmet/index.html`
- `tr/names/ali/index.html`

**C10 content: no related names** (class B)

- `ur/names/aaliyah-d/index.html`
- `ur/names/aayat/index.html`
- `ar/names/aaliyah-d/index.html`
- `ar/names/aayat/index.html`
- `hi/names/ouassila/index.html`
- `hi/names/payam/index.html`

**C13 page sends the reader to the English page for the rest** (class B)

- `ar/names/aaliyah-d/index.html`: /names/aaliyah-d/  "اقرأ الصفحة الإنجليزية"
- `hi/names/aairah/index.html`: /names/aairah/  "अंग्रेज़ी पृष्ठ"
- `ar/names/aayat/index.html`: /names/aayat/  "اقرأ الصفحة الإنجليزية"
- `hi/names/aamira/index.html`: /names/aamira/  "अंग्रेज़ी पृष्ठ"
- `ar/names/abd-ar-rahman-ibn-awf/index.html`: /names/abd-ar-rahman-ibn-awf/  "اقرأ الصفحة الإنجليزية"

**C3 "this name in other languages" misses a language that has the page** (class A)

- `ar/names/ahmet/index.html`: missing: tr

**C12 most of the running text is wording shared with many other pages** (class B)

- `ar/names/maram/index.html`: 96 of 125 paragraph words are shared

**C2 name page has no English page** (class D)

- `tr/names/hacer/index.html`: /tr/names/hacer/
- `tr/names/halime/index.html`: /tr/names/halime/
- `tr/names/havva/index.html`: /tr/names/havva/
- `tr/names/miray/index.html`: /tr/names/miray/
- `tr/names/nergis/index.html`: /tr/names/nergis/

## Links

| Check | Class | Urdu | Arabic | Hindi | Turkish | Pages |
|---|---|---|---|---|---|---|
| L3 translated link label leads to an English-only page | B | 2450 | 2450 | 502 | 169 | 5571 |
| L5 breadcrumb: two steps go to the same page | A | 2411 | 2411 |  |  | 4822 |
| L6 breadcrumb on the page and breadcrumb in the data disagree | A | 2411 | 2411 |  |  | 4822 |
| L7 breadcrumb wording differs between the page and the data | A | 2008 |  | 500 | 168 | 2676 |
| L2 link goes to the English page although a Urdu page exists | A | 1 |  |  |  | 1 |
| L2 link goes to the English page although a Arabic page exists | A |  | 1 |  |  | 1 |

**L3 translated link label leads to an English-only page** (class B)

- `ur/index.html`: /letters/  "اٹھائیس حروف"
- `ar/index.html`: /letters/  "الحروف الثمانية والعشرين"
- `hi/index.html`: /about/  "परिचय"
- `tr/names/ada/index.html`: /contact/  "Düzeltme bildirin"
- `ur/index.html`: /about/  "اَثَر نام کے بارے میں"

**L5 breadcrumb: two steps go to the same page** (class A)

- `ur/names/aabid/index.html`: "ابتدائی صفحہ" -> /ur/ , "نام" -> /ur/
- `ar/names/aabid/index.html`: "الرئيسية" -> /ar/ , "الأسماء" -> /ar/

**L6 breadcrumb on the page and breadcrumb in the data disagree** (class A)

- `ur/names/aabid/index.html`: page ['/ur/', '/ur/'] vs data ['/ur/', '/ur/names/']
- `ar/names/aabid/index.html`: page ['/ar/', '/ar/'] vs data ['/ar/', '/ar/names/']

**L7 breadcrumb wording differs between the page and the data** (class A)

- `ur/names/aabid/index.html`: page "ابتدائی صفحہ" vs data "گھر"
- `hi/names/aairah/index.html`: page "नाम" vs data "मुखपृष्ठ"
- `tr/names/ada/index.html`: page "İsimler" vs data "Ana sayfa"

**L2 link goes to the English page although a Urdu page exists** (class A)

- `ur/index.html`: /  "اثر نام AsrNaam"  (/ur/ exists)
- `ur/index.html`: /  "صفحہ اول پر اپنا نام درج کریں"  (/ur/ exists)
- `ur/index.html`: /names/  "تمام نام"  (/ur/names/ exists)
- `ur/index.html`: /names/muhammad/  "محمد"  (/ur/names/muhammad/ exists)

**L2 link goes to the English page although a Arabic page exists** (class A)

- `ar/index.html`: /  "اثر نام AsrNaam"  (/ar/ exists)
- `ar/index.html`: /  "ابدأ بإدخال اسمك في الصفحة الرئيسية"  (/ar/ exists)
- `ar/index.html`: /names/  "جميع الأسماء"  (/ar/names/ exists)
- `ar/index.html`: /names/muhammad/  "محمد"  (/ar/names/muhammad/ exists)

## FAQ on the page against FAQ in the search data

| Check | Class | Urdu | Arabic | Hindi | Turkish | Pages |
|---|---|---|---|---|---|---|
| Q3 FAQ: answer in the data differs from the answer on the page | A |  | 1 |  |  | 1 |

**Q3 FAQ: answer in the data differs from the answer on the page** (class A)

- `ar/names/mustasim/index.html`: ما معنى اسم الْمُسْتَعْصِم؟ | data: الْمُسْتَعْصِم (Mustasim). المُعتصِم، المستمسكُ بحفظ الله. | page: الْمُسْتَعْصِم الذي يطلب العصمةَ والحماية من الله

## Page structure

| Check | Class | Urdu | Arabic | Hindi | Turkish | Pages |
|---|---|---|---|---|---|---|
| X1 HTML: block element never closed | A |  | 1994 | 29 |  | 2023 |
| X6 section numbers skip or run out of order | A | 1364 | 625 |  |  | 1989 |
| X4b fact row with an empty value | B |  | 43 |  |  | 43 |
| X2 HTML: closing tag without an opening tag | A |  |  | 1 |  | 1 |

**X1 HTML: block element never closed** (class A)

- `ar/names/aabid/index.html`: article
- `hi/names/ali/index.html`: div

**X6 section numbers skip or run out of order** (class A)

- `ur/names/aahil/index.html`: 1 2 3 4 6  (حصہ ۱ · عربی جذر | حصہ ۲ · علم الحروف | حصہ ۳ · قراءت کا خلاصہ | حصہ ۴ · عام معنی | حصہ ۶ · تلفظ)
- `ar/names/aaliyah-d/index.html`: 2  (القسم 2 · علم الحروف)
- `ar/names/abbas/index.html`: 1 2 3 5  (القسم 1 · الجذر العربي | القسم 2 · علم الحروف | القسم 3 · المعنى العائلي | القسم 5 · الحاملون)
- `ur/names/abdelouahid/index.html`: 1 2 3 4 6 7  (حصہ ۱ · عربی جذر | حصہ ۲ · علم الحروف | حصہ ۳ · قراءت کا خلاصہ | حصہ ۴ · عام معنی | حصہ ۶ · تلفظ | حصہ ۷ · املائیں)

**X4b fact row with an empty value** (class B)

- `ar/names/ghazan/index.html`: label "الجذر العربي"

**X2 HTML: closing tag without an opening tag** (class A)

- `hi/names/zavian/index.html`: div

## Latin-letter strings found in Urdu, Arabic and Hindi pages

Number of pages on which each string appears. "Leftover" strings are the untranslated ones; names of the page itself, the brand, web addresses and the language switch are counted as legitimate.

### Urdu

| Kind | Distinct strings | Pages x strings | Most frequent |
|---|---|---|---|
| LEFTOVER interface or English words | 201 | 329 | Earth (40); Dhal (29); Fire (29); Air (10); Turkic (5); quality (5); Fula (3); Mauritanian (3); Rumaisa (3); French (3); er (2); ou (2) |
| LEFTOVER person or place names | 1206 | 1366 | Muhammad (11); Husayn ibn Ali (5); Maymunah bint al-Harith (5); Umm Sulaym (5); Rumaysa (5); David (4); Umm Kulthum bint Muhammad (4); Hudhayfah ibn al-Yaman (4); Alp Arslan (3); ʿAʾisha bint Abi Bakr (3); Job (3); Prophet Ibrahim (3) |
| Pronunciation in Latin letters (decision) | 2154 | 2182 | ab-dur-rah-MAAN (2); AH-mad (2); AA-i-sha (2); ah-MEER (2); AA-mi-na (2); bi-LAAL (2); FAA-ti-ma (2); HAF-sa (2); ka-REEM (2); kha-DEE-ja (2); KHAA-lid (2); LAI-la (2) |
| A to Z index letters (decision) | 26 | 26 | A (1); B (1); C (1); D (1); E (1); F (1); G (1); H (1); I (1); J (1); K (1); L (1) |
| LEFTOVER English abbreviations | 15 | 105 | b (44); c (29); h (12); d (4); AS (3); d. c (2); RA (2); g (2); ş (1); E (1); y (1); p (1) |
| LEFTOVER roots in Latin letters | 8 | 9 | s-m-r (2); ḥ-w-h (1); ḥ-m-d (1); n-d-w (1); r-b-ʿ (1); r-n-w (1); r-y-m (1); s-l-m (1) |
| LEFTOVER another name in Latin letters | 27 | 96 | Aisha (47); Erkam (18); Lejla (5); Leyla (2); Lyla (2); Abeer (1); Ahmed (1); kerim (1); Cyrus (1); Darius (1); Alma (1); Amir (1) |
| legitimate: the name itself, romanised | 2627 | 2632 | Faiz (2); Sad (2); Safiyyah (2); Salim (2); Yaqub (2); Aabid (1); Aabida (1); Aahil (1); Aairah (1); Aaliya (1); Aaliyah (1); Aamir (1) |
| legitimate: brand | 1 | 2413 | AsrNaam (2413) |
| legitimate: language switch | 5 | 5023 | English (2450); EN (2412); Türkçe (159); English A (1); Z (1) |
| legitimate: phonetic notation | 1 | 2 | zajn (2) |

### Arabic

| Kind | Distinct strings | Pages x strings | Most frequent |
|---|---|---|---|
| LEFTOVER interface or English words | 991 | 1446 | Earth (48); Air (36); Dhal (29); Fire (29); Baghdad (11); Arabic (10); Asian (9); North African spelling (8); root (8); Turkic (7); North African girls name (7); Fula (7) |
| LEFTOVER person or place names | 78 | 84 | Wet-nurse of the Prophet (2); al-Andalus (2); ibn (2); Abi (2); Abu (2); Al-Rauf (2); Abū Bakr Muḥammad ibn Zakariyyāʾ al-Rāzī (1); Abū Ḥanīfa al-Nuʿmān ibn Thābit ibn Zūṭā ibn Marzubān (1); Abū ʿAbd Allāh Muḥammad ibn Jābir ibn Sinān al-Battānī al-Ḥarrānī al-Ṣābiʾ (1); Abū al-Rayḥān Muḥammad ibn Aḥmad al-Bīrūnī (1); Abū Ḥanīfa Aḥmad ibn Dāwūd al-Dīnawarī (1); Abū Naṣr Muḥammad ibn Muḥammad al-Fārābī (1) |
| A to Z index letters (decision) | 26 | 26 | A (1); B (1); C (1); D (1); E (1); F (1); G (1); H (1); I (1); J (1); K (1); L (1) |
| LEFTOVER English abbreviations | 19 | 127 | CE (35); AH (34); c (23); h (10); s (9); g (2); e (2); d (1); I (1); E (1); y (1); p (1) |
| LEFTOVER roots in Latin letters | 29 | 41 | j-b-r (4); a-n-s (3); j-l-l (2); j-n-n (2); j-r-r (2); j-w-d (2); j-h-r (2); s-l-m (2); s-m-r (2); ḥ-w-h (1); a-m-n (1); n-w-r (1) |
| LEFTOVER another name in Latin letters | 49 | 62 | Ruqayyah (7); Umayma (3); Medina (2); Muadh (2); Walid (2); Uthman (2); Sufyan (2); Abeer (1); Ahmed (1); kerim (1); Cyrus (1); Darius (1) |
| legitimate: the name itself, romanised | 2468 | 2473 | Faiz (2); Sad (2); Safiyyah (2); Salim (2); Yaqub (2); Aabid (1); Aabida (1); Aahil (1); Aairah (1); Aaliya (1); Aaliyah (1); Aamir (1) |
| legitimate: brand | 1 | 2413 | AsrNaam (2413) |
| legitimate: language switch | 5 | 4906 | English (2450); EN (2412); Türkçe (42); English A (1); Z (1) |

### Hindi

| Kind | Distinct strings | Pages x strings | Most frequent |
|---|---|---|---|
| LEFTOVER interface or English words | 2 | 2 | ay (1); Ash (1) |
| LEFTOVER person or place names | 19 | 38 | Abu Bakr al-Razi (2); Abu Hurairah (2); Abd ar Rahman (2); Abd al-Mumin (2); Al-Khwarizmi (2); Al-Ghazali (2); Al-Zahrawi (2); Al-Tusi (2); Al-Biruni (2); Al-Husain (2); Ibn al-Nafis (2); Ibn Sina (2) |
| Pronunciation in Latin letters (decision) | 451 | 456 | LAI-la (2); moo-HAM-mad (2); su-LAY-mahn (2); YOO-suf (2); ZAI-nab (2); aa-I-rah (1); aa-MI-ra (1); AA-riz (1); ab-dar-RAH-man (1); AB-dou (1); ab-dou-LAY-e (1); ab-dul-MA-lik (1) |
| LEFTOVER another name in Latin letters | 1 | 1 | nur (1) |
| legitimate: the name itself, romanised | 519 | 1480 | Yaqub (4); Ansar (3); Anas (3); Anis (3); Abul-Qasim (3); Abdou (3); Abdurrazzaq (3); Abdulaziz (3); Abdulqayyum (3); Abdulqadir (3); Abdulghani (3); Abdulghafoor (3) |
| legitimate: brand | 1 | 502 | AsrNaam (502) |
| legitimate: language switch | 2 | 532 | English (502); Türkçe (30) |

### Turkish: English words found

and (2); Urdu (1)

## Site name: spellings in use

- Urdu: اثر نام on 2450 pages; AsrNaam on 2413 pages; اسرنام on 1 pages
- Arabic: أثر نام on 2450 pages; AsrNaam on 2413 pages; اثر نام on 1 pages
- Hindi: असर नाम on 502 pages; AsrNaam on 502 pages; अस्रनाम on 1 pages
- Turkish: AsrNaam on 169 pages; اثر نام on 1 pages

## Letter forms

- Urdu pages, inside a word that also has Urdu-only letters (certain error): ى alef maksura (Urdu uses ی): 1 words on 1 pages; ك Arabic kaf (Urdu uses ک): 236 words on 118 pages; ه Arabic ha (Urdu uses ہ or ھ): 257 words on 17 pages; ة ta marbuta (Urdu uses ہ or ۃ): 21 words on 1 pages
- Urdu pages, in a word written wholly in the other form (may be a cited word): ي Arabic ya (Urdu uses ی): 13 words on 6 pages; ك Arabic kaf (Urdu uses ک): 1 words on 1 pages; ه Arabic ha (Urdu uses ہ or ھ): 136 words on 76 pages; ة ta marbuta (Urdu uses ہ or ۃ): 24 words on 7 pages
- Arabic pages, inside a word that also has Arabic-only letters (certain error): ی Farsi/Urdu ya (Arabic uses ي or ى): 19 words on 8 pages; ک Urdu kaf (Arabic uses ك): 22 words on 9 pages; ہ Urdu he (Arabic uses ه): 35 words on 14 pages; ۃ Urdu ta marbuta: 34 words on 20 pages
- Arabic pages, in a word written wholly in the other form (may be a cited word): ی Farsi/Urdu ya (Arabic uses ي or ى): 357 words on 220 pages; ک Urdu kaf (Arabic uses ك): 70 words on 24 pages; ہ Urdu he (Arabic uses ه): 134 words on 101 pages; ھ Urdu do-chashmi he: 1 words on 1 pages; ۃ Urdu ta marbuta: 6 words on 5 pages

Counted outside the name's own Arabic spelling, the root, the letter cards, quoted Arabic in « », and fully vowelled Arabic words.

## Wording shared across many pages

**Urdu**: 19% of paragraph words sit in paragraphs that are identical on 49 or more pages once the name and numbers are blanked. Most repeated:

- 2367 pages: حسابِ جُمل کے مطابق دکھائے ہوئے حروف کا مجموعہ # ہے، اور اس کا مختصر عدد # ہے۔ یہی اس نام کا ابجد خوش نصیب عدد ہے۔
- 2165 pages: بہن بھائی کے نام خاندان کا ذوق ہے۔ نیچے متعلقہ نام ◌ سے حرف، جذر، یا روایت میں ملتے ہیں۔ یہ جوڑ کوئی قاعدہ نہیں۔
- 986 pages: وہی عربی نام مختلف خطوں میں مختلف رومن املا لیتا ہے۔ حروف اور جذر وہی رہتے ہیں۔
- 588 pages: انگریزی میں اسے ◌ لکھا جاتا ہے، اور مختلف اسلامی علاقوں میں اس کے تلفظ میں معمولی فرق ہوتا ہے۔

**Arabic**: 29% of paragraph words sit in paragraphs that are identical on 49 or more pages once the name and numbers are blanked. Most repeated:

- 1989 pages: مجموع قيم حروف الاسم بحساب الجُمَّل هو #، ورقمه المختزل #. اقرأ دلالة كل حرف في قسم القراءة حرفاً بحرف أعلاه.
- 1355 pages: يُكتب الاسم بالعربية: ◌، وبالإنجليزية: ◌. وبالأردية يُكتب: ◌.
- 687 pages: ◌ يُقرأ ثلاث قراءات, معنى الاسم، ودلالة حروفه، وما يستدعيه من حامله.
- 593 pages: يُكتَب ◌ في الإنجليزية، ويُقرأ في البيئات الإسلامية المختلفة بنُطقٍ يَختلف قليلاً بحَسَب المنطقة.

**Hindi**: 27% of paragraph words sit in paragraphs that are identical on 20 or more pages once the name and numbers are blanked. Most repeated:

- 500 pages: प्राप्त होता है। यह गणना इस्लामी अक्षर-विज्ञान (इल्म-उल-हुरूफ़) की सदियों पुरानी पद्धति से की गई है:
- 500 pages: इल्म-उल-हुरूफ़ (अबजद गणना) के अनुसार इस नाम के अक्षरों का योग # है, और इसका शुभ अंक # है।
- 370 pages: यह नाम अरबी में ◌ और उर्दू में ◌ लिखा जाता है; अंग्रेज़ी में ◌।
- 228 pages: । यह लड़कियों का नाम है, जिसकी अरबी लिखावट ◌ है। उर्दू में इसे ◌ लिखा जाता है।

**Turkish**: 21% of paragraph words sit in paragraphs that are identical on 20 or more pages once the name and numbers are blanked. Most repeated:

- 168 pages: eder; bu sayının rakamları tek haneye inene kadar toplandığında ebced rakamı
- 168 pages: Bu sayfada bir hata mı gördünüz ya da bu isim hakkında bir sorunuz mu var?
- 159 pages: Ebced hesabına göre ◌ harflerinin toplamı #, rakamları tek haneye inene kadar toplanınca # elde edilir.
- 132 pages: Ebced hesabında Arap alfabesinin her harfinin geleneksel bir sayı değeri vardır. ◌ isminin Arapça yazılışı

## English text added by scripts after the page loads

A static read of the HTML cannot see this text. These script files are loaded by the translated pages and contain English strings that they write into the page:

- `/asr-redesign.js` (reads the page language: no): Copied; Copy link; Favourites; Play pronunciation; Saved in this browser; Search another name
- `/asr-theme.js` (reads the page language: no): Toggle theme

Measured in a real browser (`redesign/lang/runtime.json`): strings present after scripts ran that are not in the HTML file.

- `ur/names/zayd/index.html`: "Save" (span); "Share" (span); "Abjad lucky number" (span.rd-kicker); "Advertisement" (span.asr-ad-label); "Search another name" (label.rd-sr); "Toggle theme" (@aria-label button.asr-theme-toggle); "Favourites" (@aria-label a.rd-nav-heart); "Play pronunciation" (@aria-label button.rd-play); "peace be upon him" (@aria-label span.saw); "Advertisement" (@aria-label aside.asr-ad); "Search another name" (@placeholder input#rd-m-q); "Save to favourites" (@aria-label button.h); "Share" (@aria-label button.s)
- `ar/names/zayd/index.html`: "Save" (span); "Share" (span); "Abjad lucky number" (span.rd-kicker); "Advertisement" (span.asr-ad-label); "Search another name" (label.rd-sr); "Toggle theme" (@aria-label button.asr-theme-toggle); "Favourites" (@aria-label a.rd-nav-heart); "Play pronunciation" (@aria-label button.rd-play); "peace be upon him" (@aria-label span.saw); "Advertisement" (@aria-label aside.asr-ad); "Search another name" (@placeholder input#rd-m-q); "Save to favourites" (@aria-label button.h); "Share" (@aria-label button.s)
- `hi/names/ali/index.html`: "Toggle theme" (@aria-label button.asr-theme-toggle); "Favourites" (@aria-label a.rd-nav-heart)
- `tr/names/osman/index.html`: "Toggle theme" (@aria-label button.asr-theme-toggle); "Favourites" (@aria-label a.rd-nav-heart)
- `ur/index.html`: "Advertisement" (span.asr-ad-label); "Toggle theme" (@aria-label button.asr-theme-toggle); "Advertisement" (@aria-label aside.asr-ad)
- `ur/names/index.html`: "Advertisement" (span.asr-ad-label); "Toggle theme" (@aria-label button.asr-theme-toggle); "Favourites" (@aria-label a.rd-nav-heart); "Advertisement" (@aria-label aside.asr-ad)

## Site-level

- C1 section exists only in English: 20 (/ur/letters/, /ur/about/, /ur/contact/, /ur/privacy/, /ur/terms/)
- P16 language has no home page: 1 (/tr/)
- Sitemaps read: sitemap-aathaar.xml, sitemap-ar.xml, sitemap-basaair.xml, sitemap-blog-meta.xml, sitemap-canonicals.xml, sitemap-hi.xml, sitemap-letters.xml, sitemap-tr.xml, sitemap-ur.xml, sitemap.xml

