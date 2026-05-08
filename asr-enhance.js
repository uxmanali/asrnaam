/* AsrNaam — Enhancement layer JS (theme toggle + share + index search) */
(function(){
  // ---- Theme toggle ----
  function applyTheme(t){
    if(t==='dark') document.documentElement.setAttribute('data-theme','dark');
    else document.documentElement.removeAttribute('data-theme');
  }
  try{
    var saved = localStorage.getItem('asr-theme');
    if(saved){ applyTheme(saved); }
    else{
      var dark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      if(dark) applyTheme('dark');
    }
  }catch(e){}

  document.addEventListener('DOMContentLoaded', function(){
    // ---- Cycle 23: Skip-to-content link for keyboard a11y ----
    if(!document.querySelector('.asr-skip-link')){
      var skip = document.createElement('a');
      skip.className = 'asr-skip-link';
      skip.href = '#main-content';
      skip.textContent = 'Skip to main content';
      document.body.insertBefore(skip, document.body.firstChild);
      // Find a likely main element to anchor to
      var main = document.querySelector('main, .content, .hero, #content');
      if(main && !main.id) main.id = 'main-content';
    }

    // Inject theme toggle into nav (after existing nav-links / nav-cta)
    var nav = document.querySelector('nav');
    if(nav && !nav.querySelector('.asr-theme-toggle')){
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
        try{ localStorage.setItem('asr-theme', nw); }catch(e){}
      });
      // Append into nav-links or as last child of nav
      var links = nav.querySelector('.nav-links');
      if(links) links.appendChild(btn);
      else nav.appendChild(btn);
    }

    // ---- Share button on name pages ----
    var hero = document.querySelector('.hero');
    if(hero && !hero.querySelector('.asr-share')){
      var h1 = document.querySelector('h1');
      if(h1){
        var name = (h1.textContent||'').split('—')[0].trim();
        if(name){
          var sb = document.createElement('button');
          sb.className = 'asr-share';
          sb.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>'+
                       '<span>Share</span>';
          sb.addEventListener('click', async function(){
            var url = window.location.href;
            var title = document.title;
            try{
              if(navigator.share){
                await navigator.share({title:title, url:url});
              } else if(navigator.clipboard){
                await navigator.clipboard.writeText(url);
                sb.querySelector('span').textContent = 'Copied!';
                setTimeout(function(){ sb.querySelector('span').textContent='Share'; }, 1500);
              }
            }catch(e){ /* user cancelled */ }
          });
          hero.appendChild(sb);
        }
      }
    }

    // ---- Index page: search + filter ----
    var indexSearch = document.querySelector('#asr-search-input');
    if(indexSearch){
      var allLinks = Array.from(document.querySelectorAll('a[href*="/names/"][href$="/"]')).filter(function(a){
        return /\/names\/[a-z0-9-]+\/$/.test(a.getAttribute('href')||'');
      });
      var counter = document.querySelector('#asr-results-count');
      var activeGender = 'all';
      var activeLetter = 'all';

      function refresh(){
        var q = (indexSearch.value||'').toLowerCase().trim();
        var visible = 0;
        allLinks.forEach(function(a){
          var slug = (a.getAttribute('href').match(/\/names\/([a-z0-9-]+)\//)||[])[1] || '';
          var label = (a.textContent||'').toLowerCase();
          var first = slug.charAt(0);
          var matchesQ = !q || slug.indexOf(q)>=0 || label.indexOf(q)>=0;
          var matchesL = activeLetter==='all' || first===activeLetter;
          var matchesG = true; // gender data isn't on /names/ for now
          if(matchesQ && matchesL && matchesG){ a.classList.remove('asr-hidden'); visible++; }
          else { a.classList.add('asr-hidden'); }
        });
        if(counter){
          counter.textContent = visible + ' name' + (visible===1?'':'s') + (q?' matching “'+q+'”':'');
        }
        // Hide letter sections that have zero visible items
        document.querySelectorAll('.asr-letter-section').forEach(function(s){
          var has = !!s.querySelector('a[href*="/names/"]:not(.asr-hidden)');
          s.classList.toggle('asr-hidden', !has);
        });
      }
      indexSearch.addEventListener('input', refresh);
      indexSearch.addEventListener('keydown', function(e){ if(e.key==='Escape'){ indexSearch.value=''; refresh(); } });

      document.querySelectorAll('.asr-chip').forEach(function(chip){
        chip.addEventListener('click', function(){
          var letter = chip.dataset.letter;
          var gender = chip.dataset.gender;
          if(letter){
            document.querySelectorAll('.asr-chip[data-letter]').forEach(function(c){ c.classList.remove('active'); });
            chip.classList.add('active');
            activeLetter = letter;
          } else if(gender){
            document.querySelectorAll('.asr-chip[data-gender]').forEach(function(c){ c.classList.remove('active'); });
            chip.classList.add('active');
            activeGender = gender;
          }
          refresh();
        });
      });
      refresh();
    }
  });
})();
