/* AsrNaam — standalone theme engine (2026-07-25).
   For pages that do not load asr-enhance.js (blog, aathaar, basaair,
   reader, hubs, legal, AR/UR mirrors). Honors the saved theme choice by
   retargeting every @media (prefers-color-scheme: dark) block at runtime:
   dark -> 'all', light -> 'not all', auto -> restore the original query.
   Injects the same sun/moon toggle, self-styled so it needs no external CSS.
   Skips itself entirely when asr-enhance.js is on the page. */
(function(){
  if(document.querySelector('script[src*="asr-enhance.js"]')) return;
  var KEY='asr-theme';
  var rules=[]; var scanned=(typeof WeakSet!=='undefined')?new WeakSet():null;
  function collect(){
    var s=document.styleSheets;
    for(var i=0;i<s.length;i++){
      var ss=s[i];
      if(scanned){ if(scanned.has(ss)) continue; scanned.add(ss); }
      var rs; try{ rs=ss.cssRules; }catch(e){ continue; }
      if(!rs) continue;
      for(var j=0;j<rs.length;j++){
        var r=rs[j];
        if(r.media){
          var c=r.media.mediaText||'';
          if(c.indexOf('prefers-color-scheme')!==-1 && c.indexOf('dark')!==-1) rules.push(r.media);
        }
      }
    }
  }
  function retarget(mode){
    collect();
    var t = mode==='dark' ? 'all' : mode==='light' ? 'not all' : '(prefers-color-scheme: dark)';
    for(var i=0;i<rules.length;i++){ try{ rules[i].mediaText=t; }catch(e){} }
    /* Chromium does not invalidate styles on CSSOM mediaText edits;
       force a synchronous recalc so the change paints immediately. */
    try{
      var h=document.documentElement;
      h.classList.add('asr-theme-sync'); void h.offsetHeight; h.classList.remove('asr-theme-sync');
    }catch(e){}
  }
  function osDark(){ return !!(window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches); }
  function saved(){ try{ return localStorage.getItem(KEY); }catch(e){ return null; } }
  function effectiveDark(){ var s=saved(); if(s==='dark')return true; if(s==='light')return false; return osDark(); }
  function apply(t){
    var dark=(t==='dark')||(t==='auto'&&osDark());
    if(dark) document.documentElement.setAttribute('data-theme','dark');
    else document.documentElement.removeAttribute('data-theme');
    retarget(t==='auto'?'auto':t);
    try{ document.documentElement.style.colorScheme=(t==='auto')?'':(dark?'dark':'light'); }catch(e){}
    try{
      var ms=document.querySelectorAll('meta[name="theme-color"]');
      for(var i=0;i<ms.length;i++){ if(t!=='auto') ms[i].setAttribute('content', dark?'#1a1a1a':'#FAFAF8'); }
    }catch(e){}
  }
  function init(){ var s=saved(); apply(s==='dark'||s==='light'?s:'auto'); }
  function injectToggle(){
    var nav=document.querySelector('nav');
    if(!nav||nav.querySelector('.asr-theme-toggle')) return;
    var st=document.createElement('style');
    st.textContent='.asr-theme-toggle{background:none;border:1px solid rgba(139,105,20,.35);border-radius:6px;cursor:pointer;padding:.35rem .5rem;margin-left:.8rem;color:inherit;vertical-align:middle;line-height:1;}'+
      '.asr-theme-toggle svg{width:15px;height:15px;display:block;}'+
      '.asr-theme-toggle .asr-icon-sun{display:none;}'+
      'html[data-theme="dark"] .asr-theme-toggle .asr-icon-sun{display:block;}'+
      'html[data-theme="dark"] .asr-theme-toggle .asr-icon-moon{display:none;}'+
      'html[data-theme="dark"] .asr-theme-toggle{border-color:rgba(212,175,108,.45);color:#d4af6c;}';
    document.head.appendChild(st);
    var btn=document.createElement('button');
    btn.className='asr-theme-toggle';
    btn.setAttribute('aria-label','Toggle theme');
    btn.innerHTML='<svg class="asr-icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>'+
      '<svg class="asr-icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>';
    btn.addEventListener('click',function(){
      var nw=effectiveDark()?'light':'dark';
      if((nw==='dark')===osDark()){
        try{ localStorage.removeItem(KEY); }catch(e){}
        apply('auto');
      } else {
        try{ localStorage.setItem(KEY,nw); }catch(e){}
        apply(nw);
      }
    });
    var links=nav.querySelector('.nav-links');
    if(links) links.appendChild(btn); else nav.appendChild(btn);
  }
  init();
  function late(){ init(); injectToggle(); setTimeout(init,800); }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',late);
  else late();
  window.addEventListener('load',function(){ init(); });
  try{
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',function(){
      var s=saved(); if(s!=='dark'&&s!=='light') apply('auto');
    });
  }catch(e){}
})();
