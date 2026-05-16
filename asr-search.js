/* AsrNaam — Search-as-you-type with fuzzy matching (Levenshtein) + dropdown.
   Loads on /names/ and similar index pages where #nameSearch + window.__asrAlts exist.
   Provides typo-tolerant suggestions in a dropdown without removing the existing
   in-grid filter behaviour. */
(function(){
  function ready(fn){
    if(document.readyState!=='loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }
  ready(function(){
    var input = document.getElementById('nameSearch');
    if(!input) return;
    if(!window.__asrAlts) return;

    // Build flat list of {token, canon, isAlt}
    var index = [];
    var canonMap = window.__asrAlts;
    Object.keys(canonMap).forEach(function(canon){
      index.push({t: canon, c: canon, a: 0});
      var alts = canonMap[canon] || [];
      for(var i=0;i<alts.length;i++){
        var a = (alts[i]||'').toLowerCase();
        if(a) index.push({t: a, c: canon, a: 1});
      }
    });

    // Levenshtein + scoring come from the shared /asr-matcher.js module
    // (loaded before this script). If it's missing, abort: dropdown is non-essential.
    if(!window.ASR_MATCHER){ return; }
    var lev = window.ASR_MATCHER.lev;
    var score = window.ASR_MATCHER.score;

    var box = input.parentNode;
    box.style.position = 'relative';
    var dd = document.createElement('div');
    dd.id = 'asr-search-dd';
    dd.style.cssText = [
      'position:absolute','top:100%','left:0','right:0',
      'background:var(--surface,#fff)',
      'border:1px solid var(--border,#E8E2D4)',
      'border-radius:0 0 8px 8px',
      'box-shadow:0 8px 24px rgba(0,0,0,0.12)',
      'max-height:360px','overflow-y:auto','z-index:1000',
      'display:none','margin-top:2px'
    ].join(';');
    box.appendChild(dd);

    var st = document.createElement('style');
    st.textContent = [
      '#asr-search-dd .asr-sd-item{display:block;padding:.55rem .9rem;color:inherit;text-decoration:none;border-bottom:1px solid var(--border,#E8E2D4);font-family:inherit;font-size:.95rem;cursor:pointer;}',
      '#asr-search-dd .asr-sd-item:last-child{border-bottom:none;}',
      '#asr-search-dd .asr-sd-item:hover,#asr-search-dd .asr-sd-item.asr-sd-active{background:var(--warm-mid,#F2EFE8);color:var(--gold,#8B6914);}',
      '#asr-search-dd .asr-sd-name{font-weight:500;text-transform:capitalize;}',
      '#asr-search-dd .asr-sd-via{font-size:.78rem;color:var(--text-secondary,#6B6B6B);margin-left:.45rem;font-style:italic;}',
      '#asr-search-dd .asr-sd-variants{display:block;margin-top:.25rem;font-size:.75rem;color:var(--text-secondary,#6B6B6B);font-style:italic;}',
      '#asr-search-dd .asr-sd-variant{display:inline-block;margin-right:.5rem;padding:.05rem .45rem;border:1px solid var(--border,#E8E2D4);border-radius:8px;background:var(--warm-mid,#F2EFE8);font-size:.72rem;font-style:normal;text-transform:capitalize;}',
      '#asr-search-dd .asr-sd-empty{padding:.7rem .9rem;color:var(--text-secondary,#6B6B6B);font-size:.9rem;font-style:italic;}',
      '#asr-search-dd .asr-sd-cta{display:block;padding:.7rem .9rem;background:rgba(139,105,20,.06);border-top:1px dashed rgba(139,105,20,.3);color:var(--gold,#8B6914);font-family:inherit;font-size:.9rem;cursor:pointer;text-decoration:none;transition:background .2s;}',
      '#asr-search-dd .asr-sd-cta:hover{background:rgba(139,105,20,.14);}',
      '#asr-search-dd .asr-sd-cta strong{font-family:"Cinzel",serif;font-size:.7rem;letter-spacing:.18em;text-transform:uppercase;display:block;margin-bottom:.2rem;}',
      '#asr-search-dd .asr-sd-cta-name{font-style:italic;text-transform:capitalize;}',
      '#asr-search-dd .asr-sd-cta-sub{display:block;font-size:.78rem;color:var(--text-secondary,#6B6B6B);margin-top:.2rem;font-style:italic;}',
      '@media(prefers-color-scheme:dark){#asr-search-dd{background:#1f1f1f;color:#e8e2d4;border-color:#3a3a3a}#asr-search-dd .asr-sd-item{border-color:#3a3a3a}#asr-search-dd .asr-sd-item:hover,#asr-search-dd .asr-sd-item.asr-sd-active{background:#2a2a2a;color:#d4b86a}#asr-search-dd .asr-sd-cta{background:rgba(212,184,106,.08);color:#d4b86a;border-color:rgba(212,184,106,.3)}}'
    ].join('\n');
    document.head.appendChild(st);

    var activeIdx = -1, lastResults = [];

    function escapeHtml(s){return String(s).replace(/[&<>\"']/g, function(c){return ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"})[c];});}

    function ctaHtml(q){
      var safeQ = escapeHtml(q || '');
      var encoded = encodeURIComponent(q || '');
      return '<a class="asr-sd-cta" href="/reader/?name='+encoded+'">' +
        '<strong>Generate a reading →</strong>' +
        '<span>Read "<span class="asr-sd-cta-name">' + safeQ + '</span>" letter by letter — even if we don\'t have a page yet.</span>' +
        '<span class="asr-sd-cta-sub">Our letter-based tool composes a fresh reading on the fly.</span>' +
      '</a>';
    }

    function render(results, q){
      lastResults = results;
      activeIdx = -1;
      if(!results.length){
        dd.innerHTML = '<div class="asr-sd-empty">No exact matches in our verified library.</div>' + ctaHtml(q);
        dd.style.display = 'block';
        return;
      }
      var html = '';
      for(var i=0;i<results.length;i++){
        var r = results[i];
        var label = r.c.replace(/-/g,' ');
        var variantsHtml = '';
        if(r.variants && r.variants.length){
          var chips = r.variants.slice(0, 5).map(function(v){
            return '<span class="asr-sd-variant">'+escapeHtml(v)+'</span>';
          }).join('');
          variantsHtml = '<div class="asr-sd-variants">also: '+chips+'</div>';
        } else if(r.a && r.t!==r.c){
          variantsHtml = '<span class="asr-sd-via">via spelling: '+escapeHtml(r.t)+'</span>';
        }
        html += '<a href="/names/'+encodeURIComponent(r.c)+'/" class="asr-sd-item" data-idx="'+i+'"><span class="asr-sd-name">'+escapeHtml(label)+'</span>'+variantsHtml+'</a>';
      }
      // If the best match is only a fuzzy/Levenshtein hit (score >= 3),
      // also surface the dynamic-reader CTA so the user can read THEIR exact spelling.
      var bestScore = (results[0] && typeof results[0].score === 'number') ? results[0].score : 0;
      if(bestScore >= 3 && q){ html += ctaHtml(q); }
      dd.innerHTML = html;
      dd.style.display = 'block';
    }

    function search(q){
      q = (q||'').toLowerCase().trim();
      if(!q || q.length<2){ dd.style.display='none'; return; }
      // Per-canonical: collect best score, the matching token, and any other matching variants
      var grouped = Object.create(null);
      for(var i=0;i<index.length;i++){
        var ent = index[i];
        var sc = score(ent.t, q);
        if(sc<999){
          var g = grouped[ent.c];
          if(!g){
            g = grouped[ent.c] = {entry: ent, score: sc, variants: []};
          } else if(sc < g.score){
            // Move previous best to variants
            if(g.entry.t !== ent.t) g.variants.push(g.entry.t);
            g.entry = ent;
            g.score = sc;
          } else if(ent.t !== g.entry.t){
            g.variants.push(ent.t);
          }
        }
      }
      var hits = [];
      Object.keys(grouped).forEach(function(k){ hits.push(grouped[k]); });
      // STRICT TIER PRECEDENCE: drop fuzzy/substring hits when an exact /
      // prefix hit exists. Tiers 0=exact, 1=prefix, 2=substring, 3=fuzzy.
      // This makes typing "Orhan" surface /names/orhan/ — never /names/burhan/.
      var tierFn = (window.ASR_MATCHER && window.ASR_MATCHER.tier) ? window.ASR_MATCHER.tier : function(s){ return s<=-1?0 : (s===0?1 : (s<=2?2 : 3)); };
      var minTier = 4;
      hits.forEach(function(h){ h._tier = tierFn(h.score); if(h._tier < minTier) minTier = h._tier; });
      if(minTier < 4) hits = hits.filter(function(h){ return h._tier === minTier; });
      hits.sort(function(a,b){
        if(a.score!==b.score) return a.score-b.score;
        // Within same score, prefer canonical-name-match first
        var ac = a.entry.t === a.entry.c ? 0 : 1;
        var bc = b.entry.t === b.entry.c ? 0 : 1;
        if(ac!==bc) return ac-bc;
        // C6 — shorter canonical wins (popularity proxy: short canonical names tend to be the common forms)
        var lenDiff = a.entry.c.length - b.entry.c.length;
        if(lenDiff!==0) return lenDiff;
        return a.entry.c.localeCompare(b.entry.c);
      });
      var top = hits.slice(0, 12).map(function(h){
        // Dedupe variants and exclude the canonical name
        var seen = {};
        var unique = [];
        h.variants.forEach(function(v){
          if(v !== h.entry.c && !seen[v]){ seen[v] = 1; unique.push(v); }
        });
        return {c:h.entry.c, t:h.entry.t, a:h.entry.a, variants: unique, score: h.score};
      });
      render(top, q);
    }

    function setActive(idx){
      var items = dd.querySelectorAll('.asr-sd-item');
      items.forEach(function(el,i){
        if(i===idx) el.classList.add('asr-sd-active'); else el.classList.remove('asr-sd-active');
      });
      activeIdx = idx;
      if(idx>=0 && items[idx] && items[idx].scrollIntoView) items[idx].scrollIntoView({block:'nearest'});
    }

    var debounceT;
    input.addEventListener('input', function(){
      clearTimeout(debounceT);
      var v = input.value;
      debounceT = setTimeout(function(){ search(v); }, 60);
    });
    input.addEventListener('keydown', function(e){
      if(dd.style.display==='none') return;
      var items = dd.querySelectorAll('.asr-sd-item');
      if(e.key==='ArrowDown'){ e.preventDefault(); setActive(Math.min(activeIdx+1, items.length-1)); }
      else if(e.key==='ArrowUp'){ e.preventDefault(); setActive(Math.max(activeIdx-1, 0)); }
      else if(e.key==='Enter'){
        if(activeIdx>=0 && items[activeIdx]){ e.preventDefault(); window.location.href = items[activeIdx].getAttribute('href'); }
        else if(items[0]){ e.preventDefault(); window.location.href = items[0].getAttribute('href'); }
      } else if(e.key==='Escape'){ dd.style.display='none'; }
    });
    input.addEventListener('blur', function(){ setTimeout(function(){ dd.style.display='none'; }, 180); });
    input.addEventListener('focus', function(){ if(input.value && input.value.length>=2) search(input.value); });
    document.addEventListener('click', function(e){
      if(e.target===input || dd.contains(e.target)) return;
      dd.style.display='none';
    });
  });
})();
