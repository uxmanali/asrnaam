/* AsrNaam redesign behaviour: search, filters, favourites, pronunciation,
   lucky-number working, and the mobile bar. No network except the name index. */
(function () {
  'use strict';
  if (window.__asrRedesign) return;
  window.__asrRedesign = true;

  var LS_KEY = 'asr-favorites';
  var ABJAD = {
    'ا': 1, 'أ': 1, 'إ': 1, 'آ': 1, 'ٱ': 1, 'ء': 1,
    'ب': 2, 'پ': 2, 'ج': 3, 'چ': 3, 'د': 4,
    'ه': 5, 'ة': 5, 'ہ': 5, 'ھ': 5, 'ح': 8,
    'و': 6, 'ؤ': 6, 'ز': 7, 'ژ': 7, 'ط': 9,
    'ي': 10, 'ى': 10, 'ی': 10, 'ئ': 10,
    'ك': 20, 'ک': 20, 'گ': 20, 'ل': 30, 'م': 40, 'ن': 50,
    'س': 60, 'ع': 70, 'ف': 80, 'ص': 90, 'ق': 100,
    'ر': 200, 'ش': 300, 'ت': 400, 'ث': 500, 'خ': 600,
    'ذ': 700, 'ض': 800, 'ظ': 900, 'غ': 1000
  };

  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }
  function getFavs() {
    try {
      var v = JSON.parse(localStorage.getItem(LS_KEY) || '[]');
      return Array.isArray(v) ? v : [];
    } catch (e) { return []; }
  }
  function setFavs(arr) {
    try { localStorage.setItem(LS_KEY, JSON.stringify(arr)); } catch (e) {}
    document.dispatchEvent(new CustomEvent('asr-favs'));
  }
  function digits(n) {
    var s = 0;
    String(n).split('').forEach(function (d) { s += parseInt(d, 10) || 0; });
    return s;
  }
  function reduce(n) {
    var steps = [n];
    var x = n;
    while (x > 9) { x = digits(x); steps.push(x); }
    return { root: x, steps: steps };
  }
  function abjadOf(text) {
    var parts = [];
    var sum = 0;
    var chars = Array.from(String(text || ''));
    chars.forEach(function (ch) {
      if (ABJAD[ch] != null) {
        parts.push({ g: ch, v: ABJAD[ch] });
        sum += ABJAD[ch];
      }
    });
    return { parts: parts, sum: sum, red: reduce(sum) };
  }
  function slugFromPath() {
    var p = location.pathname.replace(/\/+$/, '');
    var m = p.match(/\/names\/([a-z0-9-]+)$/i);
    return m ? m[1].toLowerCase() : null;
  }
  function isNamePage() {
    if (document.querySelector('meta[http-equiv="refresh"]')) return false;
    var slug = slugFromPath();
    if (!slug) return false;
    if (document.getElementById('asr-namecard') || document.querySelector('.asr-name-hero')) return true;
    return !!(document.querySelector('.arabic-name') && document.querySelector('.asr-v2-letters'));
  }
  function pageName() {
    var h = document.querySelector('h1');
    if (!h) return slugFromPath() || '';
    var t = (h.textContent || '').split('—')[0].split('|')[0].split(',')[0].trim();
    t = t.replace(/\s+name meaning.*$/i, '').replace(/\s+نام.*$/, '').trim();
    return t || slugFromPath() || '';
  }
  function speakable() {
    return !!(window.speechSynthesis && window.SpeechSynthesisUtterance);
  }
  function speak(text) {
    if (!speakable() || !text) return false;
    try {
      window.speechSynthesis.cancel();
      var u = new SpeechSynthesisUtterance(text);
      u.lang = 'ar';
      var voices = window.speechSynthesis.getVoices() || [];
      var ar = voices.filter(function (v) { return /^ar/i.test(v.lang); })[0];
      if (ar) u.voice = ar;
      window.speechSynthesis.speak(u);
      return true;
    } catch (e) { return false; }
  }
  function wrapSaw(root) {
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    var nodes = [];
    var n;
    while ((n = walker.nextNode())) {
      if (n.nodeValue && n.nodeValue.indexOf('ﷺ') !== -1) nodes.push(n);
    }
    nodes.forEach(function (node) {
      if (node.parentNode && node.parentNode.classList && node.parentNode.classList.contains('saw')) return;
      var parts = node.nodeValue.split('ﷺ');
      var frag = document.createDocumentFragment();
      parts.forEach(function (part, i) {
        if (part) frag.appendChild(document.createTextNode(part));
        if (i < parts.length - 1) {
          var s = document.createElement('span');
          s.className = 'saw';
          s.setAttribute('aria-label', 'peace be upon him');
          s.textContent = 'ﷺ';
          frag.appendChild(s);
        }
      });
      node.parentNode.replaceChild(frag, node);
    });
  }

  function heartSVG(filled) {
    return '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" ' +
      (filled ? 'fill="currentColor"' : 'fill="none"') +
      ' stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>';
  }

  function updateBadges() {
    var n = getFavs().length;
    document.querySelectorAll('.rd-badge').forEach(function (b) {
      b.textContent = String(n);
      b.hidden = n === 0;
    });
  }

  function toggleFav(entry) {
    var favs = getFavs();
    var i = favs.findIndex(function (e) { return e && e.slug === entry.slug; });
    var on;
    if (i >= 0) { favs.splice(i, 1); on = false; }
    else {
      favs.unshift({
        slug: entry.slug, name: entry.name, meaning: entry.meaning || '',
        arabic: entry.arabic || '', urdu: entry.urdu || '', gender: entry.gender || '',
        ts: Date.now()
      });
      if (favs.length > 200) favs = favs.slice(0, 200);
      on = true;
    }
    setFavs(favs);
    updateBadges();
    return on;
  }

  function injectNavHeart() {
    if (document.querySelector('.rd-nav-heart')) { updateBadges(); return; }
    var nav = document.querySelector('.asr-site-header .nav-links, nav.asr-nav .nav-links, nav.asr-nav');
    if (!nav) return;
    var a = document.createElement('a');
    a.className = 'rd-nav-heart';
    a.href = '/favourites/';
    a.setAttribute('aria-label', 'Favourites');
    a.innerHTML = heartSVG(false) + '<span class="rd-badge" hidden>0</span>';
    if (nav.classList.contains('nav-links')) nav.appendChild(a);
    else nav.appendChild(a);
    updateBadges();
  }

  function nameEntryFromPage() {
    var card = document.getElementById('asr-namecard');
    var data = {};
    if (card) { try { data = JSON.parse(card.textContent); } catch (e) {} }
    var meaning = '';
    var md = document.querySelector('[data-asr-field="meaning-dict"]');
    if (md) meaning = md.textContent.trim();
    else if (data.meaning && data.meaning.dict) meaning = data.meaning.dict;
    var ur = document.querySelector('[data-asr-field="urdu"]');
    return {
      slug: slugFromPath(),
      name: (data.english || pageName()),
      meaning: meaning,
      arabic: data.arabic || (document.querySelector('.asr-name-hero-arabic, .arabic-name') || {}).textContent || '',
      urdu: (ur && ur.textContent.trim()) || data.urdu || '',
      gender: data.gender || ''
    };
  }

  function wirePlay(host) {
    if (!host || host.querySelector('.rd-play')) return;
    if (!speakable()) return;
    var entry = nameEntryFromPage();
    var audio = document.querySelector('audio[src]');
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'rd-play';
    btn.setAttribute('aria-label', 'Play pronunciation');
    var pron = document.querySelector('[data-asr-field="pronunciation"], .asr-pronunciation strong');
    var label = pron ? pron.textContent.trim() : entry.name;
    btn.innerHTML = '<span class="play" aria-hidden="true"><svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg></span><span><b>' +
      esc(entry.name) + '</b><small>' + esc(label) + '</small></span>';
    btn.addEventListener('click', function () {
      if (audio) { audio.play(); return; }
      var said = speak(entry.arabic || entry.name);
      if (!said) btn.hidden = true;
    });
    var sub = host.querySelector('.asr-name-hero-sub, .hero-subtitle, h1');
    if (sub && sub.parentNode === host) sub.insertAdjacentElement('afterend', btn);
    else host.appendChild(btn);
  }

  function luckyCard() {
    if (document.querySelector('.rd-lucky')) return;
    var glyphs = [];
    document.querySelectorAll('.asr-v2-letter-arabic').forEach(function (el) {
      glyphs.push((el.textContent || '').trim());
    });
    var source = glyphs.join('') || (document.querySelector('.asr-name-hero-arabic, .arabic-name') || {}).textContent || '';
    var calc = abjadOf(source);
    if (!calc.parts.length) return;
    var published = '';
    var luckyEl = document.querySelector('[data-asr-field="lucky"]');
    if (luckyEl) published = (luckyEl.textContent || '').trim();
    else {
      document.querySelectorAll('.qf-row').forEach(function (row) {
        var lab = row.querySelector('.qf-label');
        if (lab && /lucky|ابجد|خوش/i.test(lab.textContent || '')) {
          var val = row.querySelector('.qf-value');
          if (val) published = (val.textContent || '').trim();
        }
      });
    }
    if (luckyEl && luckyEl.closest) {
      var luckyRow = luckyEl.closest('.r, .qf-row');
      if (luckyRow) luckyRow.classList.add('rd-hide');
    }
    document.querySelectorAll('.qf-row').forEach(function (row) {
      var lab = row.querySelector('.qf-label');
      if (lab && /lucky|ابجد|خوش/i.test(lab.textContent || '')) row.classList.add('rd-hide');
    });
    var pubNum = parseInt(String(published).replace(/[^\d]/g, ''), 10);
    var show = calc.red.root;
    var equation = calc.parts.map(function (p) { return p.v; }).join('+') + ' = ' + calc.sum;
    calc.red.steps.forEach(function (step, i) {
      if (i === 0) return;
      equation += ' → ' + step;
    });
    var note = '';
    if (pubNum && pubNum !== show && pubNum !== calc.sum) {
      show = pubNum;
      note = 'The page records ' + pubNum + '. The letters shown add to ' + calc.sum + ', which reduces to ' + calc.red.root + '.';
    }
    var card = document.createElement('div');
    card.className = 'rd-lucky';
    card.innerHTML = '<span class="rd-kicker">Abjad lucky number</span><div class="n">' + show +
      '</div><div class="work"><div class="rd-chips">' +
      calc.parts.map(function (p) { return '<span><i>' + p.g + '</i>' + p.v + '</span>'; }).join('') +
      '</div>' + esc(equation) + (note ? '<div>' + esc(note) + '</div>' : '') + '</div>';
    var rows = document.querySelector('.asr-answer-rows');
    if (rows) rows.appendChild(card);
    else {
      var qf = document.querySelector('.quick-facts');
      if (qf) qf.appendChild(card);
    }
  }

  function wireFavButton() {
    var entry = nameEntryFromPage();
    if (!entry.slug) return;
    function paint(btn) {
      var on = getFavs().some(function (e) { return e.slug === entry.slug; });
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
      var span = btn.querySelector('span');
      if (span) span.textContent = on ? 'Saved' : 'Save';
      btn.classList.toggle('on', on);
    }
    var host = document.querySelector('.asr-name-hero, article > .hero, main > .hero');
    if (!host) return;
    var bar = host.querySelector('.asr-action-bar');
    if (!bar) {
      bar = document.createElement('div');
      bar.className = 'asr-action-bar';
      host.appendChild(bar);
    }
    var existing = bar.querySelector('.asr-fav') || host.querySelector('.asr-fav');
    if (existing) {
      if (existing.parentNode !== bar) bar.appendChild(existing);
      existing.addEventListener('click', function () { setTimeout(function () { paint(existing); updateBadges(); }, 0); });
    } else {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'rd-btn asr-fav';
      btn.innerHTML = heartSVG(true) + '<span>Save</span>';
      btn.addEventListener('click', function () {
        toggleFav(entry);
        paint(btn);
      });
      bar.appendChild(btn);
      paint(btn);
    }
    if (!bar.querySelector('.asr-share, .rd-share')) {
      var share = document.createElement('button');
      share.type = 'button';
      share.className = 'rd-btn rd-share asr-share';
      share.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/></svg><span>Share</span>';
      share.addEventListener('click', function () {
        var url = location.href;
        var text = (entry.name || document.title) + ' ' + url;
        if (navigator.share) navigator.share({ title: document.title, text: text, url: url }).catch(function () {});
        else window.open('https://wa.me/?text=' + encodeURIComponent(text), '_blank', 'noopener');
      });
      bar.appendChild(share);
    }
  }

  function promoteSections() {
    if (document.getElementById('rd-raised-done')) return;
    var anchor = document.querySelector('.asr-answer') || document.querySelector('.quick-facts');
    if (!anchor || !anchor.parentNode) return;
    // Some older pages put the answer box above the hero. Raising the letter and
    // bearer sections after it then pushed the name and title 2,000px down the
    // page (48 pages, found 13 Nov). Keep the hero first.
    var heroEl = document.querySelector('.asr-name-hero, article > .hero, main > .hero');
    if (heroEl && heroEl.parentNode === anchor.parentNode &&
        (anchor.compareDocumentPosition(heroEl) & Node.DOCUMENT_POSITION_FOLLOWING)) {
      anchor.parentNode.insertBefore(heroEl, anchor);
    }
    var pieces = [
      document.querySelector('.asr-v2-letters'),
      document.querySelector('.asr-v2-bearers'),
      document.querySelector('.related-section')
    ];
    var after = anchor;
    pieces.forEach(function (el) {
      if (!el) return;
      el.classList.add('rd-raised');
      after.insertAdjacentElement('afterend', el);
      after = el;
    });
    var mark = document.createElement('span');
    mark.id = 'rd-raised-done';
    mark.hidden = true;
    anchor.parentNode.appendChild(mark);
  }

  function mobileBar() {
    if (!isNamePage() || document.querySelector('.rd-mbar')) return;
    var bar = document.createElement('div');
    bar.className = 'rd-mbar';
    bar.innerHTML =
      '<form class="in" action="/reader/" method="get" role="search">' +
      '<label class="rd-sr" for="rd-m-q">Search another name</label>' +
      '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3-3"/></svg>' +
      '<input id="rd-m-q" name="name" type="search" placeholder="Search another name" enterkeyhint="search">' +
      '</form>' +
      '<button type="button" class="h" aria-label="Save to favourites" aria-pressed="false">' + heartSVG(true) + '</button>' +
      '<button type="button" class="s" aria-label="Share">' +
      '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/></svg></button>';
    document.body.appendChild(bar);
    document.body.classList.add('rd-hasbar');
    var entry = nameEntryFromPage();
    var heart = bar.querySelector('.h');
    function paint() {
      var on = getFavs().some(function (e) { return e.slug === entry.slug; });
      heart.setAttribute('aria-pressed', on ? 'true' : 'false');
    }
    heart.addEventListener('click', function () { toggleFav(entry); paint(); });
    paint();
    bar.querySelector('.s').addEventListener('click', function () {
      var url = location.href;
      var text = entry.name + ' — ' + (entry.meaning || 'name meaning') + ' ' + url;
      if (navigator.share) {
        navigator.share({ title: document.title, text: text, url: url }).catch(function () {});
      } else {
        window.open('https://wa.me/?text=' + encodeURIComponent(text), '_blank', 'noopener');
      }
    });
  }

  var INDEX = null;
  function loadIndex() {
    if (INDEX) return Promise.resolve(INDEX);
    return fetch('/names/names-index.json', { cache: 'force-cache' }).then(function (r) {
      if (!r.ok) throw new Error('index');
      return r.json();
    }).then(function (arr) { INDEX = arr; return arr; });
  }

  function fmt(n) { return Number(n).toLocaleString('en-US'); }

  function syncCount(arr) {
    var n = fmt(arr.length);
    document.querySelectorAll('[data-name-count]').forEach(function (el) { el.textContent = n; });
  }

  function mountHome() {
    var input = document.getElementById('rd-q');
    var box = document.getElementById('rd-ac');
    if (!input || !box) return;
    var form = input.closest('form');
    var active = -1;
    var current = [];

    function close() {
      box.hidden = true;
      input.setAttribute('aria-expanded', 'false');
      form.classList.remove('is-open');
      active = -1;
    }
    function highlight(q, text) {
      var i = text.toLowerCase().indexOf(q.toLowerCase());
      if (i < 0 || !q) return esc(text);
      return esc(text.slice(0, i)) + '<mark>' + esc(text.slice(i, i + q.length)) + '</mark>' + esc(text.slice(i + q.length));
    }
    function render(q, rows) {
      current = rows;
      active = rows.length ? 0 : -1;
      if (!q) { close(); return; }
      var html = rows.map(function (row, i) {
        var g = /f/i.test(row.g) ? 'girl' : 'boy';
        var gl = /f/i.test(row.g) ? 'Girl' : (/m/i.test(row.g) ? 'Boy' : row.g);
        return '<a role="option" id="rd-opt-' + i + '" href="/names/' + esc(row.s) + '/" aria-selected="' + (i === 0 ? 'true' : 'false') + '">' +
          '<span><b>' + highlight(q, row.n) + '</b><small>' + esc(row.m || '') + '</small></span>' +
          '<span class="rd-tag ' + g + '">' + esc(gl) + '</span>' +
          '<span class="ar" lang="ar" dir="rtl">' + esc(row.a || '') + '</span></a>';
      }).join('');
      html += '<div class="rd-ac-foot"><span>Try a meaning, an Arabic letter, or a lucky number</span><span>' + rows.length + ' shown</span></div>';
      box.innerHTML = html;
      box.hidden = false;
      input.setAttribute('aria-expanded', 'true');
      form.classList.add('is-open');
      if (rows[0]) input.setAttribute('aria-activedescendant', 'rd-opt-0');
    }
    function search(arr, q) {
      q = q.trim();
      if (!q) return [];
      var ql = q.toLowerCase();
      var starts = [], contains = [];
      for (var i = 0; i < arr.length; i++) {
        var row = arr[i];
        var name = (row.n || '').toLowerCase();
        var blob = name + ' ' + (row.m || '').toLowerCase() + ' ' + (row.a || '') + ' ' + (row.u || '') + ' ' + (row.v || []).join(' ').toLowerCase();
        if (name.indexOf(ql) === 0 || (row.a || '').indexOf(q) === 0) starts.push(row);
        else if (blob.indexOf(ql) !== -1 || blob.indexOf(q) !== -1) contains.push(row);
        if (starts.length >= 6) break;
      }
      return starts.concat(contains).slice(0, 6);
    }
    var timer;
    input.addEventListener('input', function () {
      var q = input.value;
      clearTimeout(timer);
      timer = setTimeout(function () {
        loadIndex().then(function (arr) {
          syncCount(arr);
          render(q, search(arr, q));
        }).catch(function () { close(); });
      }, 40);
    });
    input.addEventListener('keydown', function (e) {
      if (box.hidden) return;
      var opts = box.querySelectorAll('[role="option"]');
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        if (!opts.length) return;
        active = e.key === 'ArrowDown' ? Math.min(opts.length - 1, active + 1) : Math.max(0, active - 1);
        opts.forEach(function (o, i) { o.setAttribute('aria-selected', i === active ? 'true' : 'false'); });
        input.setAttribute('aria-activedescendant', opts[active].id);
        opts[active].scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'Enter' && active >= 0 && current[active]) {
        e.preventDefault();
        location.href = '/names/' + current[active].s + '/';
      } else if (e.key === 'Escape') close();
    });
    document.addEventListener('click', function (e) {
      if (!form.contains(e.target)) close();
    });
    form.addEventListener('submit', function (e) {
      if (current[0] && input.value.trim()) {
        e.preventDefault();
        location.href = '/names/' + (active >= 0 && current[active] ? current[active].s : current[0].s) + '/';
      }
    });
    loadIndex().then(syncCount).catch(function () {});
    mountFilters();
  }

  function mountFilters() {
    var root = document.querySelector('.rd-filters');
    if (!root) return;
    var out = document.getElementById('rd-filter-results');
    var state = { letter: '', length: '', lucky: '' };
    function apply() {
      var keys = Object.keys(state).filter(function (k) { return state[k]; });
      if (!keys.length) { out.hidden = true; return; }
      loadIndex().then(function (arr) {
        var rows = arr.filter(function (row) {
          if (state.letter && (row.n || '').charAt(0).toUpperCase() !== state.letter) return false;
          var len = (row.n || '').replace(/[^A-Za-z]/g, '').length;
          if (state.length === 'short' && (len < 3 || len > 4)) return false;
          if (state.length === 'medium' && (len < 5 || len > 7)) return false;
          if (state.length === 'long' && len < 8) return false;
          if (state.lucky) {
            var root = abjadOf(row.a).red.root;
            if (String(root) !== String(state.lucky)) return false;
          }
          return true;
        });
        var shown = rows.slice(0, 12);
        var meta = out.querySelector('.rd-results-meta');
        var grid = out.querySelector('.rd-results-grid');
        meta.textContent = fmt(rows.length) + (rows.length === 1 ? ' name' : ' names');
        grid.innerHTML = shown.map(function (row) {
          var g = /f/i.test(row.g) ? 'girl' : 'boy';
          return '<a class="rd-ncard" href="/names/' + esc(row.s) + '/"><span class="ar" lang="ar" dir="rtl">' +
            esc(row.a || '') + '</span><span class="nm">' + esc(row.n) + '</span><span class="mn">' +
            esc(row.m || '') + '</span><span class="rd-tag ' + g + '">' + esc(row.g || '') + '</span></a>';
        }).join('') || '<p>No names match these filters.</p>';
        out.hidden = false;
      }).catch(function () {});
    }
    root.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-f]');
      if (!btn) return;
      if (btn.tagName === 'A' && btn.getAttribute('data-f') === 'go') return;
      e.preventDefault();
      var kind = btn.getAttribute('data-f');
      var val = btn.getAttribute('data-v');
      if (state[kind] === val) state[kind] = '';
      else state[kind] = val;
      root.querySelectorAll('[data-f="' + kind + '"]').forEach(function (el) {
        el.setAttribute('aria-pressed', el.getAttribute('data-v') === state[kind] ? 'true' : 'false');
      });
      apply();
    });
  }

  function mountFavourites() {
    var list = document.getElementById('rd-fav-list');
    if (!list) return;
    var params = new URLSearchParams(location.search);
    var shared = (params.get('names') || '').split(',').map(function (s) { return s.trim().toLowerCase(); }).filter(Boolean);
    var sharedMode = shared.length > 0;
    function draw(arr) {
      var favs = sharedMode ? shared.map(function (s) { return { slug: s }; }) : getFavs();
      var bySlug = {};
      (arr || []).forEach(function (row) { bySlug[row.s] = row; });
      var countEl = document.getElementById('rd-fav-count');
      if (countEl) countEl.textContent = String(favs.length);
      var lead = document.getElementById('rd-fav-lead');
      if (lead && sharedMode) {
        lead.textContent = favs.length + (favs.length === 1 ? ' name in this shared list.' : ' names in this shared list.') + ' Save them in this browser if you want to keep them.';
      }
      if (!favs.length) {
        list.innerHTML = '<div class="rd-empty"><p>No names saved yet. Open a name and tap the heart. The list stays in this browser.</p><p><a href="/names/">Browse names</a></p></div>';
        return;
      }
      list.innerHTML = favs.map(function (f) {
        var row = bySlug[f.slug] || {};
        var name = row.n || f.name || f.slug;
        var meaning = row.m || f.meaning || '';
        var arabic = f.arabic || row.a || '';
        var urdu = f.urdu || row.u || '';
        var g = f.gender || row.g || '';
        var tag = /f/i.test(g) ? 'girl' : 'boy';
        return '<article class="rd-fav"><div class="sc"><span class="ar" lang="ar" dir="rtl">' + esc(arabic) +
          '</span><span class="ur" lang="ur" dir="rtl">' + esc(urdu) + '</span></div><div><h2><a href="/names/' +
          esc(f.slug) + '/">' + esc(name) + '</a></h2><p>' + esc(meaning) + '</p>' +
          (g ? '<span class="rd-tag ' + tag + '">' + esc(g) + '</span>' : '') +
          '</div><button type="button" class="rd-btn rd-btn-ghost" data-remove="' + esc(f.slug) + '" aria-label="Remove ' +
          esc(name) + '">' + heartSVG(true) + '</button></article>';
      }).join('');
    }
    loadIndex().then(function (arr) { draw(arr); }).catch(function () { draw(null); });
    list.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-remove]');
      if (!btn || sharedMode) return;
      var slug = btn.getAttribute('data-remove');
      setFavs(getFavs().filter(function (f) { return f.slug !== slug; }));
      loadIndex().then(draw).catch(function () { draw(null); });
    });
    function shareURL() {
      var slugs = sharedMode ? shared : getFavs().map(function (f) { return f.slug; });
      var u = new URL('/favourites/', location.origin);
      if (slugs.length) u.searchParams.set('names', slugs.join(','));
      return u.toString();
    }
    var wa = document.getElementById('rd-wa');
    var copy = document.getElementById('rd-copy');
    if (wa) wa.addEventListener('click', function () {
      var url = shareURL();
      var text = 'Names we are considering: ' + url;
      location.href = 'https://wa.me/?text=' + encodeURIComponent(text);
    });
    if (copy) copy.addEventListener('click', function () {
      var url = shareURL();
      var done = function () { copy.textContent = 'Copied'; setTimeout(function () { copy.textContent = 'Copy link'; }, 1200); };
      if (navigator.clipboard) navigator.clipboard.writeText(url).then(done).catch(function () {});
      else done();
    });
    var saveShared = document.getElementById('rd-save-shared');
    if (saveShared) saveShared.addEventListener('click', function () {
      loadIndex().then(function (arr) {
        var by = {};
        arr.forEach(function (r) { by[r.s] = r; });
        shared.forEach(function (slug) {
          if (getFavs().some(function (f) { return f.slug === slug; })) return;
          var row = by[slug] || {};
          toggleFav({ slug: slug, name: row.n || slug, meaning: row.m || '', arabic: row.a || '', urdu: row.u || '', gender: row.g || '' });
        });
        saveShared.textContent = 'Saved in this browser';
      });
    });
  }

  function guardAds() {
    function sweep() {
      document.querySelectorAll('.google-auto-placed, ins.adsbygoogle-noablate, [id^="google-anno"], .google-ad-content').forEach(function (n) {
        if (n.closest && n.closest('.asr-ad')) return;
        n.remove();
      });
      document.querySelectorAll('iframe').forEach(function (n) {
        var src = n.getAttribute('src') || '';
        if (src.indexOf('googlesyndication') === -1 && src.indexOf('doubleclick') === -1) return;
        if (n.closest && n.closest('.asr-ad')) return;
        n.remove();
      });
      document.querySelectorAll('ins.adsbygoogle').forEach(function (n) {
        if (n.closest && n.closest('.asr-ad')) return;
        if (!n.getAttribute('data-ad-slot')) n.remove();
      });
    }
    sweep();
    if (window.MutationObserver) {
      var mo = new MutationObserver(function () { sweep(); });
      mo.observe(document.documentElement, { childList: true, subtree: true });
      setTimeout(function () { mo.disconnect(); }, 8000);
    }
  }

  ready(function () {
    wrapSaw(document.body);
    injectNavHeart();
    if (isNamePage()) {
      var hero = document.querySelector('.asr-name-hero, article > .hero, main > .hero');
      promoteSections();
      wirePlay(hero);
      luckyCard();
      wireFavButton();
      mobileBar();
    }
    mountHome();
    mountFavourites();
    document.addEventListener('asr-favs', updateBadges);
    // guardAds() removed 12 Nov: it deleted Google Auto Ads and anchor ads, which
    // cut ad impressions per page by about a third. Never remove or hide ads in code;
    // turn ad formats on or off in AdSense instead (programme policy).
  });
})();
