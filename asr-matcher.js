/* AsrNaam — Shared search-matcher module.
   Exposes window.ASR_MATCHER with: lev, score, tier, normQuery, normArabic,
   normLatin, isArabic, isGibberish, levDist, popularity, maxLevForQuery,
   buildTokenIndex, runSearch.

   STRICT TIER PRECEDENCE (lower tier number wins; ties broken by raw score):
     Tier 0 — exact match            (score: -1)
     Tier 1 — prefix match           (score:  0)   q is a prefix of token
     Tier 2 — substring/partial-word (score:  1, 2)
     Tier 3 — fuzzy Levenshtein      (score:  3..9; max distance scales by q len)
   Consumers SHOULD show only the highest non-empty tier; fall to the next
   tier ONLY if the higher tier has fewer than 3 results.
   When tier-0 (exact) results exist, NO lower-tier fallback runs — instead the
   cross-spelling cluster (canonicals sharing the exact-match's normalized
   Arabic root) is surfaced after the exact hit(s).
*/
(function(){

  // ---- Arabic normalization ----
  var ARABIC_DIACRITIC_RE = /[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]/g;

  function stripHarakat(s){
    return s.replace(ARABIC_DIACRITIC_RE, '');
  }

  function normArabic(s){
    if(!s) return '';
    var t = stripHarakat(s);
    t = t.replace(/[أإآٱ]/g, 'ا');
    t = t.replace(/ى/g, 'ي');
    t = t.replace(/ة/g, 'ه');
    t = t.replace(/ی/g, 'ي');
    t = t.replace(/ک/g, 'ك');
    t = t.replace(/ـ/g, '');
    t = t.replace(/[\s\-]+/g, '');
    return t.trim();
  }

  function isArabic(s){
    return /[\u0600-\u06FF\u0750-\u077F]/.test(s);
  }

  // ---- Latin normalization ----
  function normLatin(s){
    if(!s) return '';
    s = String(s).toLowerCase();
    try { s = s.normalize('NFD').replace(/[̀-ͯ]/g, ''); } catch(e){}
    s = s.replace(/ß/g,'ss').replace(/œ/g,'oe').replace(/æ/g,'ae').replace(/ø/g,'o');
    s = s.replace(/[Ѐ-ӿ]/g,'');
    s = s.replace(/[^a-z0-9 \-]/g, '');
    return s.replace(/\s+/g, ' ').trim();
  }

  function normQuery(q){
    if(q===null || q===undefined) return '';
    q = String(q);
    q = q.replace(/^[\s .,!?;:'"()*\[\]{}]+|[\s .,!?;:'"()*\[\]{}]+$/g, '');
    if(!q) return '';
    if(isArabic(q)) return normArabic(q);
    return normLatin(q);
  }

  function isGibberish(q){
    if(!q) return true;
    if(/^\d+$/.test(q)) return true;
    if(!/[a-z\u0600-\u06FF]/i.test(q)) return true;
    return false;
  }

  // ---- Levenshtein ----
  function lev(a, b, maxDist){
    if(a===b) return 0;
    if(maxDist===undefined) maxDist = 99;
    var la=a.length, lb=b.length;
    if(Math.abs(la-lb)>maxDist) return maxDist+1;
    var prev=new Array(lb+1), cur=new Array(lb+1);
    for(var j=0;j<=lb;j++) prev[j]=j;
    for(var i=1;i<=la;i++){
      cur[0]=i;
      var rowMin=cur[0];
      var ca=a.charCodeAt(i-1);
      for(var j2=1;j2<=lb;j2++){
        var cost=(ca===b.charCodeAt(j2-1))?0:1;
        var v=Math.min(prev[j2]+1, cur[j2-1]+1, prev[j2-1]+cost);
        cur[j2]=v;
        if(v<rowMin) rowMin=v;
      }
      if(rowMin>maxDist) return maxDist+1;
      var tmp=prev; prev=cur; cur=tmp;
    }
    return prev[lb];
  }

  function maxLevForQuery(q){
    if(!q) return 0;
    // Short queries get a tight budget so noisy 7-char queries like
    // "brennan" can't pick up lev-3 matches like "renad".
    return q.length <= 7 ? 2 : 3;
  }

  function score(token, q){
    if(token===q) return -1;
    if(!q || !token) return 999;
    if(token.indexOf(q)===0) return 0;
    if(token.indexOf(q)>=0) return 1;
    if(q.length>=4 && token.length>=4){
      // Partial-word: q's first 4..6 chars appear as substring of token.
      // We only check Q-prefix-in-token (not the reverse), since
      // token-prefix-in-q creates noisy matches (e.g. "renn" of "rennad"
      // hitting query "brennan").
      for(var pl = Math.min(q.length, 6); pl>=4; pl--){
        if(token.indexOf(q.slice(0, pl))>=0){ return 2; }
      }
    }
    if(q.length>=3){
      var maxD = maxLevForQuery(q);
      var headLen = Math.min(token.length, q.length + 2);
      var head = token.slice(0, headLen);
      var dp = lev(head, q, maxD);
      if(dp<=maxD) return 3 + dp;
      var d = lev(token, q, maxD);
      if(d<=maxD) return 7 + d;
    }
    return 999;
  }

  function tier(s){
    if(s === -1) return 0;
    if(s === 0)  return 1;
    if(s === 1 || s === 2) return 2;
    if(s >= 3 && s < 999) return 3;
    return 4;
  }

  function levDist(s){
    if(s <= 0) return 0;
    if(s <= 2) return 0;
    if(s < 7) return s - 3;
    return s - 7;
  }

  // Popularity bias for the most common Muslim names. Adds a tiebreaker so
  // "mu" → Muhammad (not muaaz/muad/etc.), "ahmed" → Ahmed etc.
  var POP = {
    'muhammad':100,'mohammed':96,'mohammad':94,'muhammed':90,'muhammet':70,
    'ali':95,'fatima':95,'fatimah':92,
    'aisha':90,'ayesha':88,'aishah':82,
    'khadija':92,'khadijah':88,'khadeeja':70,'khadijat':60,
    'omar':92,'umar':92,'umer':82,'usman':90,'uthman':82,
    'hassan':90,'hussain':90,'hussein':86,'husayn':80,'hasan':86,
    'ibrahim':92,'yusuf':90,'maryam':92,'zainab':92,'zaynab':80,
    'amina':88,'aminah':85,'sara':86,'sarah':86,'noor':88,'nur':84,
    'rashid':82,'ahmed':94,'ahmad':94,'hamza':88,'bilal':86,'tariq':80,
    'abd-ar-rahman':86,'abdurrahman':84,'abdulrahman':84,'abdirahman':70,'abderrahmane':60,
    'sumaira':70,'sumayra':50,'orhan':70,
    'abdullah':92,'abdulla':80,
    'rayyan':82,'rehan':70,'reyhan':60,
    'zara':80,'zahra':86,'safiya':80,'safiyyah':78,
    'salman':82,'sulaiman':82,'sulayman':80,
    'khalid':86,'khaled':82,'tahir':78,'taher':70,
    'idris':80,'ismail':82,'ishaq':80,'dawood':80,'dawud':80
  };

  function popularity(slug){
    if(!slug) return 0;
    return POP[String(slug).toLowerCase()] || 0;
  }

  // ---- Token index builder ----
  // Builds an alphabetised array of tokens from a corpus of canonical entries.
  // Each token: {t (normalized search-string), i (corpus index), kind}.
  // kind ∈ {'canon','slug','variant','arabic','urdu'}.
  function buildTokenIndex(corpus){
    var tokens = [];
    for(var k=0;k<corpus.length;k++){
      var ent = corpus[k];
      var nameNorm = normLatin(ent.n || '');
      var sl = (ent.s || '').toLowerCase();
      var slugSpaced = sl.replace(/-/g,' ');
      var slugSpacedNorm = normLatin(slugSpaced);
      if(nameNorm) tokens.push({t: nameNorm, i: k, kind: 'canon'});
      if(slugSpacedNorm && slugSpacedNorm !== nameNorm) tokens.push({t: slugSpacedNorm, i: k, kind: 'slug'});
      if(sl && sl !== nameNorm && sl !== slugSpacedNorm) tokens.push({t: sl, i: k, kind: 'slug'});
      var vs = ent.v || [];
      for(var j=0;j<vs.length;j++){
        var v = normLatin((vs[j]||'').replace(/-/g,' '));
        if(v) tokens.push({t: v, i: k, kind: 'variant'});
      }
      if(ent.a){
        var ar = normArabic(ent.a);
        if(ar) tokens.push({t: ar, i: k, kind: 'arabic'});
      }
      if(ent.u){
        var ur = normArabic(ent.u);
        if(ur) tokens.push({t: ur, i: k, kind: 'urdu'});
      }
    }
    tokens.sort(function(a,b){ return a.t<b.t?-1:a.t>b.t?1:0; });
    return tokens;
  }

  // ---- Corpus search pipeline ----
  function runSearch(corpus, tokens, rawQ, opts){
    opts = opts || {};
    var MAX = opts.max || 10;
    var SCAP = opts.singleCharCap || 8;
    var qn = normQuery(rawQ);
    if(!qn) return {q:'', mode:'empty', results:[]};
    if(isGibberish(qn)) return {q: qn, mode:'cta', results:[]};

    var arabicQuery = isArabic(qn);

    var best = Object.create(null);
    for(var p=0; p<tokens.length; p++){
      var tt = tokens[p];
      var isArTok = tt.kind === 'arabic' || tt.kind === 'urdu';
      if(arabicQuery && !isArTok) continue;
      if(!arabicQuery && isArTok) continue;
      var s = score(tt.t, qn);
      if(s>=999) continue;
      var cur = best[tt.i];
      if(!cur || s < cur.s){ best[tt.i] = {s: s, tok: tt.t, kind: tt.kind}; }
    }

    var raw = [];
    var keys = Object.keys(best);
    for(var k=0; k<keys.length; k++){
      var i = keys[k];
      var e = corpus[i]; if(!e) continue;
      var b = best[i];
      raw.push({e:e, score:b.s, tier:tier(b.s), tok:b.tok, kind:b.kind, isCluster:false});
    }

    // Tier-3 (fuzzy) post-filter: the CANONICAL name itself must be within
    // maxLev of the query. This prevents variant-only fuzzy matches from
    // surfacing canonicals that are themselves far from the query
    // (e.g. "brennan" hitting variant "rennad" whose canonical "renad"
    // is lev 3 from the query).
    if(!arabicQuery){
      var maxD = maxLevForQuery(qn);
      raw = raw.filter(function(r){
        if(r.tier < 3) return true;
        var canon = (r.e.n || r.e.s || '').toLowerCase();
        return lev(canon, qn, maxD) <= maxD;
      });
    }

    if(!arabicQuery && qn.length === 1){
      raw = raw.filter(function(r){ return r.tier <= 1; });
      _sortResults(raw, qn);
      return {q: qn, mode:'list', results: raw.slice(0, SCAP)};
    }

    if(!raw.length){
      return {q: qn, mode:'cta', results:[]};
    }

    var byTier = {0:[],1:[],2:[],3:[]};
    raw.forEach(function(r){ byTier[r.tier].push(r); });

    var out = [];
    if(byTier[0].length){
      _sortResults(byTier[0], qn);
      out = byTier[0].slice();
      out = _expandCluster(out, corpus, MAX);
    } else {
      for(var t=1; t<=3 && out.length < 3; t++){
        if(byTier[t].length){
          _sortResults(byTier[t], qn);
          var seen = Object.create(null);
          out.forEach(function(r){ seen[r.e.s] = 1; });
          byTier[t].forEach(function(r){
            if(!seen[r.e.s]) out.push(r);
          });
        }
      }
    }

    if(!out.length){
      return {q: qn, mode:'cta', results:[]};
    }
    return {q: qn, mode:'list', results: out.slice(0, MAX)};
  }

  function _expandCluster(seedHits, corpus, MAX){
    var seedSlugs = Object.create(null);
    var roots = Object.create(null);
    seedHits.forEach(function(r){
      seedSlugs[r.e.s] = 1;
      var root = normArabic(r.e.a || '');
      if(root) roots[root] = 1;
    });
    if(!Object.keys(roots).length) return seedHits.slice(0, MAX);
    var siblings = [];
    for(var i=0;i<corpus.length;i++){
      var c = corpus[i];
      if(seedSlugs[c.s]) continue;
      var cr = normArabic(c.a || '');
      if(cr && roots[cr]){
        siblings.push({e:c, score:0, tier:0, tok:c.s, kind:'cluster', isCluster:true});
      }
    }
    siblings.sort(function(a,b){
      var pa = popularity(a.e.s), pb = popularity(b.e.s);
      if(pa !== pb) return pb - pa;
      return a.e.s < b.e.s ? -1 : 1;
    });
    return seedHits.concat(siblings).slice(0, MAX);
  }

  function _sortResults(arr, qn){
    arr.sort(function(a, b){
      if(a.score !== b.score) return a.score - b.score;
      var pa = popularity(a.e.s), pb = popularity(b.e.s);
      if(pa !== pb) return pb - pa;
      var canA = (a.e.n || a.e.s || '').toLowerCase();
      var canB = (b.e.n || b.e.s || '').toLowerCase();
      var da = lev(canA, qn, 4);
      var db = lev(canB, qn, 4);
      if(da !== db) return da - db;
      if(canA.length !== canB.length) return canA.length - canB.length;
      return canA < canB ? -1 : (canA > canB ? 1 : 0);
    });
  }

  window.ASR_MATCHER = {
    lev: lev,
    score: score,
    tier: tier,
    normArabic: normArabic,
    normLatin: normLatin,
    normQuery: normQuery,
    isArabic: isArabic,
    isGibberish: isGibberish,
    levDist: levDist,
    popularity: popularity,
    maxLevForQuery: maxLevForQuery,
    stripHarakat: stripHarakat,
    buildTokenIndex: buildTokenIndex,
    runSearch: runSearch
  };
})();
