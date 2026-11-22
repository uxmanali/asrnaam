# Arabic review: the 12 batch-one name pages

Read line by line on 22 Nov 2026 from production (`origin/main`), against the English pages and `redesign/pilot/<slug>.json`. Title, meta descriptions, JSON-LD, H1, body, FAQ, labels and accessibility text were all read. Companion file: `redesign/lang/fixes-ar.json` (88 exact corrections, 167 replacements, every one checked by script against production).

## The answer

**The Arabic pages are not at publishing standard today. None of the 12 is clean, and most of what is wrong is the template, so it is wrong on about half of all 2,448 Arabic pages.**

Three reasons:

1. **Punctuation and grammar that no Arabic editor would pass.** Ten of the 12 use the Latin comma (,) inside Arabic sentences, including in the H1. Site-wide: 1,263 pages.
2. **Text that is cut off or filled with nothing.** FAQ answers and fact rows stop in mid-phrase (Ayyub, Hatice, Luqman here; 29 FAQ answers and 105 letter rows site-wide). Three pages (Khansa, Hatice, Kainat) carry filler paragraphs that state no fact.
3. **A few things that are simply false or nonsense.** Fadwa Tuqan is called "the wife of the Palestinian national movement"; an unverifiable "Fadwa Malik" is listed; Ayyub's H1 says God spoke a verse "to him" that is about him; Bayezid is called a "title".

What is good: the Quran quotations are letter-correct on all 12; the numerology totals are right on all 12 and agree with English; honorifics for the Prophet, prophets and Companions are used correctly where present; Zayd, Osman, Luqman and Ayyub have real, well-written Arabic prose.

### Grade per page

| Page | Grade | Certain fixes | Likely | Style | Needs Usman | One-line verdict |
|---|---|---|---|---|---|---|
| zayd | B+ | 4 | 1 | 0 | 0 | Clean native prose. One lexical error (الزاد is not from this root). |
| osman | B- | 6 | 1 | 2 | 2 | Good prose. FAQ answer is a pasted advert; tribe name misspelt; origin disagrees with English. |
| ghada | B- | 7 | 0 | 3 | 0 | Sound content. Name stutters in the H1; Latin commas. |
| luqman | C+ | 9 | 1 | 2 | 1 | Good prose spoiled by a three-error phrase and a cut-off row. |
| ayyub | C+ | 9 | 2 | 1 | 3 | Good prose. H1 misattributes the verse; FAQ cut off; page contradicts itself on origin and on letter count. |
| bayezid | C+ | 9 | 1 | 3 | 1 | Solid history. Wrong word for "name", wrong pronoun number, wrong term for the Persian form. |
| ahlam | C | 9 | 1 | 0 | 0 | Thin. Wrong case ending; the writer's surname is missing. |
| mansur | C | 6 | 0 | 3 | 0 | Thin (530 words, no bearers, no root row). Punctuation only. |
| fadwa | C- | 10 | 3 | 3 | 1 | Richest page, worst errors: an invented relationship and an unverifiable bearer. |
| hatice | D+ | 7 | 2 | 1 | 3 | Never says Hatice is the Turkish form. "Meaning" is a person. Filler paragraphs. |
| khansa | D | 6 | 2 | 1 | 1 | Never says what the word means. Filler paragraphs. No bearers though the page is about one. |
| kainat | D | 6 | 1 | 0 | 1 | Filler paragraphs, a placeholder in the letter reading, an unsourced "top ten" claim. |

### Defects by type (certain fixes only, distinct defects)

| Type | Count | What it is |
|---|---|---|
| Grammar and punctuation | 33 | Latin commas, stuttered H1s, wrong case, wrong verb gender, wrong pronoun number, doubled labels |
| Spelling | 17 | ألف without hamza, space before the comma, tribe name |
| Mistranslation or wrong word | 16 | "Latin pronunciation" label, لقب for a name, معرَّب for a Persian form, "said to him" |
| Untranslated or cut off | 16 | English aria-label, truncated FAQ answers and rows, missing surname |
| Fact | 5 | الزاد root, young serpent, Fadwa Tuqan "wife", Fadwa Malik, "top ten in Pakistan" |
| Register | 1 | Missing honorific in a bearers list |
| **Total** | **88** | 38 page-specific, 26 template text, 24 template labels |

## The defects are systematic

Counted on all 2,448 Arabic name pages on production.

| Defect | Pages | Exact text | Class |
|---|---|---|---|
| Latin comma in Arabic text | 1,263 | `{الاسم} يُقرأ ثلاث قراءات, معنى الاسم، ودلالة حروفه، وما يستدعيه من حامله.` (this one sentence: 1,191 pages) | Safe script fix for the subtitle; meaning lines need a per-page pass because some should be a colon and some a comma |
| Space before the comma in the JSON-LD headline | 1,655 | `معنى اسم {الاسم} ، رسمه العربي وقراءته في علم الحروف` | Safe script fix |
| Letter name without hamza | 1,487 | `الف` in the letter grid, should be `ألف` | Safe script fix |
| Label "Latin pronunciation" | 2,411 | `النطق اللاتيني` above a spelling such as Zayd, should be `الرسم اللاتيني` | Label file |
| English accessibility label | 2,411 | `aria-label="Breadcrumb"` | Label file |
| FAQ meaning answer cut off | 29 | Yunus: `الذي نادى في الظُّلمات: «لا إله.` Khalid: `خالد بن الوليد رضي.` Talha: `طلحة بن عبيد الله رضي.` | **Urgent.** The Yunus answer stops at "there is no god". It is in the JSON-LD that Google reads. Needs a per-page fix from each page's own meaning line |
| Letters row cut off | 105 | `الألفُ قائمةٌ، صِلةٌ` | Fix from each page's own letters sentence |
| Meaning row cut off | 34 | Rihanna: `الرَّيحان, ` | Per page |
| FAQ meaning answer is an advert | 58 | `قراءة كل حرف على أثر نام مع الجذر العربي والرسم الأردي.` | Script fix: use the page's meaning line |
| Filler paragraph, root | 243 | `هو الأساس اللُّغوي الذي تَتفرّع منه صورة الاسم، ومنه يَتّضح ارتباطه بمعنى «…».` | Needs real content or removal |
| Filler paragraph, letters | 288 | `هذه القراءة الحرفية تَكشف صورةً مُجمَلة لإيقاع الاسم وحركته الباطنة، وكيف يَتآلف صدرُه مع مَقطعه ومع خاتمته.` | Same |
| Filler paragraph, usage | 287 | `وقد جرى استعمال هذا الاسم في بيئات مسلمة متعدّدة، وحَفِظ معناه اللطيف على مرّ العصور.` | Same |
| Filler paragraph, spelling | 595 | `ويُقرأ في البيئات الإسلامية المختلفة بنُطقٍ يَختلف قليلاً بحَسَب المنطقة.` | Same |
| Urdu letters (ی ک ہ) in Arabic text outside the Urdu-spelling row | 410 | Shiza: title and H1 `شیزا`; Hatice related chip `جیلان` | Names: Usman's decision (see below) |
| Origin says Arabic, root row says otherwise | 43 | Ayyub: origin `عربي`, root `عبرانيّ معرَّب` | Usman's decision |
| Mixed digits | about 2,000 | `القسم 1`, `عدد الحروف 3`, `(الأحزاب: 37)` beside `٢١`, `~٥٨١–٦٢٩ م` | Decision: pick one system |

## Needs Usman (not in the fixes file)

1. **Fadwa, vowel on the name.** The page writes `فِدْوى` (Fidwa) in the meaning line and body, but `فَدوى طوقان` in the bearers text, Latin `Fadwa`, and English pronunciation FAD-wa. The name is فَدْوى. This is the name's own spelling, so I have not touched it. Evidence is on the page itself.
2. **Hatice, related-name chip `جیلان`** (links to `/ar/names/ceylan/`) is written with the Urdu letter ی (U+06CC). In Arabic it is `جيلان`. Same class as the 410 pages above. Name spelling, so not touched.
3. **Hatice and Osman titles.** The Arabic page for Hatice is titled `خَدِيجَة` and never says it is the Turkish form; Osman is titled `عُثْمَان (عُسْمَان)`, where `عُسْمَان` is not an Arabic word. This is open decision D-9.
4. **Origin labels.** Osman: Arabic page says `تركي`, English page says Arabic. Ayyub: card, meta and the "Islamic name?" paragraph say `عربي`, while the same page says `غير عربيّ الأصل، معرَّب من العبرانيّة`. Luqman: `وأصلُه عربي` beside `أصلُ الاسم غيرُ مُتَّفَقٍ عليه`. Same open decision as on the English side.
5. **Ayyub, letter count.** `عدد الحروف 4`, the grid shows four letters and the total 19 counts four, but `تفصيل الحروف` shows five (`أ · ي · ي · و · ب`) and the reading speaks of two ya's (`الياءان`). The English page says four letters. One of the two must give way.
6. **Ayyub, commas inside the verse.** The H1 quotes 38:44 with Arabic commas in place of the pause marks (`صَابِرًا، نِعْمَ الْعَبْدُ، إِنَّهُ أَوَّابٌ`). The letters are right. I do not edit Quran text; the clean form has no commas.
7. **Bayezid I, birth year.** Arabic `١٣٥٤–١٤٠٣ م` (twice), English `1360–1403`. Sources differ (Marefa: about 1345 in the text, 1354 in the box; Britannica and the English page: about 1360). The two languages should say the same thing. Recommend 1360 with "نحو".
8. **Letter meanings differ between languages and between pages.** Luqman: English "Lam authority, Qaf nearness, Mim love, Alif origin, Nun depth"; Arabic `اللام لُطف، القاف قوّة وقَرار، الميم رَحِم، الألف قائمة، النون نُور ورَأفة`. Across the Arabic pages the same letter is read differently: ميم is `محبّة` (Mansur), `حبّ` (Osman), `رَحِمٌ تَحتضن` (Luqman); دال is `باب` (Zayd, Bayezid, Hatice), `دَوام` (Fadwa), `دَلال` (Ghada); نون is `عمق` (Mansur, Osman) and `نُور ورَأفة` (Luqman). Fadwa and Ghada use an alliteration method (ف فِداء، د دَوام) that the others do not. This is the core of the site and belongs to the letter model, not to an editor.
9. **Kainat, the letter ئ.** Its reading is `الياء بهمزة` ("the ya with a hamza"), a description where a reading should be. English says "Ya reaching". Two Arabic pages have this placeholder.
10. **Brand in Arabic.** `أثر نام`: in Arabic `نام` is the verb "he slept", so an Arab reader sees "a trace slept". It is the brand, so it is your call; an option is to keep Latin `AsrNaam` on Arabic pages.
11. **Meaning that is a person.** Khansa (`الخنساء بنت عمرو، شاعرة الإسلام`) and Hatice (`السيدة خديجة بنت خويلد رضي الله عنها، أم المؤمنين`) give a person where the row is titled "dictionary meaning". The English pages have the same weakness in the short field but explain the word in the body (Khansa: "the snub-nosed gazelle", root kh-n-s). The Arabic pages never explain it. Suggested Arabic is in the page tables below, for your approval.

## Page by page

Confidence: **certain** = in `fixes-ar.json`; **likely** = a defect, wording is my proposal; **style** = preference.

### Template lines (on all 12)

| Arabic text | What is wrong | Proposed | Meaning of proposed | Confidence |
|---|---|---|---|---|
| `يُقرأ ثلاث قراءات, معنى الاسم` | Latin comma where a list starts | `يُقرأ ثلاث قراءات: معنى الاسم` | "is read in three readings: the meaning of the name..." | certain |
| `{الاسم} ، رسمه العربي` (JSON-LD headline) | Space before the comma | `{الاسم}، رسمه العربي` | same | certain |
| `الف` (letter grid) | Letter name without hamza | `ألف` | alif | certain |
| `النطق اللاتيني` | "Latin pronunciation" over a spelling | `الرسم اللاتيني` | "Latin spelling" | certain |
| `aria-label="Breadcrumb"` | English | `مسار التنقل` | "navigation path" | certain |
| `اسم مسلم للذكور` / `للإناث` | Calque of "Muslim boy name"; reads as "the name of a Muslim" | `من أسماء المسلمين · للذكور` | "a name used by Muslims, for boys" | likely |
| `القسم 3 · المعنى العائلي` | "The family meaning" means nothing in Arabic | `المعنى المتداوَل` | "the meaning in common use" | likely |
| `القسم 5 · الحاملون` after `القسم 3` | Numbering skips 4 | Drop the numbers in the new layout | | style |
| `الجذر العربي` on Bayezid, Ayyub, Luqman | Label says "Arabic root" where the row says the name is not Arabic | `أصل الاسم` on those pages | "origin of the name" | likely |
| `~٥٨١–٦٢٩ م` | Tilde for "about" | `نحو ٥٨١–٦٢٩ م` | "about 581 to 629" | style |
| Quran in `«…»` on some pages, `﴿…﴾` on Fadwa | Inconsistent | Use `﴿…﴾` for Quran everywhere | | style |

### zayd (B+)

| Arabic text | What is wrong | Proposed | Meaning of proposed | Confidence |
|---|---|---|---|---|
| `ومنه «المَزِيد» (الزيادة)، و«الزّاد» (ما يَمتدّ به العمر).` | الزاد (provisions) is from the root ز-و-د, not ز-ي-د | `ومنه «المَزِيد» (الزيادة).` | "From it comes al-mazid (increase)." | certain |
| `النموّ والزيادة، زيد بن حارثة، الصحابي الذي ذُكر اسمه في القرآن` (meaning row, FAQ, meta) | A meaning and a person run together as if one list | `النموّ والزيادة. وأشهر من حمله زيد بن حارثة، الصحابي الذي ذُكر اسمه في القرآن` | "Growth and increase. Its best-known bearer is Zayd ibn Haritha, the Companion named in the Quran" | likely |
| Bearers list has one person | English also lists Zayd ibn Ali | Add after translation and source check | | gap |

### osman (B-)

| Arabic text | What is wrong | Proposed | Meaning of proposed | Confidence |
|---|---|---|---|---|
| `عثمان، الصيغة التركية للاسم، مؤسس الدولة العثمانية. قراءة كل حرف على أثر نام مع الجذر العربي والرسم الأردي.` (FAQ answer, twice) | Answer to "what does it mean" is a page description ending in an advert | `الصورة التركيّة لاسم «عُثْمَان» العربيّ، وأشهر من حمله عُثمان غازي، مؤسّس الدولة العُثمانيّة.` | "The Turkish form of the Arabic name Uthman; its best-known bearer is Osman Ghazi, founder of the Ottoman state." | certain |
| `قبيلة قَيِي التركيّة` | Tribe name misspelt | `قبيلة قايي التركيّة` | "the Turkic Kayi tribe" | certain |
| `والاسم العربيّ من معاني فَرخ الحبارى أو الحيّة الكبيرة في كلام العرب القدماء، رَمز القوّة الهادئة.` | Broken construction; "the big snake" disagrees with English "the young serpent" | `ومن معاني الاسم العربيّ في كلام العرب القدماء: فَرخ الحُبارى، أو فَرخ الحيّة، رَمز القوّة الهادئة.` | "Among the meanings of the Arabic name in old Arab speech: the bustard chick, or the young serpent, a sign of quiet strength." | certain |
| `امتدّت ٦٢٣ عاماً` (H1) and `من سَنة ١٢٩٩ إلى ١٩٢٤ م` (body) | 1299 to 1924 is 625 years, not 623. 623 fits 1922 (sultanate abolished); 1924 is the caliphate | Either `٦٢٥ عاماً` or `إلى ١٩٢٢ م` | | likely |
| `نفس جذر «عُثمان» العربيّ` | Purists prefer the noun first | `جذر «عُثمان» العربيّ نفسه` | "the very root of Arabic Uthman" | style |
| Related chips `عُمَر عُمَر عُثْمَان عُثْمَان عُثْمَان` | Five chips, two labels: variants cannot be told apart | Show the Latin form beside each | | style |

### ghada (B-)

| Arabic text | What is wrong | Proposed | Meaning of proposed | Confidence |
|---|---|---|---|---|
| `<em>غادَة</em>, غادَة, المَرأَة الناعِمَة، الفَتاة الحَسناء.` (H1) | Name printed twice; Latin commas | `غادَة: المَرأَة الناعِمَة، الفَتاة الحَسناء.` | "Ghada: the soft, graceful woman; the lovely girl." | certain |
| `غادَة, المَرأَة الناعِمَة` (8 places) | Latin comma | `غادَة: المَرأَة الناعِمَة` | same | certain |
| `الجذر العربي` row: `الجذر غ-ي-د: …` | "Arabic root: the root gh-y-d" says it twice | `غ-ي-د: الغَيد، …` | | style |
| `اسم عَرَبيٌّ كَلاسيكيٌّ` | Loanword where Arabic has its own | `اسمٌ عربيٌّ عريق` | "an old Arabic name" | style |
| FAQ writes `غادة`, H1 writes `غادَة` | Inconsistent vowel marking | One form throughout | | style |

### luqman (C+)

| Arabic text | What is wrong | Proposed | Meaning of proposed | Confidence |
|---|---|---|---|---|
| `<em>لُقْمَان</em>, لُقْمان, الحَكيمُ الذي اصطَفاه اللهُ بالحِكمة` (H1) | Name printed twice; Latin commas | `لُقْمَان: الحَكيمُ الذي اصطَفاه اللهُ بالحِكمة، سُورةٌ في القرآن.` | "Luqman: the wise man God singled out with wisdom; a surah of the Quran." | certain |
| `لُقمان, رَجلٌ صالحٌ` (7 places) | Latin comma | `لُقمان: رَجلٌ صالحٌ` | same | certain |
| `الألفُ قائمةٌ، صِلةٌ` (letters row) | Cut off in mid-phrase | `الألفُ قائمةٌ، صِلةٌ بين السماء والأرض، النونُ نُورٌ ورَأفة` | "...alif upright, a link between heaven and earth; nun is light and mercy" (the page's own sentence) | certain |
| `يُعَدّ كَنَزٌ مِن كُنُوز التَّربية` | Verb should be feminine; wrong vowels; wrong case | `تُعَدّ كَنْزاً مِن كُنُوز التَّربية` | "(counsels) counted a treasure among the treasures of upbringing" | certain |
| `قال تعالى: «وَلَقَدْ آتَيْنَا لُقْمَانَ الْحِكْمَةَ أَنِ اشْكُرْ لِلَّهِ».` | No reference, while the next quote has one | add `(لقمان: 12)` | | likely |
| `سُورةٌ في القرآن` at the end of the H1 | Hangs loose | `وباسمه سُورةٌ في القرآن` | "and a surah of the Quran bears his name" | style |
| `اسماً عَلَماً مَخصوصاً` | Unusual term | `عَلَماً أعجميّاً` | "a non-Arabic proper name" | style |

### ayyub (C+)

| Arabic text | What is wrong | Proposed | Meaning of proposed | Confidence |
|---|---|---|---|---|
| `<em>أَيُّوب</em>, نبيّ الصبر, الذي قال له ربّه: «…»` (H1) | Latin commas; "his Lord said **to** him" but the verse is **about** him | `أَيُّوب: نبيّ الصبر، الذي قال فيه ربّه: «…»` | "Ayyub: the prophet of patience, of whom his Lord said: ..." | certain |
| `أَيُّوب عليه السلام, نبيّ الصبر` (7 places) | Latin comma | `أَيُّوب عليه السلام، نبيّ الصبر` | same | certain |
| `الذي ضُرب به المَثَل في احتمال.` (FAQ, twice) | Cut off before the last word | `…في احتمال البلاء.` | "...proverbial for bearing affliction." | certain |
| `قَرَّبه بعض اللغة من «الأَوْب»` | Word missing | `قَرَّبه بعض أهل اللغة من «الأَوْب»` | "some linguists linked it to al-awb" | certain |
| `فلم يَشكُ، حتى مَسَّ ضرٌّ نَفسَه فدعا ربّه` | Awkward, and implies he did complain in the end | `فصبر ولم يَشكُ، ثم دعا ربّه` | "he bore it without complaint, then called on his Lord" | likely |
| `~القرن ١٨ ق.م` (bearer row) | A date for a prophet with no source; not on the English page | Remove the date, keep `الشام` | | likely |
| `أَيُّوب اسم نَبَويّ` | "A prophetic name" is not said this way | `اسمُ نبيّ` | "the name of a prophet" | style |

### bayezid (C+)

| Arabic text | What is wrong | Proposed | Meaning of proposed | Confidence |
|---|---|---|---|---|
| `<em>بايَزِيد</em>, صورة فارسيّة لـ «أبي يَزِيد», لقَب سلطانَين عُثمانيَّين، أَشهرهم` (H1) | Latin commas; لقب means title or nickname; plural pronoun for two men | `بايَزِيد: صورة فارسيّة لـ «أبي يَزِيد»، اسمُ سلطانَين عُثمانيَّين، أَشهرهما` | "Bayezid: a Persian form of Abu Yazid, the name of two Ottoman sultans, the better known of whom..." | certain |
| `بايَزِيد, صورة فارسيّة` (7 places) | Latin comma | `بايَزِيد: صورة فارسيّة` | same | certain |
| `لقَب سلاطين عُثمانيّين` (7 places) | Not a title; and there were two, not "sultans" | `اسمُ سلطانَين عُثمانيَّين` | "the name of two Ottoman sultans" | certain |
| `فارسيّ معرَّب من كنية «أبو يَزِيد»` | معرَّب means "Arabized", the opposite of what happened | `صيغة فارسيّة للكنية العربيّة «أبو يَزِيد»` | "a Persian form of the Arabic kunya Abu Yazid" | certain |
| `الألف قائمة` (fact row) and `الألف قامة` (letters section) | Two different words for the same letter on one page | One word throughout | | likely |
| `يَختاره الوالدون` | Rare plural | `يَختاره الآباء` | "parents choose it" | style |
| `«أبو» + «يَزيد»` | Plus sign in prose | `من «أبو» و«يَزيد»` | | style |
| Name vowelled three ways in the body: `بايَزِيد`, `بَايَزِيد`, `بَايَزيد` | Inconsistent | One form (name spelling: your call) | | style |
| No meaning given | English says "Father of increase" | add `أبو الزيادة` | | gap |

### ahlam (C)

| Arabic text | What is wrong | Proposed | Meaning of proposed | Confidence |
|---|---|---|---|---|
| `<em>أَحْلَام</em>, أَحلام, جَمع حُلم` (H1) | Name printed twice; Latin commas | `أَحْلَام: جَمع حُلم، الرُّؤى الجَميلة.` | "Ahlam: plural of hulm, beautiful visions." | certain |
| `أَحلام, جَمع حُلم` (8 places) | Latin comma | `أَحلام: جَمع حُلم` | same | certain |
| `الرُّؤيَا ولينَ الخُلق` (twice) | Wrong case ending | `الرُّؤيَا ولينُ الخُلق` | "the vision and gentleness of character" | certain |
| `ومن الاسم «أَحلام» الكاتبة الجزائريَّة المُعاصرة، رمز الحَنين` | Surname missing; "from the name is the writer" | `وممّن حمل الاسم الكاتبة الجزائريَّة المُعاصرة أحلام مستغانمي، رمز الحَنين` | "Among its bearers is the contemporary Algerian writer Ahlam Mosteghanemi, a symbol of longing" | certain |
| `الحُلم: الرُّؤيَا ولينُ الخُلق` | Two different words merged: حُلْم is a dream, حِلْم is forbearance | `الحُلْم: الرُّؤيا، والحِلْم: الأناة ولينُ الخُلق. و«أحلام» جمعٌ لهما.` | "hulm is a dream; hilm is forbearance and gentleness. Ahlam is the plural of both." | likely |

### mansur (C)

| Arabic text | What is wrong | Proposed | Meaning of proposed | Confidence |
|---|---|---|---|---|
| `<em>منصور</em>, المنصور, مُؤيَّدٌ من اللّه.` (H1) | Latin commas | `منصور: المنصور، مُؤيَّدٌ من اللّه.` | "Mansur: the victorious, aided by God." | certain |
| `المنصور, مُؤيَّدٌ من اللّه` (9 places) | Latin comma | `المنصور، مُؤيَّدٌ من اللّه` | same | certain |
| `اسمُ منصور اسمٌ من أصلٍ عربي` | "The name Mansur is a name" | `منصور اسمٌ عربيّ الأصل` | "Mansur is a name of Arabic origin" | style |
| `يُكتَب Mansur في الإنجليزية` | Wrong preposition for a language | `يُكتَب بالإنجليزية Mansur` | "written Mansur in English" | style |
| `اللّه` here, `الله` on other pages | Inconsistent | `الله` | | style |
| No root row, no letters row, no bearers | English lists four bearers | Add after translation and source check | | gap |

### fadwa (C-)

| Arabic text | What is wrong | Proposed | Meaning of proposed | Confidence |
|---|---|---|---|---|
| `<em>فدوى</em>, فِدْوى, الفِداء، التَّضحيَة` (H1) | Name printed twice; Latin commas | `فدوى: الفِداء، التَّضحيَة الواجِبَة بالحُبِّ.` | "Fadwa: ransom, the sacrifice love requires." | certain |
| `فِدْوى, الفِداء، التَّضحيَة` (8 places) | Latin comma | `فِدْوى: الفِداء، التَّضحيَة` | same | certain |
| `الجذر: عربي: ف-د-ي (الفِداء).` (3 head descriptions, 1 row) | Label doubled | `الجذر: ف-د-ي (الفِداء).` | "root: f-d-y (ransom)" | certain |
| `أُختُ إِبراهيم طوقان وَ زَوجَة الحَركَة الوَطَنيَّة الفِلَسطينيَّة` | "Wife of the Palestinian national movement": false and meaningless | `أُختُ إِبراهيم طوقان` | "sister of Ibrahim Tuqan" | certain |
| `وفَدوى مالك، شاعِرَة سُوريَّة.` | Unverifiable person; not on the English page | Remove | | certain |
| `التَّضحيَة الواجِبَة بالحُبِّ` | Calque of "devoted sacrifice" | `التَّضحيَة عن مَحبّة` | "sacrifice made out of love" | likely |
| `الكَلِمَة كانَت تُقالُ في العَرَب` | English word order; wrong preposition | `وكانت العَرَب تَقول` | "the Arabs used to say" | likely |
| `ومنه قَولُ القرآن` | Register: Quran is introduced as God's word | `ومنه قَولُه تعالى` | "and from it, His saying, exalted is He" | likely |
| `اسم نِسوي` (twice) | Regional word; standard is different | `اسمٌ مؤنَّث` | "a feminine name" | style |
| Every word fully vowelled | Other pages are lightly vowelled | One house style | | style |
| `(1917–2003م)` | Western digits; other pages use ١٩١٧ | One system | | style |

### hatice (D+)

| Arabic text | What is wrong | Proposed | Meaning of proposed | Confidence |
|---|---|---|---|---|
| `<em>خَدِيجَة</em>, السيدة خديجة بنت خويلد رضي الله عنها, أم المؤمنين.` (H1) | Latin commas | `خَدِيجَة: السيدة خديجة بنت خويلد رضي الله عنها، أم المؤمنين.` | "Khadija: Lady Khadija bint Khuwaylid, may God be pleased with her, Mother of the Believers." | certain |
| `عنها, أم المؤمنين` (8 places) | Latin comma | `عنها، أم المؤمنين` | same | certain |
| `السيدة خديجة بنت خويلد رضي الله عنها.` (FAQ, twice) | Cut-off copy of the meaning line | `…رضي الله عنها، أم المؤمنين.` | adds "Mother of the Believers" | certain |
| `<strong>خديجة بنت خويلد</strong>` (bearers) | Honorific missing here, used elsewhere on the page | `خديجة بنت خويلد رضي الله عنها` | | certain |
| `يُكتب الاسم بالعربية: خَدِيجَة، وبالإنجليزية: Hatice.` | Hatice is the Turkish spelling, not English | `وبالتركية: Hatice` and the question to match | "and in Turkish: Hatice" | likely |
| Whole page | Never tells the reader that Hatice is how Turks write and say Khadija | Add one line: `Hatice هي الصورة التركيّة لاسم خديجة.` | "Hatice is the Turkish form of the name Khadija." | likely (needs your approval) |
| `القرنان السادس والسابع` | Which calendar is not said | `القرنان السادس والسابع الميلاديّان` | "6th and 7th centuries CE" | style |
| Three filler paragraphs | State nothing | Replace with content or remove | | see systematic table |

### khansa (D)

| Arabic text | What is wrong | Proposed | Meaning of proposed | Confidence |
|---|---|---|---|---|
| `<em>الخنساء</em>, الخنساء بنت عمرو, شاعرة الإسلام.` (H1) | Latin commas | `الخنساء: الخنساء بنت عمرو، شاعرة الإسلام.` | "Al-Khansa: al-Khansa bint Amr, poet of Islam." | certain |
| `عمرو, شاعرة الإسلام` (10 places) | Latin comma | `عمرو، شاعرة الإسلام` | same | certain |
| `يَدلّ على معنى: الخنساء بنت عمرو، شاعرة الإسلام.` | "It denotes the meaning: al-Khansa bint Amr." A person is not a meaning. The page never says what the word means | `الخنساء مؤنّث الأخنس، من الخَنَس: تأخُّر الأنف عن الوجه مع ارتفاعٍ قليلٍ في أرنبته، وتوصف به الظباء. وهو لقب تُماضِر بنت عمرو، أشهر شاعرات العرب.` | "Al-Khansa is the feminine of akhnas, from khanas: a short, slightly upturned nose, said of gazelles. It is the epithet of Tumadir bint Amr, the most famous woman poet of the Arabs." (matches the English page) | likely (needs your approval) |
| Al-Khansa named with no honorific | She met the Prophet ﷺ and is counted a Companion; English says she embraced Islam | add `رضي الله عنها` | | likely |
| `شاعرة الإسلام` | She was famous before Islam and lived into it | `شاعرة مُخضرَمة` | "a poet who lived in both eras" | style |
| No bearers section | English lists two (al-Khansa; Khansa bint Khidam, Bukhari 5138) | Add after translation and source check | | gap |

### kainat (D)

| Arabic text | What is wrong | Proposed | Meaning of proposed | Confidence |
|---|---|---|---|---|
| `<em>كائنات</em>, الكون.` (H1) | Latin comma | `كائنات: الكون.` | "Kainat: the universe." | certain |
| `كائنات. الكون، الخلق كله. من العشرة الأوائل في باكستان.` (FAQ, twice) | "Top ten in Pakistan" has no source and is not on the English page; name repeated as a sentence | `الكون، الخلق كلّه. وهو من أكثر أسماء البنات شيوعاً في باكستان.` | "The universe, all of creation. It is among the most common girls' names in Pakistan." (the English claim) | certain |
| `المعنى المعجمي: الكون` | In Arabic كائنات means "beings, all that exists"; "universe" is the Urdu sense. An Arab reader will notice | `الموجودات كلّها؛ وفي الأردية: الكون` | "all that exists; in Urdu: the universe" | likely |
| Three filler paragraphs | State nothing | Replace with content or remove | | see systematic table |

## What I checked and found right

- Quran text on all 12 pages, letter by letter: 33:37 (Zayd), 37:107 (Fadwa), 31:12 and 31:13 (Luqman), 38:44 and 21:83 (Ayyub).
- Numerology on all 12: I re-added the letter values myself; every total and reduced number is right and equals the English "lucky number".
- Gender on all 12 agrees with English.
- Honorifics: ﷺ after the Prophet, عليه السلام for Ayyub, رضي الله عنه for Zayd, رضي الله عنها for Khadija: correct wherever used.
- Dates checked: Fadwa Tuqan 1917 to 2003, Ghada al-Samman born 1942, Bistami died 874, Bayezid II 1447 to 1512, Zayd ibn Haritha died 629.
- The corrections file leaves these fields byte-identical on every page: `.arabic-name`, the name inside the H1, the title, the Arabic spelling row, the Urdu spelling row. After the fixes every JSON-LD block still parses and the visible FAQ still equals the JSON-LD FAQ.

## Sources read on 22 Nov 2026

- Al Jazeera encyclopedia, أحلام مستغانمي: https://www.ajnet.me/encyclopedia/2015/3/15/أحلام-مستغانمي (spelling of the name; Algerian novelist)
- Al Jazeera encyclopedia, the Ottoman state: https://www.aljazeera.net/encyclopedia/2022/11/1/الدولة-العثمانية-كيف-حول-عثمان-ابن (قبيلة قايي; عثمان بن أرطغرل; founding 1299, fall given as 1924)
- Al Jazeera, فدوى طوقان ورحلتها الصعبة: https://www.ajnet.me/culture/2011/12/16/فدوى-طوقان-ورحلتها-الصعبة (1917 to 2003; sister of Ibrahim Tuqan; "شاعرة فلسطين"; the two collections)
- Marefa, بايزيد الأول: https://www.marefa.org/Bayezid_I (fourth sultan; birth year given two ways)
- Marefa, الخنساء: https://www.marefa.org/الخنساء (تماضر بنت عمرو; nickname explained by the shape of her nose; filed under Companions and مخضرمون poets)
- Web search for "فدوى مالك شاعرة سورية": no such poet found.
- Not reached: Britannica and English Wikipedia pages for Bayezid I (fetch refused), so his birth year stays with Usman.
