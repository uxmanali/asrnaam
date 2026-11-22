# Hindi name pages: line-by-line review

Reviewed 22 Nov 2026 against production (`origin/main`). Read in full: mansur, bayezid, khansa, fadwa, luqman, kainat. Read for pattern: aisha, ibrahim, muhammad, yusuf, zainab, omar, hamza, noor. Also read: every unique template sentence used on all 500 Hindi pages (38 letter lines, 25 divine-name lines, 4 element lines) and all 500 meaning lines.

## Answer first

**The Hindi pages are grammatical but machine-templated, and they are not yet at the standard of the English pages.** The spelling of each name is consistent everywhere (title, H1, body, JSON-LD) and nuqta use is correct. The weaknesses are four:

1. **One sentence on all 500 pages states a false cause** ("therefore earth is the element of patience"). Certain, fixable by script.
2. **The reading itself disagrees with the English page on most names.** Hindi always names one "dominant element", even on a tie; English often says the name draws on many elements. 167 of 500 Hindi pages declare a winner on a tie. Needs your decision, not a script.
3. **The "names starting with the same letter" list is wrong on 53 pages** (91 wrong entries). Example: Luqman lists Gulnaz and Gulzar under Lam.
4. **Register is mixed.** Correct Urdu-origin words with nuqta sit next to stiff Sanskrit terms and literal English calques ("एक कोमल और गर्म ध्यान"). 12 pages call Allah "ईश्वर" while the same pages have a section headed "अल्लाह के नाम".

**Certain fixes written: 9 on the six batch-one pages, 518 more on other pages for the same three template defects** (`redesign/lang/fixes-hi.json`, every `old` string verified against production, count exact).

| Page | Grade | Why |
|---|---|---|
| mansur | C+ | False-cause sentence; FAQ answer leaves out Urdu; "ईश्वर"; calques |
| bayezid | C+ | False-cause sentence; meaning line is a note, not a meaning; reading disagrees with English |
| khansa | C | All of the above, plus hamza has no element, element count is 6 for 7 letters, broken noun "ठहर", "meaning" is a description of a person, same-letter list is under Alif because of "al-" |
| fadwa | B- | False-cause sentence; "उद्घाटन" for "opening"; last letter named differently from English |
| luqman | C+ | False-cause sentence; two wrong names in the Lam list; calques |
| kainat | B- | False-cause sentence; Sanskritised meaning; letter named differently from English |

What is right and should be kept: name spellings and nuqta (मंसूर, बायज़ीद, ख़नसा, फ़दवा, लुक़मान, कायनात) are correct and identical in title, H1, body and JSON-LD; gender, lucky number, abjad total, root and pronunciation match the English page on all six; "पैग़म्बर साहब", "क़ुरआन", "इल्म-उल-हुरूफ़", "अबजद" are the natural words; the Bayezid pronunciation fix (ba-ye-ZEED) is live.

The two title patterns (247 pages "Mansur Name Meaning in Hindi: ...", 253 pages "बायज़ीद (Bayezid) नाम का मतलब हिन्दी में: ...") are the two arms of the snippet test, not a defect. Left alone.

## Defects by type

| Type | Batch-one pages | Whole Hindi set | Fixable by script |
|---|---|---|---|
| False cause "इसलिए" | 6 of 6 | 500 of 500 | Yes, in fixes file |
| Broken noun "एक हल्की ठहर" | khansa | 20 pages | Yes, in fixes file |
| Letter name misspelt "आलिफ़ मम्दूदा" | none | 5 pages | Yes, in fixes file |
| FAQ answer leaves out Urdu although the question asks for it | mansur, khansa | 126 pages | Mansur in fixes file; rest need the generator |
| Dominant element declared on a tie | khansa | 167 pages | No. Needs Usman |
| Element counts do not add up to the letter count | khansa | 33 pages | No. Needs the generator |
| Wrong names in the same-letter list | luqman | 53 pages, 91 entries | No. Needs the generator |
| Divine name spelt "अल-मुअमिन" (site elsewhere: "अल-मोमिन") | mansur, luqman | 92 pages | After your nod |
| "ईश्वर" for Allah | mansur | 12 pages | After your nod |
| Calques and Sanskritised glosses | all 6 | all 500 | After a wording pass you approve |
| Mixed spelling conventions (परम्परा / परंपरा) | all 6 | all 500 | After your nod |
| English label in code (`aria-label="Breadcrumb"`) | all 6 | all 500 | Agent B's label file |

## Template sentences on all six pages

| Exact text | What is wrong | Proposed | Meaning of the proposal | Confidence |
|---|---|---|---|---|
| बीच में जो तत्व सबसे भारी पड़ता है वह पृथ्वी है, इसलिए पृथ्वी धैर्य और स्थिरता का तत्व है। | "इसलिए" (therefore) states a false cause: being the heaviest element does not make earth the element of patience. | ...वह पृथ्वी है, और पृथ्वी धैर्य और स्थिरता का तत्व है। | "...is earth, and earth is the element of patience and steadiness." | Certain. In fixes. |
| इस्लामी परम्परा नाम में अच्छा अर्थ चाहती है और यह कि वह अल्लाह के विशेष नामों में से न हो, और यह नाम दोनों शर्तें पूरी करता है। | Clumsy double "और"; "चाहती है ... और यह कि" is translated English. | इस्लामी परंपरा चाहती है कि नाम का अर्थ अच्छा हो और वह अल्लाह के ख़ास नामों में से न हो; यह नाम दोनों शर्तें पूरी करता है। | "Islamic tradition asks that a name have a good meaning and not be one of Allah's own names; this name meets both." | Likely |
| साइट की संपादकीय दृष्टि से हाँ (यह धार्मिक फ़तवा नहीं है) | "संपादकीय दृष्टि" is stiff. | हमारी राय में हाँ (यह कोई फ़तवा नहीं है) | "In our view, yes (this is not a fatwa)" | Style |
| यह गणना इस्लामी अक्षर-विज्ञान (इल्म-उल-हुरूफ़) की सदियों पुरानी पद्धति से की गई है: अंग्रेज़ी पृष्ठ पर अक्षर-दर-अक्षर विवरण उपलब्ध है। | Sends the reader to the English page for a letter-by-letter account that this page itself gives two sections later. | Drop the second half, or point to the section below. | n/a | Likely |
| इस नाम को MAN-sur बोला जाता है। | Pronunciation is given only in English capitals on a Hindi page. Devanagari already shows the sound. | इस नाम को "मन-सूर" बोला जाता है (अंग्रेज़ी में: MAN-sur)। | "Said as man-soor (in English: MAN-sur)." | Likely. Stress placement needs your call, so not in fixes. |
| X नाम अरबी और उर्दू में कैसे लिखा जाता है? (question starts with the Latin name: "Mansur नाम ...") | The other three questions use Devanagari. Probably deliberate for search. | Leave, or use Devanagari. | n/a | Style. Needs Usman. |
| अग्नि / पृथ्वी / जल / वायु | Sanskrit terms. A Muslim family would say आग, मिट्टी, पानी, हवा. | आग, मिट्टी, पानी, हवा | fire, earth, water, air | Style, systematic |
| आत्म-चिन्तन का एक ढाँचा | Stiff. | ख़ुद पर ग़ौर करने का एक ज़रिया | "a way to reflect on oneself" | Style |
| परम्परा, अन्त, आन्तरिक, सम्बन्ध, चिन्तन, बन्द, लम्बा, शान्त (body) against परंपरा, संतुलन, संपर्क, एकांत (same page) | Two spelling conventions on one page. The standard is the anusvara form. | परंपरा, अंत, आंतरिक, संबंध, चिंतन, बंद, लंबा, शांत | same words | Certain that it is inconsistent; the direction is a house-style choice |

## Divine-name lines (shared across pages)

| Exact text | On | What is wrong | Proposed | Meaning | Confidence |
|---|---|---|---|---|---|
| अल-मुअमिन (सुरक्षा देने वाला) | mansur, luqman, 92 pages | Reads "mu-a-min". The Hindi word is मोमिन, and the site itself writes "अल-मोमिन" (abd-al-mumin page) and "उम्मुल-मोमिनीन" (aisha page). English page glosses it "The Faithful". | अल-मोमिन (अमन देने वाला) | "Al-Mu'min (the giver of security)" | Certain that the site contradicts itself. I could not confirm the Devanagari form in an outside Hindi source today, so it is not in fixes. |
| अल-लतीफ़ (सूक्ष्मदर्शी), एक कोमल और गर्म ध्यान | khansa, luqman, 105 pages | "सूक्ष्मदर्शी" is the everyday Hindi word for a microscope. "गर्म ध्यान" is a literal copy of "warm attention" and is not Hindi. | अल-लतीफ़ (बारीकी से जानने वाला, मेहरबान), नर्म और मोहब्बत भरी तवज्जो | "Al-Latif (the subtle, the kind), a gentle and loving attention" | Likely |
| अन-नूर (प्रकाश), वह रोशनी जो कमरे को स्थिर कर देती है | mansur, 88 pages | Literal copy of "light that steadies the room". | अन-नूर (रोशनी), वह रोशनी जिससे माहौल में सुकून आ जाता है | "the light that brings calm to a room" | Likely |
| अल-अहद (एक), अविभाजित उपस्थिति | bayezid, khansa, kainat, 161 pages | "undivided presence" copied word for word. | अल-अहद (अकेला, यकता), पूरी तरह हाज़िर रहना | "Al-Ahad (the One), being fully present" | Style |
| अल-क़य्यूम (स्वयंस्थित) | bayezid, kainat, 234 pages | Coined Sanskrit compound. | अल-क़य्यूम (सबको थामने वाला) | "the one who sustains all" | Style. The site's own abdulqayyum page says "सबको संभालने वाले". |
| अल-ख़बीर (सूक्ष्म ज्ञाता), अल-क़ादिर (सामर्थ्यवान), अस-समद (आश्रयदाता), अद-दय्यान (न्यायकर्ता), अल-वदूद (प्रेममय), अल-बातिन (गुप्त) | various | Sanskritised glosses for Arabic names; readable but not the words Muslim readers use. | ख़बर रखने वाला; क़ुदरत वाला; बेनियाज़; बदला देने वाला; मोहब्बत करने वाला; छिपा हुआ | aware; powerful; needing none; the judge; the loving; the hidden | Style |
| अल-क़ादिर (सामर्थ्यवान), वह सामर्थ्य जो शान्त रहती है | luqman | "सामर्थ्य" is masculine in dictionaries ("रहता है"); feminine use exists. | वह ताक़त जो शांत रहती है | "the strength that stays calm" | Likely |

## Per page

### mansur

| Exact text | What is wrong | Proposed | Meaning | Confidence |
|---|---|---|---|---|
| FAQ answer: यह नाम अरबी में منصور लिखा जाता है; अंग्रेज़ी में Mansur। | The question asks for Arabic and Urdu; the answer gives Arabic only. The page's own row says Urdu is منصور. | यह नाम अरबी और उर्दू दोनों में منصور लिखा जाता है; अंग्रेज़ी में Mansur। | "Written منصور in both Arabic and Urdu; in English Mansur." | Certain. In fixes (JSON-LD and body). |
| विजयी, जिसे ईश्वर की मदद प्राप्त हो (title tag description, og, quick facts, body x3, FAQ, JSON-LD) | "ईश्वर" on a page whose own heading says "अल्लाह के नाम". | फ़तहमंद, जिसे अल्लाह की मदद हासिल हो | "victorious, one who has Allah's help" | Likely. Meaning line, so your call. |
| Whole page | No origin, no bearers, no "did you know", no story. English has all four, including the corrected caliph list. | Translate from the English page. | n/a | Gap, not an error |

### bayezid

| Exact text | What is wrong | Proposed | Meaning | Confidence |
|---|---|---|---|---|
| मतलब: बढ़ोतरी का पिता; उस्मानी सुल्तानों का नाम, then "इसका प्रचलित अर्थ है: बढ़ोतरी का पिता; उस्मानी सुल्तानों का नाम।" | The second half is a note about who bore the name, not a meaning, so the sentence "its meaning is: ... name of Ottoman sultans" is false as written. Same on luqman and khansa. | Split the field: meaning "बढ़ोतरी का पिता"; note "उस्मानी सुल्तानों का नाम". | "father of increase" / "name of Ottoman sultans" | Likely. Generator change. |
| Reading: "यहाँ प्रधान तत्व पृथ्वी है" | English page says the letters "draw from many elements at once, a full palette, not a single note". The two languages give opposite readings of the same name. | Needs Usman. | n/a | Certain that they disagree |
| Pronunciation: ba-ye-ZEED | Matches the corrected English page. | none | n/a | OK |

### khansa

| Exact text | What is wrong | Proposed | Meaning | Confidence |
|---|---|---|---|---|
| हम्ज़ा (ء): हम्ज़ा, एक हल्की ठहर। | "ठहर" is not a noun. | हम्ज़ा, एक हल्का ठहराव। | "Hamza, a light pause." | Certain. In fixes. |
| Letter card "ء हम्ज़ा" with no element; "अग्नि (2), जल (2), पृथ्वी (1), वायु (1)" | Seven letters, six counted. English gives hamza as Fire, so English has Fire 3. | Needs the generator. | n/a | Certain |
| यहाँ प्रधान तत्व अग्नि है | Declared on a 2 to 2 tie as shown on this page. English says "many elements at once". | Needs Usman. | n/a | Certain that they disagree |
| मतलब: अरब की सबसे महान कवयित्री अल-ख़नसा; "ख़नसा मुसलमानों में प्रचलित नाम है। इसका प्रचलित अर्थ है: अरब की सबसे महान कवयित्री अल-ख़नसा।" | This describes a person. It is not what the word means. The English page has the same fault ("Al-Khansa, greatest Arab poetess"). | Needs Usman: a real meaning from a source, on both pages. | n/a | Certain it is not a meaning |
| उर्दू: الخنساء | The Urdu row repeats the Arabic form with the article. Name spelling, so not touched. | Needs Usman (INC-01). | n/a | Flag only |
| अलिफ़ (ا) से शुरू होने वाले और नाम: अल-बिरूनी, अल-ग़ज़ाली ... | Khansa is filed under Alif because the Arabic spelling carries "al-". A reader expects names starting with Kha. | Needs the generator. | n/a | Likely |
| FAQ answer leaves out Urdu | Same as mansur, but the fix would repeat the doubtful Urdu form above. | Hold until the Urdu form is settled. | n/a | Held |

### fadwa

| Exact text | What is wrong | Proposed | Meaning | Confidence |
|---|---|---|---|---|
| फ़ा (ف): फ़ा खुलने और उद्घाटन का अक्षर है। (78 pages) | "उद्घाटन" means an inauguration ceremony. | फ़ा खुलने और शुरुआत का अक्षर है। | "Fa is the letter of opening and beginning." | Likely |
| ى अलिफ़ मक़्सूरा | English page calls the same letter "Ya" with Al-Qayyum. Same number and element, different letter name. | Needs Usman (letter model). | n/a | Certain that they disagree |
| समर्पित त्याग, बलिदान | "बलिदान" and "त्याग" are Hindu-register words for this idea. | फ़िदा होना, क़ुर्बानी | "to be devoted, sacrifice" | Style. Meaning line, your call. |

### luqman

| Exact text | What is wrong | Proposed | Meaning | Confidence |
|---|---|---|---|---|
| लाम (ل) से शुरू होने वाले और नाम: गुलनाज़, गुलज़ार, लाइबा ... | Gulnaz (گلناز) and Gulzar (گلزار) start with Gaf, not Lam. The list skips letters that are not in the Arabic alphabet. | Remove the two, or fix the generator. | n/a | Certain. Not in fixes because it removes links. |
| मतलब: हकीम लुक़मान; क़ुरआन की सूरह 31 का नाम | A description, not a meaning (same as English). Reads acceptably. | none now | n/a | Style |

### kainat

| Exact text | What is wrong | Proposed | Meaning | Confidence |
|---|---|---|---|---|
| समस्त सृष्टि, ब्रह्मांड | Both words are Sanskrit; "सृष्टि" carries Hindu overtones. The name itself is the Urdu word. | पूरी कायनात, तमाम मख़लूक़ | "the whole universe, all of creation" | Style. Meaning line, your call. |
| ئ हम्ज़ा (या पर) | English page calls it "Ya". Same number and element. | Needs Usman (letter model). | n/a | Certain that they disagree |
| Reading: "प्रधान तत्व पृथ्वी है" | English says the name "joins fire to earth". | Needs Usman. | n/a | Certain that they disagree |
| Pronunciation KAI-nat | Same as English. No bearer on the Hindi page, so the Kainat Imtiaz change does not apply. | none | n/a | OK |

## Systematic defects: the template sentence and how many pages carry it

| Template sentence | Pages | Fix |
|---|---|---|
| "...वह X है, इसलिए X ... का तत्व है।" | 500 | In fixes file, one entry per page |
| "हम्ज़ा, एक हल्की ठहर।" | 20 | In fixes file |
| "आलिफ़ मम्दूदा" | 5 (adamu, aynur, aysun, ayzal, emina) | In fixes file |
| "अल-मुअमिन (सुरक्षा देने वाला)" | 92 | After your nod |
| "एक कोमल और गर्म ध्यान" | 105 | After wording approval |
| "वह रोशनी जो कमरे को स्थिर कर देती है" | 88 | After wording approval |
| "फ़ा खुलने और उद्घाटन का अक्षर है" | 78 | After wording approval |
| Dominant element named on a tie | 167 | Decision on the reading rule |
| Same-letter list with a wrong entry | 53 pages, 91 entries (44 Gaf names under Lam; 36 under Sheen that start with Ba or Alif; 9 Kaf names under Qaf; 2 other) | Generator |
| Element counts do not add up to the letter count | 33 | Generator |
| FAQ asks "Arabic and Urdu", answer gives Arabic only | 126 | Generator |
| "ईश्वर" for Allah in the meaning line | 12 (ayaan, ayaana, ghofran, hiba, hibah, ismail, mansur, mujahid, mujeeb, mujtaba, noor, nurul) | After your nod |

## Needs Usman

1. **Reading rule.** Hindi names one dominant element on every page, ties included. English often says "many elements at once". On bayezid, khansa, fadwa, luqman and kainat the two languages read the same name differently. Which is the house rule?
2. **Letter names.** English calls ى and ئ "Ya"; Hindi calls them "अलिफ़ मक़्सूरा" and "हम्ज़ा (या पर)". One model across languages?
3. **Khansa.** The "meaning" is a description of the poet on both the English and Hindi pages; and the Urdu spelling row shows الخنساء. I have not touched either.
4. **"अल-मोमिन" against "अल-मुअमिन"**, and **"अल्लाह" against "ईश्वर"**: say yes and both become script fixes (92 and 12 pages).
5. **Register pass.** Do you want the Hindustani wording (आग, मिट्टी, पानी, हवा; क़ुर्बानी; कायनात) across the template? It is a one-time change to about 70 template sentences, then every page follows.
6. **Prophet's name.** The Muhammad page writes "पैग़म्बर साहब" without a salutation. The Turkish pages carry one (s.a.v.). One rule for Hindi?

Outside this review: the English Bayezid page says the name "resolves on Alif"; it ends on Dal.
