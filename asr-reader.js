/* AsrNaam — Dynamic Reader (composeReading on the fly for any name)
   Loads on /reader/ and any page that wires #reader-output / #reader-form / #reader-input.
   The L data, D dictionary, ARABIC_MAP, and parsers are mirrored from index.html
   to keep this file fully self-contained. Single source of truth: keep them in sync
   if index.html L / D / parser changes. */
(function(){
// L is now provided by /data/asr-letters.js (loaded ahead of this file)

// D is now provided by /data/asr-letters.js (loaded ahead of this file)

// ARABIC_MAP is now provided by /data/asr-letters.js (loaded ahead of this file)

const SP=[['kh','kh'],['gh','gh'],['sh','sh'],['th','th'],['dh','dh'],['ch','kh'],['q','q'],['z','z'],['b','b'],['d','d'],['f','f'],['h','hh'],['j','j'],['k','k'],['l','l'],['m','m'],['n','n'],['r','r'],['s','s'],['t','t'],['w','w'],['y','y'],['v','w']];
const MP=[['kh','kh'],['gh','gh'],['sh','sh'],['th','th'],['dh','dh'],['ch','kh'],['ai','e'],['ay','e'],['ee','y'],['oo','w'],['aw','w'],['ow','w'],['q','q'],['z','z'],['b','b'],['d','d'],['f','f'],['j','j'],['k','k'],['l','l'],['m','m'],['n','n'],['r','r'],['s','s'],['t','t'],['w','w'],['y','y'],['a','a'],['e','a'],['i','a'],['o','a'],['u','a'],['h','hh']];

function isAr(s){return/[\u0600-\u06FF]/.test(s);}
function parseAr(w){const r=[];for(const c of w){const k=ARABIC_MAP[c];if(k===undefined||k==='')continue;if(L[k]&&(r.length===0||r[r.length-1]!==k))r.push(k);}return r;}
function parseTr(w){const r=[];let i=0;const dig2=[['sh','sh'],['kh','kh'],['gh','gh'],['th','th'],['dh','dh'],['ch','sh'],['ph','f'],['qu','q'],['ee','y'],['ii','y'],['oo','w'],['ou','w'],['aa','a'],['ai','e'],['ay','e'],['aw','w'],['ow','w']];while(i<w.length){const rem=w.slice(i);let matched=false;for(const[p,k]of dig2){if(rem.startsWith(p)){if(L[k]&&(r.length===0||r[r.length-1]!==k))r.push(k);i+=p.length;matched=true;break;}}if(matched)continue;const c=w[i];if(i>0&&c===w[i-1]&&!'aeiou'.includes(c)){i++;continue;}if('aeiou'.includes(c)){const isFirst=i===0;const isLast=i===w.length-1;const prevVowel=i>0&&'aeiou'.includes(w[i-1]);if(isFirst){const k=(c==='u'||c==='o')?'e':'a';if(L[k])r.push(k);}else if(isLast&&(c==='a'||c==='i'||c==='u')){const k=c==='a'?'a':c==='i'?'y':'w';if(L[k]&&(r.length===0||r[r.length-1]!==k))r.push(k);}else if(prevVowel){const k=(c==='i'||c==='e')?'y':(c==='u'||c==='o')?'w':null;if(k&&L[k]&&(r.length===0||r[r.length-1]!==k))r.push(k);}i++;continue;}const cmap={'b':'b','t':'t','j':'j','h':'hh','d':'d','r':'r','z':'z','s':'s','f':'f','q':'q','k':'k','l':'l','m':'m','n':'n','w':'w','y':'y','p':'b','v':'w','g':'gh','x':'kh','c':'k'};const k=cmap[c];if(k&&L[k]&&(r.length===0||r[r.length-1]!==k))r.push(k);i++;}return r;}
function parseWord(w){if(isAr(w))return parseAr(w);const l=w.toLowerCase();if(D[l])return D[l];return parseTr(l);}
function parseName(n){if(!n)return[];return n.trim().split(/\s+/).flatMap(w=>parseWord(w));}
function letter(k){return L[k]||null;}


// ── ROMAN→ARABIC reverse map (best-effort; uses ARABIC_MAP for lookup) ──
const REV_ARABIC = (function(){
  const m = {};
  Object.keys(ARABIC_MAP).forEach(function(ar){
    const k = ARABIC_MAP[ar];
    if(!k) return;
    if(!m[k]) m[k] = ar;
  });
  return m;
})();

function bestArabicForLetter(k){
  const l = L[k];
  if(l && l.arabic) return l.arabic;
  return REV_ARABIC[k] || '';
}

function transliterateToArabic(letters){
  // Use the canonical Arabic glyph from each L entry (matches the static-page convention).
  let out = '';
  for(let i=0;i<letters.length;i++){
    const k = letters[i];
    const l = L[k];
    if(!l) continue;
    out += l.arabic || REV_ARABIC[k] || '';
  }
  return out;
}

// ── DOMINANT LETTER + ELEMENT ─────────────────────────────────────
function pickDominant(letters){
  // First letter is *the* dominant in Ilm ul Huroof tradition (the outward face).
  // We also surface the most-frequent letter as a secondary "weight" signal.
  if(!letters.length) return null;
  const counts = Object.create(null);
  for(let i=0;i<letters.length;i++){ counts[letters[i]] = (counts[letters[i]]||0)+1; }
  let topK = letters[0], topN = 0;
  for(const k in counts){ if(counts[k] > topN){ topN = counts[k]; topK = k; } }
  return { first: letters[0], heaviest: topK, count: topN };
}

function elementMix(letters){
  const tally = {Fire:0,Earth:0,Air:0,Water:0,Other:0};
  for(let i=0;i<letters.length;i++){
    const l = L[letters[i]]; if(!l) continue;
    if(tally[l.element] !== undefined) tally[l.element]++;
    else tally.Other++;
  }
  let topE = 'Fire', topN = -1;
  ['Fire','Earth','Air','Water'].forEach(function(e){ if(tally[e] > topN){ topN = tally[e]; topE = e; } });
  return { tally: tally, dominant: topE };
}

// ── PERSONALITY OBSERVATION composer ──────────────────────────────
const ELEMENT_VOICE = {
  Fire:  'rises and decides — a temperament that warms whatever it stands close to and burns through what blocks it',
  Earth: 'stays and holds — a temperament that gathers what others scatter and gives weight to what others would let pass',
  Air:   'moves and connects — a temperament that carries word and intent across distance, rarely staying long in one shape',
  Water: 'feels and shapes — a temperament that takes the form of what it meets, then re-emerges with the meeting changed'
};

function personalityObservation(name, letters){
  if(!letters.length) return '';
  const first = letters[0];
  const last  = letters[letters.length-1];
  const fl = L[first];
  const ll = L[last];
  const mix = elementMix(letters);
  const dom = pickDominant(letters);

  let out = '';
  out += '<p>' + esc(name) + ' is a name whose outward face is set by <strong>' + fl.name + '</strong> — ' + (fl.core || '') + '</p>';
  out += '<p>The wider element of the name is <em>' + mix.dominant + '</em>: this is a constitution that ' + ELEMENT_VOICE[mix.dominant] + '.</p>';
  if(dom && dom.count >= 2 && dom.heaviest !== first){
    const hl = L[dom.heaviest];
    out += '<p>One letter recurs — <strong>' + hl.name + '</strong>, ' + dom.count + ' times. ' + (hl.in_name || hl.character || '').replace(/^[A-Z][a-z]+ /, '') + '</p>';
  }
  if(ll && ll !== fl){
    out += '<p>The name resolves on <strong>' + ll.name + '</strong> — ' + (ll.in_name || ll.character || '') + '</p>';
  }
  return out;
}

// ── HELPERS ───────────────────────────────────────────────────────
function esc(s){ return String(s||'').replace(/[&<>"']/g, function(c){return ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"})[c];}); }

function sanitizeName(raw){
  // Strip everything except letters, spaces, hyphens; collapse whitespace
  let s = String(raw||'');
  // Allow Arabic block + Latin letters + hyphen + space + apostrophe
  s = s.replace(/[^؀-ۿA-Za-z\s'\-]/g, '');
  s = s.replace(/\s+/g, ' ').trim();
  // Cap length
  if(s.length > 60) s = s.slice(0, 60);
  return s;
}

function titleCase(s){
  return String(s||'').toLowerCase().split(/\s+/).map(function(w){
    if(!w) return '';
    return w.charAt(0).toUpperCase() + w.slice(1);
  }).join(' ');
}

// ── COMPOSE THE READING (returns HTML string) ─────────────────────
function composeReading(rawName){
  const name = sanitizeName(rawName);
  if(!name) {
    return '<div class="reader-empty"><h2>Type a name to read it</h2><p>Enter any name above — Arabic, English transliteration, or a Muslim/Arabic-derived name. The tool will read it letter by letter through Ilm ul Huroof.</p></div>';
  }
  if(name.replace(/[\s\-]/g,'').length < 2){
    return '<div class="reader-empty"><h2>That name is a little short</h2><p>Try a name with at least 2 letters. A single letter is not enough for a reading — Ilm ul Huroof reads letters in relation to each other.</p></div>';
  }

  const display = titleCase(name);
  const firstWord = name.split(' ')[0];
  const letters = parseName(firstWord);

  if(!letters.length){
    return '<div class="reader-empty"><h2>Could not read this name</h2><p>The tool could not map "' + esc(display) + '" to Arabic letters. Try a different spelling, or check that you used Latin or Arabic characters only.</p></div>';
  }

  const arabic = transliterateToArabic(letters);
  const breakdown = letters.map(function(k){ return L[k] ? L[k].name : k; }).join(' · ');
  const mix = elementMix(letters);
  const dom = pickDominant(letters);

  let html = '';

  // Dynamic-reading flag
  html += '<div class="reader-flag">Dynamic Reading · Composed on the fly · Not yet in our verified library</div>';

  // Hero
  html += '<div class="hero">';
  html += '<div class="arabic-name" lang="ar" dir="rtl">' + esc(arabic) + '</div>';
  html += '<div class="name-badge">Generated Reading &nbsp;·&nbsp; <span>Ilm ul Huroof</span></div>';
  html += '<h1><em>' + esc(display) + '</em></h1>';
  html += '<p class="hero-subtitle">' + esc(display) + ' read through its letters — composed on the fly using the same letter-analysis the static library uses.</p>';
  html += '</div>';

  // Quick facts
  html += '<div class="content">';
  html += '<aside class="quick-facts" aria-label="Quick facts about ' + esc(display) + '">';
  html += '<div class="qf-row"><span class="qf-label">English</span><span class="qf-value">' + esc(display) + '</span></div>';
  html += '<div class="qf-row"><span class="qf-label">Arabic (estimate)</span><span class="qf-value qf-arabic" lang="ar" dir="rtl">' + esc(arabic) + '</span></div>';
  html += '<div class="qf-row"><span class="qf-label">Letters</span><span class="qf-value">' + letters.length + '</span></div>';
  html += '<div class="qf-row"><span class="qf-label">Dominant Element</span><span class="qf-value">' + mix.dominant + '</span></div>';
  if(dom && L[dom.heaviest]){
    html += '<div class="qf-row"><span class="qf-label">Heaviest Letter</span><span class="qf-value">' + esc(L[dom.heaviest].name) + ' <span lang="ar" dir="rtl">' + esc(L[dom.heaviest].arabic) + '</span></span></div>';
  }
  html += '<div class="qf-row" style="grid-column:1/-1"><span class="qf-label">Breakdown</span><span class="qf-value">' + esc(breakdown) + '</span></div>';
  html += '</aside>';

  // Letter cards
  html += '<div class="section-label">The Letters of ' + esc(display) + '</div>';
  html += '<div class="letter-cards">';
  letters.forEach(function(k, i){
    const l = L[k]; if(!l) return;
    const isFirst = i === 0;
    const isLast  = i === letters.length - 1 && letters.length > 1;
    const pos = isFirst ? 'First' : isLast ? 'Last' : 'Interior';
    html += '<div class="letter-card">';
    html += '<span class="letter-arabic" lang="ar" dir="rtl">' + esc(l.arabic) + '</span>';
    html += '<span class="letter-roman">' + esc(l.name) + '</span>';
    html += '<span class="letter-pos">' + pos + '</span>';
    html += '</div>';
  });
  html += '</div>';

  // Per-letter readings (unique letters, in order)
  html += '<div class="section-label">Each Letter Read</div>';
  html += '<p class="letters-intro">Every letter of a name carries its own meaning and contributes to the person who bears it. The reading begins with each letter individually — what it means, what it carries — before the whole is synthesised.</p>';
  const seen = Object.create(null);
  letters.forEach(function(k, i){
    if(seen[k]) return; seen[k] = 1;
    const l = L[k]; if(!l) return;
    const isFirst = i === 0;
    const isLast  = i === letters.length - 1 && letters.length > 1;
    const role = isFirst ? 'first' : isLast ? 'last' : 'interior';
    const roleLabel = role === 'first'
      ? 'First letter — the outward nature, how the world sees this person'
      : role === 'last'
      ? 'Final letter — how the name resolves, what this person leaves behind'
      : 'Interior letter — the hidden character, what runs beneath the surface';
    const isDark = l.nature === 'DARK';
    html += '<div class="letter-reading-block' + (isDark ? ' dark' : '') + '">';
    html += '<div class="lrb-head"><span class="lrb-arabic" lang="ar" dir="rtl">' + esc(l.arabic) + '</span><div><strong class="lrb-name">' + esc(l.name) + (isDark ? ' <span class="lrb-dark">dark letter</span>' : '') + '</strong><br><span class="lrb-role">' + roleLabel + '</span></div></div>';
    html += '<p class="lrb-core"><em>' + esc(l.core || '') + '</em></p>';
    html += '<p class="lrb-char">' + esc(l.character || '') + '</p>';
    if(l.gift) html += '<p class="lrb-gift"><strong>Gift:</strong> ' + esc(l.gift) + '</p>';
    if(l.shadow) html += '<p class="lrb-shadow"><strong>Shadow:</strong> ' + esc(l.shadow) + '</p>';
    if(isDark && l.dark_note) html += '<p class="lrb-darknote"><em>' + esc(l.dark_note) + '</em></p>';
    html += '</div>';
  });

  // Personality observation
  html += '<div class="section-label">Personality Observation</div>';
  html += '<div class="prose">' + personalityObservation(display, letters) + '</div>';

  // Footnote: this is generated
  html += '<div class="reader-footnote">';
  html += '<strong>About this reading.</strong> This page was composed on the fly using the same letter-analysis the static library uses. It is a generated reading. Names in our verified library include additional Arabic + Urdu research, root-letter etymology, classical sources, and the famous bearers who have carried the name. ';
  html += '<a href="/names/">Browse our verified library →</a>';
  html += '</div>';

  // CTAs
  html += '<div class="reader-ctas">';
  html += '<button type="button" class="reader-cta" id="readerSaveImg">Save as image</button>';
  html += '<button type="button" class="reader-cta" id="readerShare">Share this reading</button>';
  html += '<a href="mailto:hello@asrnaam.com?subject=Add%20' + encodeURIComponent(display) + '%20to%20the%20library&body=I%27d%20like%20to%20share%20a%20reading%20for%20' + encodeURIComponent(display) + '." class="reader-cta">Add this name to the library</a>';
  html += '</div>';

  // Trust line
  html += '<p class="reader-trust">Reading grounded in Ilm ul Huroof — the Science of Letters — in the lineage of Muhyiddin Ibn Arabi. A framework for reflection, not prediction.</p>';

  html += '</div>'; // .content

  return html;
}

// ── INIT ──────────────────────────────────────────────────────────
function getQueryName(){
  try {
    const u = new URL(window.location.href);
    return u.searchParams.get('name') || '';
  } catch(e){ return ''; }
}

function cacheKey(name){ return 'asr-reader-cache:' + name.toLowerCase(); }

function readCache(name){
  try {
    const raw = localStorage.getItem(cacheKey(name));
    if(!raw) return null;
    const o = JSON.parse(raw);
    if(o && o.html && (Date.now() - o.t) < 1000 * 60 * 60 * 24 * 30) return o.html;
  } catch(e){}
  return null;
}

function writeCache(name, html){
  try { localStorage.setItem(cacheKey(name), JSON.stringify({html: html, t: Date.now()})); } catch(e){}
}

function renderInto(el, name){
  if(!el) return;
  const clean = sanitizeName(name);
  if(!clean){ el.innerHTML = composeReading(''); bindCtas(el, ''); return; }
  // Cache lookup
  const cached = readCache(clean);
  if(cached){ el.innerHTML = cached; bindCtas(el, clean); return; }
  const html = composeReading(clean);
  el.innerHTML = html;
  writeCache(clean, html);
  bindCtas(el, clean);
  updateUrl(clean);
  updateMeta(clean);
}

function updateUrl(name){
  try {
    const u = new URL(window.location.href);
    u.searchParams.set('name', name);
    history.replaceState(null, '', u.toString());
  } catch(e){}
}

function updateMeta(name){
  const display = titleCase(name);
  document.title = display + ' — Dynamic Ilm ul Huroof Reading | AsrNaam';
  const md = document.querySelector('meta[name="description"]');
  if(md) md.setAttribute('content', display + ' — a generated Ilm ul Huroof reading composed letter by letter, using the same letter-analysis the AsrNaam library uses.');
}

function bindCtas(el, name){
  const save = el.querySelector('#readerSaveImg');
  const share = el.querySelector('#readerShare');
  if(save) save.addEventListener('click', function(){
    if(window.print) window.print();
  });
  if(share) share.addEventListener('click', async function(){
    const url = window.location.href;
    const title = titleCase(name) + ' — Reading on AsrNaam';
    if(navigator.share){
      try { await navigator.share({title: title, url: url}); } catch(e){}
    } else if(navigator.clipboard){
      try { await navigator.clipboard.writeText(url); share.textContent = 'Link copied!'; setTimeout(function(){share.textContent='Share this reading';}, 1800); } catch(e){}
    }
  });
}

document.addEventListener('DOMContentLoaded', function(){
  const out = document.getElementById('reader-output');
  const form = document.getElementById('reader-form');
  const input = document.getElementById('reader-input');
  if(!out) return;

  const initial = getQueryName();
  if(initial) {
    if(input) input.value = sanitizeName(initial);
    renderInto(out, initial);
  } else {
    out.innerHTML = composeReading('');
  }

  if(form){
    form.addEventListener('submit', function(e){
      e.preventDefault();
      const v = input ? input.value : '';
      renderInto(out, v);
      // Scroll to result
      out.scrollIntoView({behavior:'smooth', block:'start'});
    });
  }
});

})();
