/* AsrNaam — shared letter-data module.
   Source of truth for the Ilm-ul-Huroof letter table (L), the lemma/word
   dictionary (D), and the Arabic-script-to-key map (ARABIC_MAP).

   Loaded by both index.html (inline reader) and asr-reader.js (the /reader/
   tool). Exposes the three constants on window.ASR_LETTERS and also makes
   them available as plain globals (window.L, window.D, window.ARABIC_MAP)
   so the legacy inline code that referenced them by bare name keeps working.
*/
(function(){
  const L = {

// ═══════════════════════════════════════════════════════════════════
// REAL ILMU UL HUROOF — ELEMENTAL FRAMEWORK
// Sources: Ibn Arabi (Futuhat al-Makkiyya), Ahmad al-Buni (Shams al-Maarif)
//
// FOUR ELEMENTS (7 letters each):
// FIRE  : ا ه ط م ف ش ذ  — hot, ascending, expansive
// EARTH : ب و ي ن ص ت ض  — cold, containing, stable  
// AIR   : ج ز ك س ق ث ظ  — light, moving, penetrating
// WATER : د ح ل ع ر خ غ  — flowing, deep, receptive
//
// DARK LETTERS (absent from Al-Fatiha): ج ز ف ث خ ظ ش
// These carry double nature — intensity beneath their primary quality
// ═══════════════════════════════════════════════════════════════════

// ── FIRE LETTERS ─────────────────────────────────────────────────

  'a': {
    arabic:'ا', name:'Alif', abjad:1,
    element:'Fire', nature:'Luminous', temperament:'Hot-Dry', planet:'Saturn',
    divine_name:'Al-Ahad (The One)',
    core:'The Pole of all letters — every Arabic letter is derived from Alif. Saturn\'s fire. Hot-Dry: energy rises and does not pool.',
    character:'The Alif person has one direction — upward. They do not bend easily. Their constitution is hot and dry: they rise, decide, act. Saturn brings discipline and solitude — they often lead alone. The singular quality of Alif (اجد 1, the One) means they resist categorisation and compromise in equal measure. They burn clearly but their dryness means they need deliberate grounding or they exhaust those around them.',
    gift:'Singular clarity of direction. Natural authority. They see what should be done before others do.',
    shadow:'The dryness of their fire — they can exhaust relationships and environments. The heat of conviction can become the heat of inflexibility.',
    in_name:'As the first letter, Alif sets the entire name on fire — hot, ascending, singular. As an interior letter, Alif is the inner flame that drives. As the final letter, Alif means the life resolves into singular essential truth.',
    muq_note:'Alif opens most Muqattaat combinations (الم، الر). As the Pole of all letters, its presence at the threshold of divine surahs represents origin itself being placed at the door of guidance.',
    keywords:['singular','ascending','hot-dry','Saturn','solitary authority'],
    combos:{'l':'Alif+Lam = Al — the definite article. Origin meeting belonging. In the name of Allah this combination becomes absolute. In a personal name it produces someone who is definitively themselves — what they are, they are completely.','m':'Alif+Meem opens Surah Baqarah. Fire+Fire: double combustion. Origin meeting tidal love. Enormous creative and emotional intensity.'}
  },

  'hh': {
    arabic:'ه', name:'Ha', abjad:5,
    element:'Fire', nature:'Luminous', temperament:'Hot-Wet', planet:'Mars-Aries',
    divine_name:'Al-Hadi (The Guide)',
    core:'The breath letter — the sound of exhaling is Ha. Hot-Wet fire: fire with moisture. Not the dryness of Alif but fire that generates steam.',
    character:'Hot-Wet fire produces enormous creative energy. The Ha person generates heat and moisture simultaneously: passion (fire) with emotional depth (wet). This combination makes them charismatic, expressive, and intensely sensitive. They feel the world with the same intensity they project into it. Surah Ta-Ha contains Ha in the divine address to the Prophet — breath of divine intimacy.',
    gift:'Charismatic presence. Creative fire that does not burn dry. Genuine emotional resonance — they make others feel the aliveness of things.',
    shadow:'Hot-Wet intensity exhausts itself and others. The highs are very high and the lows are very low. They can overwhelm.',
    in_name:'Ha anywhere in a name adds breath and presence — the animating quality. At the start: presence as the primary mode. Inside: the emotional intensity hidden beneath the surface. At the end: the name resolves into breath and presence.',
    muq_note:'Ha appears in طه (Ta-Ha) where Allah addresses the Prophet directly — the most intimate Quranic address. A name carrying Ha carries a trace of that intimacy.',
    keywords:['breath','presence','charismatic','Hot-Wet fire','intense'],
    combos:{'m':'Ha+Meem opens all seven Hawameem surahs (40-46). The largest consecutive Muqattaat group. Water fire meeting tidal fire — sustained revelation. In a name: this person loves with the quality of sustained illumination.','tw':'Ta+Ha = طه. Solar fire meeting breath. The complete cycle of living breath. Divine intimacy.'}
  },

  'tw': {
    arabic:'ط', name:'Ta', abjad:9,
    element:'Fire', nature:'Luminous', temperament:'Hot-Dry', planet:'Sun',
    divine_name:'Al-Lateef (The Subtle)',
    core:'The Sun letter. Solar fire — consistent, central, giving. Abjad 9: the number of completion (9 is the last single digit). Hot-Dry solar fire.',
    character:'The Ta person radiates like the sun — consistently, centrally, without effort. Everyone orbits them without this having been chosen. Their Hot-Dry constitution means they process and complete quickly: the Sun rises and sets, a new cycle begins. Ta carries the wheel (Tawaf) — circular return, completion. They are the people who finish cycles and begin new ones, who come back, who complete what they began.',
    gift:'Solar consistency — people can rely on their warmth. Fast completion. The ability to begin new cycles without being trapped in old ones.',
    shadow:'Solar fire can cause drought. Those closest to a Ta person can be burned by proximity. The dryness means they move on before others have finished grieving what was.',
    in_name:'Ta as the first letter places solar energy at the front — this person leads with warmth and completion. Inside a name, Ta is the solar cycle hidden in the interior. At the end, the name resolves in solar completion.',
    muq_note:'Ta opens طه (Ta-Ha) and طس (An-Naml, Al-Qasas) and طسم. The solar principle placed at the threshold of divine guidance — the sun that illuminates the path.',
    keywords:['solar','completing','Hot-Dry','cyclical','central presence'],
    combos:{'s':'Ta+Seen opens طس (An-Naml). Solar fire + swift air = the sun carried by wind. In a name: the solar nature that spreads itself through movement and communication.','hh':'Ta+Ha = طه. Solar fire meeting breath. Divine intimacy.'}
  },

  'm': {
    arabic:'م', name:'Meem', abjad:40,
    element:'Fire', nature:'Luminous', temperament:'Hot-Wet', planet:'Moon',
    divine_name:'Al-Mumin (The Faithful)',
    core:'Moon-governed fire. Hot-Wet: fire in tide. Abjad 40: the number of transformation (40 days in the wilderness, 40 years of wandering). The mother letter.',
    character:'Every human language uses Meem for mother — mama, mère, madre, maa, umm. This is not coincidence in the Ibn Arabi framework. The letter carries the principle, and the principle expresses itself wherever that reality is present. The Moon governs tides: the Meem person loves in tides — consistently, powerfully, cyclically. Hot-Wet fire is fire with moisture — warmth that does not dry out, heat that nourishes rather than burns.',
    gift:'Tidal love — consistent, rhythmic, sustaining. The number 40 means they transform through sustained presence, not sudden action. Their warmth is real and reliable.',
    shadow:'Tidal love also means tidal grief. The Meem person grieves as deeply as they love — these are the same water at different temperatures. Moon-governed fire can become overwhelming in its depth.',
    in_name:'Meem anywhere in a name adds emotional depth and tidal love. At the start: the love principle governs the whole. Inside: the ocean of feeling behind whatever is shown externally. At the end: the name resolves into nourishing depth.',
    muq_note:'Meem appears in الم (Baqarah, Al-Imran) and all seven حم Hawameem surahs. The moon-fire of sustained revelation — the most love-saturated letter grouping.',
    keywords:['tidal love','Moon-fire','sustaining','Hot-Wet','transforming through presence'],
    combos:{'a':'Meem+Alif: Fire+Fire. Tidal love meeting singular origin. Opens Surah Baqarah (الم) — double fire at the threshold of the longest surah. Enormous emotional and creative intensity.','h':'Ha+Meem: water-fire meeting Moon-fire. Opens seven consecutive Hawameem surahs — the longest consecutive Muqattaat group. In a name: sustained illuminated love.','s':'Meem+Seen: Moon-fire meeting swift air. The tide that carries the wind — love that always moves forward.'}
  },

  'f': {
    arabic:'ف', name:'Fa', abjad:80,
    element:'Fire', nature:'DARK', temperament:'Hot-Dry', planet:'Venus',
    divine_name:'Al-Fattah (The Opener)',
    core:'DARK FIRE. Venus-governed. Absent from Al-Fatiha. Hot-Dry fire with Venusian beauty. The fire that opens beautifully.',
    character:'The beautiful opener. Venus gives the Fa person aesthetic intelligence and relational charm — they open things with grace. But Fa is DARK fire: the opening also burns through what it opens. Al-Fattah means to open by conquering — it is not a gentle unlocking but a forceful opening that changes the state of what was opened. The Fa person follows through on what they begin (Fa in Arabic grammar marks consequence — "therefore, then"). What they touch is changed. Sometimes beautifully. Sometimes irreversibly.',
    gift:'The ability to open what was closed — conversations, possibilities, people — with charm and grace. Follow-through. Consequential action.',
    shadow:'Dark fire: the opening leaves scorched earth. The Fa person can be unaware of how dramatically they change what they touch. Venus\'s beauty can disguise the intensity of the burning.',
    in_name:'Fa as the first letter: this person opens the world before them wherever they go. Inside: the dark fire burning behind whatever charm is shown. At the end: the name resolves through a great consequential opening.',
    muq_note:'Fa does not appear in the Muqattaat but Al-Fattah is among the divine names — the Opener of all creation.',
    keywords:['DARK fire','Venus','consequential','beautiful opener','Hot-Dry'],
    combos:{}
  },

  'sh': {
    arabic:'ش', name:'Sheen', abjad:300,
    element:'Fire', nature:'DARK', temperament:'Hot-Dry', planet:'Sun (intensified)',
    divine_name:'Al-Shakur (The Appreciative)',
    core:'DARK FIRE at maximum intensity. Absent from Al-Fatiha. Abjad 300 — the highest fire value. The spreading fire letter. The shape of Sheen shows three flames spreading outward simultaneously.',
    character:'Shams (Sun, شمس) begins with Sheen — and this is not accidental. Sheen IS solar combustion. Not the gentle circular sun of Ta (which completes cycles) but fire that spreads outward in all directions simultaneously. Three points of Sheen: three tongues of flame. The DARK quality doubles the intensity — this is fire with hidden depth. The person whose name opens with Sheen carries the energy of the sun itself: brilliant, warming from a distance, dangerous in proximity. The rage that comes with Sheen names is elemental physics — DARK Fire (Sheen) wants to spread in all directions. When something blocks this spreading, the fire turns inward. Compressed spreading fire is explosion. The Sheen person is not angry by choice; they are a sun that was given a container too small.',
    gift:'Enormous radiant energy — physical, intellectual, social. They illuminate everything around them. Their generosity of spirit is solar — they give light without counting.',
    shadow:'The fire that burns what it warms. Compressed spreading fire becomes rage. The DARK quality means the depth of their intensity is not always visible until it erupts. They need enormous space — to think, to act, to be.',
    in_name:'Sheen as the first letter: this person leads with solar fire. Everything about their outward self radiates and spreads. Inside a name: the dark fire hidden behind whatever exterior quality leads. At the end: the name resolves in spreading — they leave their mark on everything they have touched.',
    muq_note:'Sheen appears in عسق (Ash-Shura, Surah 42) — the surah about the mechanism of revelation spreading outward. In Shams al-Maarif (literally The Sun of Knowledge), al-Buni explores Sheen as the letter of solar illumination — that which radiates divine names into the world.',
    keywords:['DARK fire','spreading','solar rage','Hot-Dry','Abjad 300','combustion'],
    combos:{}
  },

  'dh': {
    arabic:'ذ', name:'Dhal', abjad:700,
    element:'Fire', nature:'DARK', temperament:'Hot-Dry', planet:'Saturn',
    divine_name:'Al-Dhul-Jalal (The Lord of Majesty)',
    core:'DARK FIRE + Saturn. Absent from Al-Fatiha. Abjad 700 — ancient accumulated fire. Saturn\'s slow burning. Dhikr (remembrance) begins with Dhal.',
    character:'The oldest fire. Saturn does not move quickly — it takes 29 years to complete its cycle. Dhal burns with that slowness and that weight. The Dhal person does not forget — they carry the fire of what has happened to them across enormous spans of time. Their anger, when it comes, is old anger: it has been burning slowly for years. Their love is old love too — it does not begin yesterday. The DARK quality and high Abjad value make this the most complex fire: it burns across time, not across space. These are the people who outlast everything.',
    gift:'Persistence that outlasts opposition. Memory as fire — what matters to them burns forever. Dhikr: their remembrance of the divine is total and consuming.',
    shadow:'Slow fire is also slow to forgive. The Dhal person carries grudges not from weakness but from the structural quality of their fire — it does not go out easily.',
    in_name:'Dhal anywhere in a name adds ancient weight and persistence. The fire here is old and sustained.',
    muq_note:'Dhal does not appear in the Muqattaat but Al-Dhul-Jalal (Lord of Majesty) is among the most complete divine names.',
    keywords:['DARK fire','Saturn','ancient','Hot-Dry','persistent memory','Abjad 700'],
    combos:{}
  },

// ── EARTH LETTERS ────────────────────────────────────────────────

  'b': {
    arabic:'ب', name:'Ba', abjad:2,
    element:'Earth', nature:'Luminous', temperament:'Cold-Wet', planet:'Mercury',
    divine_name:'Al-Batin (The Interior/Hidden)',
    core:'The container letter. Cold-Wet Earth: the womb. Abjad 2: the first of duality. Opens Bismillah — all divine action passes first through Ba\'s interior.',
    character:'The Quran opens with Ba — and this means something. Before the word for the name of Allah is the letter of the interior: the intention, the container, the hidden space where something is held before it enters the world. The Ba person is constitutionally a container — for people, for ideas, for what is fragile. Mercury gives them quickness of thought and communication: they think fast and hold deep. Cold-Wet earth is the womb — receptive, nourishing, dark in the generative sense.',
    gift:'People feel held, contained, safer in the Ba person\'s presence without being able to explain why. The Bismillah quality: they invoke presence before they begin anything.',
    shadow:'The container is always full. The Ba person gives shelter without accounting for their own need for shelter. Cold-Wet earth without warmth can become damp and heavy — they can become overburdened by what they carry for others.',
    in_name:'Ba as the first letter: this person leads with containment and interior intelligence. Inside: hidden warmth and structure beneath what is shown. At the end: the name resolves in building something lasting.',
    muq_note:'Ba opens Bismillah and therefore opens the Quran itself — all creation passed through the interior of Ba into manifestation.',
    keywords:['container','Cold-Wet earth','interior intelligence','Mercury','womb quality'],
    combos:{'l':'Ba+Lam: Earth container + Water belonging. What is contained moves toward what it belongs to. Foundation with direction.'}
  },

  'w': {
    arabic:'و', name:'Waw', abjad:6,
    element:'Earth', nature:'Luminous', temperament:'Cold-Wet', planet:'Jupiter',
    divine_name:'Al-Wadud (The Loving)',
    core:'The conjunction — the word "and". Abjad 6: Ibn Arabi specifically identifies 6 as the first perfect number. Jupiter Earth: abundant stable structure. The connector of things.',
    character:'The Waw person is the "and" between things — constitutionally a connector. Jupiter gives this connection abundance: things grow wherever they connect. Cold-Wet earth is the most generative soil — it holds moisture and supports growth without burning. Abjad 6 (the perfect number) means their connections have a quality of wholeness — they do not connect arbitrarily but bring things into right relation. Al-Wadud: the love that connects without possessing.',
    gift:'Structural connection. Things do not fall apart around a Waw person because they are the and that holds them together. Their love is stable, generous, growing.',
    shadow:'The connector who loses themselves. The Waw person can become defined entirely by their connections — the and without its own identity.',
    in_name:'Waw inside a name (usually as a long vowel O or U sound like in Dawood or Noor) adds the connective quality to the letter before and after it — it links them.',
    muq_note:'Waw does not appear in the Muqattaat but is among the most written letters of the Quran — the conjunction that holds the divine speech together.',
    keywords:['connection','Cold-Wet earth','Jupiter','perfect number 6','abundance'],
    combos:{}
  },

  'y': {
    arabic:'ي', name:'Ya', abjad:10,
    element:'Earth', nature:'Luminous', temperament:'Cold-Dry', planet:'Mercury',
    divine_name:'Al-Qayyum (The Self-Sustaining)',
    core:'The hand letter — Ya is the shape of a hand reaching. Cold-Dry Earth: the firmest ground. Mercury: quick purposeful reaching. Abjad 10: the first of the tens — new scale of magnitude.',
    character:'The reaching from a fixed point. The Ya person extends purposefully from stable ground — not the restless movement of air, not the flowing of water, but the deliberate extension of a hand from a body that knows where it stands. Ya is also the intimate vocative in Arabic — O! — the letter with which you call what you love from a distance. Mercury gives this reaching quickness. Cold-Dry earth gives it stability of purpose. Opens Ya-Seen (the Heart of the Quran) — this reaching is the opening gesture of the most beloved surah.',
    gift:'Purposeful extension. They reach toward what matters with consistency and Mercury swiftness. Their calling — the Ya vocative — is genuine and specific.',
    shadow:'Cold-Dry earth can become rigid. The reaching can become yearning without arrival. The stability of their purpose can look like stubbornness from outside.',
    in_name:'Ya as the first letter: this person leads with purposeful reaching. As an interior letter (common): the inner reaching quality, the longing that drives.',
    muq_note:'Ya opens يس (Ya-Seen, Surah 36 — called the Heart of the Quran). The hand reaching toward the Seen horizon. The first gesture of the most complete surah.',
    keywords:['reaching','Cold-Dry earth','Mercury','vocative calling','purposeful'],
    combos:{'s':'Ya+Seen opens يس (Ya-Seen — the Heart of the Quran). Earth reaching into Air: the grounded hand extending toward the flowing horizon. The complete gesture of purposeful seeking.'}
  },

  'n': {
    arabic:'ن', name:'Nun', abjad:50,
    element:'Earth', nature:'Luminous', temperament:'Cold-Wet', planet:'Jupiter',
    divine_name:'Al-Nur (The Light)',
    core:'The inkwell letter — Nun resembles a vessel of ink. Cold-Wet Earth with Jupiter: depth that illuminates and preserves. The whale that held Yunus in the deep. Abjad 50: release (the Jubilee number).',
    character:'The Nun person carries what must be written. They are the inkwell — the preserved depth from which permanent marks are made. Cold-Wet earth means they absorb deeply and hold permanently. Jupiter means their depth has a quality of abundance and illumination — Al-Nur, the light, is the divine name. What is preserved in a Nun person eventually illuminates. The whale of Yunus: terrible containment that became the condition for prophetic return.',
    gift:'They carry what must not be lost. Their depth preserves what others let go. When they finally release what they hold, it matters.',
    shadow:'Cold-Wet earth absorbs slowly and releases slowly. The Nun person can carry burdens of preservation long after they need to be released. The weight of what they hold is real.',
    in_name:'Nun ending a name (as in Usman, Imran, Sulaiman) means the name closes with preserved depth — the person leaves something written. Nun inside: the deep preserving quality within.',
    muq_note:'Nun opens Surah Al-Qalam (68) alone — the surah of the Pen, of divine writing and preservation. One of only five surahs to open with a single letter. Al-Qalam: the pen that writes what will be preserved forever.',
    keywords:['preserved depth','Cold-Wet earth','Jupiter','inkwell','the light in darkness'],
    combos:{}
  },

  'sw': {
    arabic:'ص', name:'Sad', abjad:90,
    element:'Earth', nature:'Luminous', temperament:'Cold-Dry', planet:'Sun',
    divine_name:'Al-Samad (The Eternal Refuge)',
    core:'The truth letter. Cold-Dry Earth + Sun: the bedrock that receives and reflects solar clarity. Abjad 90: truth at the scale of almost-completion. Opens Surah Sad (38) alone — the surah of prophets standing for truth.',
    character:'The Sad person has integrity that is geological, not moral — not a virtue they practice but the composition of their ground. Cold-Dry earth is the most inert and stable: it does not move for heat (fire), does not absorb (water), does not float (air). It IS what it is. The Sad person is what they are across all conditions, for all audiences, in all circumstances. The Sun illuminates them clearly — there is no shadow-self hiding behind a presented version. Al-Samad: the refuge that is eternal because it does not change.',
    gift:'Structural truth. You always know where they stand because they have never stood anywhere else. The Sad person is among the most trustworthy letter constitutions.',
    shadow:'The world is not as honest as they are. The Sad person can be bewildered, hurt, and disappointed by the gap between their structural truth and others\' contextual honesty.',
    in_name:'Sad in a name adds geological integrity to that position. As the first letter: truth is the leading quality. Inside: the immovable bedrock beneath whatever is shown.',
    muq_note:'Sad opens Surah Sad (38) alone — the surah of David, Solomon, Job — prophets of patience and truth. Truth maintained alone under opposition.',
    keywords:['geological integrity','Cold-Dry earth','Solar truth','immovable','Al-Samad'],
    combos:{}
  },

  't': {
    arabic:'ت', name:'Ta', abjad:400,
    element:'Earth', nature:'Luminous', temperament:'Cold-Dry', planet:'Venus',
    divine_name:'Al-Tawwab (The Relenting)',
    core:'The completion letter — Arabic feminine marker. Cold-Dry Earth with Venus: completed beauty. Abjad 400: the highest stable earth value. Al-Tawwab: return and acceptance.',
    character:'The Ta person closes circles — not from aggression or urgency but from the Cold-Dry quality of their earth: what is open must close, what is begun must complete. Venus gives this completion an aesthetic quality — what they finish has beauty. Abjad 400 means their completions carry enormous accumulated weight — they are the culmination of long processes. Al-Tawwab means the returning, the accepting — there is mercy in completion.',
    gift:'They finish. This is biological, not chosen. What others abandon, they return to. What is incomplete in their presence creates a kind of existential discomfort they cannot ignore.',
    shadow:'Not everything needs to be closed. The Ta person\'s drive for completion can close things that needed to remain open — conversations, possibilities, relationships.',
    in_name:'Ta inside a name (especially as feminine marker in Arabic names ending in ة) adds completion to the whole name — the name itself completes something.',
    muq_note:'Ta does not appear in the Muqattaat but Al-Tawwab (The Returning/Relenting) is among the most comforting divine names — divine completion that accepts return.',
    keywords:['completion','Cold-Dry earth','Venus','Abjad 400','feminine culmination'],
    combos:{}
  },

  'dw': {
    arabic:'ض', name:'Dad', abjad:800,
    element:'Earth', nature:'Luminous', temperament:'Cold-Wet', planet:'Jupiter',
    divine_name:'Al-Darr (The Tester)',
    core:'Arabic is called Lughah al-Dad — the language of Dad. No other language articulates this sound identically. Abjad 800: the highest Earth value. Cold-Wet Earth with Jupiter: abundant singular originality.',
    character:'The Dad person is genuinely one of a kind — not as aspiration but as elemental fact. The same way Arabic is the language of this letter (no other language claims ownership of a specific sound in the same way), the Dad person has a quality that cannot be replicated elsewhere. Cold-Wet Jupiter earth means they are abundantly generative in their uniqueness — they nourish others with what only they can provide. Al-Darr is the divine name of testing: their singularity is also their trial — they do not belong fully anywhere.',
    gift:'Irreplaceable. Their uniqueness genuinely cannot be replaced — there is no substitute for what they bring.',
    shadow:'The isolation of true uniqueness. They are the letter that has no equivalent anywhere else — which means they have no full mirror of themselves in others.',
    in_name:'Dad in a name adds singular constitutional originality to that position.',
    muq_note:'Dad does not appear in the Muqattaat — it is unique even in its absence from the cosmic keys.',
    keywords:['irreplaceable singularity','Cold-Wet earth','Jupiter','Abjad 800','the letter of Arabic itself'],
    combos:{}
  },

// ── AIR LETTERS ──────────────────────────────────────────────────

  'j': {
    arabic:'ج', name:'Jim', abjad:3,
    element:'Air', nature:'DARK', temperament:'Hot-Wet', planet:'Jupiter',
    divine_name:'Al-Jami (The Gatherer)',
    core:'DARK AIR. Absent from Al-Fatiha. Hot-Wet air: warm breath that gathers. Jupiter: abundant gathering. Abjad 3: the first triangle, the first completeness.',
    character:'The Jim person breathes life into spaces. Hot-Wet air is the most generative — it carries moisture that feeds growth. Jupiter makes this abundant. The DARK quality means beneath their warmth there is complex depth — they are not simply warm, they gather with a kind of intensity that can be overwhelming. Jannah (paradise) begins with Jim. Al-Jami (the Gatherer): their nature is to bring scattered things into wholeness.',
    gift:'They make things come alive. Their presence is warm, generative breath — things grow in their company.',
    shadow:'The gathering can become overwhelming — they collect too much, hold too many people, carry too many things. The dark quality means their intensity beneath the warmth is underestimated by others.',
    in_name:'Jim in a name adds warm gathering energy to that position.',
    muq_note:'Jim appears in the Abjad system as the third letter — the first complete shape (triangle). Its dark quality and Hot-Wet element make it among the most complex air letters.',
    keywords:['DARK air','gathering','Hot-Wet','Jupiter','Jannah','Abjad 3'],
    combos:{}
  },

  'z': {
    arabic:'ز', name:'Zayn', abjad:7,
    element:'Air', nature:'DARK', temperament:'Hot-Dry', planet:'Saturn',
    divine_name:'Al-Zahir (The Manifest)',
    core:'DARK AIR. Absent from Al-Fatiha. Hot-Dry air: swift precise movement. Saturn: structured manifestation. Abjad 7: the number of completion in sacred geometry.',
    character:'The Zayn person makes what is invisible visible — Al-Zahir, The Manifest. Their beauty is real but Saturn makes it structured, earned, not accidental. Hot-Dry air is fast and precise: the Zayn person perceives beauty with accuracy and expresses it deliberately. The DARK quality means their aesthetic sense has hidden depth — they are not simply appreciating surface beauty but manifesting the deep structure of what is true and beautiful. Abjad 7: the sacred completion that their manifestation serves.',
    gift:'They reveal the beauty in what others overlook. They manifest what was hidden in a form that others can now see.',
    shadow:'Their DARK aesthetic precision can become exacting. Nothing is beautiful enough, nothing is quite right. Saturn\'s demands are high.',
    in_name:'Zayn adds precise aesthetic intelligence to its position in the name.',
    muq_note:'Zayn does not appear in Muqattaat but Al-Zahir (The Manifest) is among the most important divine names — the principle by which the hidden becomes visible.',
    keywords:['DARK air','Saturn','manifest beauty','Hot-Dry','Abjad 7','precise'],
    combos:{}
  },

  'k': {
    arabic:'ك', name:'Kaf', abjad:20,
    element:'Air', nature:'Luminous', temperament:'Cold-Dry', planet:'Sun',
    divine_name:'Al-Karim (The Generous)',
    core:'Luminous Air. Cold-Dry: the clearest air — no moisture to blur, no heat to distort. Sun: illumination without burning. Kaf is the Arabic particle meaning "like" — the letter of comparison and analogy.',
    character:'The Kaf person sees clearly and gives that clarity generously — Al-Karim. Cold-Dry air is the most precise — nothing obscures perception. The Sun illuminates what is already there without generating its own heat (in this air form). The particle "like" means they understand everything through comparison — they make the unfamiliar familiar by finding its equivalent. Solar Kaf means they give this clarity away rather than hoarding it.',
    gift:'Generous clarity. They make things understandable. Their analogical intelligence builds bridges between worlds.',
    shadow:'Clarity can feel brutal. The Kaf person\'s precision can strip away the comfortable fog others live in.',
    in_name:'Kaf in a name adds analytic clarity and generous illumination to that position.',
    muq_note:'Kaf does not appear in the Muqattaat but Al-Karim (The Generous) is one of the most encompassing divine names.',
    keywords:['luminous air','Cold-Dry','Solar','generous clarity','analogy','Kaf particle'],
    combos:{}
  },

  's': {
    arabic:'س', name:'Seen', abjad:60,
    element:'Air', nature:'Luminous', temperament:'Cold-Dry', planet:'Mercury',
    divine_name:'Al-Sami (The All-Hearing)',
    core:'Swift clear air. Mercury: quickest planet, quickest movement. Cold-Dry: unobstructed movement. Abjad 60: active movement scale. Sirr (innermost secret), Salam (peace), Sabeel (path) — all Seen words.',
    character:'The Seen person moves with extraordinary clarity and speed — not restlessly but directionally. Mercury gives them quickness and communicative power. Cold-Dry air moves through without pooling or accumulating — the Seen person processes, moves through, and continues. The Sirr (the innermost secret of the heart) is a Seen word because secrets move like air: silently, swiftly, without resistance. Al-Sami: they hear what others cannot — the frequencies others miss.',
    gift:'Swift intelligent movement toward what matters. They arrive at understanding before others have finished the question.',
    shadow:'They move through before others have finished. Cold-Dry air does not linger — the Seen person can leave people behind without intending to.',
    in_name:'Seen in a name adds swift directional movement. At the start: this person leads by moving. Inside: the swift intelligent motion within a broader character. At the end: the name resolves in movement toward peace (Salam).',
    muq_note:'Seen appears in يس (Ya-Seen — Heart of the Quran), طس (An-Naml, Al-Qasas), طسم (Ash-Shu\'ara), and عسق (Ash-Shura). The letter of the horizon placed at the threshold of the most beloved surah.',
    keywords:['swift air','Mercury','Cold-Dry','Al-Sami','Sirr','Salam'],
    combos:{'y':'Ya+Seen opens يس. Earth reaching + swift air = the purposeful hand extending toward the flowing horizon. The Heart of the Quran opens with this gesture.','e':'Ain+Seen+Qaf = عسق (Ash-Shura). Water perception + swift air + deep air = the mechanism by which divine knowledge flows into the world.'}
  },

  'q': {
    arabic:'ق', name:'Qaf', abjad:100,
    element:'Air', nature:'Luminous', temperament:'Cold-Dry', planet:'Saturn',
    divine_name:'Al-Qadir (The All-Capable)',
    core:'High-altitude air. Saturn: the furthest visible planet. Cold-Dry air at maximum altitude: thin, clear, powerful. Abjad 100: the scale of hundreds — cosmic magnitude. Opens Surah Qaf alone.',
    character:'The Qaf person operates from the furthest reach — not among ordinary concerns but at the level of final causes. The mountain Qaf in Islamic cosmology is at the edge of the world. Their air is thin and clear — inaccessible to most but with extraordinary range of vision. Saturn gives them patience across enormous time spans. Al-Qadir: their power is real but rarely displayed because it operates from too great a distance to be visibly immediate.',
    gift:'They see the final cause of things before others have noticed the beginning. Their patience is not resignation but the patience of the long view.',
    shadow:'Altitude isolates. The Qaf person is difficult to reach, difficult to understand. The thin air at their level is not comfortable for most visitors.',
    in_name:'Qaf in a name adds high-altitude clarity and Saturn patience to that position.',
    muq_note:'Qaf opens Surah Qaf (50) alone — one of only five single-letter surah openers. The surah of divine decree, resurrection, and the Qaf mountain at the edge of creation. Unconditioned divine power.',
    keywords:['high-altitude air','Saturn','Cold-Dry','Abjad 100','Al-Qadir','cosmic scale'],
    combos:{}
  },

  'th': {
    arabic:'ث', name:'Tha', abjad:500,
    element:'Air', nature:'DARK', temperament:'Cold-Dry', planet:'Saturn',
    divine_name:'Al-Thabit (The Firm)',
    core:'DARK AIR. Absent from Al-Fatiha. Cold-Dry air + Saturn + Abjad 500: heavy, accumulated, dense air. Thamara (fruit), Thaqal (weight) — Tha words. Air that has become heavy through age.',
    character:'The Tha person carries enormous weight in an air constitution — the contradiction of lightness and density. Dark Air + Saturn + Cold-Dry = fog that has thickened to the point of touching earth. They have the reaching quality of air but the weight of accumulated Saturn experience. Their fruit (Thamara) comes slowly but is substantial — they are not quick to produce but what they produce lasts.',
    gift:'Accumulated wisdom and substance. What they carry has been refined across enormous time. Their heaviness is the weight of maturity.',
    shadow:'The density can become immovable. The Tha person can carry the weight of the past so completely that the present cannot reach them.',
    in_name:'Tha adds weight and accumulated complexity to its position in a name.',
    muq_note:'Tha does not appear in the Muqattaat — its darkness and weight are interior rather than cosmic-opening.',
    keywords:['DARK air','Saturn','Cold-Dry','Abjad 500','accumulated weight','slow fruit'],
    combos:{'m':'Tha+Meem: DARK Air + Moon-Fire. The weight of accumulated experience meeting the tidal depth of love. Together: someone who carries enormous emotional weight and loves with the persistence of old fire.'}
  },

  'dth': {
    arabic:'ظ', name:'Dha', abjad:900,
    element:'Air', nature:'DARK', temperament:'Hot-Wet', planet:'Saturn',
    divine_name:'Al-Dhahir (The Outer Manifest)',
    core:'DARK AIR. Absent from Al-Fatiha. Hot-Wet air: steam. Abjad 900: the pinnacle of air. Saturn: slow, deliberate, weighty. The letter of manifestation through pressure.',
    character:'Dha brings things into visible form from enormous accumulated pressure. Hot-Wet air at Abjad 900 with Saturn creates steam — what appears through a Dha person has been building under pressure for a very long time. Al-Dhahir: what manifests. Their manifestations carry the weight of everything that went into producing them. DARK quality: the process of manifestation is not gentle — it involves pressure, heat, transformation.',
    gift:'They are agents of significant manifestation. When things appear through them, they arrive with full weight.',
    shadow:'High-pressure manifestation is not always controllable. The steam can release before the vessel is ready.',
    in_name:'Dha adds pressure-driven manifestation to its position.',
    muq_note:'Dha does not appear in the Muqattaat but Al-Dhahir (The Manifest) pairs with Al-Batin (The Hidden) — the cosmic pair of inner and outer.',
    keywords:['DARK air','Hot-Wet steam','Saturn','Abjad 900','pressure manifestation'],
    combos:{}
  },

// ── WATER LETTERS ────────────────────────────────────────────────

  'd': {
    arabic:'د', name:'Dal', abjad:4,
    element:'Water', nature:'Luminous', temperament:'Cold-Wet', planet:'Venus',
    divine_name:'Al-Dayyan (The Judge)',
    core:'The door of water. Cold-Wet: deeply receptive and flowing. Venus: beauty in the threshold. Deen and Dunya both begin with Dal — the path and the world. Abjad 4: the four-directions completeness.',
    character:'The Dal person creates passages — between states, between people, between ways of understanding. Venus gives their thresholds grace and beauty. Cold-Wet water means they are deeply receptive: they hear what others cannot, feel currents others miss. Al-Dayyan: things flow eventually toward right placement — the Dal person facilitates this. The door is the most important part of any structure — it is where the inside meets the outside.',
    gift:'They open passage. Their presence creates movement between previously separate things.',
    shadow:'A door exists in the liminal space between inside and outside — it is rarely fully either. The Dal person can feel perpetually in-between.',
    in_name:'Dal in a name adds the threshold quality — the place of passage.',
    muq_note:'Dal appears in the Abjad system and in Deen itself — the path of access to the divine is named with the threshold letter.',
    keywords:['threshold','Cold-Wet water','Venus','Abjad 4','passage','Deen'],
    combos:{}
  },

  'h': {
    arabic:'ح', name:'Ha', abjad:8,
    element:'Water', nature:'Luminous', temperament:'Cold-Wet', planet:'Sun',
    divine_name:'Al-Hamid (The Praiseworthy)',
    core:'Sunlit water. Cold-Wet + Sun = the most life-giving combination. Hamd (praise), Haqq (truth), Hayat (life), Hikmah (wisdom) — all begin with Ha. Abjad 8: the number of cosmic completion.',
    character:'The water Ha is the letter of life\'s essential qualities. Sunlit Cold-Wet water is photosynthesis — the fundamental creative act of the universe. The Ha person carries what living requires: praise, truth, life, wisdom. They give these without counting. Al-Hamid: they are genuinely worthy of the praise they receive because what they give is life itself. Abjad 8: the octave, the number beyond the seven that completes the cosmic scale.',
    gift:'Life-giving at the foundational level. Their presence provides what living requires. The wisdom quality (Hikmah) means their giving is not random — it is what is needed.',
    shadow:'Giving life is exhausting. The Ha person gives what others need to survive — which means their own needs can be systematically overlooked.',
    in_name:'Ha in a name adds the life-giving quality of sunlit water. At the start: life and praise as the leading mode. Inside: the hidden wisdom and life-force within.',
    muq_note:'Ha appears in حم — the Hawameem group opening seven consecutive surahs. The sunlit water of revealed love — sustained divine life-giving.',
    keywords:['sunlit water','Cold-Wet','Solar life-giving','Al-Hamid','Abjad 8','wisdom'],
    combos:{'m':'Ha+Meem: sunlit water + Moon fire. Hawameem — seven surahs. The most sustained letter pairing in the Quran. In a name: someone who illuminates with warmth that sustains across time.'}
  },

  'l': {
    arabic:'ل', name:'Lam', abjad:30,
    element:'Water', nature:'Luminous', temperament:'Cold-Wet', planet:'Saturn',
    divine_name:'Al-Latif (The Subtle/Gracious)',
    core:'Deep Saturn water. The only letter that becomes mufakhkhama (heavy) in Allah\'s name — belonging made absolute. Cold-Wet + Saturn: the deepest, most gravitational water. Abjad 30: sustained water depth.',
    character:'The Lam person belongs — completely, gravitationally, structurally. Saturn\'s gravity makes this belonging ancient and non-negotiable. Cold-Wet deep water is tidal in the largest sense — not the Moon\'s tides but Saturn\'s slow gravitational pull. In Allah\'s name (الله), Lam becomes the heaviest letter: this is belonging made cosmic. The Lam person is incomplete without their object of belonging — whether a person, a truth, or a purpose. Al-Latif: their belonging has subtle, gracious intelligence — it perceives what is needed.',
    gift:'Total loyalty at the depth of the ocean floor. When a Lam person gives their belonging, it does not withdraw.',
    shadow:'When the object of their belonging is wrong or lost, the Lam person is lost. Saturn\'s gravity is not gentle in its correction.',
    in_name:'Lam in a name adds deep-water Saturn belonging. In Allah, Lam becomes heavy — the divine name itself carries the Lam belonging at cosmic scale.',
    muq_note:'Lam appears in الم (Baqarah, Al-Imran etc.) and الر (Yunus, Hud, Yusuf). In Allah\'s name it becomes heavy — the only letter to do so. Belonging at absolute scale.',
    keywords:['deep water','Saturn','Cold-Wet','absolute belonging','Lam in Allah','Abjad 30'],
    combos:{'a':'Alif+Lam = Al — the definite article. Fire origin + deep water belonging = what is definitively itself. The most common letter pair in Arabic.','m':'Lam+Meem: deep water belonging + Moon-fire depth. Double depth from different elements. Belongs completely and loves completely.'}
  },

  'e': {
    arabic:'ع', name:'Ain', abjad:70,
    element:'Water', nature:'Luminous', temperament:'Cold-Wet', planet:'Jupiter',
    divine_name:'Al-Alim (The All-Knowing)',
    core:'The spring and the eye — both called Ain because both are sources that flow with perception. Cold-Wet Jupiter water: the abundant spring of knowledge. Abjad 70: vast knowledge scale (the 70 scholars). Opens عسق (Ash-Shura) — the mechanism of revelation.',
    character:'The Ain person sees and from what they see, something flows. The spring of an eye and the spring of water share their Arabic name because both are sources — both receive what is in them from deep below and both offer it outward in continuous flow. Jupiter makes this abundant: they do not see a little, they see a great deal, and it flows from them as naturally as water from a spring. Al-Alim: divine omniscience has this letter — the knowledge that flows from depth. Cold-Wet perception means they absorb before they express — the spring is fed from below.',
    gift:'Perception that flows. They cannot stop seeing what is true, and what they see, they share. Their insight is genuine — it comes from depth, not surface observation.',
    shadow:'The spring that cannot stop. They feel everything that flows through the Ain — which is everything. There is no shallow layer in an Ain person. Everything lands, everything is felt at the level of essence.',
    in_name:'Ain as the first letter (common in Usman, Ali, Adnan) means the whole name operates through the spring of perception — this person\'s leading mode is deep seeing. Inside: the perceiving depth behind whatever leads. At the end: the name resolves in the act of becoming a source for others.',
    muq_note:'Ain appears in عسق (Ash-Shura, Surah 42). Ain+Seen+Qaf: the flowing spring (Ain) carried by swift air (Seen) to the furthest altitude (Qaf). The full mechanism of how divine knowledge travels from source to world — the act of revelation encoded in three letters.',
    keywords:['spring of perception','Cold-Wet water','Jupiter','Al-Alim','Abjad 70','source'],
    combos:{'s':'Ain+Seen: the spring that flows swiftly. Water perception + swift air = the knowledge that moves. The act of insight becoming communication.','l':'Ain+Lam: the perceiving spring that belongs. Jupiter water + Saturn deep water. The knowing that is complete when it finds what it belongs to. Ali (عليّ) — Ain+Lam+Ya = spring belonging toward purpose.'}
  },

  'r': {
    arabic:'ر', name:'Ra', abjad:200,
    element:'Water', nature:'Luminous', temperament:'Cold-Wet', planet:'Sun',
    divine_name:'Al-Rahman (The Merciful)',
    core:'Mercy as flowing sunlit water. Rahman and Raheem — the two names by which the Quran begins every surah — both begin with Ra. Cold-Wet + Sun: warm water, life-giving. Abjad 200: abundant water at large scale.',
    character:'The Ra person is constitutionally merciful — not as a moral achievement but as a physical property. The way water is cold and wet, Ra is merciful. Rahman is the most comprehensive divine name after Allah — it encompasses all of creation in its mercy. Ra carries this cosmic quality into personal character. Cold-Wet flowing sunlit water is the most life-giving substance in creation: Ra is the letter of what the world needs to survive. Their mercy flows toward what needs it without being directed.',
    gift:'Mercy that does not need activation. Their warmth is sunlit water — it nourishes without burning. People revive in their presence.',
    shadow:'Flowing mercy can be taken advantage of. The Ra person gives without installing boundaries because boundaries are contrary to the nature of flowing water.',
    in_name:'Ra in a name adds merciful movement to that position. At the start: mercy as the leading mode. Inside: the flowing compassion within. At the end: the name resolves in mercy and flow.',
    muq_note:'Ra appears in الر (Yunus, Hud, Yusuf, Ibrahim, Al-Hijr) — five surahs of divine patience and mercy through trial. Mercury letter in the surah of divine stories: mercy flowing through narrative.',
    keywords:['flowing mercy','Cold-Wet water','Solar','Al-Rahman','Abjad 200','sustaining'],
    combos:{}
  },

  'kh': {
    arabic:'خ', name:'Kha', abjad:600,
    element:'Water', nature:'DARK', temperament:'Cold-Dry', planet:'Saturn',
    divine_name:'Al-Khabir (The Aware)',
    core:'DARK WATER. Absent from Al-Fatiha. Cold-Dry Saturn water: the coldest, darkest depth — deep ocean without light. Abjad 600: profound depth. Al-Khabir: awareness of what is hidden.',
    character:'The deep ocean trench. The Kha person goes where nothing else reaches — not from courage but from constitution. Al-Khabir: they know what is hidden not because they were told but because they went there. Cold-Dry water (paradoxically) is water that has become crystalline at depth — the ice of the deep ocean, cold beyond temperature. Saturn\'s patience is necessary: you cannot reach these depths quickly. DARK quality: their knowledge has no warmth attached to it. It is simply true.',
    gift:'They know what is genuinely hidden. Their knowledge of the unseen layers of things is comprehensive and cold — it is true regardless of whether it is comfortable.',
    shadow:'Depth without warmth can feel devastating to receive. The Kha person\'s knowledge is accurate but cold — they can speak truth that destroys because they do not know how to warm it.',
    in_name:'Kha in a name (as in Khalid, Khurram) adds the quality of cold penetrating depth to the name\'s character.',
    muq_note:'Kha does not appear in the Muqattaat but Al-Khabir (The Fully Aware) is among the most sobering divine names — awareness of the absolutely hidden.',
    keywords:['DARK water','Saturn','Cold-Dry','Al-Khabir','Abjad 600','deep ocean truth'],
    combos:{}
  },

  'gh': {
    arabic:'غ', name:'Ghain', abjad:1000,
    element:'Water', nature:'Luminous', temperament:'Cold-Wet', planet:'Jupiter',
    divine_name:'Al-Ghani (The Self-Sufficient)',
    core:'The infinite ocean. Ghayb (the unseen world) begins with Ghain. Abjad 1000: the highest value of all 28 letters. Cold-Wet Jupiter water: infinite, abundant, encompassing. Al-Ghani: self-sufficient in divine richness.',
    character:'Abjad 1000 — beyond all other letters. The Ghain person touches the furthest magnitude. Their Cold-Wet Jupiter water is the most abundant and most encompassing — it includes everything. The Ghayb (the unseen) is their native territory: they know and sense what has not yet appeared. Al-Ghani: they are rich in what others lack — the perception of what is beyond the visible. This can make them seem absent from the visible world because they are partially present in what others cannot access.',
    gift:'They exist partially in the unseen. Abjad 1000: they carry the largest magnitude. Their self-sufficiency (Al-Ghani) means they do not need external validation.',
    shadow:'Their presence in the Ghayb can make them unreachable in ordinary life. Abjad 1000 is also solitude — the furthest number from ordinary scale.',
    in_name:'Ghain in a name adds the quality of the unseen ocean — vast, encompassing, partially inaccessible.',
    muq_note:'Ghain does not appear in the Muqattaat — Al-Ghayb (the unseen) is itself the letter\'s domain, beyond the visible keys.',
    keywords:['infinite water','Jupiter','Cold-Wet','Al-Ghani','Abjad 1000','the unseen'],
    combos:{}
  },
};
  const D = {
  // AIN starters
  'usman':['e','th','m','a','n'],'uthman':['e','th','m','a','n'],'osman':['e','th','m','a','n'],
  'umar':['e','m','r'],'omar':['e','m','r'],
  'ali':['e','l','y'],'aly':['e','l','y'],
  'aliya':['e','l','y','y','a'],'aaliyah':['e','l','y','y','a'],
  'alam':['e','l','a','m'],'aleem':['e','l','y','m'],
  'ala':['e','l','a'],'alaa':['e','l','a'],
  'alim':['e','l','y','m'],
  'abdul':['e','b','d','l'],'abdur':['e','b','d','r'],
  'abdullah':['e','b','d','a','l','l','hh'],'abdallah':['e','b','d','a','l','l','hh'],
  'abid':['e','b','y','d'],'abeed':['e','b','y','d'],
  'obaid':['e','b','y','d'],'ubaid':['e','b','y','d'],
  'abeer':['e','b','y','r'],'abir':['e','b','y','r'],
  'abla':['e','b','l','a'],
  'abbas':['e','b','a','s'],
  'adil':['e','d','y','l'],'adeel':['e','d','l'],
  'adnan':['e','d','n','a','n'],
  'afaf':['e','f','a','f'],'affan':['e','f','f','a','n'],'afif':['e','f','y','f'],
  'aqeel':['e','q','y','l'],'aqil':['e','q','y','l'],'aqila':['e','q','y','l','a'],
  'arif':['e','r','f'],'areef':['e','r','f'],
  'asim':['e','s','m'],'aseem':['e','s','m'],
  'aziz':['e','z','y','z'],'azeez':['e','z','y','z'],
  'ata':['e','tw','a'],'atif':['e','tw','f'],'ateef':['e','tw','f'],
  'aun':['e','w','n'],'awn':['e','w','n'],
  'imran':['e','m','r','a','n'],'amran':['e','m','r','a','n'],
  'irfan':['e','r','f','a','n'],
  'ishaq':['e','sh','a','q'],'ishaque':['e','sh','a','q'],
  'aisha':['e','y','sh','a'],'ayesha':['e','y','sh','a'],'aysha':['e','y','sh','a'],
  'isa':['e','s','a'],'essa':['e','s','a'],'eisa':['e','s','a'],
  'ammar':['e','m','m','a','r'],'amar':['e','m','m','a','r'],
  'amr':['e','m','r'],'amer':['e','m','r'],
  'aamir':['e','m','y','r'],
  'akif':['e','k','y','f'],
  // ALIF starters
  'amir':['a','m','y','r'],
  'amina':['a','m','y','n','a'],
  'aamina':['a','m','y','n','a'],
  'aminah':['a','m','y','n','a'],'amna':['a','m','n','a'],
  'iqbal':['a','q','b','a','l'],
  'awais':['a','w','a','y','s'],
  'owais':['a','w','a','y','s'],
  'ahmad':['a','h','m','d'],'ahmed':['a','h','m','d'],
  'ahsan':['a','h','s','n'],'ahlam':['a','h','l','a','m'],
  'ibrahim':['a','b','r','a','h','m'],'ibraheem':['a','b','r','a','h','m'],
  'ismail':['a','s','m','a','e','l'],
  'idris':['a','d','r','y','s'],
  'ilyas':['a','l','y','a','s'],'elias':['a','l','y','a','s'],
  'asad':['a','s','a','d'],'assad':['a','s','a','d'],
  'akbar':['a','k','b','r'],'akmal':['a','k','m','a','l'],'akram':['a','k','r','m'],
  'afzal':['a','f','z','l'],
  'amal':['a','m','a','l'],'amani':['a','m','a','n','y'],'amjad':['a','m','j','a','d'],
  'anas':['a','n','a','s'],'anis':['a','n','y','s'],'anisa':['a','n','y','s','a'],
  'anwar':['a','n','w','r'],
  'aqsa':['a','q','s','a'],
  'arshad':['a','r','sh','a','d'],
  'ashraf':['a','sh','r','a','f'],'ashfaq':['a','sh','f','a','q'],
  'asif':['a','s','f'],'asma':['a','s','m','a'],
  'ayman':['a','y','m','a','n'],'aiman':['a','y','m','a','n'],
  'adham':['a','d','h','a','m'],
  // MEEM
  'muhammad':['m','h','m','d'],'mohammed':['m','h','m','d'],
  'mohammad':['m','h','m','d'],'muhammed':['m','h','m','d'],
  'mustafa':['m','s','tw','f','a'],
  'musa':['m','w','s','a'],'moosa':['m','w','s','a'],
  'maryam':['m','r','y','m'],'mariam':['m','r','y','m'],
  'mahnoor':['m','a','hh','n','w','r'],'mehwish':['m','hh','w','sh'],
  // SEEN
  'sumaira':['s','m','y','r','a'],'sumera':['s','m','r','a'],
  'sana':['s','n','a'],'sara':['s','r','a'],'sarah':['s','r','a','hh'],
  'salma':['s','l','m','a'],'salman':['s','l','m','a','n'],
  'saad':['s','a','d'],'sajid':['s','a','j','d'],
  'saima':['s','a','y','m','a'],'saira':['s','a','y','r','a'],
  'samina':['s','m','y','n','a'],
  'sulaiman':['s','l','y','m','a','n'],'suleman':['s','l','y','m','a','n'],
  // SAD
  'safiya':['sw','f','y','y','a'],'safia':['sw','f','y','a'],
  'sobia':['sw','w','b','y','a'],
  // SHEEN
  'shahid':['sh','a','h','y','d'],'shaheen':['sh','a','h','y','n'],
  'shazia':['sh','a','z','y','a'],'shahzad':['sh','a','h','z','a','d'],
  'shoaib':['sh','w','e','y','b'],'shehzad':['sh','hh','z','a','d'],
  'shahbaz':['sh','a','h','b','a','z'],'shakeel':['sh','a','k','y','l'],
  // HEAVY TA
  'tahira':['tw','a','h','r','a'],'tahir':['tw','a','h','r'],
  'talha':['tw','l','h','a'],'tariq':['tw','a','r','q'],
  'taha':['tw','hh'],'taimur':['tw','y','m','w','r'],
  'tayyab':['tw','y','b'],'talib':['tw','a','l','b'],
  'talal':['tw','l','a','l'],'talhah':['tw','l','h','a'],
  // LIGHT TA
  'taufiq':['t','w','f','y','q'],
  'tawfiq':['t','w','f','y','q'],
  // RA
  'rafique':['r','f','y','q'],'rafiq':['r','f','y','q'],
  'raheel':['r','h','y','l'],'rashid':['r','sh','y','d'],
  'rizwan':['r','z','w','a','n'],'rehan':['r','y','h','a','n'],
  'raza':['r','z','a'],'rabia':['r','a','b','y','a'],
  'rimsha':['r','m','sh','a'],'rukhsana':['r','kh','s','a','n','a'],
  // HA SOFT
  'hamza':['h','m','z','a'],'hassan':['h','s','n'],'hasan':['h','s','n'],
  'husain':['h','s','y','n'],'hussain':['h','s','y','n'],
  'hamid':['h','a','m','d'],'hafiz':['h','a','f','z'],
  'haris':['h','a','r','s'],'hafsa':['h','f','sw','a'],'hira':['h','y','r','a'],
  // HA BREATH
  'haroon':['hh','r','w','n'],
  'harun':['hh','r','w','n'],
  'huma':['hh','m','a'],
  // FA
  'fatima':['f','a','tw','m','a'],'fatiha':['f','a','tw','h','a'],
  'faisal':['f','y','sw','l'],'farhan':['f','r','h','a','n'],
  'farida':['f','r','y','d','a'],'farrukh':['f','r','kh'],
  // KHA
  'khalid':['kh','a','l','d'],'khaled':['kh','a','l','d'],
  'khurram':['kh','r','m'],'khurshid':['kh','r','sh','y','d'],
  // ZAYN
  'zainab':['z','y','n','b'],'zaynab':['z','y','n','b'],
  'zahra':['z','hh','r','a'],'zara':['z','r','a'],
  'zubair':['z','b','y','r'],'zafar':['z','f','r'],'zahid':['z','a','h','y','d'],
  // NUN
  'nawaz':['n','w','a','z'],'nadia':['n','a','d','y','a'],
  'noor':['n','w','r'],'nur':['n','w','r'],
  'naeem':['n','e','y','m'],'najma':['n','a','j','m','a'],
  'naveed':['n','a','w','y','d'],'nabeel':['n','a','b','y','l'],
  'naila':['n','a','y','l','a'],'naima':['n','e','y','m','a'],'nimra':['n','m','r','a'],
  // BA
  'bilal':['b','l','a','l'],'bushra':['b','sh','r','a'],
  'babar':['b','a','b','r'],'badar':['b','a','d','r'],
  // DAL
  'dawood':['d','a','w','d'],'daud':['d','a','w','d'],
  // YA
  'yusuf':['y','w','s','f'],'yousef':['y','w','s','f'],'yousuf':['y','w','s','f'],
  'yahya':['y','hh','y','a'],'yasir':['y','a','s','r'],'yasser':['y','a','s','r'],
  // QAF
  'qasim':['q','a','s','m'],'qadir':['q','a','d','r'],'qaisar':['q','y','s','r'],
  // LAM
  'layla':['l','y','l','a'],'laila':['l','y','l','a'],
  'lubna':['l','b','n','a'],'laraib':['l','a','r','a','y','b'],
  // GHAIN
  'ghulam':['gh','l','a','m'],'ghazala':['gh','z','a','l','a'],
  // WAW
  'wasim':['w','a','s','m'],'waqar':['w','a','q','r'],'waqas':['w','a','q','a','s'],
  // SURNAMES
  'chohan':['ch','w','h','a','n'],'chaudhry':['ch','w','dh','r','y'],
  'khan':['kh','a','n'],'malik':['m','a','l','k'],
  'qureshi':['q','r','sh','y'],'ansari':['a','n','s','a','r','y'],
  'siddiqui':['s','d','y','q','y'],'bukhari':['b','kh','a','r','y'],
  // ADDITIONAL VERIFIED NAMES
  'feroz':['f','y','r','w','z'],'feroze':['f','y','r','w','z'],
  'firoz':['f','y','r','w','z'],'firoze':['f','y','r','w','z'],
  'fairuz':['f','y','r','w','z'],'fayruz':['f','y','r','w','z'],
  'sajjad':['s','j','a','d'],'sajad':['s','j','a','d'],
  'uzma':['e','dth','m'],'uzmah':['e','dth','m'],
  'shams':['sh','m','s'],
  'quratulain':['q','r','t','l','e','y','n'],
  'qurratulain':['q','r','t','l','e','y','n'],
  'qurat':['q','r','t'],'qurrat':['q','r','t'],
  'abrar':['a','b','r','a','r'],
  'afshan':['a','f','sh','a','n'],
  'ahmer':['a','h','m','r'],
  'aimen':['a','y','m','n'],
  'aleena':['e','l','y','n','a'],'alina':['e','l','y','n','a'],
  'ammara':['e','m','m','a','r','a'],'ammarah':['e','m','m','a','r','a'],
  'arman':['a','r','m','a','n'],
  'aroha':['e','r','w','hh','a'],'arwa':['e','r','w','a'],
  'aryan':['a','r','y','a','n'],
  'asher':['a','sh','r'],
  'ayaan':['a','y','a','n'],'ayan':['a','y','a','n'],
  'ayat':['a','y','a','t'],
  'azaan':['a','dh','a','n'],'azan':['a','dh','a','n'],
  'baber':['b','a','b','r'],
  'danish':['d','a','n','y','sh'],
  'danyal':['d','a','n','y','a','l'],'daniel':['d','a','n','y','a','l'],
  'daud':['d','a','w','d'],
  'dua':['d','e','a'],
  'dunya':['d','n','y','a'],
  'ehsan':['a','h','s','a','n'],'ihsan':['a','h','s','a','n'],
  'emaan':['a','y','m','a','n'],'iman':['a','y','m','a','n'],
  'faraz':['f','r','a','z'],
  'farooq':['f','r','w','q'],'farouk':['f','r','w','q'],
  'farzana':['f','r','z','a','n','a'],
  'fatimah':['f','a','tw','m','a'],
  'furqan':['f','r','q','a','n'],
  'gulshan':['gh','l','sh','a','n'],
  'gulnaz':['gh','l','n','a','z'],
  'hameed':['h','a','m','y','d'],
  'hareem':['h','r','y','m'],
  'harith':['h','a','r','y','th'],
  'haya':['h','y','a'],
  'hoorain':['hh','w','r','a','n'],'hourain':['hh','w','r','a','n'],
  'ibtisam':['e','b','t','y','s','a','m'],
  'inaya':['e','n','a','y','a'],'inayah':['e','n','a','y','a'],
  'iqra':['e','q','r','a'],
  'isra':['e','s','r','a'],
  'jabir':['j','a','b','r'],
  'javed':['j','a','w','y','d'],'javid':['j','a','w','y','d'],
  'jawad':['j','w','a','d'],
  'junaid':['j','n','y','d'],
  'kainat':['k','a','y','n','a','t'],
  'kamran':['k','m','r','a','n'],
  'kashif':['k','sh','a','f'],
  'khurrum':['kh','r','r','a','m'],
  'luqman':['l','q','m','a','n'],
  'majid':['m','a','j','y','d'],'majeed':['m','a','j','y','d'],
  'malaika':['m','l','a','y','k','a'],'malaak':['m','l','a','y','k'],
  'maaz':['m','e','a','z'],'muaaz':['m','e','a','z'],
  'mehreen':['m','hh','r','y','n'],
  'mehrnaz':['m','hh','r','n','a','z'],
  'mobeen':['m','b','y','n'],'mobin':['m','b','y','n'],
  'muneeb':['m','n','y','b'],
  'munir':['m','n','y','r'],'muneer':['m','n','y','r'],
  'musab':['m','sw','e','b'],
  'muskan':['m','s','k','a','n'],
  'naimat':['n','e','m','a','t'],
  'nasir':['n','a','s','r'],'nasser':['n','a','s','r'],
  'nauman':['n','e','m','a','n'],'nouman':['n','e','m','a','n'],
  'obaid':['e','b','y','d'],
  'rafay':['r','f','y'],
  'ramzan':['r','m','dw','a','n'],'ramadan':['r','m','dw','a','n'],
  'rania':['r','a','n','y','a'],
  'rashida':['r','sh','y','d','a'],
  'rehana':['r','y','h','a','n','a'],
  'rukhsar':['r','kh','s','a','r'],
  'ruksana':['r','kh','s','a','n','a'],
  'sabeeh':['s','b','y','hh'],'sabih':['s','b','y','hh'],
  'sadia':['s','a','d','y','a'],
  'sajida':['s','a','j','d','a'],
  'saman':['s','m','a','n'],
  'sameer':['s','m','y','r'],'samir':['s','m','y','r'],
  'saqib':['s','a','q','b'],
  'shabnam':['sh','b','n','a','m'],
  'shafiq':['sh','a','f','y','q'],'shafique':['sh','a','f','y','q'],
  'shakil':['sh','a','k','y','l'],
  'shamim':['sh','m','y','m'],
  'shanza':['sh','a','n','z','a'],
  'shareef':['sh','r','y','f'],'sharif':['sh','r','y','f'],
  'sibghat':['s','b','gh','a','t'],
  'siddiq':['s','d','y','q'],'siddique':['s','d','y','q'],
  'subhan':['s','b','h','a','n'],
  'suhaib':['s','hh','y','b'],'suhayb':['s','hh','y','b'],
  'sultan':['s','l','tw','a','n'],
  'sundas':['s','n','d','s'],
  'tasneem':['t','s','n','y','m'],'tasnim':['t','s','n','y','m'],
  'umer':['e','m','r'],'umair':['e','m','y','r'],
  'uzair':['e','z','y','r'],
  'wahab':['w','hh','a','b'],'wahhab':['w','hh','a','b'],
  'waleed':['w','l','y','d'],'walid':['w','l','y','d'],
  'waseem':['w','s','y','m'],
  'yasmeen':['y','a','s','m','y','n'],'yasmine':['y','a','s','m','y','n'],
  'yousaf':['y','w','s','f'],'younus':['y','w','n','s'],
  'yunus':['y','w','n','s'],
  'zahir':['z','a','h','y','r'],
  'zaki':['z','k','y'],'zakir':['z','a','k','r'],
  'zia':['dh','y','a'],
  'zobia':['z','w','b','y','a'],
  'zoha':['dh','hh','a'],'zuha':['dh','hh','a'],
  'zoya':['z','w','y','a'],
  'zuberi':['z','b','y','r','y'],
};
  const ARABIC_MAP={
  'ا':'a','أ':'a','إ':'a','آ':'a','ب':'b','ت':'t','ث':'th','ج':'j',
  'ح':'h','خ':'kh','د':'d','ذ':'dh','ر':'r','ز':'z','س':'s','ش':'sh',
  'ص':'sw','ض':'dw','ط':'tw','ظ':'dth','ع':'e','غ':'gh','ف':'f',
  'ق':'q','ك':'k','ل':'l','م':'m','ن':'n','ه':'hh','و':'w','ي':'y','ى':'y',
  'پ':'b','ٹ':'t','ڈ':'d','ڑ':'r','ژ':'z','گ':'q','چ':'j','ں':'n',
  'ہ':'hh','ے':'y','ئ':'y','ۃ':'hh',
  '\u064B':'','\u064C':'','\u064D':'','\u064E':'','\u064F':'',
  '\u0650':'','\u0651':'','\u0652':'','\u0670':'','\u0640':'',
};
  window.ASR_LETTERS = { L: L, D: D, ARABIC_MAP: ARABIC_MAP };
  window.L = L;
  window.D = D;
  window.ARABIC_MAP = ARABIC_MAP;
})();
