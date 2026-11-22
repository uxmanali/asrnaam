# Site script change needed for the translated name pages

`asr-redesign.js` writes five interface strings in English on every name page: the play button label,
Save, Saved, Share, and "Search another name" in the phone bar. The redesigned Urdu and Arabic pages carry
their own wording on the article element (`data-l-play`, `data-l-save`, `data-l-saved`, `data-l-share`,
`data-l-search`) and the name to show on the play button (`data-np-name`). The script has to read them.

- English pages have none of these attributes, so every string falls back to today's English text: no change there.
- Without this change the Urdu and Arabic pages still work, but show "Save" and "Share" in English, and the
  Arabic play button shows the whole H1 sentence instead of the name.
- The last hunk also stops the phone share text ending in the English words "name meaning" on pages that have
  no `data-asr-field="meaning-dict"` (every translated page): it shares the page title instead.
- The play button drops its second line when it would only repeat the name (Arabic pages, which have no stress guide).
- After applying, bump `VER` in `redesign/np_build.py` and rebuild, so no stored copy of the old script is used.

Tested with this exact patch served in place of the script (22 Nov 2026): Urdu and Arabic pages show the
translated labels, English `/names/hatice/` is unchanged, no console errors.

```diff
--- asr-redesign.js
+++ asr-redesign.js (proposed)
@@ -72,7 +72,14 @@
     if (document.getElementById('asr-namecard') || document.querySelector('.asr-name-hero')) return true;
     return !!(document.querySelector('.arabic-name') && document.querySelector('.asr-v2-letters'));
   }
+  /* Translated name pages carry their interface labels and the name on the article (data-l-*, data-np-name). */
+  function uiText(key, fallback) {
+    var art = document.querySelector('.asr-np');
+    return (art && art.getAttribute('data-l-' + key)) || fallback;
+  }
   function pageName() {
+    var art = document.querySelector('.asr-np[data-np-name]');
+    if (art) return art.getAttribute('data-np-name');
     var h = document.querySelector('h1');
     if (!h) return slugFromPath() || '';
     var t = (h.textContent || '').split('—')[0].split('|')[0].split(',')[0].trim();
@@ -195,11 +202,11 @@
     var btn = document.createElement('button');
     btn.type = 'button';
     btn.className = 'rd-play';
-    btn.setAttribute('aria-label', 'Play pronunciation');
+    btn.setAttribute('aria-label', uiText('play', 'Play pronunciation'));
     var pron = document.querySelector('[data-asr-field="pronunciation"], .asr-pronunciation strong');
     var label = pron ? pron.textContent.trim() : entry.name;
     btn.innerHTML = '<span class="play" aria-hidden="true"><svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg></span><span><b>' +
-      esc(entry.name) + '</b><small>' + esc(label) + '</small></span>';
+      esc(entry.name) + '</b>' + (label && label !== entry.name ? '<small>' + esc(label) + '</small>' : '') + '</span>';
     btn.addEventListener('click', function () {
       if (audio) { audio.play(); return; }
       var said = speak(entry.arabic || entry.name);
@@ -275,7 +282,7 @@
       var on = getFavs().some(function (e) { return e.slug === entry.slug; });
       btn.setAttribute('aria-pressed', on ? 'true' : 'false');
       var span = btn.querySelector('span');
-      if (span) span.textContent = on ? 'Saved' : 'Save';
+      if (span) span.textContent = on ? uiText('saved', 'Saved') : uiText('save', 'Save');
       btn.classList.toggle('on', on);
     }
     var host = document.querySelector('.asr-name-hero, article > .hero, main > .hero');
@@ -294,7 +301,7 @@
       var btn = document.createElement('button');
       btn.type = 'button';
       btn.className = 'rd-btn asr-fav';
-      btn.innerHTML = heartSVG(true) + '<span>Save</span>';
+      btn.innerHTML = heartSVG(true) + '<span>' + esc(uiText('save', 'Save')) + '</span>';
       btn.addEventListener('click', function () {
         toggleFav(entry);
         paint(btn);
@@ -306,7 +313,7 @@
       var share = document.createElement('button');
       share.type = 'button';
       share.className = 'rd-btn rd-share asr-share';
-      share.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/></svg><span>Share</span>';
+      share.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/></svg><span>' + esc(uiText('share', 'Share')) + '</span>';
       share.addEventListener('click', function () {
         var url = location.href;
         var text = (entry.name || document.title) + ' ' + url;
@@ -354,12 +361,12 @@
     bar.className = 'rd-mbar';
     bar.innerHTML =
       '<form class="in" action="/reader/" method="get" role="search">' +
-      '<label class="rd-sr" for="rd-m-q">Search another name</label>' +
+      '<label class="rd-sr" for="rd-m-q">' + esc(uiText('search', 'Search another name')) + '</label>' +
       '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3-3"/></svg>' +
-      '<input id="rd-m-q" name="name" type="search" placeholder="Search another name" enterkeyhint="search">' +
+      '<input id="rd-m-q" name="name" type="search" placeholder="' + esc(uiText('search', 'Search another name')) + '" enterkeyhint="search">' +
       '</form>' +
-      '<button type="button" class="h" aria-label="Save to favourites" aria-pressed="false">' + heartSVG(true) + '</button>' +
-      '<button type="button" class="s" aria-label="Share">' +
+      '<button type="button" class="h" aria-label="' + esc(uiText('save', 'Save to favourites')) + '" aria-pressed="false">' + heartSVG(true) + '</button>' +
+      '<button type="button" class="s" aria-label="' + esc(uiText('share', 'Share')) + '">' +
       '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/></svg></button>';
     document.body.appendChild(bar);
     document.body.classList.add('rd-hasbar');
@@ -373,7 +380,7 @@
     paint();
     bar.querySelector('.s').addEventListener('click', function () {
       var url = location.href;
-      var text = entry.name + ' — ' + (entry.meaning || 'name meaning') + ' ' + url;
+      var text = (entry.meaning ? entry.name + ' — ' + entry.meaning : document.title) + ' ' + url;
       if (navigator.share) {
         navigator.share({ title: document.title, text: text, url: url }).catch(function () {});
       } else {
```
