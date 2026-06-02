/* AsrNaam — Search-as-you-type dropdown for /names/ index pages.
   Mounts on #nameSearch. Fetches /names/names-index.json once, then delegates
   query → results to window.ASR_MATCHER.runSearch (see /asr-matcher.js).
   Renders a listbox with role="option" rows + aria-activedescendant management,
   keyboard nav, single CTA fallback when no real matches exist. */
(function(){
  function ready(fn){
    if(document.readyState!=='loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }
  ready(function(){
    var input = document.getElementById('nameSearch');
    if(!input) return;
    if(!window.ASR_MATCHER) return;
    var M = window.ASR_MATCHER;

    // ---- Corpus loader (shared with Cmd-K / homepage hero search) ----
    var CORPUS = null, TOKENS = null, LOADING = false;
    function fetchCorpus(){
      if(CORPUS) return Promise.resolve(CORPUS);
      if(LOADING) return new Promise(function(res){ var t = setInterval(function(){ if(CORPUS){ clearInterval(t); res(CORPUS); } }, 30); });
      LOADING = true;
      return fetch('/names/names-index.json', {cache:'force-cache'}).then(function(r){
        if(!r.ok) throw new Error('idx '+r.status);
        return r.json();
      }).then(function(arr){
        CORPUS = arr;
        TOKENS = M.buildTokenIndex(arr);
        LOADING = false;
        return CORPUS;
      }).catch(function(){
        LOADING = false;
        // Fallback to legacy __asrAlts so the dropdown still works offline.
        var alts = window.__asrAlts || {};
        var arr = Object.keys(alts).map(function(canon){
          return {s: canon, n: canon.replace(/-/g,' ').replace(/\b\w/g, function(c){return c.toUpperCase();}), v: alts[canon] || []};
        });
        CORPUS = arr;
        TOKENS = M.buildTokenIndex(arr);
        return CORPUS;
      });
    }

    // ---- Styles ----
    var box = input.parentNode;
    box.style.position = 'relative';
    var dd = document.createElement('div');
    dd.id = 'asr-search-dd';
    dd.setAttribute('role','listbox');
    dd.setAttribute('aria-label','Name suggestions');
    box.appendChild(dd);

    // ARIA wiring on the input
    input.setAttribute('role','combobox');
    input.setAttribute('aria-autocomplete','list');
    input.setAttribute('aria-controls', 'asr-search-dd');
    input.setAttribute('aria-expanded','false');

    var st = document.createElement('style');
    st.textContent = [
      '#asr-search-dd{position:absolute;top:100%;left:0;right:0;background:var(--surface,#fff);border:1px solid var(--border,#E8E2D4);border-radius:0 0 8px 8px;box-shadow:0 8px 24px rgba(0,0,0,0.12);max-height:380px;overflow-y:auto;z-index:1000;display:none;margin-top:2px;}',
      '#asr-search-dd .asr-sd-item{display:block;padding:.55rem .9rem;color:inherit;text-decoration:none;border-bottom:1px solid var(--border,#E8E2D4);font-family:inherit;font-size:.95rem;cursor:pointer;}',
      '#asr-search-dd .asr-sd-item:last-child{border-bottom:none;}',
      '#asr-search-dd .asr-sd-item:hover,#asr-search-dd .asr-sd-item[aria-selected="true"]{background:var(--warm-mid,#F2EFE8);color:var(--gold,#8B6914);}',
      '#asr-search-dd .asr-sd-name{font-weight:500;text-transform:capitalize;}',
      '#asr-search-dd .asr-sd-ar{display:inline-block;margin-left:.55rem;font-family:"Amiri",serif;font-size:.95rem;color:var(--gold,#8B6914);vertical-align:baseline;}',
      '#asr-search-dd .asr-sd-meaning{display:block;margin-top:.2rem;font-size:.78rem;color:var(--text-secondary,#6B6B6B);font-style:italic;}',
      '#asr-search-dd .asr-sd-badge{display:inline-block;margin-left:.5rem;padding:.05rem .45rem;border:1px solid rgba(139,105,20,0.3);border-radius:8px;font-size:.65rem;letter-spacing:.08em;text-transform:uppercase;color:var(--gold,#8B6914);font-style:normal;vertical-align:middle;}',
      '#asr-search-dd .asr-sd-empty{padding:.7rem .9rem;color:var(--text-secondary,#6B6B6B);font-size:.9rem;font-style:italic;}',
      '#asr-search-dd .asr-sd-cta{display:block;padding:.7rem .9rem;background:rgba(139,105,20,.06);border-top:1px dashed rgba(139,105,20,.3);color:var(--gold,#8B6914);font-family:inherit;font-size:.9rem;cursor:pointer;text-decoration:none;transition:background .2s;}',
      '#asr-search-dd .asr-sd-cta:hover,#asr-search-dd .asr-sd-cta[aria-selected="true"]{background:rgba(139,105,20,.14);}',
      '#asr-search-dd .asr-sd-cta strong{font-family:"Cinzel",serif;font-size:.7rem;letter-spacing:.18em;text-transform:uppercase;display:block;margin-bottom:.2rem;}',
      '#asr-search-dd .asr-sd-cta-name{font-style:italic;text-transform:capitalize;}',
      '#asr-search-dd .asr-sd-cta-sub{display:block;font-size:.78rem;color:var(--text-secondary,#6B6B6B);margin-top:.2rem;font-style:italic;}',
      '@media(prefers-color-scheme:dark){#asr-search-dd{background:#1f1f1f;color:#e8e2d4;border-color:#3a3a3a}#asr-search-dd .asr-sd-item{border-color:#3a3a3a}#asr-search-dd .asr-sd-item:hover,#asr-search-dd .asr-sd-item[aria-selected="true"]{background:#2a2a2a;color:#d4b86a}#asr-search-dd .asr-sd-cta{background:rgba(212,184,106,.08);color:#d4b86a;border-color:rgba(212,184,106,.3)}#asr-search-dd .asr-sd-ar{color:#d4b86a;}#asr-search-dd .asr-sd-meaning{color:#b6b0a2;}}'
    ].join('\n');
    document.head.appendChild(st);

    var activeIdx = -1, lastItems = [];

    function escapeHtml(s){return String(s).replace(/[&<>\"']/g, function(c){return ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"})[c];});}

    function ctaHtml(q){
      var safeQ = escapeHtml(q || '');
      var encoded = encodeURIComponent(q || '');
      return '<a class="asr-sd-cta" id="asr-sd-cta" role="option" aria-selected="false" href="/reader/?name='+encoded+'">' +
        '<strong>Generate a reading →</strong>' +
        '<span>Read "<span class="asr-sd-cta-name">' + safeQ + '</span>" letter by letter — even if we don\'t have a page yet.</span>' +
        '<span class="asr-sd-cta-sub">Our letter-based tool composes a fresh reading on the fly.</span>' +
      '</a>';
    }

    function shortMeaning(m){
      if(!m) return '';
      var s = String(m).trim();
      var dash = s.indexOf('—');
      if(dash > 0 && dash <= 110) return s.slice(0, dash).trim();
      var dot = s.search(/[.!?]/);
      if(dot > 0 && dot <= 140) return s.slice(0, dot).trim();
      return s.length > 140 ? s.slice(0, 137).trim() + '…' : s;
    }

    function render(result, rawQ){
      activeIdx = -1;
      input.setAttribute('aria-expanded','true');
      if(result.mode === 'empty'){
        dd.style.display = 'none';
        input.setAttribute('aria-expanded','false');
        input.removeAttribute('aria-activedescendant');
        lastItems = [];
        return;
      }
      if(result.mode === 'cta'){
        dd.innerHTML = '<div class="asr-sd-empty">No exact matches in our verified library.</div>' + ctaHtml(rawQ);
        dd.style.display = 'block';
        lastItems = dd.querySelectorAll('.asr-sd-cta');
        return;
      }
      var html = '';
      var items = result.results.slice(0, 10);
      for(var i=0;i<items.length;i++){
        var r = items[i];
        var e = r.e;
        var label = (e.n || e.s || '').replace(/-/g,' ');
        var arabic = e.a ? ' <span class="asr-sd-ar" lang="ar" dir="rtl">'+escapeHtml(e.a)+'</span>' : '';
        var meaning = shortMeaning(e.m);
        var meanHtml = meaning ? '<span class="asr-sd-meaning">'+escapeHtml(meaning)+'</span>' : '';
        var clusterBadge = r.isCluster ? '<span class="asr-sd-badge">also spelt</span>' : '';
        html += '<a href="/names/'+encodeURIComponent(e.s)+'/" class="asr-sd-item" id="asr-sd-o'+i+'" role="option" aria-selected="false" data-idx="'+i+'"><span class="asr-sd-name">'+escapeHtml(label)+'</span>'+arabic+clusterBadge+meanHtml+'</a>';
      }
      dd.innerHTML = html;
      dd.style.display = 'block';
      lastItems = dd.querySelectorAll('.asr-sd-item');
    }

    function doSearch(rawV){
      fetchCorpus().then(function(){
        var res = M.runSearch(CORPUS, TOKENS, rawV, {max: 10, singleCharCap: 8});
        render(res, rawV);
        try{ if(typeof gtag==='function' && rawV && rawV.trim().length>=2) gtag('event','search',{search_term:rawV.trim(),results:(res&&res.results?res.results.length:0)}); }catch(e){}
      });
    }

    function setActive(idx){
      var items = dd.querySelectorAll('.asr-sd-item, .asr-sd-cta');
      if(!items.length){ activeIdx = -1; input.removeAttribute('aria-activedescendant'); return; }
      if(idx < 0) idx = 0;
      if(idx >= items.length) idx = items.length - 1;
      items.forEach(function(el,i){
        if(i===idx) el.setAttribute('aria-selected','true');
        else el.setAttribute('aria-selected','false');
      });
      activeIdx = idx;
      var sel = items[idx];
      if(sel){
        var id = sel.id || ('asr-sd-o'+idx);
        if(!sel.id) sel.id = id;
        input.setAttribute('aria-activedescendant', id);
        if(sel.scrollIntoView) sel.scrollIntoView({block:'nearest'});
      }
    }

    var debounceT;
    input.addEventListener('input', function(){
      clearTimeout(debounceT);
      var v = input.value;
      debounceT = setTimeout(function(){ doSearch(v); }, 60);
    });
    input.addEventListener('keydown', function(e){
      if(dd.style.display==='none') return;
      var items = dd.querySelectorAll('.asr-sd-item, .asr-sd-cta');
      if(!items.length) return;
      if(e.key==='ArrowDown'){ e.preventDefault(); setActive(activeIdx < 0 ? 0 : Math.min(activeIdx+1, items.length-1)); }
      else if(e.key==='ArrowUp'){ e.preventDefault(); setActive(Math.max(activeIdx-1, 0)); }
      else if(e.key==='Home'){ e.preventDefault(); setActive(0); }
      else if(e.key==='End'){ e.preventDefault(); setActive(items.length-1); }
      else if(e.key==='Enter'){
        var pick = activeIdx >= 0 ? items[activeIdx] : items[0];
        if(pick){ e.preventDefault(); window.location.href = pick.getAttribute('href'); }
      } else if(e.key==='Escape'){
        dd.style.display='none';
        input.setAttribute('aria-expanded','false');
        input.removeAttribute('aria-activedescendant');
      }
    });
    input.addEventListener('blur', function(){
      setTimeout(function(){
        dd.style.display='none';
        input.setAttribute('aria-expanded','false');
      }, 180);
    });
    input.addEventListener('focus', function(){
      if(input.value && input.value.length>=1){ doSearch(input.value); }
      else { fetchCorpus(); }
    });
    document.addEventListener('click', function(e){
      if(e.target===input || dd.contains(e.target)) return;
      dd.style.display='none';
      input.setAttribute('aria-expanded','false');
    });
  });
})();
