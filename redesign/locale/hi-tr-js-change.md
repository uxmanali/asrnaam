# Script change needed for the Hindi and Turkish name pages (not applied; asr-redesign.js is not this agent's file)

## Why

`asr-redesign.js` treats any page with a `.asr-name-hero` as a name page. The old Hindi and Turkish pages had no such hero, so the
script did nothing on them. The migrated pages use the shared hero, so the script now adds, in English:

- the play button, whose two lines are both the H1 cut at the first comma ("मंसूर नाम का मतलब"), with the label "Play pronunciation";
- the Save and Share buttons ("Save", "Saved", "Share");
- on phones, the bottom bar "Search another name", whose search goes to the English /reader/.

## The change (8 small edits, 14 lines)

The migrated pages already carry the translated words on the article:
`data-l-name` (the name in the page's own script), `data-l-save`, `data-l-saved`, `data-l-share`, `data-l-play`.
The script reads them and falls back to today's English when they are absent, so English, Urdu and Arabic pages behave exactly as now.
The phone bar is not built on a translated page unless the page carries `data-l-search` (none does yet), because its search leads to an English page.

Tested in a browser with the patched file swapped in for the request (repo file untouched): hi/names/mansur, hi/names/kainat,
tr/names/hatice show the translated play, Save and Share labels; English pages unchanged. After applying, bump the `?v=` tag (VER in np_build.py).

```diff
--- asr-redesign.js	2026-11-22 19:08:35.883487978 +1100
+++ asr-redesign.js (proposed)	2026-11-22 19:30:29.765653801 +1100
@@ -168,6 +168,12 @@
     updateBadges();
   }
 
+  /* Labels for translated name pages: the page carries them as data-l-* on the article (redesign/locale/<lang>.json). */
+  function L(key, fallback) {
+    var art = document.querySelector('.asr-np');
+    var v = art && art.getAttribute('data-l-' + key);
+    return v || fallback;
+  }
   function nameEntryFromPage() {
     var card = document.getElementById('asr-namecard');
     var data = {};
@@ -179,7 +185,7 @@
     var ur = document.querySelector('[data-asr-field="urdu"]');
     return {
       slug: slugFromPath(),
-      name: (data.english || pageName()),
+      name: (data.english || L('name', '') || pageName()),
       meaning: meaning,
       arabic: data.arabic || (document.querySelector('.asr-name-hero-arabic, .arabic-name') || {}).textContent || '',
       urdu: (ur && ur.textContent.trim()) || data.urdu || '',
@@ -195,9 +201,9 @@
     var btn = document.createElement('button');
     btn.type = 'button';
     btn.className = 'rd-play';
-    btn.setAttribute('aria-label', 'Play pronunciation');
+    btn.setAttribute('aria-label', L('play', 'Play pronunciation'));
     var pron = document.querySelector('[data-asr-field="pronunciation"], .asr-pronunciation strong');
-    var label = pron ? pron.textContent.trim() : entry.name;
+    var label = pron ? pron.textContent.trim() : L('play', entry.name);
     btn.innerHTML = '<span class="play" aria-hidden="true"><svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg></span><span><b>' +
       esc(entry.name) + '</b><small>' + esc(label) + '</small></span>';
     btn.addEventListener('click', function () {
@@ -275,7 +281,7 @@
       var on = getFavs().some(function (e) { return e.slug === entry.slug; });
       btn.setAttribute('aria-pressed', on ? 'true' : 'false');
       var span = btn.querySelector('span');
-      if (span) span.textContent = on ? 'Saved' : 'Save';
+      if (span) span.textContent = on ? L('saved', 'Saved') : L('save', 'Save');
       btn.classList.toggle('on', on);
     }
     var host = document.querySelector('.asr-name-hero, article > .hero, main > .hero');
@@ -294,7 +300,7 @@
       var btn = document.createElement('button');
       btn.type = 'button';
       btn.className = 'rd-btn asr-fav';
-      btn.innerHTML = heartSVG(true) + '<span>Save</span>';
+      btn.innerHTML = heartSVG(true) + '<span>' + esc(L('save', 'Save')) + '</span>';
       btn.addEventListener('click', function () {
         toggleFav(entry);
         paint(btn);
@@ -306,7 +312,7 @@
       var share = document.createElement('button');
       share.type = 'button';
       share.className = 'rd-btn rd-share asr-share';
-      share.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/></svg><span>Share</span>';
+      share.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/></svg><span>' + esc(L('share', 'Share')) + '</span>';
       share.addEventListener('click', function () {
         var url = location.href;
         var text = (entry.name || document.title) + ' ' + url;
@@ -350,6 +356,8 @@
 
   function mobileBar() {
     if (!isNamePage() || document.querySelector('.rd-mbar')) return;
+    // the bar's search goes to the English reader: translated pages show it only once they carry a label for it
+    if (L('name', '') && !L('search', '')) return;
     var bar = document.createElement('div');
     bar.className = 'rd-mbar';
     bar.innerHTML =
```

## Not covered by this change

- The heart in the site header links to /favourites/, an English page, and a saved name opens the English name page.
  Turkish-only names (no English page of the same slug) would open a missing page from there.
- `asr-ads.js` labels its slots "Advertisement" and `asr-theme.js` labels the theme button "Toggle theme", in English, on every language.
