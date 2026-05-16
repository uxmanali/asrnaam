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
    if(CMDK_LOADING) return new Promise(function(res){ var t=setInterval(function(){ if(CMDK_CORPUS){ clearInterval(t); res(CMDK_CORPUS); } }, 30); });
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
      // Build alphabetised token array.
      var tokens = [];
      for(var k=0;k<out.length;k++){
        var ent = out[k];
        tokens.push({t: ent.nl, i: k});
        if(ent.sl && ent.sl !== ent.nl) tokens.push({t: ent.sl, i: k});
        var vs = ent.v;
        for(var j=0;j<vs.length;j++){
          var v = (vs[j]||'').toLowerCase().replace(/-/g,' ');
          if(v) tokens.push({t: v, i: k});
        }
      }
      tokens.sort(function(a,b){ return a.t<b.t?-1:a.t>b.t?1:0; });
      CMDK_TOKENS = tokens;
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
      }).catch(function(){ return []; });
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
  // Levenshtein with early termination at maxDist
  function _lev(a, b, maxDist){
    if(a===b) return 0;
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
  // Tiered search: prefix → substring → Levenshtein.
  // Returns up to MAX results, ranked:
  //   exact-prefix > shorter Levenshtein > shorter canonical name
  function tieredSearch(q, MAX){
    MAX = MAX || 10;
    if(!CMDK_TOKENS || !q) return [];
    var seen = Object.create(null);
    var results = [];

    function push(i, tier, dist, tok){
      if(seen[i]!==undefined) return;
      var e = CMDK_CORPUS[i];
      if(!e) return;
      seen[i] = results.length;
      results.push({e:e, tier:tier, dist:dist||0, tok:tok||e.nl});
    }

    // TIER 1 — exact-prefix via binary search.
    var idx = _lowerBound(CMDK_TOKENS, q);
    for(var k=idx; k<CMDK_TOKENS.length; k++){
      var t = CMDK_TOKENS[k];
      if(t.t.indexOf(q)!==0) break;
      push(t.i, 1, 0, t.t);
      if(results.length>=MAX) break;
    }

    // TIER 2 — substring linear scan (only if prefix hits <5).
    if(results.length<5){
      for(var p=0; p<CMDK_TOKENS.length; p++){
        var tt = CMDK_TOKENS[p];
        if(tt.t.indexOf(q)>=0){
          push(tt.i, 2, 0, tt.t);
          if(results.length>=MAX) break;
        }
      }
    }

    // TIER 3 — Levenshtein <=3, lazy across all length-compatible tokens.
    // We pre-filter by |len(tok) - len(q)| <= 3 (Levenshtein lower bound),
    // run _lev with early termination at maxDist=3, then keep the top 50
    // by smallest distance. Empirically: 6.8k tokens at 1-2µs each = ~10ms.
    if(results.length<5){
      var qlen = q.length;
      var lev = [];
      for(var p2=0; p2<CMDK_TOKENS.length; p2++){
        var tt2 = CMDK_TOKENS[p2];
        if(seen[tt2.i]!==undefined) continue;
        if(Math.abs(tt2.t.length - qlen) > 3) continue;
        var d = _lev(tt2.t, q, 3);
        if(d<=3) lev.push({i:tt2.i, d:d, t:tt2.t});
      }
      lev.sort(function(a,b){ return a.d-b.d; });
      // Top-50 nearest, distance-capped at 3.
      var limit = Math.min(lev.length, 50);
      for(var l=0; l<limit && results.length<MAX; l++){
        push(lev[l].i, 3, lev[l].d, lev[l].t);
      }
    }

    // Ranking: tier ascending, then distance, then canonical length.
    results.sort(function(a,b){
      if(a.tier!==b.tier) return a.tier-b.tier;
      if(a.dist!==b.dist) return a.dist-b.dist;
      if(a.e.nl.length!==b.e.nl.length) return a.e.nl.length-b.e.nl.length;
      return a.e.nl<b.e.nl?-1:a.e.nl>b.e.nl?1:0;
    });
    return results.slice(0, MAX);
  }

  // Levenshtein with early termination at maxDist (used by C6 fuzzyMatch)
  function _levCmdk(a, b, maxDist){
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
  function fuzzyMatch(q, s){
    s = s.toLowerCase(); q = q.toLowerCase();
    if(s===q) return 100;
    if(s.indexOf(q)===0) return 90;
    if(s.indexOf(q)>=0) return 70;
    // C6 — case-insensitive partial-word: a 3+ char head of q appears in s
    if(q.length>=3 && s.length>=3){
      for(var pl = Math.min(q.length, 6); pl>=3; pl--){
        if(s.indexOf(q.slice(0, pl))>=0) return 60 - (q.length - pl);
      }
    }
    // C6 — prefix Levenshtein <=3 (loosened): compare head-slice of s against q
    if(q.length>=3){
      var headLen = Math.min(s.length, q.length + 2);
      var head = s.slice(0, headLen);
      var dp = _levCmdk(head, q, 3);
      if(dp<=3) return 55 - dp*4;
    }
    // C6 — whole-token Levenshtein <=2 (substring fuzz)
    var dw = _levCmdk(s, q, 2);
    if(dw<=2) return 48 - dw*4;
    // simple subseq (kept as last-chance match)
    var i=0,j=0,gaps=0;
    while(i<s.length && j<q.length){
      if(s[i]===q[j]){ j++; }
      else if(j>0){ gaps++; }
      i++;
    }
    if(j===q.length) return 40 - Math.min(gaps,20);
    return 0;
  }

  function cmdkReaderCta(q){
    if(!q) return '';
    var qsafe = esc(q);
    var qenc = encodeURIComponent(q);
    return '<a class="asr-cmdk-item asr-cmdk-reader-cta" href="/reader/?name=' + qenc + '" style="background:rgba(139,105,20,.06);border-top:1px dashed rgba(139,105,20,.3);">' +
      '<span class="asr-cmdk-name" style="font-style:italic">↻ Generate a reading for "' + qsafe + '"</span>' +
      '<span class="asr-cmdk-meaning">Read it letter by letter — even if not in the library yet.</span>' +
    '</a>';
  }

  function cmdkRender(items, listEl, q){
    if(!items.length){
      listEl.innerHTML = '<div class="asr-cmdk-empty">No exact matches for "'+esc(q)+'" in our verified library.</div>' + cmdkReaderCta(q);
      return;
    }
    listEl.innerHTML = items.slice(0,30).map(function(e,i){
      return '<a class="asr-cmdk-item'+(i===0?' active':'')+'" href="'+e.h+'" data-i="'+i+'">'+
        '<span class="asr-cmdk-name">'+esc(e.n)+'</span>'+
        (e.m?'<span class="asr-cmdk-meaning">'+esc(e.m)+'</span>':'')+
      '</a>';
    }).join('') + cmdkReaderCta(q);
  }

  function openCmdk(){
    if(document.querySelector('.asr-cmdk-overlay')) return;
    var ov = document.createElement('div');
    ov.className = 'asr-cmdk-overlay';
    ov.innerHTML = '<div class="asr-cmdk" role="dialog" aria-label="Quick search">'+
      '<div class="asr-cmdk-head">'+
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>'+
      '<input type="search" class="asr-cmdk-input" placeholder="Search 1,996 names…" aria-label="Quick search" autocomplete="off" autofocus>'+
      '<kbd>Esc</kbd>'+
      '</div>'+
      '<div class="asr-cmdk-list" role="listbox"><div class="asr-cmdk-loading"><div class="asr-skel"></div><div class="asr-skel"></div><div class="asr-skel"></div></div></div>'+
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
      q = (q||'').toLowerCase().trim();
      if(!q){
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
        lastResults=[]; return;
      }
      if(!CMDK_CORPUS){ return; }
      // Tiered: prefix(binary) → substring → Levenshtein. 10 results.
      var ranked = tieredSearch(q, 10);
      var items = ranked.map(function(r){ return r.e; });
      // If still empty (e.g. 1-char query), fall back to legacy fuzzy on meaning.
      if(!items.length && q.length<=2){
        for(var i=0;i<CMDK_CORPUS.length && items.length<10;i++){
          var e = CMDK_CORPUS[i];
          if((e.nl||'').indexOf(q)===0) items.push(e);
        }
      }
      lastResults = items;
      active = 0;
      cmdkRender(items, listEl, q);
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
      items.forEach(function(el,i){ el.classList.toggle('active', i===active); });
      if(items[active] && items[active].scrollIntoView) items[active].scrollIntoView({block:'nearest'});
    }
  }

  // ---- Global Cmd-K shortcut ----
  function bindCmdkShortcut(){
    document.addEventListener('keydown', function(e){
      var isMac = /Mac|iPhone|iPad/.test(navigator.platform);
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

  document.addEventListener('DOMContentLoaded', function(){
    injectSkipLink();
    injectThemeToggle();
    injectCmdkTrigger();
    injectHeroActions();
    injectReadAnother();
    enhanceStaticReadAnother();
    recordRecent();
    injectNamesIndexFeatures();
    bindCmdkShortcut();
    bindFadeIn();
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
