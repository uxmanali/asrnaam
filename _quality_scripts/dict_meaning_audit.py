#!/usr/bin/env python3
"""Audit and rewrite the dictionary meaning (MEAN-DICT block + asr-namecard JSON
meaning.dict field) on canonical name pages.

Two failure modes are addressed:

  A. Template/AI-slop entries (~156 pages) — bodies that read like
     "{Name} — {short meaning} — {region}. This name carries deep roots in
      Islamic naming tradition and is honoured across Muslim communities
      worldwide. The spiritual reading through Ilm ul Huroof reveals the
      complete quality of this name."
     These are replaced wholesale with a hand-written concise meaning.

  B. SEO-leak entries — substantive meanings with internal product copy
     appended ("Maximum coverage", "Captures the X audience distinct from Y",
     "second max coverage", etc.). These are scrubbed in-place.

The script is idempotent. Run it from the repo root.
"""
import json, os, re, html, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMES_DIR = os.path.join(ROOT, 'names')

# ─────────────────────────────────────────────────────────────────────────────
# A. Hand-written replacements for the 156 template/AI-slop entries
#    Format: slug -> dictionary meaning text (no HTML tags)
#    1-2 short sentences. Be specific. Never invent.
# ─────────────────────────────────────────────────────────────────────────────
FRESH_MEANINGS = {
  # ── A ──
  'arfaa':       "Most exalted, highest in rank — from the Arabic root r-f-ʿ ('to raise, to elevate'). Feminine intensive of Rafiʿ.",
  'bahja':       "Splendour, joy, radiance — from the Arabic root b-h-j ('to be bright, joyful'). The visible beauty that gives pleasure to the eye.",
  'bana':        "A young, tender tree — also: stature, build. From Arabic بانة, evoking a graceful, willowy figure.",
  'basant':      "Spring — from the Persian/Urdu بسنت, the season of yellow mustard blossom celebrated across South Asia.",
  'djemai':      "Of the gathering, the communal one — Kabyle/Algerian form derived from Arabic jamʿ ('gathering, community').",
  'donia':       "The world, worldly life — Maghrebi/French spelling of Arabic dunyā (دنيا), the present world as opposed to the hereafter.",
  'ensar':       "The Helpers — Turkish form of Arabic Ansar (أنصار), the Medinan companions who supported the Prophet ﷺ after the Hijra.",
  'fadila':      "Virtuous, of high merit — feminine of Fadil, from the Arabic root f-d-l ('to surpass, to be excellent').",
  'fayez':       "The victor, the successful one — Egyptian/Levantine spelling of Faiz, from Arabic root f-w-z ('to triumph, to attain').",
  'fayha':       "Fragrant, wide and aromatic — an epithet of Damascus (الفيحاء), describing a place that breathes out perfume. From root f-y-h.",
  'fella':       "Jasmine flower — the Kabyle/Algerian word for jasmine, used widely as a girls' name in North Africa.",
  'feriel':      "From the Persian/Arabic Faryāl, meaning ornament, jewelled headdress — common in Tunisia and the Maghreb.",
  'gaith':       "Rain, especially the first rain that revives the land — from Arabic غيث, used in the Quran for the rain that gives life.",
  'galil':       "Majestic, great — Egyptian spelling of Jalil. Al-Jalil ('the Majestic') is one of the divine names of Allah.",
  'gamal':       "Beauty, grace — Egyptian spelling of Jamal, from the Arabic root j-m-l ('to be beautiful').",
  'ghali':       "Precious, dear, costly — from Arabic غالي, that which is valued and not easily attainable.",
  'ghanem':      "Victorious, the one who gains spoils — from the Arabic root gh-n-m ('to gain, to win'). Levantine/Gulf form of Ghanim.",
  'ghazwan':     "The warrior, the one who undertakes expeditions — from the Arabic root gh-z-w ('to set out on campaign'). Borne by the companion Ghazwan ibn al-Harith.",
  'ghena':       "Wealth, sufficiency — from the Arabic root gh-n-y. Al-Ghani ('the Self-Sufficient') is one of the divine names.",
  'hadeel':      "The cooing of doves — from Arabic هديل, the soft sound a pigeon makes for its mate, evoking gentleness and longing.",
  'hadil':       "Cooing — Egyptian/Levantine variant of Hadeel. The sound of the dove.",
  'hamad':       "Praise, the act of praising — Gulf form of Hamd, from the Arabic root ḥ-m-d, the same root as Muhammad and Ahmad.",
  'hamdah':      "Praise — feminine of Hamd, from the Arabic root ḥ-m-d ('to praise').",
  'hazem':       "Resolute, decisive, firm in judgement — from the Arabic root ḥ-z-m ('to bind firmly, to be resolved').",
  'hossam':      "Sharp sword — Egyptian/Levantine spelling of Hussam, the cutting blade. From Arabic husām.",
  'intisar':     "Victory, triumph — from the Arabic root n-ṣ-r ('to help, to give victory'). The verbal noun of intaṣara.",
  'ishraq':      "Sunrise, radiant illumination — from the Arabic root sh-r-q ('to rise, to shine'). The light of the sun breaking the horizon.",
  'jarir':       "The one who draws, drags, or leads — from Arabic root j-r-r. Jarir ibn ʿAtiyya was a famous Umayyad-era Arab poet.",
  'jawhar':      "Essence, jewel, gem — from Arabic جوهر (via Persian gawhar), denoting the inner substance of a thing as well as a precious stone.",
  'jihan':       "World — Persian جهان (jahān), 'the world'. Used in Egyptian/Turkish Muslim communities.",
  'jood':        "Generosity, open-handed giving — from the Arabic root j-w-d. Al-Jawād ('the Most Generous') is one of the divine names.",
  'joumana':     "Silver pearl — Levantine spelling of Jumana, from Arabic جمانة, a pearl of pure silver colour.",
  'juri':        "Damask rose — from Arabic جوري, a particularly fragrant variety of rose cultivated in the Levant and Persia.",
  'lamar':       "Pure water, the radiance of pearls — from Arabic لُمار, used in the Gulf for shining brightness and clear water.",
  'lameen':      "The trustworthy — North African/Maghrebi form of Al-Amin, an epithet of the Prophet ﷺ. From the Arabic root ʾ-m-n ('to be trustworthy').",
  'layal':       "Nights — plural of Layla (ليلة, night). Used for the rich, dark beauty of the night.",
  'lhaj':        "The pilgrim — Maghrebi form of Al-Hajj, used as an honorific for one who has performed the Hajj.",
  'lotfi':       "Of gentleness, kindness — Tunisian/Maghrebi nisba form of Lutfi, from the Arabic root l-ṭ-f ('to be gentle'). Al-Latif is a divine name.",
  'lounes':      "Companion, the friend — Kabyle/Berber name carrying the sense of intimate companionship.",
  'luban':       "Frankincense — the aromatic resin (Arabic لُبان) burnt as incense, prized in Arabia since antiquity.",
  'maram':       "Wish, aspiration, that which is sought — from the Arabic root r-w-m ('to desire, to aim for').",
  'melia':       "Honey-sweetness — from Greek méli ('honey'). Used in some Turkish and Western convert communities.",
  'melisa':      "Honey bee — Turkish form of Greek mélissa ('bee'), the honey-gatherer.",
  'meral':       "Doe, gazelle — Turkish word for the female deer (from Persian māral), evoking gentle grace.",
  'mirna':       "Tender affection, delight — a Levantine girls' name, often associated with the Aramaic/Greek sense of 'sweet, gentle'.",
  'mouhamad':    "The praised one — West African (Senegalese/Mauritanian) spelling of Muhammad ﷺ. From the Arabic root ḥ-m-d ('to praise').",
  'mounsef':     "The just, the impartial — Tunisian/Maghrebi form of Munsif, from the Arabic root n-ṣ-f ('to do justice, to be fair').",
  'naffees':     "Precious, valuable — South Asian doubled-f spelling of Nafis, feminine, from the Arabic root n-f-s ('to be precious').",
  'naim':        "Bliss, ease, comfort — from the Arabic root n-ʿ-m. Jannat al-Naʿim is one of the names of Paradise in the Quran.",
  'najat':       "Salvation, deliverance — from the Arabic root n-j-w ('to be saved'). Surah Ghafir refers to 'the day of salvation' (yawm al-tanād / al-najāt).",
  'nasri':       "Of victory — nisba of Nasr ('help, victory'). From the Arabic root n-ṣ-r.",
  'nawaf':       "High, lofty, elevated — Gulf name from the Arabic root n-w-f ('to rise, to surmount').",
  'nayera':      "Luminous, radiant — Egyptian spelling of Nayira, feminine of Nayyir, from the Arabic root n-w-r ('to shine, to give light').",
  'nidal':       "Struggle, striving in a just cause — from the Arabic root n-ḍ-l ('to compete, to contend'). Used for both boys and girls.",
  'nihal':       "Saplings, young plants — Arabic plural of nahla, evoking fresh growth. Also used as a Turkish girls' name.",
  'nihan':       "Hidden, secret — Persian/Turkish نهان (nihān), 'concealed'. Used in Sufi poetry for the hidden beloved.",
  'nisa':        "Women — Arabic نساء, the title of Surah 4 (An-Nisaʾ). The collective noun for women.",
  'nizar':       "Of small but precious quantity — from the Arabic root n-z-r. Nizar ibn Maʿadd is a major ancestor of the northern Arab tribes.",
  'noha':        "Intellect, reason — Arabic نهى, the plural of nuhya, used in the Quran (20:54, 20:128) for 'people of understanding'.",
  'noorhan':     "Light of the king, full of light — Egyptian compound of Arabic nūr ('light') with Persian khān ('lord, sovereign').",
  'ouissam':     "Medal, badge of honour — Maghrebi/French spelling of Wissam, from the Arabic root w-s-m ('to mark, to brand').",
  'oulimata':    "Learned, the one who knows — Fula/Wolof form derived from Arabic ʿālima (feminine of ʿālim, 'one of knowledge').",
  'oumkheir':    "Mother of goodness — Maghrebi compound of Arabic umm ('mother') and khayr ('good').",
  'oumnia':      "Wish, aspiration — Moroccan spelling of Umnia, from the Arabic root m-n-y ('to desire, to wish for').",
  'ousmane':     "West African (Wolof/Fula) form of Uthman — name of the third Caliph ʿUthman ibn ʿAffan (RA), Dhu al-Nurayn.",
  'ousseini':    "West African (Hausa/Songhai) diminutive form of Husain, grandson of the Prophet ﷺ.",
  'outhmane':    "Mauritanian/Maghrebi spelling of Uthman — name of the third Caliph ʿUthman ibn ʿAffan (RA).",
  'parham':      "Persian پرهام, a name of pre-Islamic Zoroastrian origin associated with virtue and goodness; in modern usage often linked to Bahman/Bahrām.",
  'payam':       "Message, dispatch — Persian پیام, used for a message bearing meaning or news.",
  'pelin':       "Wormwood, artemisia — Turkish word for the bitter aromatic herb. Common Turkish girls' name.",
  'perihan':     "Queen of the fairies — Persian/Turkish compound of parī ('fairy') and khan ('lord, queen').",
  'pinar':       "Spring, fountain, source of water — Turkish پینار (pınar).",
  'polat':       "Steel — Turkish form of Persian pūlād, denoting strength and tempered hardness.",
  'poyraz':      "The north-east wind — Turkish word (from Greek boreas), the cold wind that blows over Anatolia.",
  'putra':       "Son, prince — Malay/Sanskrit-derived word for a son, also used as a title for royal sons.",
  'qaboos':      "The handsome one, the strong — from Arabic قابوس, an old name carried most recently by Sultan Qaboos bin Said of Oman.",
  'qaid':        "Leader, commander — from the Arabic root q-w-d ('to lead'). The verbal participle.",
  'qanita':      "Devoutly obedient, constant in worship — feminine of Qanit, from the Arabic root q-n-t. Surah At-Tahrim (66:12) praises Maryam as qānita.",
  'qays':        "Firmness, measure — from the Arabic root q-y-s ('to measure'). Qays ibn al-Mulawwah was the legendary lover of Layla.",
  'quds':        "Holiness, sanctity — from the Arabic root q-d-s. Al-Quds is the Arabic name for Jerusalem. Al-Quddus is one of the divine names.",
  'qusay':       "From afar, the distant — from the Arabic root q-ṣ-w. Qusay ibn Kilab was a major ancestor of the Prophet ﷺ and the Quraysh.",
  'qutb':        "Pole, axis, pivot — Arabic قطب, used in Sufi terminology for the spiritual pole around whom the age turns.",
  'rafa':        "Wellbeing, prosperity, ease — Gulf form related to the Arabic root r-f-h ('to live in comfort').",
  'rafah':       "Welfare, ease of life, comfortable living — from the Arabic root r-f-h.",
  'ramla':       "Sand, a sandy patch of ground — from Arabic رملة. Umm Habiba's given name was Ramla bint Abi Sufyan, a wife of the Prophet ﷺ.",
  'roa':         "Visions, dreams — Arabic رؤى, plural of ruʾyā, the dreams that the Quran takes seriously as a form of revelation (as with Prophet Yusuf).",
  'roudha':      "Garden, meadow — Gulf/Maghrebi spelling of Rawda. The Prophet ﷺ described the area between his pulpit and his house as 'a garden of Paradise' (rawda min riyāḍ al-janna).",
  'sabiha':      "Of the morning, beautiful of face — from the Arabic root ṣ-b-ḥ ('morning'). Feminine of Sabih.",
  'sahba':       "Of a deep tawny, golden hue — from Arabic صهباء, originally describing wine of a reddish-amber colour, then a light reddish-brown complexion.",
  'saja':        "The stillness of night, deep calm — from the Arabic root s-j-w. The Quran swears by 'the night when it is still' (sajā) in Surah Ad-Duha (93:2).",
  'sakhr':       "Rock, hard stone — from Arabic صخر. Sakhr ibn Harb was the given name of Abu Sufyan.",
  'salsabila':   "A spring in Paradise — Indonesian spelling of Salsabil, named in Surah Al-Insan (76:18) as a fountain in the gardens of bliss.",
  'saqer':       "Falcon — Gulf spelling of Saqr, from Arabic صقر, the noble hunting bird of Arabia.",
  'sarfaraz':    "Exalted in rank, head held high — Persian/Urdu compound سرفراز ('head-raised'). Common Pakistani name.",
  'soukayna':    "Tranquillity, divine calm — Moroccan spelling of Sakinah. Surah At-Tawbah and Al-Fath speak of God sending down sakīna into the hearts of believers.",
  'soumaiya':    "Diminutive of samra ('the dark-complexioned one') — North African spelling of Sumayya. Sumayya bint Khayyat was the first martyr of Islam.",
  'soumaya':     "West African spelling of Sumayya — diminutive of samra, 'dark-complexioned'. Carried by Sumayya bint Khayyat, the first martyr in Islam.",
  'soumia':      "Algerian spelling of Sumayya — diminutive of samra, 'dark-complexioned'. Carried by Sumayya bint Khayyat, the first martyr in Islam.",
  'suad':        "Happiness, good fortune — from the Arabic root s-ʿ-d. Feminine of Saʿd. The plural form (suʿūd) means 'risings, ascents'.",
  'subhi':       "Of the morning — nisba of ṣubḥ ('dawn'). From the Arabic root ṣ-b-ḥ.",
  'sumbal':      "Hyacinth — Persian/Urdu سنبل (sunbul), the fragrant spike flower. Also: spikenard, an ancient perfume.",
  'tahani':      "Congratulations, blessings — plural of tahniya, from the Arabic root h-n-ʾ ('to find pleasant').",
  'taif':        "A passing apparition, a night vision — from the Arabic root ṭ-y-f. Also the name of the city of Ṭāʾif near Mecca.",
  'tamara':      "Date palm, date — from Arabic تمر (tamr) via Aramaic/Hebrew tamar. Also a Slavic name from the same Semitic root.",
  'tamim':       "Complete, perfect, sound — from the Arabic root t-m-m ('to be complete'). Tamim al-Dari was a companion of the Prophet ﷺ.",
  'tammam':      "The most complete, perfectly whole — intensive form from the Arabic root t-m-m.",
  'taqiyy':      "God-fearing, pious — from the Arabic root w-q-y ('to guard against'). The taqiy is the one shielded by taqwā.",
  'tarkan':      "Lord, noble — old Turkic title used for distinguished warriors, from the same root as Turkic 'tarkhan'.",
  'tawba':       "Repentance, turning back to God — from the Arabic root t-w-b. Surah At-Tawbah is the ninth chapter of the Quran.",
  'tayba':       "The good, the pure — also an old name of Medina (Ṭayba/Ṭāba). From the Arabic root ṭ-y-b ('to be good, pleasant').",
  'thabet':      "Firm, steadfast, established — Egyptian/Levantine spelling of Thabit. Thabit ibn Qays was a companion of the Prophet ﷺ.",
  'thana':       "Praise — Arabic ثناء. Used in the opening supplication of prayer (du'a al-thana) that praises Allah.",
  'thuraya':     "The Pleiades — Arabic name of the seven-star cluster mentioned in classical Arabic astronomy and poetry.",
  'tiba':        "Goodness, sweetness — from the Arabic root ṭ-y-b. Variant of Tayba, also an old name of Medina.",
  'toujan':      "Crowns — Jordanian/Levantine girls' name, possibly from the Arabic root t-w-j ('to crown') or Persian tāj.",
  'ubaid':       "Little servant — Arabic diminutive of ʿabd ('servant'). Used in the form ʿUbayd Allah ('little servant of Allah').",
  'ulya':        "Highest, uppermost — feminine of Aʿlā, from the Arabic root ʿ-l-w. 'Al-kalimat al-ʿulyā' (the highest word) refers to God's word in the Quran.",
  'umama':       "Three hundred, a multitude — also a diminutive of umm ('mother'). Umama bint Abi al-ʿAs was a beloved granddaughter of the Prophet ﷺ.",
  'umniyya':     "Wish, hope, aspiration — classical Arabic form of Umnia, from the root m-n-y.",
  'uns':         "Intimacy, companionable closeness — from the Arabic root ʾ-n-s. In Sufi terminology, uns is the felt nearness of the Divine.",
  'uqaylah':     "The intelligent, sensible woman — from the Arabic root ʿ-q-l. Sayyida Zaynab bint Ali was titled ʿAqīlat Banī Hāshim ('the sage of the House of Hashim').",
  'uqba':        "Outcome, what follows after — from the Arabic root ʿ-q-b. ʿUqba ibn Nafiʿ was the companion who carried Islam across North Africa to the Atlantic.",
  'urwa':        "A firm handhold, the strong loop — from Arabic عروة. The Quran calls true faith 'the most trustworthy handhold' (al-ʿurwat al-wuthqā, 2:256). ʿUrwa ibn al-Zubayr was a leading early jurist of Medina.",
  'valentina':   "Strong, healthy — from the Latin Valentinus, from valere ('to be strong'). Used as a Muslim convert name in Western communities.",
  'valerie':     "Strong, vigorous — French form of Latin Valeria, from valere ('to be strong').",
  'vanessa':     "A literary name coined by Jonathan Swift in 1726 (from Esther Vanhomrigh). Used in Western convert communities.",
  'veda':        "Farewell, leave-taking — Turkish veda (from Arabic wadāʿ). Used as a Turkish girls' name.",
  'vera':        "Faith, truth — Russian/Slavic vera ('faith'); also Latin verus ('true'). A bridge name in European convert communities.",
  'victor':      "Conqueror, victor — from the Latin victor ('the one who has prevailed'). Used in some convert communities.",
  'vildan':      "The young attendants of Paradise — Turkish form of Arabic wildān, mentioned in Surah Al-Insan (76:19) as 'youths of perpetual freshness'.",
  'vince':       "Conqueror — short form of Vincent, from the Latin vincere ('to conquer').",
  'wafik':       "Successful, well-suited, harmonious — from the Arabic root w-f-q ('to be in accord'). Variant of Wafiq.",
  'wahb':        "Gift, the act of giving — from the Arabic root w-h-b. Al-Wahhab ('the Bestower') is one of the divine names. Wahb ibn Munabbih was an early scholar of the second Islamic generation.",
  'wajda':       "Ecstasy, the rapture of finding — from the Arabic root w-j-d, the same root from which Sufis derive wajd (mystical ecstasy).",
  'wamda':       "Flash, glint, a brief flicker of light — from the Arabic root w-m-ḍ.",
  'wasif':       "Describer, the one of eloquent description — from the Arabic root w-ṣ-f ('to describe').",
  'watfa':       "Of long, full eyelashes — Arabic وطفاء, a classical descriptor for eyes shaded by thick lashes, considered beautiful.",
  'wejdan':      "Feeling, sentiment, conscience — from the Arabic root w-j-d ('to find, to feel deeply'). Plural of wijdan.",
  'wessal':      "Union, reunion — Gulf spelling of Wisal, from the Arabic root w-ṣ-l ('to join, to reach'). In Sufi poetry, wiṣāl is the union with the Beloved.",
  'wissale':     "Union, reunion — Moroccan spelling of Wisal, from the Arabic root w-ṣ-l. Sufi term for spiritual union with the Beloved.",
  'yaqeen':      "Certainty, sure knowledge — from the Arabic root y-q-n. The Quran speaks of three degrees: ʿilm al-yaqīn, ʿayn al-yaqīn, and ḥaqq al-yaqīn.",
  'yasser':      "Ease, the bringer of ease — English-spelling form of Yasir, from the Arabic root y-s-r. 'Allah desires ease for you and does not desire hardship' (2:185).",
  'yazan':       "An old South Arabian name borne by Sayf ibn Dhi Yazan, a 6th-century Himyarite king of Yemen who expelled the Abyssinians.",
  'yehia':       "He shall live — Egyptian/Levantine form of Yahya, the prophet John the Baptist (AS). From the Arabic root ḥ-y-y ('to live').",
  'yekta':       "Unique, the only one — Persian یکتا, used as a Turkish/Iranian girls' name.",
  'yildiz':      "Star — Turkish word for a star (yıldız), also the name of an Ottoman imperial palace in Istanbul.",
  'yosef':       "Hebrew/Western form of Yusuf — the Prophet Yusuf (AS), whose story occupies the longest continuous narrative in the Quran (Surah Yusuf, 12).",
  'yuna':        "Dove, also the name of the prophet Yunus (AS, Jonah) — used as a girls' name in Turkey and the Maghreb.",
  'yusaira':     "Ease, gentle facility — feminine diminutive of Yusr, from the Arabic root y-s-r ('to be easy').",
  'yusr':        "Ease — from the Arabic root y-s-r. The Quran promises in Surah Ash-Sharh (94:5–6): 'With every hardship there is ease.'",
  'zafirah':     "Victorious, the one who attains — feminine of Zafir, from the Arabic root ẓ-f-r ('to triumph, to obtain').",
  'zakiya':      "Pure, untainted — feminine of Zakiy, from the Arabic root z-k-w ('to be pure, to grow in goodness'). The same root as zakāt.",
  'zaria':       "From Persian zarrīn ('golden') — also the name of an ancient Hausa city in northern Nigeria, now used as a girls' name in West Africa.",
  'zinat':       "Adornment, ornament — Persian/Urdu form of Arabic zīna. Surah Al-Aʿraf (7:31) speaks of taking one's zīna for the place of prayer.",
  'zinedine':    "Adornment of religion — Maghrebi/French spelling of Zayn al-Din, popularised by the footballer Zinedine Zidane.",
  'zohour':      "Flowers, blossoms — Arabic plural of zahra ('flower'). Maghrebi spelling of Zuhour.",
}

# ─────────────────────────────────────────────────────────────────────────────
# B. Hand-written replacements for SEO-leak entries (substantive meaning was
#    correct but was buried under product/SEO copy). Same format.
# ─────────────────────────────────────────────────────────────────────────────
FRESH_MEANINGS_SEO = {
  'aamira':       "She who builds and makes flourish — feminine of Amir, from the Arabic root ʿ-m-r ('to populate, to make prosper'). The same root from which ʿumra ('lesser pilgrimage') is taken.",
  'abdelkarim':   "Servant of Al-Karim (the Most Generous) — Maghrebi/French spelling of ʿAbd al-Karim. Al-Karim is one of the divine names of Allah.",
  'abderrahmane': "Servant of Ar-Rahman (the Most Merciful) — Maghrebi/French spelling of ʿAbd al-Rahman. The Prophet ﷺ said the names most beloved to Allah are ʿAbdullah and ʿAbd al-Rahman.",
  'abdirahman':   "Servant of Ar-Rahman (the Most Merciful) — Somali/East African spelling of ʿAbd al-Rahman.",
  'aboubakr':     "Maghrebi/French spelling of Abu Bakr. The companion Abu Bakr al-Siddiq (RA) was the Prophet ﷺ's closest friend and the first Caliph of Islam.",
  'aboubakry':    "Senegalese/Guinean Wolof-influenced spelling of Abu Bakr. Refers to Abu Bakr al-Siddiq (RA), first Caliph of Islam.",
  'abubakr':      "South Asian/Gulf spelling of Abu Bakr al-Siddiq (RA), the Prophet ﷺ's closest companion and the first Caliph of Islam.",
  'aisyah':       "Living, full of life — Malay/Indonesian spelling of Aisha. From the Arabic root ʿ-y-sh ('to live'). Refers to ʿA'isha bint Abi Bakr, wife of the Prophet ﷺ.",
  'al-husain':    "The little beautiful one — formal form of Husain with the definite article. From the Arabic root ḥ-s-n ('to be beautiful'). Refers to Al-Husain ibn Ali (RA), the Prophet ﷺ's grandson, martyred at Karbala.",
  'alaia':        "Sublime, elevated — variant of ʿAliyya, from the Arabic root ʿ-l-w ('to be high'). Al-ʿAli is one of the divine names.",
  'ayesha':       "Living, prosperous — South Asian/UK diaspora spelling of Aisha, from the Arabic root ʿ-y-sh. Refers to ʿA'isha bint Abi Bakr, wife of the Prophet ﷺ.",
  'ayshah':       "Living — Levantine/scholarly transliteration of Aisha (with -ah ending), from the Arabic root ʿ-y-sh.",
  'baran':        "Rain — Persian/Turkish باران, the blessed rain that the Quran repeatedly describes as a sign of divine mercy reviving dead earth.",
  'basma':        "A smile — from the Arabic root b-s-m ('to smile'). The Prophet ﷺ said: 'Your smile in the face of your brother is charity.'",
  'batoul':       "The chaste one, the virgin devoted entirely to worship — Maghrebi spelling of Batool, an epithet of Maryam (mother of Prophet ʿIsa) and of Fatima al-Zahra.",
  'eshal':        "A flower of Paradise — alternate spelling of Eshaal. A modern South Asian Urdu girls' name.",
  'fatima':       "The one who weans, who detaches — from the Arabic root f-ṭ-m. Fatima al-Zahra (RA), beloved daughter of the Prophet ﷺ, is the namesake. The Prophet said: 'Fatima is a part of me — whoever angers her angers me.'",
  'hadijat':      "Hausa/West African spelling of Khadijah (with H- initial). Refers to Khadijah bint Khuwaylid (RA), the Prophet ﷺ's first wife and the first person to accept Islam.",
  'hassen':       "The beautiful, the good — Tunisian spelling of Hassan, from the Arabic root ḥ-s-n. Refers to Al-Hasan ibn Ali (RA), the Prophet ﷺ's grandson.",
  'hudhayfah':    "Scholarly Arabic spelling of Huzaifa. Hudhayfa ibn al-Yaman (RA) was a senior companion to whom the Prophet ﷺ entrusted the names of the hypocrites — known as Ṣāḥib al-Sirr (Keeper of the Secret).",
  'husain':       "The little beautiful one — scholarly Arabic transliteration with a single 'n' of Hussain. From the Arabic root ḥ-s-n. Refers to Al-Husain ibn Ali (RA), grandson of the Prophet ﷺ.",
  'ibraheem':     "Father of nations — Western diaspora spelling (double-e) of Ibrahim. Refers to the Prophet Ibrahim (AS), Khalil Allah ('the Friend of God').",
  'jasmine':      "The jasmine flower — Western/English spelling of Yasmin, from the Persian yāsamīn (the fragrant white blossom).",
  'kawtar':       "Abundance — Maghrebi/French spelling of Kawthar. Surah 108 (Al-Kawthar) opens: 'We have given you al-Kawthar' — also the name of a river in Paradise.",
  'khadija':      "Born early, premature — also: the trusted, the prosperous trader. Maghrebi/French spelling of Khadijah. Refers to Khadijah bint Khuwaylid (RA), the Prophet ﷺ's first wife and the first person to accept Islam.",
  'loay':         "Shield, the protector — alternate Gulf spelling of Lu'ay. Lu'ay ibn Ghalib was a major ancestor of the Quraysh, and of the Prophet ﷺ.",
  'loujain':      "Pure silver — Maghrebi/French spelling of Lujain. Surah Al-Insan (76:15) describes vessels of silver passed among the dwellers of Paradise.",
  'maleeka':      "Queen — South Asian doubled-e spelling of Malika, feminine of Malik. From the Arabic root m-l-k ('to own, to rule'). Al-Malik is a divine name.",
  'mohammed':     "The most praised — common English/diaspora spelling of Muhammad ﷺ. From the Arabic root ḥ-m-d ('to praise'). The most-used name on earth.",
  'mohsin':       "The doer of beautiful good — from the Arabic root ḥ-s-n. The muḥsin lives by iḥsān, defined by the Prophet ﷺ as 'to worship Allah as though you see Him'.",
  'mouhamed':     "The most praised — West African (Mauritanian/Senegalese) spelling of Muhammad ﷺ. From the Arabic root ḥ-m-d.",
  'moussa':       "Maghrebi/West African spelling of Musa — the Prophet Musa (AS, Moses), the most-mentioned prophet in the Quran (136 times).",
  'muhammet':     "The most praised — Turkish spelling of Muhammad ﷺ. From the Arabic root ḥ-m-d.",
  'naeema':       "Blessed, in comfort — feminine of Naʿim, from the Arabic root n-ʿ-m. Jannat al-Naʿim is one of the names of Paradise in the Quran.",
  'nesrin':       "Wild rose — Turkish/Persian form of Nasrin, the dog-rose that grows untamed across Persia and Anatolia.",
  'noorin':       "Two lights, of doubled light — intensive feminine of Noor, from the Arabic root n-w-r.",
  'nour-houda':   "Light of guidance — Maghrebi compound of nūr ('light') and hudā ('guidance'). The Quran is described as both light and guidance.",
  'nur-ul-ain':   "Light of the eye — the source of joy and consolation. The Quran's phrase qurrat aʿyun ('coolness of the eyes', 25:74) is a prayer of the righteous.",
  'nura':         "Light — short feminine form of Noor, from the Arabic root n-w-r. Al-Nur is one of the divine names; Surah 24 is named An-Nur.",
  'okba':         "Maghrebi spelling of ʿUqba — the companion ʿUqba ibn Nafiʿ, who led the Muslim armies across North Africa to the Atlantic. From the Arabic root ʿ-q-b ('what follows after').",
  'ranya':        "She who gazes intently, with pleasure — from the Arabic root r-n-w ('to gaze fixedly').",
  'rayhan':       "Fragrant herb, sweet basil — Arabic ريحان. Mentioned in Surah Ar-Rahman (55:12) and Al-Waqiʿa (56:89) as a blessing of creation and a delight reserved for the near ones of Allah.",
  'reda':         "Contentment, divine pleasure — Maghrebi/French spelling of Rida. From the Arabic root r-ḍ-y. The highest station the Quran promises is one in which 'Allah is pleased with them, and they are pleased with Him' (98:8).",
  'roumayssae':   "Moroccan -ae spelling of Rumaysa. Rumaysa bint Milhan (RA), known as Umm Sulaym, made her acceptance of Islam her dowry — one of the most honoured women among the Ansar.",
  'serhan':       "Wolf — Turkish form of Arabic sirhān, the wolf. Used widely as a Turkish boys' name.",
  'shahad':       "Honey — Gulf five-letter spelling of Shahd. The Quran describes honey as a healing 'in which there is cure for people' (16:69).",
  'sherine':      "Sweet — Arabicised form of the Persian Shirin. The legendary Shirin was the beloved of Khusraw in Nizami's poem Khusraw and Shirin.",
  'slimane':      "Algerian/Maghrebi spelling of Sulayman — the Prophet Sulayman (AS, Solomon), to whom the Quran gives dominion over jinn, humans, birds, and the wind (Surah An-Naml).",
  'smail':        "Algerian contracted spelling of Ismail — the Prophet Ismail (AS, Ishmael), son of Ibrahim (AS), ancestor of the Arabs.",
  'sude':         "Pure, untouched — likely from Persian sūda ('that which has been refined'). One of the most popular Turkish girls' names of recent decades.",
  'sulayman':     "Man of peace — Arabic سُلَيْمَان, from a root related to salām. Refers to the Prophet Sulayman (AS, Solomon), to whom the Quran gives dominion over jinn, humans, birds, and the wind.",
  'taufiq':       "Divine enabling, God-given success — Indonesian/Malay spelling of Tawfiq, from the Arabic root w-f-q. The grace by which Allah aligns a servant with right action.",
  'timur':        "Iron — Turkic/Mongolic temür. Borne by Timur ibn Taraghay Barlas (Tamerlane, d. 1405), founder of the Timurid empire.",
  'uthman':       "Young bustard, a noble bird — from Arabic عثمان. Refers to ʿUthman ibn ʿAffan (RA), the third Caliph of Islam, called Dhu al-Nurayn ('Owner of Two Lights') because he married two of the Prophet ﷺ's daughters.",
  'wania':        "God's gracious gift — compact spelling of Waniya. A modern Urdu girls' name carrying the sense of a gift bestowed by divine grace.",
  'wedad':        "Love, affection — Egyptian spelling of Widad. Al-Wadud ('the Most Loving') is one of the divine names of Allah.",
  'wisal':        "Union, reunion — from the Arabic root w-ṣ-l ('to join, to reach'). In Sufi poetry, wiṣāl is the moment of union with the Beloved.",
  'yacoub':       "Maghrebi/West African spelling of Yaqub — the Prophet Yaʿqub (AS, Jacob), father of the twelve patriarchs and of Prophet Yusuf (AS).",
  'zaara':        "South Asian Urdu spelling of Zahra, 'the radiant, the blossoming one'. From the Arabic root z-h-r ('to flower, to shine').",
  'zainub':       "Bangladeshi/South Asian spelling of Zaynab — a fragrant flowering tree in classical Arabic. Refers to Zaynab bint Muhammad (RA), the Prophet ﷺ's eldest daughter, and other women of the early community.",
  'zakariyya':    "The Prophet Zakariyya (AS, Zechariah) — father of the Prophet Yahya (John the Baptist). His prayer for a son in old age is recorded in Surah Maryam (19:2–6).",
  'zaydan':       "Growth, abundant increase — variant of Zidan. From the Arabic root z-y-d ('to grow, to increase').",
  'zein':         "Adornment, beauty — Levantine spelling of Zayn. Zayn al-ʿAbidin (RA) was the great-grandson of the Prophet ﷺ, the only adult Hashemite male to survive Karbala.",
  'zouheir':      "Bright, flourishing — Algerian/French spelling of Zuhayr. From the Arabic root z-h-r ('to bloom, to shine'). Zuhayr ibn Abi Sulma was one of the great pre-Islamic poets.",
}

# Merge
ALL = {}
ALL.update(FRESH_MEANINGS)
ALL.update(FRESH_MEANINGS_SEO)

def replace_block(html_text, name_english, new_text):
    """Replace MEAN-DICT:START..END block with a clean canonical version."""
    new_block = (
        '<!-- MEAN-DICT:START -->\n'
        '<p class="section-label">Dictionary Meaning</p>\n'
        f' <h2>What <em>{html.escape(name_english)}</em> means</h2>\n'
        f' <div class="prose"><p>{new_text}</p></div>\n'
        '<!-- MEAN-DICT:END -->'
    )
    return re.sub(
        r'<!-- MEAN-DICT:START -->.*?<!-- MEAN-DICT:END -->',
        lambda _m: new_block,
        html_text,
        count=1,
        flags=re.S,
    )

def update_namecard_json(html_text, new_dict):
    """Update meaning.dict in the asr-namecard <script type="application/json">."""
    m = re.search(r'(<script type="application/json" id="asr-namecard">)(\{.*?\})(</script>)',
                  html_text, re.S)
    if not m: return html_text, False
    try:
        data = json.loads(m.group(2))
    except json.JSONDecodeError:
        return html_text, False
    if 'meaning' not in data or not isinstance(data['meaning'], dict):
        return html_text, False
    if data['meaning'].get('dict') == new_dict:
        return html_text, False
    data['meaning']['dict'] = new_dict
    new_json = json.dumps(data, ensure_ascii=False, separators=(', ', ': '))
    return html_text[:m.start()] + m.group(1) + new_json + m.group(3) + html_text[m.end():], True

def main():
    idx_path = os.path.join(NAMES_DIR, 'names-index.json')
    idx = json.load(open(idx_path))
    idx_by_slug = {e['s']: e for e in idx}

    updated_html = 0
    updated_json = 0
    updated_idx  = 0
    missing = []

    for slug, new_meaning in ALL.items():
        page = os.path.join(NAMES_DIR, slug, 'index.html')
        if not os.path.isfile(page):
            missing.append(slug); continue
        text = open(page).read()
        if '<!-- MEAN-DICT:START -->' not in text:
            missing.append(slug); continue

        english = idx_by_slug.get(slug, {}).get('n', slug.title())
        text2 = replace_block(text, english, new_meaning)
        if text2 != text:
            updated_html += 1
            text = text2

        text2, changed = update_namecard_json(text, new_meaning)
        if changed:
            updated_json += 1
            text = text2

        with open(page, 'w') as f:
            f.write(text)

        # Update names-index.json entry's 'm' (short blurb) — keep it tight.
        if slug in idx_by_slug:
            short = f"{english} — {new_meaning}"
            # Truncate to a sane length but at a sentence/em-dash boundary if possible
            if len(short) > 220:
                cut = short.rfind('. ', 0, 220)
                if cut < 80: cut = 220
                short = short[:cut].rstrip(' .,;:—-') + '.'
            if idx_by_slug[slug].get('m') != short:
                idx_by_slug[slug]['m'] = short
                updated_idx += 1

    json.dump(idx, open(idx_path, 'w'), ensure_ascii=False, separators=(',', ':'))

    print(f"updated HTML blocks:       {updated_html}")
    print(f"updated namecard JSON:     {updated_json}")
    print(f"updated names-index.json:  {updated_idx}")
    if missing:
        print(f"missing slugs:             {len(missing)} -> {missing[:10]}{'…' if len(missing)>10 else ''}")
    print(f"total mapping entries:     {len(ALL)}")

if __name__ == '__main__':
    main()
