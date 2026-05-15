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

    // Levenshtein with early termination at maxDist
    function lev(a, b, maxDist){
      if(a===b) return 0;
      var la=a.length, lb=b.length;
      if(Math.abs(la-lb)>maxDist) return maxDist+1;
      var prev = new Array(lb+1), cur = new Array(lb+1);
      for(var j=0;j<=lb;j++) prev[j]=j;
      for(var i=1;i<=la;i++){
        cur[0]=i;
        var rowMin=cur[0];
        var ca=a.charCodeAt(i-1);
        for(var j2=1;j2<=lb;j2++){
          var cost = (ca===b.charCodeAt(j2-1)) ? 0 : 1;
          var v = Math.min(prev[j2]+1, cur[j2-1]+1, prev[j2-1]+cost);
          cur[j2]=v;
          if(v<rowMin) rowMin=v;
        }
        if(rowMin>maxDist) return maxDist+1;
        var tmp=prev; prev=cur; cur=tmp;
      }
      return prev[lb];
    }

    // C6 — loosened tolerance:
    //   * exact match           -> -1
    //   * exact-prefix          -> 0
    //   * substring             -> 1
    //   * partial-word (token contains a >=3 char head of q, or vice-versa) -> 2
    //   * Levenshtein <=3 against a prefix of the token            -> 3 + d
    //   * Levenshtein <=2 against the whole token (substring fuzz) -> 7 + d
    // Ranking falls out of the score buckets:
    //   exact-prefix > shorter-distance > shorter-token (token-length tiebreak ≈ popularity proxy)
    function score(token, q){
      if(token===q) return -1;
      if(token.indexOf(q)===0) return 0;
      if(token.indexOf(q)>=0) return 1;
      if(q.length>=3 && token.length>=3){
        // token contains a 3+ char head of q
        for(var pl = Math.min(q.length, 6); pl>=3; pl--){
          if(token.indexOf(q.slice(0, pl))>=0){ return 2; }
        }
        // q contains a 3+ char head of token (handles partial-word from the other side)
        for(var pl2 = Math.min(token.length, 6); pl2>=3; pl2--){
          if(q.indexOf(token.slice(0, pl2))>=0){ return 2; }
        }
      }
      // Prefix Levenshtein <=3 — compare a head-slice of token against q
      if(q.length>=3){
        var headLen = Math.min(token.length, q.length + 2);
        var head = token.slice(0, headLen);
        var dp = lev(head, q, 3);
        if(dp<=3) return 3 + dp;
      }
      // Whole-token Levenshtein <=2 — substring-tolerance fallback
      var d = lev(token, q, 2);
      if(d<=2) return 7 + d;
      return 999;
    }

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
      '@media(prefers-color-scheme:dark){#asr-search-dd{background:#1f1f1f;color:#e8e2d4;border-color:#3a3a3a}#asr-search-dd .asr-sd-item{border-color:#3a3a3a}#asr-search-dd .asr-sd-item:hover,#asr-search-dd .asr-sd-item.asr-sd-active{background:#2a2a2a;color:#d4b86a}}'
    ].join('\n');
    document.head.appendChild(st);

    var activeIdx = -1, lastResults = [];

    function escapeHtml(s){return String(s).replace(/[&<>\"']/g, function(c){return ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"})[c];});}

    function render(results){
      lastResults = results;
      activeIdx = -1;
      if(!results.length){
        dd.innerHTML = '<div class="asr-sd-empty">No matches. Try fewer letters or check spelling.</div>';
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
        return {c:h.entry.c, t:h.entry.t, a:h.entry.a, variants: unique};
      });
      render(top);
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
