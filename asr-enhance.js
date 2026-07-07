/* AsrNaam — Enhancement layer JS
   Theme toggle, share, favorites, recently-viewed, compare, Cmd-K, animations.
   Loads on every page; feature blocks self-detect their context. */
(function(){
  'use strict';
  var LS = {
    theme:'asr-theme',
    favs:'asr-favorites',
    recent:'asr-recent'
  };
  var REDUCED = (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  // ---- Theme toggle ----
  function applyTheme(t){
    if(t==='dark') document.documentElement.setAttribute('data-theme','dark');
    else document.documentElement.removeAttribute('data-theme');
  }
  try{
    var saved = localStorage.getItem(LS.theme);
    if(saved){ applyTheme(saved); }
    else{
      var dark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      if(dark) applyTheme('dark');
    }
  }catch(e){}

  // ---- Storage helpers (graceful degrade) ----
  function lsGet(k, def){ try{ var v=localStorage.getItem(k); return v?JSON.parse(v):def; }catch(e){ return def; } }
  function lsSet(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)); return true; }catch(e){ return false; } }

  function getFavs(){ var v=lsGet(LS.favs, []); return Array.isArray(v)?v:[]; }
  function setFavs(arr){ return lsSet(LS.favs, arr); }
  function getRecent(){ var v=lsGet(LS.recent, []); return Array.isArray(v)?v:[]; }
  function setRecent(arr){ return lsSet(LS.recent, arr); }

  // ---- Page introspection ----
  function pageContext(){
    var p = location.pathname.replace(/\/+$/,'');
    var isNamesIndex = (p==='/names' || p==='/names/index.html');
    var isHome = (p==='' || p==='/index.html');
    // Per-name page: /names/<slug>/
    var nameMatch = p.match(/^\/names\/([a-z0-9-]+)$/i);
    var slug = nameMatch ? nameMatch[1].toLowerCase() : null;
    return {isNamesIndex:isNamesIndex, isHome:isHome, slug:slug, path:p};
  }

  function pageNameFromHero(){
    var h1 = document.querySelector('h1');
    if(!h1) return null;
    var t = (h1.textContent||'').split('—')[0].split('|')[0].trim();
    return t || null;
  }

  // ---- Recently viewed: record on per-name page ----
  function recordRecent(){
    var ctx = pageContext();
    if(!ctx.slug) return;
    var name = pageNameFromHero() || ctx.slug;
    var meta = document.querySelector('meta[name="description"]');
    var meaning = meta ? (meta.content||'').split('—')[0].trim().slice(0, 90) : '';
    var entry = {slug:ctx.slug, name:name, meaning:meaning, ts:Date.now()};
    var list = getRecent().filter(function(e){ return e && e.slug && e.slug !== ctx.slug; });
    list.unshift(entry);
    if(list.length>10) list = list.slice(0,10);
    setRecent(list);
  }

  // ---- Theme toggle injection ----
  function injectThemeToggle(){
    var nav = document.querySelector('nav');
    if(!nav || nav.querySelector('.asr-theme-toggle')) return;
    var btn = document.createElement('button');
    btn.className = 'asr-theme-toggle';
    btn.setAttribute('aria-label','Toggle theme');
    btn.innerHTML =
      '<svg class="asr-icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>'+
      '<svg class="asr-icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>';
    btn.addEventListener('click', function(){
      var cur = document.documentElement.getAttribute('data-theme')==='dark' ? 'dark' : 'light';
      var nw = cur==='dark' ? 'light' : 'dark';
      applyTheme(nw);
      try{ localStorage.setItem(LS.theme, nw); }catch(e){}
    });
    var links = nav.querySelector('.nav-links');
    if(links) links.appendChild(btn); else nav.appendChild(btn);
  }

  // ---- Cmd-K trigger button (subtle, in nav) ----
  function injectCmdkTrigger(){
    var nav = document.querySelector('nav');
    if(!nav || nav.querySelector('.asr-cmdk-trigger')) return;
    var btn = document.createElement('button');
    btn.className = 'asr-cmdk-trigger';
    btn.setAttribute('aria-label','Open quick search (Cmd-K)');
    btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg><kbd>⌘K</kbd>';
    btn.addEventListener('click', openCmdk);
    var toggle = nav.querySelector('.asr-theme-toggle');
    if(toggle) toggle.parentNode.insertBefore(btn, toggle);
    else nav.appendChild(btn);
  }

  // ---- Hero: heart (favorite) + share dropdown on per-name pages ----
  function injectHeroActions(){
    var ctx = pageContext();
    if(!ctx.slug) return;
    var hero = document.querySelector('.hero');
    if(!hero) return;
    var name = pageNameFromHero();
    if(!name) return;

    // ---- Defer asr-share-card.js until user interacts with share area
    // ---- (or until browser is idle after settle — C5 perf). The script is
    // ---- NOT loaded on initial pageload — we wait for click on a share
    // ---- button, or fall back to requestIdleCallback with a 4s timeout.
    if(!window.__asrShareCardLoader){
      window.__asrShareCardLoader = function(){
        if(window.__asrShareCardLoader.done) return;
        window.__asrShareCardLoader.done = true;
        var sc = document.createElement('script');
        sc.src = '/asr-share-card.js';
        sc.async = true;
        sc.dataset.asrSharecard = '1';
        document.head.appendChild(sc);
      };
      // Eager trigger: any click in the share area or on the (post-load)
      // Save-as-image button loads the script immediately.
      document.addEventListener('click', function(e){
        if(e.target && e.target.closest &&
           e.target.closest('.asr-share-hero, .asr-save-card-cta, .asr-save-card-wrap')){
          window.__asrShareCardLoader();
        }
      }, true);
      // Backstop: load when browser is idle, so the IG/Threads/Save buttons
      // appear within ~4s without the user having to click first.
      if('requestIdleCallback' in window){
        requestIdleCallback(window.__asrShareCardLoader, { timeout: 4000 });
      } else {
        setTimeout(window.__asrShareCardLoader, 3500);
      }
    }

    // Container for the action group
    var bar = hero.querySelector('.asr-action-bar');
    if(!bar){
      bar = document.createElement('div');
      bar.className = 'asr-action-bar';
      hero.appendChild(bar);
    }

    // Favorite (heart)
    if(!bar.querySelector('.asr-fav')){
      var fav = document.createElement('button');
      fav.className = 'asr-fav';
      fav.setAttribute('aria-pressed','false');
      fav.setAttribute('aria-label','Save to favorites');
      fav.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg><span>Save</span>';
      function refreshFavBtn(){
        var favs = getFavs();
        var on = favs.some(function(e){ return e.slug===ctx.slug; });
        fav.classList.toggle('on', on);
        fav.setAttribute('aria-pressed', on?'true':'false');
        fav.querySelector('span').textContent = on ? 'Saved' : 'Save';
      }
      fav.addEventListener('click', function(){
        var meta = document.querySelector('meta[name="description"]');
        var meaning = meta ? (meta.content||'').split('—')[0].trim().slice(0,90) : '';
        var favs = getFavs();
        var i = favs.findIndex(function(e){ return e.slug===ctx.slug; });
        if(i>=0) favs.splice(i,1);
        else favs.unshift({slug:ctx.slug, name:name, meaning:meaning, ts:Date.now()});
        if(favs.length>200) favs = favs.slice(0,200);
        setFavs(favs);
        refreshFavBtn();
      });
      bar.appendChild(fav);
      refreshFavBtn();
    }

    // Share (dropdown)
    if(!bar.querySelector('.asr-share-wrap')){
      var wrap = document.createElement('div');
      wrap.className = 'asr-share-wrap';
      var sb = document.createElement('button');
      sb.className = 'asr-share';
      sb.setAttribute('aria-haspopup','menu');
      sb.setAttribute('aria-expanded','false');
      sb.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg><span>Share</span>';
      var menu = document.createElement('div');
      menu.className = 'asr-share-menu';
      menu.setAttribute('role','menu');
      var url = location.href;
      var title = document.title;
      var msg = name + ' — Islamic name meaning';
      menu.innerHTML =
        '<a role="menuitem" href="https://wa.me/?text='+encodeURIComponent(msg+' '+url)+'" target="_blank" rel="noopener">WhatsApp</a>'+
        '<a role="menuitem" href="https://twitter.com/intent/tweet?text='+encodeURIComponent(msg)+'&url='+encodeURIComponent(url)+'" target="_blank" rel="noopener">X / Twitter</a>'+
        '<a role="menuitem" href="https://www.facebook.com/sharer/sharer.php?u='+encodeURIComponent(url)+'" target="_blank" rel="noopener">Facebook</a>'+
        '<a role="menuitem" href="https://t.me/share/url?url='+encodeURIComponent(url)+'&text='+encodeURIComponent(msg)+'" target="_blank" rel="noopener">Telegram</a>'+
        '<a role="menuitem" href="https://www.threads.net/intent/post?text='+encodeURIComponent(msg+'\n'+url)+'" target="_blank" rel="noopener">Threads</a>'+
        '<button role="menuitem" type="button" class="asr-share-ig">Instagram (save card)</button>'+
        '<button role="menuitem" type="button" class="asr-share-copy">Copy link</button>'+
        '<button role="menuitem" type="button" class="asr-share-native">More…</button>';
      function close(){ wrap.classList.remove('open'); sb.setAttribute('aria-expanded','false'); }
      function toggle(){ var on=!wrap.classList.contains('open'); wrap.classList.toggle('open', on); sb.setAttribute('aria-expanded', on?'true':'false'); }
      sb.addEventListener('click', toggle);
      menu.querySelector('.asr-share-copy').addEventListener('click', async function(){
        try{
          if(navigator.clipboard){ await navigator.clipboard.writeText(url); }
          else{
            var ta=document.createElement('textarea'); ta.value=url; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta);
          }
          this.textContent='Copied!';
          setTimeout(function(b){ b.textContent='Copy link'; close(); }.bind(null,this), 900);
        }catch(e){}
      });
      menu.querySelector('.asr-share-ig').addEventListener('click', async function(){
        var saveBtn = document.querySelector('.asr-save-card-cta');
        if(saveBtn){ saveBtn.click(); }
        try{ if(navigator.clipboard) await navigator.clipboard.writeText(msg + '\n' + url); }catch(e){}
        this.textContent = '✓ Card saved · caption copied';
        var btn = this;
        setTimeout(function(){ btn.textContent = 'Instagram (save card)'; close(); }, 2400);
      });
      menu.querySelector('.asr-share-native').addEventListener('click', async function(){
        if(navigator.share){ try{ await navigator.share({title:title, url:url, text:msg}); close(); }catch(e){} }
        else { this.textContent='Not supported'; }
      });
      document.addEventListener('click', function(e){ if(!wrap.contains(e.target)) close(); });
      document.addEventListener('keydown', function(e){ if(e.key==='Escape') close(); });
      wrap.appendChild(sb);
      wrap.appendChild(menu);
      bar.appendChild(wrap);
    }
  }

  // ---- /names/ index: favorites button, recents section, compare ----
  function injectNamesIndexFeatures(){
    var ctx = pageContext();
    if(!ctx.isNamesIndex) return;

    // Insert "My Favorites" button into filter-bar
    var filterBar = document.querySelector('.filter-bar');
    if(filterBar && !filterBar.querySelector('.asr-favs-btn')){
      var fb = document.createElement('button');
      fb.className = 'filter-btn asr-favs-btn';
      fb.type='button';
      fb.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14" style="vertical-align:-2px;margin-right:4px"><path d="M12 21s-7.5-4.5-9.5-9.5C1 7 5 3 9 5c1.5.7 2.5 2 3 3 .5-1 1.5-2.3 3-3 4-2 8 2 6.5 6.5C19.5 16.5 12 21 12 21z"/></svg> Favorites';
      fb.addEventListener('click', function(){ openListModal('favorites'); });
      filterBar.appendChild(fb);
    }

    // Recently Viewed section (after Featured) — only if non-empty
    var recents = getRecent();
    if(recents.length){
      var existing = document.getElementById('asr-recently-viewed');
      if(!existing){
        var sec = document.createElement('section');
        sec.id = 'asr-recently-viewed';
        sec.className = 'recently-section';
        sec.setAttribute('aria-label','Recently viewed names');
        sec.innerHTML = '<h2 class="recently-heading">Recently Viewed</h2><div class="names-grid asr-rv-grid"></div>';
        var rec = document.getElementById('recently-updated');
        var featured = document.getElementById('featured-names');
        var anchor = featured || rec;
        if(anchor && anchor.parentNode) anchor.parentNode.insertBefore(sec, anchor.nextSibling);
        else { var m = document.querySelector('main'); if(m) m.insertBefore(sec, m.firstChild); }
      }
      var grid = document.querySelector('#asr-recently-viewed .asr-rv-grid');
      if(grid){
        grid.innerHTML = recents.map(function(e){
          var meaning = (e.meaning||'').replace(/[<>"']/g, function(c){return {'<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});
          var name = (e.name||e.slug).replace(/[<>"']/g, function(c){return {'<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});
          return '<a href="/names/'+e.slug+'/" class="name-card"><span class="name-english">'+name+'</span><span class="name-meaning">'+meaning+'</span></a>';
        }).join('');
      }
    }

    // Compare chip on each .name-card
    addCompareChips();
    initCompareUI();
  }

  // ---- Compare ----
  var COMPARE_KEY = '__asr_compare';
  function getCompare(){ if(!window[COMPARE_KEY]) window[COMPARE_KEY]=[]; return window[COMPARE_KEY]; }
  function setCompare(a){ window[COMPARE_KEY]=a; updateCompareTray(); }

  function addCompareChips(){
    document.querySelectorAll('.name-card').forEach(function(card){
      if(card.querySelector('.asr-cmp-chip')) return;
      // Skip the cards we just added in recently-viewed (still want them — fine)
      var href = card.getAttribute('href')||'';
      var m = href.match(/\/names\/([^\/]+)\//);
      if(!m) return;
      var slug = m[1];
      var nameEl = card.querySelector('.name-english');
      var meaningEl = card.querySelector('.name-meaning');
      if(!nameEl) return;
      var chip = document.createElement('button');
      chip.type='button';
      chip.className='asr-cmp-chip';
      chip.setAttribute('aria-label','Add to compare');
      chip.dataset.slug = slug;
      chip.dataset.name = nameEl.textContent;
      chip.dataset.meaning = meaningEl ? meaningEl.textContent : '';
      chip.dataset.gender = card.classList.contains('boy')?'boy':(card.classList.contains('girl')?'girl':'');
      chip.dataset.region = card.getAttribute('data-region')||'';
      chip.textContent='+';
      chip.addEventListener('click', function(e){
        e.preventDefault(); e.stopPropagation();
        toggleCompare({slug:slug, name:chip.dataset.name, meaning:chip.dataset.meaning, gender:chip.dataset.gender, region:chip.dataset.region}, chip);
      });
      card.appendChild(chip);
    });
    refreshCompareChips();
  }

  function refreshCompareChips(){
    var sel = getCompare().map(function(e){return e.slug;});
    document.querySelectorAll('.asr-cmp-chip').forEach(function(c){
      var on = sel.indexOf(c.dataset.slug)>=0;
      c.classList.toggle('on', on);
      c.textContent = on ? '✓' : '+';
    });
  }

  function toggleCompare(item, chip){
    var arr = getCompare();
    var i = arr.findIndex(function(e){ return e.slug===item.slug; });
    if(i>=0) arr.splice(i,1);
    else{
      if(arr.length>=3){ /* cap at 3 */ arr.shift(); }
      arr.push(item);
    }
    setCompare(arr);
    refreshCompareChips();
  }

  function initCompareUI(){
    if(document.getElementById('asr-cmp-tray')) return;
    var tray = document.createElement('div');
    tray.id='asr-cmp-tray';
    tray.className='asr-cmp-tray';
    tray.setAttribute('role','region');
    tray.setAttribute('aria-label','Compare selected names');
    tray.innerHTML = '<div class="asr-cmp-summary"></div><button type="button" class="asr-cmp-go">Compare</button><button type="button" class="asr-cmp-clear" aria-label="Clear comparison">×</button>';
    document.body.appendChild(tray);
    tray.querySelector('.asr-cmp-go').addEventListener('click', openCompareModal);
    tray.querySelector('.asr-cmp-clear').addEventListener('click', function(){ setCompare([]); refreshCompareChips(); });
    updateCompareTray();
  }

  function updateCompareTray(){
    var tray = document.getElementById('asr-cmp-tray');
    if(!tray) return;
    var arr = getCompare();
    tray.classList.toggle('show', arr.length>0);
    var s = tray.querySelector('.asr-cmp-summary');
    if(s) s.textContent = arr.length + ' selected';
    var go = tray.querySelector('.asr-cmp-go');
    if(go) go.disabled = arr.length<2;
  }

  function openCompareModal(){
    var arr = getCompare();
    if(arr.length<2) return;
    var rows = [
      {label:'Meaning', key:'meaning'},
      {label:'Gender', key:'gender'},
      {label:'Region', key:'region'}
    ];
    var html = '<div class="asr-cmp-grid"><div class="asr-cmp-col asr-cmp-labels"><div></div>'+
      rows.map(function(r){return '<div class="asr-cmp-label">'+r.label+'</div>';}).join('')+
      '</div>';
    arr.forEach(function(e){
      html += '<div class="asr-cmp-col">'+
              '<div class="asr-cmp-name"><a href="/names/'+e.slug+'/">'+esc(e.name)+'</a></div>'+
              rows.map(function(r){
                var v = (e[r.key]||'').toString().trim();
                if(r.key==='gender') v = v ? (v.charAt(0).toUpperCase()+v.slice(1)) : '—';
                if(!v) v='—';
                return '<div class="asr-cmp-val">'+esc(v)+'</div>';
              }).join('')+
              '</div>';
    });
    html += '</div>';
    openModal('Compare Names', html, 'asr-modal-compare');
  }

  // ---- Modal helpers ----
  function esc(s){ return (s||'').toString().replace(/[<>"']/g, function(c){return {'<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];}); }

  function openModal(title, bodyHtml, extraClass){
    closeModal();
    var ov = document.createElement('div');
    ov.className = 'asr-modal-overlay '+(extraClass||'');
    ov.innerHTML = '<div class="asr-modal" role="dialog" aria-modal="true" aria-label="'+esc(title)+'">'+
      '<div class="asr-modal-head"><h2>'+esc(title)+'</h2><button type="button" class="asr-modal-close" aria-label="Close">×</button></div>'+
      '<div class="asr-modal-body">'+bodyHtml+'</div></div>';
    document.body.appendChild(ov);
    document.body.classList.add('asr-modal-open');
    ov.addEventListener('click', function(e){ if(e.target===ov) closeModal(); });
    ov.querySelector('.asr-modal-close').addEventListener('click', closeModal);
    document.addEventListener('keydown', escClose);
    requestAnimationFrame(function(){ ov.classList.add('show'); });
  }
  function escClose(e){ if(e.key==='Escape') closeModal(); }
  function closeModal(){
    var ov = document.querySelector('.asr-modal-overlay');
    if(!ov) return;
    document.removeEventListener('keydown', escClose);
    ov.classList.remove('show');
    document.body.classList.remove('asr-modal-open');
    setTimeout(function(){ if(ov && ov.parentNode) ov.parentNode.removeChild(ov); }, 180);
  }

  function openListModal(kind){
    var arr = (kind==='favorites') ? getFavs() : getRecent();
    var title = (kind==='favorites') ? 'My Favorites' : 'Recently Viewed';
    var body = '';
    if(!arr.length){
      body = '<p class="asr-empty">No '+title.toLowerCase()+' yet. Browse names and tap the heart on any page to save.</p>';
    } else {
      body = '<div class="asr-modal-list">' + arr.map(function(e){
        return '<a href="/names/'+e.slug+'/" class="asr-modal-item">'+
          '<span class="asr-modal-item-name">'+esc(e.name||e.slug)+'</span>'+
          (e.meaning?'<span class="asr-modal-item-meaning">'+esc(e.meaning)+'</span>':'')+
        '</a>';
      }).join('') + '</div>';
      if(kind==='favorites'){
        body += '<button type="button" class="asr-modal-clear" data-kind="favorites">Clear all favorites</button>';
      }
    }
    openModal(title, body);
    var clear = document.querySelector('.asr-modal-clear');
    if(clear){ clear.addEventListener('click', function(){
      if(confirm('Remove all favorites?')){ setFavs([]); closeModal(); }
    }); }
  }

  // ---- Cmd-K global search ----
  var CMDK_CORPUS = null;
  var CMDK_LOADING = false;

  // C9 — fast tiered search: O(log n) prefix index + linear substring + lazy Levenshtein.
  // CMDK_CORPUS is an array of entries: {h,n,m,g,a,u,r,v,nl}
  //   nl = name lowercased (cached)
  // CMDK_TOKENS is a flat alphabetised array of {t,i} where t is a lowercased
  //   search-token (canonical name or variant spelling) and i is its index into
  //   CMDK_CORPUS — enabling binary-search prefix lookups across all spellings.
  var CMDK_TOKENS = null;
  function fetchCorpus(){
    if(CMDK_CORPUS) return Promise.resolve(CMDK_CORPUS);
    if(CMDK_LOADING) return new Promise(function(res){ var t=setInterval(function(){ if(CMDK_CORPUS || !CMDK_LOADING){ clearInterval(t); res(CMDK_CORPUS || []); } }, 30); });
    CMDK_LOADING = true;
    return fetch('/names/names-index.json', {cache:'force-cache'}).then(function(r){
      if(!r.ok) throw new Error('idx http '+r.status);
      return r.json();
    }).then(function(arr){
      var out = [];
      for(var i=0;i<arr.length;i++){
        var e = arr[i];
        out.push({
          h: '/names/'+e.s+'/',
          n: e.n, m: e.m||'',
          g: e.g||'', a: e.a||'', u: e.u||'',
          r: e.r||[], v: e.v||[],
          s: e.s, nl: (e.n||'').toLowerCase(), sl: e.s.toLowerCase()
        });
      }
      // Token index now built by the shared matcher (script-aware: Latin +
      // normalized Arabic/Urdu spellings). See /asr-matcher.js → buildTokenIndex.
      CMDK_TOKENS = (window.ASR_MATCHER && window.ASR_MATCHER.buildTokenIndex)
        ? window.ASR_MATCHER.buildTokenIndex(out)
        : [];
      CMDK_CORPUS = out;
      CMDK_LOADING = false;
      return CMDK_CORPUS;
    }).catch(function(err){
      CMDK_LOADING=false;
      // Fallback: scrape /names/ index as before (defensive).
      return fetch('/names/').then(function(r){ return r.text(); }).then(function(html){
        var doc = new DOMParser().parseFromString(html,'text/html');
        var out = [];
        doc.querySelectorAll('.name-card').forEach(function(a){
          var href=a.getAttribute('href')||'';
          var name=a.querySelector('.name-english');
          var meaning=a.querySelector('.name-meaning');
          if(!href||!name) return;
          out.push({h:href, n:name.textContent.trim(), nl:name.textContent.trim().toLowerCase(), m:(meaning?meaning.textContent.trim():''), v:[]});
        });
        var seen={}; var unique=[];
        out.forEach(function(e){ if(!seen[e.h]){ seen[e.h]=1; unique.push(e); } });
        CMDK_TOKENS = unique.map(function(e,i){ return {t:e.nl, i:i}; }).sort(function(a,b){return a.t<b.t?-1:a.t>b.t?1:0;});
        CMDK_CORPUS = unique;
        return CMDK_CORPUS;
      }).catch(function(){ CMDK_LOADING=false; CMDK_CORPUS = CMDK_CORPUS || []; return CMDK_CORPUS; });
    });
  }

  // Binary-search the first token whose lowercase string is >= q.
  function _lowerBound(arr, q){
    var lo=0, hi=arr.length;
    while(lo<hi){
      var mid=(lo+hi)>>>1;
      if(arr[mid].t < q) lo=mid+1; else hi=mid;
    }
    return lo;
  }
  // tieredSearch — thin adapter over the shared runSearch pipeline. Returns
  // the legacy shape {e, tier, dist, tok, mode} so existing callers (cmdk,
  // home hero) keep working without changes. mode is added: 'list'|'cta'|'empty'.
  function tieredSearch(q, MAX){
    MAX = MAX || 10;
    if(!CMDK_TOKENS || !q || !window.ASR_MATCHER || !window.ASR_MATCHER.runSearch) return [];
    var res = window.ASR_MATCHER.runSearch(CMDK_CORPUS, CMDK_TOKENS, q, {max: MAX, singleCharCap: 8});
    if(!res || res.mode !== 'list') return [];
    return res.results.map(function(r){
      var dist = window.ASR_MATCHER.levDist(r.score);
      return {e:r.e, tier:r.tier, dist:dist, tok:r.tok, _score:r.score, isCluster:!!r.isCluster};
    });
  }
  // Public for callers that need the {mode} hint (CTA gating).
  function tieredSearchFull(q, MAX){
    MAX = MAX || 10;
    if(!CMDK_TOKENS || !q || !window.ASR_MATCHER || !window.ASR_MATCHER.runSearch){
      return {q: q, mode: 'empty', results: []};
    }
    return window.ASR_MATCHER.runSearch(CMDK_CORPUS, CMDK_TOKENS, q, {max: MAX, singleCharCap: 8});
  }

  // fuzzyMatch is a thin adapter over ASR_MATCHER.score. It returns a higher-is-better
  // 0–100 score for legacy callers (see asr-region.js, hero search). 0 means no match.
  function fuzzyMatch(q, s){
    if(!window.ASR_MATCHER) return 0;
    var sc = window.ASR_MATCHER.score(s.toLowerCase(), q.toLowerCase());
    if(sc >= 999) return 0;
    if(sc === -1) return 100;
    if(sc === 0) return 90;
    if(sc === 1) return 70;
    if(sc === 2) return 60;
    if(sc <= 6) return 55 - (sc - 3) * 4;   // prefix-Lev: 55,51,47,43
    return 48 - (sc - 7) * 4;                // whole-Lev:  48,44,40
  }

  function cmdkReaderCta(q, focusable){
    if(!q) return '';
    var qsafe = esc(q);
    var qenc = encodeURIComponent(q);
    var optAttrs = focusable
      ? ' id="asr-cmdk-o0" role="option" aria-selected="true"'
      : ' role="option" aria-selected="false"';
    return '<a class="asr-cmdk-item asr-cmdk-reader-cta'+(focusable?' active':'')+'"'+optAttrs+' href="/reader/?name=' + qenc + '" style="background:rgba(139,105,20,.06);border-top:1px dashed rgba(139,105,20,.3);">' +
      '<span class="asr-cmdk-name" style="font-style:italic">↻ Generate a reading for "' + qsafe + '"</span>' +
      '<span class="asr-cmdk-meaning">Read it letter by letter — even if not in the library yet.</span>' +
    '</a>';
  }

  // mode: 'list' | 'cta' | 'empty'. CTA is rendered only when mode='cta' —
  // when actual matches exist, CTA is suppressed (defect E).
  function cmdkRender(items, listEl, q, mode){
    if(mode === 'cta' || (!items.length && q)){
      listEl.innerHTML = '<div class="asr-cmdk-empty">No exact matches for "'+esc(q)+'" in our verified library.</div>' + cmdkReaderCta(q, true);
      return;
    }
    if(!items.length){ listEl.innerHTML = ''; return; }
    listEl.innerHTML = items.slice(0, 10).map(function(e, i){
      var clusterBadge = e.__cluster ? '<span class="asr-cmdk-badge" style="display:inline-block;margin-left:.45rem;padding:.05rem .45rem;border:1px solid rgba(139,105,20,0.3);border-radius:8px;font-size:.65rem;letter-spacing:.08em;text-transform:uppercase;color:#8B6914;">also spelt</span>' : '';
      return '<a class="asr-cmdk-item'+(i===0?' active':'')+'" id="asr-cmdk-o'+i+'" role="option" aria-selected="'+(i===0?'true':'false')+'" href="'+e.h+'" data-i="'+i+'">'+
        '<span class="asr-cmdk-name">'+esc(e.n)+'</span>'+clusterBadge+
        (e.m?'<span class="asr-cmdk-meaning">'+esc(e.m)+'</span>':'')+
      '</a>';
    }).join('');
  }

  function openCmdk(){
    if(document.querySelector('.asr-cmdk-overlay')) return;
    var ov = document.createElement('div');
    ov.className = 'asr-cmdk-overlay';
    ov.innerHTML = '<div class="asr-cmdk" role="dialog" aria-label="Quick search">'+
      '<div class="asr-cmdk-head">'+
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>'+
      '<input type="search" class="asr-cmdk-input" role="combobox" aria-autocomplete="list" aria-controls="asr-cmdk-listbox" aria-expanded="true" placeholder="Search names…" aria-label="Quick search" autocomplete="off" autofocus>'+
      '<kbd>Esc</kbd>'+
      '</div>'+
      '<div class="asr-cmdk-list" id="asr-cmdk-listbox" role="listbox" aria-label="Search results"><div class="asr-cmdk-loading"><div class="asr-skel"></div><div class="asr-skel"></div><div class="asr-skel"></div></div></div>'+
      '</div>';
    document.body.appendChild(ov);
    document.body.classList.add('asr-modal-open');
    requestAnimationFrame(function(){ ov.classList.add('show'); });
    var input = ov.querySelector('.asr-cmdk-input');
    var listEl = ov.querySelector('.asr-cmdk-list');
    var active = 0;
    var lastResults = [];

    function close(){
      ov.classList.remove('show');
      document.body.classList.remove('asr-modal-open');
      setTimeout(function(){ if(ov.parentNode) ov.parentNode.removeChild(ov); }, 180);
      document.removeEventListener('keydown', kdGlobal);
    }
    function kdGlobal(e){ if(e.key==='Escape') close(); }
    document.addEventListener('keydown', kdGlobal);
    ov.addEventListener('click', function(e){ if(e.target===ov) close(); });

    function doSearch(q){
      var raw = (q||'').trim();
      if(!raw){
        listEl.innerHTML = '<div class="asr-cmdk-hint">Type to search names, meanings, or letters.</div>' +
          '<button type="button" class="asr-cmdk-random" id="asrCmdkRandom">↻ &nbsp;Try a random name</button>';
        var rb = listEl.querySelector('#asrCmdkRandom');
        if(rb) rb.addEventListener('click', function(){
          fetchCorpus().then(function(arr){
            if(!arr || !arr.length) return;
            var pick = arr[Math.floor(Math.random()*arr.length)];
            location.href = (pick.h || ('/names/'+pick.s+'/'));
          });
        });
        lastResults=[]; input.removeAttribute('aria-activedescendant'); return;
      }
      if(!CMDK_CORPUS){ return; }
      var full = tieredSearchFull(raw, 10);
      if(full.mode === 'list'){
        var items = full.results.map(function(r){
          var e = r.e;
          // Build the lightweight entry the legacy renderer expects.
          return {h: '/names/'+e.s+'/', n: e.n, m: e.m||'', s: e.s, __cluster: !!r.isCluster};
        });
        lastResults = items;
        active = 0;
        cmdkRender(items, listEl, raw, 'list');
      } else {
        // mode === 'cta' or 'empty'
        lastResults = [];
        active = 0;
        cmdkRender([], listEl, raw, 'cta');
      }
      // Wire aria-activedescendant to the first option (if any).
      var firstOpt = listEl.querySelector('.asr-cmdk-item');
      if(firstOpt){
        if(!firstOpt.id) firstOpt.id = 'asr-cmdk-o0';
        input.setAttribute('aria-activedescendant', firstOpt.id);
      } else {
        input.removeAttribute('aria-activedescendant');
      }
    }

    fetchCorpus().then(function(){ doSearch(input.value); });

    var t;
    input.addEventListener('input', function(){
      clearTimeout(t);
      t = setTimeout(function(){ doSearch(input.value); }, 30);
    });
    input.addEventListener('keydown', function(e){
      var items = listEl.querySelectorAll('.asr-cmdk-item');
      if(e.key==='ArrowDown'){ e.preventDefault(); active = Math.min(items.length-1, active+1); refreshActive(); }
      else if(e.key==='ArrowUp'){ e.preventDefault(); active = Math.max(0, active-1); refreshActive(); }
      else if(e.key==='Enter'){
        if(items[active]){ e.preventDefault(); window.location.href = items[active].getAttribute('href'); }
      }
    });
    function refreshActive(){
      var items = listEl.querySelectorAll('.asr-cmdk-item');
      items.forEach(function(el,i){
        var on = (i===active);
        el.classList.toggle('active', on);
        el.setAttribute('aria-selected', on?'true':'false');
        if(on){
          if(!el.id) el.id = 'asr-cmdk-o'+i;
          input.setAttribute('aria-activedescendant', el.id);
        }
      });
      if(items[active] && items[active].scrollIntoView) items[active].scrollIntoView({block:'nearest'});
    }
  }

  // ---- Global Cmd-K shortcut ----
  function bindCmdkShortcut(){
    document.addEventListener('keydown', function(e){
      var isMac = /Mac|iPhone|iPad/.test((navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || navigator.userAgent);
      var trigger = ( (isMac && e.metaKey) || (!isMac && e.ctrlKey) ) && (e.key==='k' || e.key==='K');
      if(trigger){
        // don't hijack inside other inputs unless it's our input
        e.preventDefault();
        if(document.querySelector('.asr-cmdk-overlay')) return;
        openCmdk();
      }
    });
  }

  // ---- Animation: fade-in DISABLED (was causing invisible text on mobile
  //      when IntersectionObserver didn't fire reliably). Kept as no-op so
  //      the rest of the init chain doesn't need to change. ----
  function bindFadeIn(){ /* intentionally disabled — see asr-enhance.css */ }

  // ---- Random discovery: pick from rich canonicals on name pages ----
  function injectReadAnother(){
    var ctx = pageContext();
    if(!ctx.slug) return;
    if(document.querySelector('.asr-read-another')) return;
    // Insert after the main reading content. Prefer LIFE:END marker, else end of main.
    var anchor = null;
    var anchorAfter = null;
    var walker = document.createNodeIterator(document.body, NodeFilter.SHOW_COMMENT, null, false);
    var c;
    while((c = walker.nextNode())){
      if(c.nodeValue){
        if(c.nodeValue.indexOf('LETTERCLUSTER:END')>=0){ anchorAfter = c; }
        else if(c.nodeValue.indexOf('LIFE:END')>=0 && !anchor){ anchor = c; }
      }
    }
    if(anchorAfter) anchor = anchorAfter;
    var wrap = document.createElement('section');
    wrap.className = 'asr-read-another';
    wrap.setAttribute('aria-label','Discover another name');
    wrap.innerHTML =
      '<div class="ra-inner">' +
        '<span class="ra-eyebrow">More from the library</span>' +
        '<h3 class="ra-title">Read another <em>name</em></h3>' +
        '<p class="ra-sub">A different name from the same tradition — chosen at random.</p>' +
        '<a href="#" class="ra-cta" id="asrReadAnother" data-loading="Loading…">' +
          '<span class="ra-cta-label">Read another →</span>' +
          '<span class="ra-cta-name" hidden></span>' +
        '</a>' +
        '<p class="ra-reader-link" style="margin-top:1.2rem;font-size:.88rem;color:rgba(245,239,227,.65);font-style:italic;line-height:1.55;">' +
          'Or — <a href="/reader/" style="color:#d4b86a;border-bottom:1px dotted rgba(212,184,106,.5);text-decoration:none;font-style:normal;">generate a fresh reading for any name →</a> using our letter-based tool, even one not yet in the library.' +
        '</p>' +
      '</div>';
    if(anchor && anchor.parentNode){
      // Insert just after the comment node
      anchor.parentNode.insertBefore(wrap, anchor.nextSibling);
    } else {
      var main = document.querySelector('main, .content, body');
      (main || document.body).appendChild(wrap);
    }

    // Pick once at pageload, deterministic for this view but varies per load.
    var cta = wrap.querySelector('#asrReadAnother');
    var label = wrap.querySelector('.ra-cta-label');
    var pickedHref = null;
    function setPicked(pick){
      pickedHref = '/names/' + pick.s + '/';
      cta.setAttribute('href', pickedHref);
      label.textContent = 'Read ' + pick.n + ' →';
    }
    fetchCorpus().then(function(arr){
      if(!arr || !arr.length) return;
      // Filter out the current slug.
      var pool = arr;
      if(arr[0] && arr[0].s !== undefined){
        pool = arr.filter(function(e){ return e.s !== ctx.slug; });
      } else {
        pool = arr.filter(function(e){ return (e.h||'').indexOf('/names/'+ctx.slug+'/')<0; });
      }
      if(!pool.length) return;
      var pick = pool[Math.floor(Math.random()*pool.length)];
      // Normalise — fetchCorpus output has .s and .n
      if(pick.s && pick.n){ setPicked(pick); }
    });
    // If clicked before the index resolves, fall back to the random homepage flow.
    cta.addEventListener('click', function(e){
      if(!pickedHref){
        e.preventDefault();
        label.textContent = 'Picking…';
        fetchCorpus().then(function(arr){
          if(!arr || !arr.length) return;
          var pool = arr.filter(function(en){ return en.s !== ctx.slug; });
          var pick = pool[Math.floor(Math.random()*pool.length)];
          location.href = '/names/' + pick.s + '/';
        });
      }
    });
  }

    // ---- Skip link (existing) ----
  function injectSkipLink(){
    if(document.querySelector('.asr-skip-link')) return;
    var main = document.querySelector('main, .content, .hero, #content');
    var targetId = (main && main.id) ? main.id : 'main-content';
    if(main && !main.id) main.id = targetId;
    if(main){
      var skip = document.createElement('a');
      skip.className = 'asr-skip-link';
      skip.href = '#' + targetId;
      skip.textContent = 'Skip to main content';
      document.body.insertBefore(skip, document.body.firstChild);
    }
  }

  // ---- Boot ----
  // ---- Static "Read another" CTAs: upgrade href + label with a random pick ----
  function enhanceStaticReadAnother(){
    var anchors = document.querySelectorAll('a[data-asr-ra]');
    if(!anchors.length) return;
    var ctx = pageContext();
    var picked = null;
    function apply(pick){
      picked = pick;
      anchors.forEach(function(a){
        a.setAttribute('href', '/names/' + pick.s + '/');
        var label = a.querySelector('.asr-ra-hero-label, .asr-ra-inline-label');
        if(label){
          if(a.getAttribute('data-asr-ra') === 'hero'){
            label.textContent = 'Or read ' + pick.n;
          } else {
            label.textContent = 'Read ' + pick.n + ' →';
          }
        }
      });
    }
    fetchCorpus().then(function(arr){
      if(!arr || !arr.length) return;
      var pool = arr.filter(function(e){ return e.s !== ctx.slug; });
      if(!pool.length) return;
      apply(pool[Math.floor(Math.random()*pool.length)]);
    });
    anchors.forEach(function(a){
      a.addEventListener('click', function(e){
        if(picked) return;
        e.preventDefault();
        fetchCorpus().then(function(arr){
          if(!arr || !arr.length){ location.href = '/names/'; return; }
          var pool = arr.filter(function(en){ return en.s !== ctx.slug; });
          var pick = pool[Math.floor(Math.random()*pool.length)];
          location.href = '/names/' + pick.s + '/';
        });
      });
    });
  }


  // Prefix-overlap and canonical-aware rerank — refines tieredSearch ranking
  // so the canonical that's *closest to the canonical name itself* (not just
  // to a registered variant) wins ties. Critical to keep e.g. "muhamad" →
  // /names/muhammad/ instead of a phonetically-similar-but-rarer canonical.
  function _prefixOverlap(a, b){
    var n = Math.min(a.length, b.length);
    for(var i=0; i<n; i++){ if(a.charCodeAt(i) !== b.charCodeAt(i)) return i; }
    return n;
  }
  function rerankByCanonical(results, q){
    for(var i=0; i<results.length; i++){
      var r = results[i];
      r.canonDist = window.ASR_MATCHER.lev(q, r.e.nl, 3);
      r.po = _prefixOverlap(q, r.e.nl);
    }
    results.sort(function(a, b){
      if(a.tier !== b.tier) return a.tier - b.tier;
      if(a.canonDist !== b.canonDist) return a.canonDist - b.canonDist;
      if(a.dist !== b.dist) return a.dist - b.dist;
      if(a.po !== b.po) return b.po - a.po;
      if(a.e.nl.length !== b.e.nl.length) return a.e.nl.length - b.e.nl.length;
      return a.e.nl < b.e.nl ? -1 : (a.e.nl > b.e.nl ? 1 : 0);
    });
    return results;
  }

  // ---- Homepage hero search: live corpus suggestions ----
  // Reuses fetchCorpus(), tieredSearch(), esc() above. Renders a dropdown below
  // the homepage hero input (#hero-search-input) with name (Cinzel) + Arabic script
  // (small) + one-line meaning. Click → /names/<slug>/. Enter / button-click:
  //   1. exact slug or canonical-name match  → /names/<slug>/
  //   2. top fuzzy hit with dist ≤ 2          → that canonical
  //   3. otherwise                            → /reader/?name=<encoded>
  // No matches in dropdown (best dist > 3) → only the fallback "Generate a
  // reading for X →" CTA is shown.
  function shortMeaning(m, name){
    if(!m) return '';
    var s = String(m).trim();
    var nameLower = String(name||'').trim().toLowerCase();
    // Strip leading "Name —" prefix if present
    var firstDash = s.indexOf('—');
    if(firstDash > -1){
      var prefix = s.slice(0, firstDash).trim().toLowerCase();
      if(prefix && prefix === nameLower){ s = s.slice(firstDash+1).trim(); }
    }
    // Cut to second em-dash if short enough — gives the "short meaning"
    var nextDash = s.indexOf('—');
    if(nextDash > 0 && nextDash <= 110){
      return s.slice(0, nextDash).trim();
    }
    // Else first sentence
    var dot = s.search(/[.!?]/);
    if(dot > 0 && dot <= 140) return s.slice(0, dot).trim();
    return s.length > 140 ? s.slice(0, 137).trim() + '…' : s;
  }

  function initHeroSearch(){
    var input = document.getElementById('hero-search-input');
    if(!input) return;
    var btn = document.querySelector('.hero-search-btn');
    var row = input.parentNode;
    if(!row) return;
    row.style.position = 'relative';

    // Inject styles (scoped to #asr-hero-dd) — mirrors /names/ dropdown look.
    if(!document.getElementById('asr-hero-dd-style')){
      var st = document.createElement('style');
      st.id = 'asr-hero-dd-style';
      st.textContent = [
        '#asr-hero-dd{position:absolute;top:100%;left:0;right:0;background:#fff;border:1px solid rgba(139,105,20,0.25);border-top:none;border-radius:0 0 6px 6px;box-shadow:0 12px 28px rgba(0,0,0,0.14);max-height:380px;overflow-y:auto;z-index:9999;display:none;margin-top:0;text-align:left;}',
        '#asr-hero-dd .ahero-item{display:block;padding:.75rem 1rem;color:#2C2C2C;text-decoration:none;border-bottom:1px solid rgba(139,105,20,0.10);cursor:pointer;}',
        '#asr-hero-dd .ahero-item:last-child{border-bottom:none;}',
        '#asr-hero-dd .ahero-item:hover,#asr-hero-dd .ahero-item.ahero-active{background:rgba(139,105,20,0.07);}',
        '#asr-hero-dd .ahero-name{font-family:"Cinzel",serif;font-size:1rem;font-weight:500;color:#111010;text-transform:capitalize;letter-spacing:.01em;}',
        '#asr-hero-dd .ahero-ar{display:inline-block;margin-left:.55rem;font-family:"Amiri",serif;font-size:.95rem;color:#8B6914;vertical-align:baseline;}',
        '#asr-hero-dd .ahero-meaning{display:block;margin-top:.2rem;font-size:.82rem;color:#5A5A5A;font-style:italic;line-height:1.45;}',
        '#asr-hero-dd .ahero-cta{display:block;padding:.85rem 1rem;background:rgba(139,105,20,0.07);border-top:1px dashed rgba(139,105,20,0.35);color:#8B6914;text-decoration:none;cursor:pointer;}',
        '#asr-hero-dd .ahero-cta:hover,#asr-hero-dd .ahero-cta.ahero-active{background:rgba(139,105,20,0.14);}',
        '#asr-hero-dd .ahero-cta strong{display:block;font-family:"Cinzel",serif;font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;color:#8B6914;margin-bottom:.25rem;font-weight:600;}',
        '#asr-hero-dd .ahero-cta strong span{font-style:italic;text-transform:capitalize;letter-spacing:.02em;}',
        '#asr-hero-dd .ahero-cta-sub{display:block;font-size:.8rem;color:#6B6B6B;font-style:italic;line-height:1.45;}',
        '@media(max-width:560px){#asr-hero-dd{position:fixed;top:auto;bottom:20px;left:12px;right:12px;max-height:min(60vh,420px);border-radius:6px;border:1px solid rgba(139,105,20,0.25);box-shadow:0 20px 48px rgba(0,0,0,0.28);z-index:9999;} }',
        '@media(prefers-color-scheme:dark){#asr-hero-dd{background:#1f1f1f;border-color:#3a3a3a;}#asr-hero-dd .ahero-item{border-color:#3a3a3a;color:#e8e2d4;}#asr-hero-dd .ahero-item:hover,#asr-hero-dd .ahero-item.ahero-active{background:#2a2a2a;}#asr-hero-dd .ahero-name{color:#f5efe3;}#asr-hero-dd .ahero-ar{color:#d4b86a;}#asr-hero-dd .ahero-meaning{color:#b6b0a2;}#asr-hero-dd .ahero-cta{background:rgba(212,184,106,.08);color:#d4b86a;border-color:rgba(212,184,106,.35);}#asr-hero-dd .ahero-cta strong{color:#d4b86a;}#asr-hero-dd .ahero-cta-sub{color:#b6b0a2;}}'
      ].join('\n');
      document.head.appendChild(st);
    }

    var dd = document.createElement('div');
    dd.id = 'asr-hero-dd';
    dd.setAttribute('role','listbox');
    row.appendChild(dd);

    var active = -1;
    var lastItems = [];

    // Add ARIA wiring on input
    input.setAttribute('role','combobox');
    input.setAttribute('aria-autocomplete','list');
    input.setAttribute('aria-controls','asr-hero-dd');
    input.setAttribute('aria-expanded','false');

    function ctaRow(q, focusable){
      var safeQ = esc(q || '');
      var enc = encodeURIComponent(q || '');
      var optAttrs = focusable
        ? ' id="ahero-o0" role="option" aria-selected="true"'
        : ' role="option" aria-selected="false"';
      return '<a class="ahero-cta'+(focusable?' ahero-active':'')+'"'+optAttrs+' href="/reader/?name=' + enc + '" data-cta="1">' +
        '<strong>Generate a reading for "<span>' + safeQ + '</span>" →</strong>' +
        '<span class="ahero-cta-sub">Not in our verified library yet — read it letter by letter with our Ilm ul Huroof tool.</span>' +
      '</a>';
    }

    function render(items, q, mode){
      lastItems = items;
      active = -1;
      input.setAttribute('aria-expanded','true');
      if(mode === 'cta' || (!items.length && q)){
        // Only show CTA when no real matches exist.
        dd.innerHTML = ctaRow(q, true);
        dd.style.display = 'block';
        try {
          var ddRectC = dd.getBoundingClientRect();
          var vhC = window.innerHeight || document.documentElement.clientHeight;
          if(ddRectC.bottom > vhC - 12){
            window.scrollBy({top: ddRectC.bottom - (vhC - 20), behavior: 'smooth'});
          }
        } catch(e) {}
        var ctaEl = dd.querySelector('.ahero-cta');
        if(ctaEl){ input.setAttribute('aria-activedescendant', ctaEl.id || 'ahero-o0'); }
        return;
      }
      if(!items.length){ dd.style.display = 'none'; input.setAttribute('aria-expanded','false'); return; }
      var html = items.slice(0, 10).map(function(r, i){
        var e = r.e || r;
        var label = (e.n || e.s || '').replace(/-/g,' ');
        var arabic = e.a ? '<span class="ahero-ar" lang="ar" dir="rtl">' + esc(e.a) + '</span>' : '';
        var meaning = shortMeaning(e.m, e.n);
        var meanHtml = meaning ? '<span class="ahero-meaning">' + esc(meaning) + '</span>' : '';
        var clusterBadge = (r && r.isCluster) ? '<span class="ahero-badge" style="display:inline-block;margin-left:.45rem;padding:.05rem .45rem;border:1px solid rgba(139,105,20,0.3);border-radius:8px;font-size:.65rem;letter-spacing:.08em;text-transform:uppercase;color:#8B6914;font-style:normal;vertical-align:middle;">also spelt</span>' : '';
        return '<a class="ahero-item" id="ahero-o' + i + '" role="option" aria-selected="false" href="/names/' + encodeURIComponent(e.s) + '/" data-i="' + i + '">' +
          '<span class="ahero-name">' + esc(label) + '</span>' + arabic + clusterBadge + meanHtml +
        '</a>';
      }).join('');
      dd.innerHTML = html;
      dd.style.display = 'block';
      // Compute anchor for dynamic max-height & scroll into view if cut off
      try {
        var inputRect = input.getBoundingClientRect();
        var anchorPx = Math.round(inputRect.bottom + window.scrollY - window.scrollY);
        dd.style.setProperty('--asr-dd-anchor', anchorPx + 'px');
        var ddRect = dd.getBoundingClientRect();
        var vh = window.innerHeight || document.documentElement.clientHeight;
        // If dropdown extends below the viewport, scroll to bring it into view
        if(ddRect.bottom > vh - 12){
          var scrollBy = Math.min(ddRect.bottom - (vh - 20), inputRect.top - 12);
          window.scrollBy({top: scrollBy, behavior: 'smooth'});
        }
      } catch(e) {}
    }

    function setActive(i){
      var els = dd.querySelectorAll('.ahero-item, .ahero-cta');
      if(!els.length){ active = -1; input.removeAttribute('aria-activedescendant'); return; }
      if(i < 0) i = 0;
      if(i >= els.length) i = els.length - 1;
      els.forEach(function(el, idx){
        if(idx === i){
          el.classList.add('ahero-active');
          el.setAttribute('aria-selected','true');
        } else {
          el.classList.remove('ahero-active');
          el.setAttribute('aria-selected','false');
        }
      });
      active = i;
      var sel = els[i];
      if(sel){
        if(!sel.id) sel.id = 'ahero-o'+i;
        input.setAttribute('aria-activedescendant', sel.id);
        if(sel.scrollIntoView) sel.scrollIntoView({block:'nearest'});
      }
    }

    function searchAndRender(v){
      var q = (v || '').trim();
      if(!q || q.length < 1){ dd.style.display = 'none'; input.setAttribute('aria-expanded','false'); return; }
      // Latin single-char: only run if user gives 1 char that the matcher will
      // serve (cap 8). Arabic single-char also valid.
      fetchCorpus().then(function(){
        var res = tieredSearchFull(v, 10);
        if(res.mode === 'list'){
          render(res.results, v, 'list');
        } else if(res.mode === 'cta'){
          render([], v, 'cta');
        } else {
          dd.style.display = 'none';
          input.setAttribute('aria-expanded','false');
        }
      });
    }

    var dt;
    input.addEventListener('input', function(){
      clearTimeout(dt);
      var v = input.value;
      dt = setTimeout(function(){ searchAndRender(v); }, 60);
    });

    input.addEventListener('keydown', function(e){
      var els = dd.querySelectorAll('.ahero-item, .ahero-cta');
      var open = (dd.style.display !== 'none') && els.length > 0;
      if(e.key === 'ArrowDown' && open){ e.preventDefault(); setActive(Math.min(active + 1, els.length - 1)); }
      else if(e.key === 'ArrowUp' && open){ e.preventDefault(); setActive(Math.max(active - 1, 0)); }
      else if(e.key === 'Enter'){
        e.preventDefault();
        if(open && active >= 0 && els[active]){
          window.location.href = els[active].getAttribute('href');
        } else {
          heroSubmit();
        }
      } else if(e.key === 'Escape'){
        dd.style.display = 'none';
      }
    });

    input.addEventListener('focus', function(){
      fetchCorpus(); // warm cache
      if(input.value && input.value.length >= 2) searchAndRender(input.value);
    });
    input.addEventListener('blur', function(){
      setTimeout(function(){ dd.style.display = 'none'; }, 200);
    });
    document.addEventListener('click', function(e){
      if(e.target === input || dd.contains(e.target)) return;
      dd.style.display = 'none';
    });

    function heroSubmit(){
      var v = (input.value || '').trim();
      if(!v) return;
      var q = v.toLowerCase().trim();
      // Slugify: spaces/underscores → hyphens; drop other non-alnum.
      var slug = q.replace(/[\s_]+/g, '-').replace(/[^a-z0-9-]/g, '').replace(/^-+|-+$/g, '');

      function route(){
        if(CMDK_CORPUS && CMDK_CORPUS.length){
          // 1. exact canonical slug or canonical lowercase name (fast path)
          for(var i = 0; i < CMDK_CORPUS.length; i++){
            var e = CMDK_CORPUS[i];
            if(e.s === slug || e.nl === q){
              window.location.href = '/names/' + e.s + '/';
              return;
            }
          }
          // 2. shared pipeline. mode='list' means the matcher accepted a hit
          //    under its strict-tier rules (canonical Lev<=maxLev for fuzzy);
          //    we route to the top result. mode='cta' means no hit worth
          //    routing — fall to /reader/.
          var res = tieredSearchFull(v, 5);
          if(res.mode === 'list' && res.results.length){
            window.location.href = '/names/' + res.results[0].e.s + '/';
            return;
          }
        }
        // 3. fallback — dynamic /reader/ tool
        window.location.href = '/reader/?name=' + encodeURIComponent(v);
      }

      if(CMDK_CORPUS){ route(); }
      else { fetchCorpus().then(route); }
    }

    // Override legacy heroRead() (defined inline in index.html) so the
    // existing onclick/onkeydown handlers route through the new logic too.
    window.heroRead = heroSubmit;

    // Defensive: also bind the button click directly in case the inline
    // onclick has been removed by a future markup change.
    if(btn){
      btn.addEventListener('click', function(e){
        e.preventDefault();
        heroSubmit();
      });
    }
  }

  function safeCall(fn, name){
    try{ fn(); }catch(err){
      if(window.console && console.warn) console.warn('AsrNaam init step failed:', name, err);
    }
  }
  function runAllInit(){
    safeCall(injectSkipLink,'injectSkipLink');
    safeCall(injectThemeToggle,'injectThemeToggle');
    safeCall(injectCmdkTrigger,'injectCmdkTrigger');
    safeCall(injectHeroActions,'injectHeroActions');
    safeCall(injectReadAnother,'injectReadAnother');
    safeCall(enhanceStaticReadAnother,'enhanceStaticReadAnother');
    safeCall(recordRecent,'recordRecent');
    safeCall(injectNamesIndexFeatures,'injectNamesIndexFeatures');
    safeCall(bindCmdkShortcut,'bindCmdkShortcut');
    safeCall(bindFadeIn,'bindFadeIn');
    safeCall(initHeroSearch,'initHeroSearch');
  }
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', runAllInit);
  } else {
    // Document already parsed. Run immediately.
    runAllInit();
  }
  // Defensive re-run: if any step earlier in the chain silently failed and
  // initHeroSearch never got to build the dropdown, retry on window.load.
  window.addEventListener('load', function(){
    if(!document.getElementById('asr-hero-dd') && document.getElementById('hero-search-input')){
      safeCall(initHeroSearch, 'initHeroSearch (late)');
    }
  });

  // Expose openers for any inline buttons (e.g. footer)
  window.AsrNaam = window.AsrNaam || {};
  window.AsrNaam.openFavorites = function(){ openListModal('favorites'); };
  window.AsrNaam.openRecent = function(){ openListModal('recent'); };
  window.AsrNaam.openCmdk = openCmdk;
})();

(function(){
  if(document.readyState!=='loading')run(); else document.addEventListener('DOMContentLoaded', run);
  function run(){

  // ---- Share Hero copy button (per-name pages) ----
  function bindShareHeroCopy(){
    var btns = document.querySelectorAll('.asr-share-btn.copy[data-url]');
    btns.forEach(function(btn){
      if(btn.__bound) return; btn.__bound = true;
      btn.addEventListener('click', async function(){
        var u = btn.getAttribute('data-url') || location.href;
        try{
          if(navigator.clipboard){ await navigator.clipboard.writeText(u); }
          else { var ta=document.createElement('textarea'); ta.value=u; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta); }
          var old = btn.innerHTML; btn.classList.add('copied'); btn.innerHTML = 'Copied!';
          setTimeout(function(){ btn.classList.remove('copied'); btn.innerHTML = old; }, 1100);
        }catch(e){}
      });
    });
  }
    bindShareHeroCopy();
  }
})();
