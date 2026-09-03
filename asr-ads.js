/* AsrNaam ad delivery.
 *
 * Inert until a publisher ID exists. Set window.ASR_ADS in /ads-config.js and
 * every slot below starts serving; leave it empty and the page renders exactly
 * as it does today, with no reserved gaps and no requests.
 *
 * Placement is deliberately conservative. The answer a searcher came for stays
 * above the fold and untouched: the first slot sits after it, the second below
 * the deep material. At this site's traffic the ranking cost of a shifted
 * layout would dwarf any RPM gained by crowding the top of the page.
 */
(function () {
  'use strict';
  var CFG = window.ASR_ADS || {};
  if (!CFG.client || !/^ca-pub-\d{10,}$/.test(CFG.client)) return;

  var SLOTS = CFG.slots || {};
  var LOADED = false;

  function el(tag, cls, attrs) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    for (var k in (attrs || {})) n.setAttribute(k, attrs[k]);
    return n;
  }

  /* A slot reserves its height before AdSense fills it, so nothing below it
     moves when the creative arrives. Cumulative Layout Shift is a ranking
     input; an unreserved ad is a self-inflicted wound. */
  function slot(name, label) {
    var id = SLOTS[name];
    if (!id) return null;
    var wrap = el('aside', 'asr-ad', {
      'aria-label': 'Advertisement', 'data-slot': name, 'role': 'complementary'
    });
    var tag = el('span', 'asr-ad-label');
    tag.textContent = label || 'Advertisement';
    var ins = el('ins', 'adsbygoogle', {
      'style': 'display:block',
      'data-ad-client': CFG.client,
      'data-ad-slot': id,
      'data-ad-format': 'auto',
      'data-full-width-responsive': 'true'
    });
    wrap.appendChild(tag);
    wrap.appendChild(ins);
    return wrap;
  }

  function push(node) {
    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch (e) { /* a blocked or failed ad must never break the page */ }
  }

  /* The AdSense library is already in the head of every page, put there for
     site verification during approval. Appending a second copy here loaded the
     same script twice on every page load: a wasted request and a second
     initialisation. Only inject it if, for some reason, it is absent. */
  function loadLibrary() {
    if (LOADED) return;
    LOADED = true;
    if (document.querySelector('script[src*="adsbygoogle.js"]')) return;
    var s = document.createElement('script');
    s.async = true;
    s.crossOrigin = 'anonymous';
    s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + CFG.client;
    document.head.appendChild(s);
  }

  /* ── FIX: an unfilled slot must not leave a labelled hole in the page ──
     A new account on a low-authority site will not fill every request, and
     Pakistan and India are among the cheapest inventory there is. Without this,
     an unfilled slot leaves a reserved gap with the word "Advertisement" above
     it and nothing underneath, which reads as broken rather than as empty.

     AdSense marks the <ins> data-ad-status="unfilled" when it declines to
     serve. We collapse the slot only while it is off screen. Collapsing a slot
     a reader is currently looking at would move the text under their thumb,
     and that shift counts against Core Web Vitals; one sitting below the fold
     costs nothing. */
  function watchFill(wrap) {
    var ins = wrap.querySelector('ins.adsbygoogle');
    if (!ins) return;
    var settled = false;
    function verdict() {
      if (settled) return;
      var st = ins.getAttribute('data-ad-status');
      if (st === 'filled') { settled = true; wrap.classList.add('is-filled'); return; }
      if (st !== 'unfilled') return;
      settled = true;
      var r = wrap.getBoundingClientRect();
      var onScreen = r.bottom > 0 && r.top < (window.innerHeight || 0);
      if (onScreen) { wrap.classList.add('is-unfilled-visible'); }
      else { wrap.classList.add('is-unfilled'); }
    }
    if ('MutationObserver' in window) {
      var mo = new MutationObserver(function () { verdict(); if (settled) mo.disconnect(); });
      mo.observe(ins, { attributes: true, attributeFilter: ['data-ad-status'] });
      setTimeout(function () { verdict(); mo.disconnect(); }, 6000);
    } else {
      setTimeout(verdict, 4000);
    }
  }

  /* Anchors are resolved by document position, not by which selector matched
     first. Otherwise the slot named "inArticle" can end up below the one named
     "belowContent", and the AdSense reports stop meaning what they say. */
  function anchors() {
    var seen = [], out = [];
    var sels = ['.asr-answer', '.asr-pa', '#reading', 'main .grid', 'main .ff-res',
                '.faq-list', '.l2-faq', '.asr-faq', '.home-faq'];
    for (var i = 0; i < sels.length; i++) {
      var n = document.querySelector(sels[i]);
      if (!n) continue;
      // an FAQ block is anchored on its container, so the ad sits above it
      if (/faq/i.test(sels[i]) && n.parentElement) n = n.parentElement;
      if (seen.indexOf(n) >= 0) continue;
      seen.push(n);
      out.push(n);
    }
    out.sort(function (a, b) {
      var pos = a.compareDocumentPosition(b);
      if (pos & Node.DOCUMENT_POSITION_FOLLOWING) return -1;
      if (pos & Node.DOCUMENT_POSITION_PRECEDING) return 1;
      return 0;
    });
    return out;
  }

  function top(n) {
    var r = n.getBoundingClientRect();
    return r.top + (window.pageYOffset || 0);
  }

  function place() {
    var a = anchors();
    if (!a.length) return;
    var first = a[0];
    // the second ad goes after the last anchor, provided it is far enough down
    // the page that the two do not stack
    var last = null;
    for (var i = a.length - 1; i > 0; i--) {
      if (top(a[i]) - top(first) > 700) { last = a[i]; break; }
    }
    var placed = 0;
    var s1 = slot('inArticle');
    if (s1 && first.parentNode) {
      first.parentNode.insertBefore(s1, first.nextSibling); push(s1); watchFill(s1); placed++;
    }
    var s2 = last ? slot('belowContent') : null;
    if (s2 && last.parentNode) {
      last.parentNode.insertBefore(s2, last.nextSibling); push(s2); watchFill(s2); placed++;
    }
    if (placed) loadLibrary();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', place);
  } else {
    place();
  }
})();
