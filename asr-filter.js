/* AsrNaam name filter.
   One engine, two mounts: the full page at /names/find/ and the compact finder
   on the home page. Follows the pattern the research points to: instant results
   on desktop with the controls staying in view, a full-screen sheet with an
   explicit "Show N names" on mobile, applied filters always visible as
   removable chips, and a count on every option so nobody picks a dead end. */
(function () {
  'use strict';
  var DATA = null, LOADING = null;
  /* The page stamps a content version here. Without it the browser happily
     serves a filters.json or a build of this file from an earlier deploy, and
     the controls render against logic that does not know about them. */
  var V = (window.ASR_FV ? '?v=' + window.ASR_FV : '');
  var GEN = ['Boy', 'Girl', 'Both'];

  function load() {
    if (DATA) return Promise.resolve(DATA);
    if (LOADING) return LOADING;
    LOADING = fetch('/names/filters.json' + V, { cache: 'force-cache' })
      .then(function (r) { if (!r.ok) throw new Error('http ' + r.status); return r.json(); })
      .then(function (d) { DATA = d; return d; });
    return LOADING;
  }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function nfmt(n) { return n.toLocaleString('en-US'); }

  /* ---------------------------------------------------------------- engine */
  function Engine(d) {
    this.d = d;
    this.S = { g: [], e: [], u: [], t: [], r: [] };
    this.q = '';
    this.sort = 'az';
  }
  /* Typing is the fastest filter there is when you half-know the name, so it
     runs over the Latin name, the Arabic, the Urdu and the meaning at once. */
  Engine.prototype.hit = function (n) {
    var q = this.q;
    if (!q) return true;
    if (n[1].toLowerCase().indexOf(q) >= 0) return true;
    if (n[2].indexOf(q) >= 0 || n[3].indexOf(q) >= 0) return true;
    if (n[5].toLowerCase().indexOf(q) >= 0) return true;
    return false;
  };
  Engine.prototype.match = function (n, skip) {
    var S = this.S;
    if (!this.hit(n)) return false;
    if (skip !== 'g' && S.g.length && S.g.indexOf(n[4]) < 0 && n[4] !== 2) return false;
    if (skip !== 'e' && S.e.length && S.e.indexOf(n[6]) < 0) return false;
    if (skip !== 'u' && S.u.length && S.u.indexOf(n[7]) < 0) return false;
    if (skip !== 't' && S.t.length) {
      for (var i = 0; i < S.t.length; i++) if (n[8].indexOf(S.t[i]) < 0) return false;
    }
    if (skip !== 'r' && S.r.length) {
      var ok = false;
      for (var j = 0; j < S.r.length; j++) if (n[9].indexOf(S.r[j]) >= 0) { ok = true; break; }
      if (!ok) return false;
    }
    return true;
  };
  Engine.prototype.results = function () {
    var out = [], n = this.d.n;
    for (var i = 0; i < n.length; i++) if (this.match(n[i])) out.push(n[i]);
    if (this.sort === 'pop') {
      out.sort(function (a, b) { return (b[10] || 0) - (a[10] || 0) || (a[1] < b[1] ? -1 : 1); });
    } else if (this.sort === 'short') {
      out.sort(function (a, b) { return a[1].length - b[1].length || (a[1] < b[1] ? -1 : 1); });
    }
    return out;
  };
  /* live counts: how many results each option would still leave, with the rest
     of the selection held. This is what stops a filter click landing on zero. */
  Engine.prototype.counts = function (k) {
    var c = {}, n = this.d.n, i, v;
    for (i = 0; i < n.length; i++) {
      if (!this.match(n[i], k)) continue;
      var row = n[i];
      if (k === 'g') { v = row[4]; if (v === 2) { c[0] = (c[0] || 0) + 1; c[1] = (c[1] || 0) + 1; } else c[v] = (c[v] || 0) + 1; }
      else if (k === 'e') { c[row[6]] = (c[row[6]] || 0) + 1; }
      else if (k === 'u') { if (row[7] >= 0) c[row[7]] = (c[row[7]] || 0) + 1; }
      else if (k === 't') { for (var a = 0; a < row[8].length; a++) c[row[8][a]] = (c[row[8][a]] || 0) + 1; }
      else if (k === 'r') { for (var b = 0; b < row[9].length; b++) c[row[9][b]] = (c[row[9][b]] || 0) + 1; }
    }
    return c;
  };
  Engine.prototype.count = function () {
    var n = this.d.n, k = 0;
    for (var i = 0; i < n.length; i++) if (this.match(n[i])) k++;
    return k;
  };
  /* which single filter, if dropped, brings a dead end back to life */
  Engine.prototype.blame = function () {
    var keys = ['t', 'r', 'u', 'e', 'g'], self = this;
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i];
      if (!this.S[k].length) continue;
      var save = this.S[k];
      this.S[k] = [];
      var n = this.count();
      this.S[k] = save;
      if (n > 0) return { k: k, n: n };
    }
    return null;
  };

  var LABEL = { g: 'Gender', e: 'English letter', u: 'Urdu letter', t: 'Meaning', r: 'Where it is used' };

  function optionLabel(d, k, v) {
    if (k === 'g') return GEN[v] + ' names';
    if (k === 'e') return v;
    if (k === 'u') return d.urdu[v] ? d.urdu[v][2] + ' ' + d.urdu[v][1] : v;
    if (k === 't') return d.themes[v] ? d.themes[v][1] : v;
    if (k === 'r') return d.regions[v] ? d.regions[v][1] : v;
    return v;
  }

  /* ------------------------------------------------------------ full page */
  function mountFull(root, d) {
    var E = new Engine(d), SHOW = 48, shown = SHOW;
    var el = {
      side: root.querySelector('[data-f=side]'),
      chips: root.querySelector('[data-f=chips]'),
      count: root.querySelector('[data-f=count]'),
      res: root.querySelector('[data-f=res]'),
      more: root.querySelector('[data-f=more]'),
      sort: root.querySelector('[data-f=sort]'),
      q: root.querySelector('[data-f=q]'),
      qclear: root.querySelector('[data-f=qclear]'),
      bar: root.querySelector('[data-f=bar]'),
      barCount: root.querySelector('[data-f=barcount]'),
      sheetBtn: root.querySelector('[data-f=apply]')
    };

    var GROUPS = [
      { k: 'g', label: 'Gender', open: true,
        opts: [[0, 'Boy'], [1, 'Girl']] },
      { k: 't', label: 'Meaning', open: true,
        opts: d.themes.map(function (t, i) { return [i, t[1]]; }) },
      { k: 'r', label: 'Where it is used', open: false,
        opts: d.regions.map(function (r, i) { return [i, r[1]]; }) },
      { k: 'e', label: 'English letter', open: false, wide: true,
        opts: (function () { var a = []; for (var c = 65; c <= 90; c++) a.push([String.fromCharCode(c), String.fromCharCode(c)]); return a; })() },
      { k: 'u', label: 'Urdu letter', open: false, rtl: true,
        opts: d.urdu.map(function (u, i) { return [i, u[1], u[2]]; }) }
    ];

    function buildSide() {
      el.side.innerHTML = GROUPS.map(function (g) {
        var body = '<div class="ff-opts' + (g.rtl ? ' rtl' : '') + (g.wide ? ' wide' : '') + '">' +
          g.opts.map(function (o) {
            return '<button type="button" class="ff-opt" data-k="' + g.k + '" data-v="' + esc(o[0]) +
              '" aria-pressed="false">' +
              (g.rtl ? '<span class="ff-ar" lang="ur" dir="rtl">' + esc(o[1]) + '</span>'
                     : '<span class="ff-l">' + esc(o[1]) + '</span>') +
              '<span class="ff-c"></span></button>';
          }).join('') + '</div>';
        return '<details class="ff-g" data-k="' + g.k + '"' + (g.open ? ' open' : '') + '>' +
          '<summary><span>' + esc(g.label) + '</span><span class="ff-sel"></span></summary>' +
          body + '</details>';
      }).join('');
    }

    function paintCounts() {
      GROUPS.forEach(function (g) {
        var c = E.counts(g.k);
        var det = el.side.querySelector('.ff-g[data-k="' + g.k + '"]');
        det.querySelectorAll('.ff-opt').forEach(function (b) {
          var raw = b.getAttribute('data-v');
          var v = (g.k === 'e') ? raw : parseInt(raw, 10);
          var n = c[v] || 0;
          var on = E.S[g.k].indexOf(v) >= 0;
          b.setAttribute('aria-pressed', on ? 'true' : 'false');
          b.querySelector('.ff-c').textContent = n ? nfmt(n) : '';
          b.disabled = (!on && n === 0);
          b.classList.toggle('ff-dead', !on && n === 0);
        });
        var sel = det.querySelector('.ff-sel');
        sel.textContent = E.S[g.k].length ? E.S[g.k].length + ' on' : '';
      });
    }

    function paintChips() {
      var parts = [];
      Object.keys(E.S).forEach(function (k) {
        E.S[k].forEach(function (v) {
          parts.push('<button type="button" class="ff-chip" data-k="' + k + '" data-v="' + esc(v) + '">' +
            '<span class="ff-chip-k">' + esc(LABEL[k]) + '</span>' +
            esc(optionLabel(d, k, v)) + '<span class="ff-x" aria-hidden="true">&times;</span>' +
            '<span class="ff-sr">, remove filter</span></button>');
        });
      });
      if (parts.length) {
        parts.push('<button type="button" class="ff-clear" data-f="clear">Clear all</button>');
        el.chips.innerHTML = parts.join('');
        el.chips.hidden = false;
      } else { el.chips.innerHTML = ''; el.chips.hidden = true; }
    }

    function card(n) {
      return '<a class="ff-card ' + (n[4] === 0 ? 'b' : (n[4] === 1 ? 'g' : '')) + '" href="/names/' + n[0] + '/">' +
        '<span class="ff-ca" lang="ar" dir="rtl">' + esc(n[2]) + '</span>' +
        '<span class="ff-cn">' + esc(n[1]) + '</span>' +
        '<span class="ff-cm">' + esc(n[5]) + '</span></a>';
    }

    function render() {
      var rows = E.results();
      var total = rows.length;
      var label = total === 0 ? 'No names match' : (total === 1 ? '1 name' : nfmt(total) + ' names');
      el.count.textContent = label;
      if (el.barCount) el.barCount.textContent = label;
      if (el.sheetBtn) el.sheetBtn.textContent = total ? 'Show ' + label : 'No matches';
      if (!total) {
        var b = E.blame();
        el.res.innerHTML = '<div class="ff-empty"><p>Nothing carries all of those at once.</p>' +
          (b ? '<p>Drop <strong>' + esc(LABEL[b.k]) + '</strong> and ' + nfmt(b.n) +
               ' names come back. <button type="button" class="ff-undo" data-f="drop" data-k="' +
               b.k + '">Remove that filter</button></p>' : '') + '</div>';
        el.more.hidden = true;
      } else {
        if (shown > total) shown = Math.max(SHOW, Math.min(shown, total));
        el.res.innerHTML = rows.slice(0, shown).map(card).join('');
        var left = total - shown;
        el.more.hidden = left <= 0;
        if (left > 0) el.more.textContent = 'Show ' + nfmt(Math.min(SHOW, left)) + ' more';
      }
      writeHash();
    }

    function writeHash() {
      var parts = [];
      Object.keys(E.S).forEach(function (k) { if (E.S[k].length) parts.push(k + '=' + encodeURIComponent(E.S[k].join(','))); });
      var h = parts.join('&');
      var target = h ? '#' + h : location.pathname;
      if ((location.hash.replace(/^#/, '')) !== h) history.replaceState(null, '', target);
    }
    function readHash() {
      var h = location.hash.replace(/^#/, '');
      E.S = { g: [], e: [], u: [], t: [], r: [] };
      if (!h) return;
      h.split('&').forEach(function (p) {
        var i = p.indexOf('='); if (i < 0) return;
        var k = p.slice(0, i); if (!(k in E.S)) return;
        E.S[k] = decodeURIComponent(p.slice(i + 1)).split(',').filter(Boolean)
          .map(function (v) { return k === 'e' ? v : parseInt(v, 10); });
      });
    }

    function toggle(k, v) {
      var i = E.S[k].indexOf(v);
      if (i >= 0) E.S[k].splice(i, 1); else E.S[k].push(v);
      shown = SHOW; paintCounts(); paintChips(); render();
    }

    root.addEventListener('click', function (ev) {
      var t = ev.target;
      var opt = t.closest ? t.closest('.ff-opt') : null;
      if (opt && !opt.disabled) {
        ev.preventDefault();
        var k = opt.getAttribute('data-k'), raw = opt.getAttribute('data-v');
        return toggle(k, k === 'e' ? raw : parseInt(raw, 10));
      }
      var chip = t.closest ? t.closest('.ff-chip') : null;
      if (chip) {
        ev.preventDefault();
        var ck = chip.getAttribute('data-k'), cr = chip.getAttribute('data-v');
        return toggle(ck, ck === 'e' ? cr : parseInt(cr, 10));
      }
      var drop = t.closest ? t.closest('[data-f=drop]') : null;
      if (drop) { E.S[drop.getAttribute('data-k')] = []; shown = SHOW; paintCounts(); paintChips(); render(); return; }
      if (t.closest && t.closest('[data-f=clear]')) {
        E.S = { g: [], e: [], u: [], t: [], r: [] };
        shown = SHOW; paintCounts(); paintChips(); render(); return;
      }
      if (t === el.more) { shown += SHOW; render(); }
    });

    if (el.q) {
      var deb;
      el.q.addEventListener('input', function () {
        clearTimeout(deb);
        deb = setTimeout(function () {
          E.q = el.q.value.trim().toLowerCase();
          if (el.qclear) el.qclear.hidden = !E.q;
          shown = SHOW; paintCounts(); render();
        }, 130);
      });
    }
    if (el.qclear) {
      el.qclear.addEventListener('click', function () {
        el.q.value = ''; E.q = ''; el.qclear.hidden = true;
        shown = SHOW; paintCounts(); render(); el.q.focus();
      });
    }
    if (el.sort) {
      el.sort.addEventListener('change', function () {
        E.sort = el.sort.value; shown = SHOW; render();
      });
    }

    window.addEventListener('hashchange', function () {
      readHash(); shown = SHOW; paintCounts(); paintChips(); render();
    });

    /* mobile sheet */
    var openBtn = root.querySelector('[data-f=open]');
    function setSheet(on) {
      root.classList.toggle('ff-sheet-open', on);
      document.body.classList.toggle('asr-modal-open', on);
      if (openBtn) openBtn.setAttribute('aria-expanded', on ? 'true' : 'false');
    }
    if (openBtn) openBtn.addEventListener('click', function () { setSheet(true); });
    root.querySelectorAll('[data-f=close],[data-f=apply]').forEach(function (b) {
      b.addEventListener('click', function () { setSheet(false); });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && root.classList.contains('ff-sheet-open')) setSheet(false);
    });

    buildSide(); readHash(); paintCounts(); paintChips(); render();
    root.querySelector('[data-f=app]').hidden = false;
    var nojs = root.querySelector('[data-f=nojs]');
    if (nojs) nojs.hidden = true;
  }

  /* ---------------------------------------------------------- home finder */
  function mountMini(root, d) {
    var E = new Engine(d);
    var res = root.querySelector('[data-f=res]'),
        cnt = root.querySelector('[data-f=count]'),
        go = root.querySelector('[data-f=go]');

    function render() {
      var rows = E.results(), total = rows.length;
      cnt.textContent = total === 0 ? 'No names match that combination'
        : (total === 1 ? '1 name' : nfmt(total) + ' names');
      res.innerHTML = rows.slice(0, 8).map(function (n) {
        return '<a class="ff-card ' + (n[4] === 0 ? 'b' : (n[4] === 1 ? 'g' : '')) + '" href="/names/' + n[0] + '/">' +
          '<span class="ff-ca" lang="ar" dir="rtl">' + esc(n[2]) + '</span>' +
          '<span class="ff-cn">' + esc(n[1]) + '</span>' +
          '<span class="ff-cm">' + esc(n[5]) + '</span></a>';
      }).join('');
      var parts = [];
      Object.keys(E.S).forEach(function (k) { if (E.S[k].length) parts.push(k + '=' + encodeURIComponent(E.S[k].join(','))); });
      go.href = '/names/find/' + (parts.length ? '#' + parts.join('&') : '');
      go.textContent = total > 8 ? 'Open all ' + nfmt(total) + ' in the full filter' : 'Open the full filter';
      root.querySelectorAll('.ff-opt').forEach(function (b) {
        var k = b.getAttribute('data-k'), raw = b.getAttribute('data-v');
        var v = (k === 'e') ? raw : parseInt(raw, 10);
        b.setAttribute('aria-pressed', E.S[k].indexOf(v) >= 0 ? 'true' : 'false');
      });
    }
    root.addEventListener('click', function (ev) {
      var opt = ev.target.closest ? ev.target.closest('.ff-opt') : null;
      if (!opt) return;
      ev.preventDefault();
      var k = opt.getAttribute('data-k'), raw = opt.getAttribute('data-v');
      var v = (k === 'e') ? raw : parseInt(raw, 10);
      var i = E.S[k].indexOf(v);
      if (k === 'g' || k === 't') { if (i >= 0) E.S[k] = []; else E.S[k] = [v]; }
      else { if (i >= 0) E.S[k].splice(i, 1); else E.S[k].push(v); }
      render();
    });
    root.querySelector('[data-f=app]').hidden = false;
    var nojs = root.querySelector('[data-f=nojs]');
    if (nojs) nojs.hidden = true;
    render();
  }

  function start() {
    var full = document.querySelector('[data-filter=full]');
    var mini = document.querySelector('[data-filter=mini]');
    if (!full && !mini) return;
    load().then(function (d) {
      if (full) mountFull(full, d);
      if (mini) mountMini(mini, d);
    }).catch(function () {
      [full, mini].forEach(function (r) {
        if (!r) return;
        var c = r.querySelector('[data-f=count]');
        if (c) c.textContent = 'Filter unavailable, use the lists below';
      });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
