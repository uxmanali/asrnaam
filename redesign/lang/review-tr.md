# Turkish name pages: line-by-line review

Reviewed 22 Nov 2026 against production (`origin/main`). Read in full: osman, hatice. Read for pattern: ayse, mehmet, zeynep, deniz, yildiz, mustafa, emine, alp-arslan. Also checked by script across all 168 Turkish pages: the meaning line as it appears mid-sentence, the element counts, and the quick-fact labels.

## Answer first

**The Turkish pages are well written. They read like a Turkish editor wrote them, and they are better than the Hindi pages by a clear margin.** Apostrophes after proper names are right throughout (Osman'ın, Hatice'nin, Kur'an'da, Türkiye'de, Osmanlı Devleti'nin), dotted and dotless i are right, Islamic terms follow Turkish usage (Hz., r.a., s.a.v., Zinnûreyn, mushaf, ebced, huruf ilmi), and nothing is left in English in the visible text.

On the two batch-one pages I found **no error I would correct without asking you**. I found four things that need your decision and a handful of style points. On one fact the Turkish page is right where the English page is wrong (Osman's root is not in the Quran).

Across the wider set there is **one certain, systematic defect**: the template lowercases the first letter of the meaning when it puts it mid-sentence, which produces "allah artırır", "hz. Peygamber'in kızının adı", "arap alfabesinin ilk harfi". 16 of 168 pages. All 16 are in `redesign/lang/fixes-tr.json`, each verified against production.

| Page | Grade | Why not higher |
|---|---|---|
| osman | A- | One historical statement is imprecise (who compiled the Mushaf); reading differs from the English page |
| hatice | B+ | "Dominant element" declared on a 2 to 2 tie; a hadith quoted with no source; two registers for the Prophet in one page |

Facts checked against the English page: gender, origin, Arabic spelling, abjad total and digit (Osman 661 and 4; Hatice 622 and 1), letter elements and divine names all match. One fact differs: whether Osman's root is in the Quran. The Turkish page says no and is right; the English page says yes (see the osman table). The Turkish pages carry no pronunciation line and no Hatice Sultan, so the two English corrections (ha-tee-JEH; Selim I's daughter, Suleiman's sister) have nothing to correct here.

## Defects by type

| Type | osman | hatice | All 168 pages | In fixes |
|---|---|---|---|---|
| Proper noun or "Hz." lowercased mid-sentence | no | no | 16 | Yes, 16 |
| "Dominant element" declared on a tie | no | yes | 52 | No. Needs Usman |
| Reading differs from the English page | yes | yes | not counted | No. Needs Usman |
| Historical precision | yes | no | not counted | No. Needs Usman |
| Hadith quoted with no source | no | yes | at least mehmet too | No. Needs Usman |
| "anlamı güzeldir:" before a plain or unflattering meaning | yes | yes | 168 | No. Wording choice |
| FAQ ebced sentence is two clauses with one verb | yes | yes | 168 | No. Likely, not certain |
| Register mix for the Prophet | no | yes | not counted | No. Style |
| English label in code (`aria-label="Breadcrumb"`) | yes | yes | 168 | Agent B's label file |

## osman

| Exact text | What is wrong | Proposed | Meaning of the proposal | Confidence |
|---|---|---|---|---|
| Hz. Osman, Kur'an'ı tek mushafta birleştirip çoğaltarak İslam beldelerine göndermiştir | Says Osman gathered the Quran into one mushaf. TDV İslâm Ansiklopedisi ("Osman"): the Quran had been collected into a mushaf under Ebû Bekir; Osman had five or seven copies made and sent them to the cities. The English page has the same looseness ("compiler of the Quran"). | Hz. Osman, Hz. Ebû Bekir döneminde bir araya getirilen Mushaf'ı çoğalttırarak İslam beldelerine göndermiştir | "Osman had the Mushaf that was compiled in Abu Bakr's time copied and sent to the Muslim cities." | Likely. Differs from the English page, so it is for you, with the English line. Source: https://islamansiklopedisi.org.tr/osman |
| Osman Müslüman aileler arasında kullanılan bir isimdir ve anlamı güzeldir: toy kuşu yavrusu; Hz. Osman'ın adı. | "Its meaning is beautiful: bustard chick" reads oddly. The claim of beauty is the template's, the meaning is plain. | ...kullanılan bir isimdir; anlamı: toy kuşu yavrusu; Hz. Osman'ın adı. | "...is a name used among Muslim families; its meaning: ..." | Likely. Template, all 168 pages. |
| Ebced hesabına göre عُثْمَان harflerinin toplamı 661, rakamları tek haneye inene kadar toplanınca 4 elde edilir. (FAQ and JSON-LD) | Two clauses share one verb that fits only the second; "rakamları" has no clear owner. The body version is correct. | Ebced hesabına göre عُثْمَان harflerinin toplamı 661'dir; bu sayının rakamları tek haneye inene kadar toplanınca 4 elde edilir. | "...the total is 661; when the digits of this number are added down to one digit, 4 is obtained." | Likely. Template, all 168 pages. |
| Ağır basan unsur ateş | English page says Osman's letters "draw from many elements at once". The two languages read the name differently. | Needs Usman. | n/a | Certain that they disagree |
| Türkiye'de ve Bosna, Arnavutluk, Kosova gibi Balkan ülkelerinde | "Bosna" for the country. | Bosna-Hersek | Bosnia and Herzegovina | Style |
| “iki nur sahibi” anlamında Zinnûreyn | Correct. TDV writes "Zü'n-nûreyn"; "Zinnûreyn" is the common Turkish form. | none | n/a | OK |
| Hayır. Osman adı Kur'an'da geçmez; adın geldiği ع-ث-م kökü de Kur'an'da yer almaz. | The Turkish is right and the English page is wrong. English Osman page: "Its Arabic root, however, appears in the Quran". The Quranic Arabic Corpus root index lists only ع ث ر and ع ث و under these two letters; ع ث م is not there. | Keep the Turkish. Correct the English page. | n/a | Certain that the two pages contradict each other. Source: https://corpus.quran.com/qurandictionary.jsp?q=Evr |
| Urduca yazılışı عُثْمَان (row and FAQ) | Same as the Arabic, with vowel marks. Name spelling, so not touched. | none | n/a | Flag only |
| Whole page | No pronunciation, no list of bearers. English has Osman Hamdi Bey and the pronunciation strip. | Translate from the English page. | n/a | Gap, not an error |

Everything else on the page read correctly: title, meta description, H1, badge, all quick-fact labels, the origin paragraph (a-s-m root; "yılan yavrusu ya da toy kuşunun yavrusu"), the Quran section, the letter names (Ayn, Se, Mim, Elif, Nun), the divine names (el-Alîm, es-Sâbit, el-Mü'min), all five FAQ items and the footer.

## hatice

| Exact text | What is wrong | Proposed | Meaning of the proposal | Confidence |
|---|---|---|---|---|
| Bu ismin harfleri unsurlara şöyle dağılır: su (2), toprak (2), hava (1). Ağır basan unsur su | Water and earth tie at 2. The page still names water as dominant. English says the name "weaves earth and water". | Needs Usman (rule for ties). | n/a | Certain |
| Hz. Peygamber onun için “İnsanlar beni inkâr ederken o bana iman etti” buyurmuştur. | A saying of the Prophet in quotation marks with no source. The English page has the same line unsourced. | Add the source after the quote, or move it out of quotation marks. | n/a | Needs Usman. I have not added a citation I did not read today. |
| Hz. Peygamber'in (s.a.v.) ilk eşi ... / Peygamber Efendimiz'in (s.a.v.) ilk hanımı ... | Two registers on one page: neutral "Hz. Peygamber, eşi" and devotional "Peygamber Efendimiz, hanımı". | Use "Hz. Peygamber'in (s.a.v.) ilk eşi" in both places. | "the Prophet's first wife" | Style |
| Hatice, Hz. Peygamber'in (s.a.v.) ilk eşi Hz. Hatice'nin (r.a.) adının Türkçedeki biçimidir. | Circular: "Hatice is the Turkish form of the name of Hz. Hatice". | Hatice, Arapça Hadîce adının Türkçedeki biçimidir; Hz. Peygamber'in (s.a.v.) ilk eşi Hz. Hatice'nin (r.a.) adıdır. | "Hatice is the Turkish form of the Arabic Hadîce; it is the name of the Prophet's first wife." | Style |
| Kaynak: Behind the Name, “Khadija” maddesi: “vaktinden önce doğan çocuk” anlamında Arapça bir addır. | The clause after the second colon has no subject. Also a thin source for a page about Hz. Hatice. | Kaynak: Behind the Name, “Khadija” maddesi; adı “vaktinden önce doğan çocuk” anlamında Arapça bir ad olarak verir. | "Source: ...; it gives the name as an Arabic name meaning 'child born early'." | Likely |
| ...ve anlamı güzeldir: vaktinden önce doğan; Hz. Hatice'nin adı. | "Its meaning is beautiful: born before time." Same template point as Osman. | ...kullanılan bir isimdir; anlamı: vaktinden önce doğan; Hz. Hatice'nin adı. | as above | Likely |
| Te (yuvarlak) harfiyle biter | Label used as a word in a sentence. | kapalı te (tâ-i merbûta) harfiyle biter | "ends with the closed te" | Style |
| FAQ ebced sentence | Same as Osman. | Same as Osman. | | Likely |

Everything else read correctly: title, meta description, H1, the Quran section, letter names (Hı, Dal, Ye, Cim), divine names (el-Habîr, ed-Deyyân, el-Kayyûm), FAQ and footer.

## Systematic defects: the template sentence and how many pages carry it

| Template sentence | Pages | Fix |
|---|---|---|
| "...ve anlamı güzeldir: " + meaning with its first letter lowercased | 168 use the sentence; 16 lowercase a proper noun or "Hz." (yusuf, ismail, melek, elif, araz, asya, meryem, yunus, zeynep, zuleyha, irem, kenan, merve, belkis, veysel, zeynab) | In fixes file. Long-term: the generator should not lowercase. |
| "Ağır basan unsur X" on a tie | 52 of 168 (hatice, ayse, mehmet, muhammed, hasan, emine, yildiz and others) | Decision on the reading rule |
| FAQ: "...harflerinin toplamı N, rakamları tek haneye inene kadar toplanınca M elde edilir." | 168 | One template edit after your nod |
| `aria-label="Breadcrumb"` | 168 | Label file |

## Seen on the sample pages (not batch one)

| Page | Exact text | Note | Confidence |
|---|---|---|---|
| zeynep | anlamı güzeldir: hz. Peygamber'in kızının adı | "hz." must be "Hz." | Certain. In fixes. |
| yusuf, ismail, melek | allah artırır; allah işitir; allah'ın elçisi | "Allah" lowercased | Certain. In fixes. |
| mehmet | “Kostantiniyye mutlaka fethedilecektir; onu fetheden komutan ne güzel komutan, onu fetheden asker ne güzel askerdir” hadisini | Quoted as a hadith with no source; its chain is disputed among scholars. | Needs Usman |
| alp-arslan | Bizans imparatoru Romen Diyojen'i | Title before a name takes a capital: "Bizans İmparatoru Romen Diyojen'i". | Likely |
| zeynep | Ebû'l-Âs b. er-Rebî' | TDV usage is "Ebü'l-Âs". Not checked against TDV today. | Style |
| yildiz, deniz | Arapça yazılış: یلدیز against دنيز | One uses the Persian and Urdu ye (ی), the other the Arabic ye (ي) under the same "Arabic spelling" label. Name spelling, not touched. | Needs Usman (INC-01) |
| ayse, mustafa, emine, deniz, yildiz | Body paragraphs | Read cleanly. Sources named in the text (Nişanyan Sözlük, İngilizce Vikipedi, Behind the Name). | OK |

## Needs Usman

1. **Reading rule on ties and on mixed names.** Same question as Hindi: Turkish names one dominant element (52 pages on a tie); English often says "many elements". Osman and Hatice read differently in the two languages today.
2. **Osman's root in the Quran.** English says the root appears in the Quran; Turkish says it does not. The corpus root index supports the Turkish. The English page needs the correction.
3. **Osman and the Mushaf.** The Turkish line and the English line ("compiler of the Quran") both credit Osman with compiling. TDV credits the compiling to Ebû Bekir's time and the copying and sending to Osman. Fix both, or leave both.
4. **Hadith lines without a source** (hatice, mehmet). Add a source read from a collection, or drop the quotation marks.
5. **"anlamı güzeldir:"** Keep the claim that every meaning is beautiful, or change the template to a neutral "anlamı:".
6. **Arabic-script spelling of Turkish-origin names** (Yıldız, Deniz): which ye is the house form.

Outside this review: the public address asrnaam@gmail.com is printed on every Turkish page ("Düzeltme bildirin veya asrnaam@gmail.com adresine yazın"). It is not the address you asked to keep hidden, but you should know it is there.
