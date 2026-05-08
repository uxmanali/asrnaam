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

    function score(token, q){
      if(token===q) return -1;
      if(token.indexOf(q)===0) return 0;
      if(token.indexOf(q)>=0) return 1;
      var d = lev(token, q, 2);
      if(d<=2) return 2 + d;
      if(q.length>=4){
        var head = token.slice(0, q.length+1);
        var d2 = lev(head, q, 2);
        if(d2<=2) return 4 + d2;
      }
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
        var via = (r.a && r.t!==r.c) ? '<span class="asr-sd-via">via spelling: '+escapeHtml(r.t)+'</span>' : '';
        html += '<a href="/names/'+encodeURIComponent(r.c)+'/" class="asr-sd-item" data-idx="'+i+'"><span class="asr-sd-name">'+escapeHtml(label)+'</span>'+via+'</a>';
      }
      dd.innerHTML = html;
      dd.style.display = 'block';
    }

    function search(q){
      q = (q||'').toLowerCase().trim();
      if(!q || q.length<2){ dd.style.display='none'; return; }
      var seen = Object.create(null);
      for(var i=0;i<index.length;i++){
        var ent = index[i];
        var sc = score(ent.t, q);
        if(sc<999){
          if(seen[ent.c]===undefined || sc < seen[ent.c].score){
            seen[ent.c] = {entry: ent, score: sc};
          }
        }
      }
      var hits = [];
      Object.keys(seen).forEach(function(k){ hits.push(seen[k]); });
      hits.sort(function(a,b){
        if(a.score!==b.score) return a.score-b.score;
        return a.entry.c.localeCompare(b.entry.c);
      });
      var top = hits.slice(0, 12).map(function(h){return {c:h.entry.c,t:h.entry.t,a:h.entry.a};});
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
