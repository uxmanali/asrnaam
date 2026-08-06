/* AsrNaam geo/language auto-routing (Aug 2026).
 * Pakistan -> Urdu (/ur/...), Arabic-speaking countries -> Arabic (/ar/...).
 *
 * Principles:
 *  - An explicit user choice always wins and is remembered (asr-lang-pref).
 *  - At most one automatic redirect per browser session (no ping-pong).
 *  - Redirect only when this page declares a matching hreflang alternate.
 *  - Browser language is checked first (instant, private); IP country via
 *    get.geojs.io only when the browser language is inconclusive.
 *  - Country result cached 30 days (asr-geo-cc) to avoid repeat lookups.
 *  - Search-engine crawlers are unaffected in practice (US-based crawling,
 *    and hreflang already maps the language versions).
 */
(function () {
  "use strict";
  var LS, SS;
  try { LS = window.localStorage; SS = window.sessionStorage; } catch (e) { return; }

  var ARABIC = { SA:1, AE:1, EG:1, DZ:1, MA:1, TN:1, LY:1, JO:1, IQ:1, SY:1,
                 LB:1, KW:1, QA:1, BH:1, OM:1, YE:1, SD:1, PS:1, MR:1, SO:1,
                 DJ:1, KM:1 };

  function get(k) { try { return LS.getItem(k); } catch (e) { return null; } }
  function set(k, v) { try { LS.setItem(k, v); } catch (e) {} }

  /* Record explicit language choices: any click on a link into another
     language version pins that language. Runs on every page. */
  document.addEventListener("click", function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest("a[href]") : null;
    if (!a) return;
    var href = a.getAttribute("href") || "";
    if (/^\/ur\//.test(href)) set("asr-lang-pref", "ur");
    else if (/^\/ar\//.test(href)) set("asr-lang-pref", "ar");
    else if (/^\/hi\//.test(href)) set("asr-lang-pref", "hi");
    else if (/^\/(names|blog|letters|basaair|aathaar|athar)?\/?/.test(href) &&
             !/^\/(ur|ar|hi)\//.test(href) &&
             /^(ur|ar|hi)$/.test(document.documentElement.lang)) {
      set("asr-lang-pref", "en");
    }
  }, true);

  /* Auto-routing runs only on English pages. */
  if (document.documentElement.lang !== "en") return;

  var pref = get("asr-lang-pref");
  if (pref === "en") return;
  try { if (SS.getItem("asr-geo-done")) return; } catch (e) {}

  function altFor(lang) {
    var l = document.querySelector('link[rel="alternate"][hreflang="' + lang + '"]');
    return l && l.href ? l.href : null;
  }
  if (!altFor("ur") && !altFor("ar") && !altFor("hi")) return;

  function go(lang) {
    var target = altFor(lang);
    if (!target || target === location.href) return false;
    try { SS.setItem("asr-geo-done", "1"); } catch (e) {}
    location.replace(target);
    return true;
  }

  /* A previously pinned ur/ar/hi preference routes immediately. */
  if (pref === "ur" || pref === "ar" || pref === "hi") { go(pref); return; }

  /* 1. Browser language — decisive when it names ur, ar or hi.
     (India is deliberately routed by language, not geography: Indian
     visitors arriving on Urdu-meaning queries should keep Urdu/English.) */
  var langs = (navigator.languages || [navigator.language || ""]).join(",").toLowerCase();
  if (/(^|,)\s*ur\b/.test(langs)) { go("ur"); return; }
  if (/(^|,)\s*ar\b/.test(langs)) { go("ar"); return; }
  if (/(^|,)\s*hi\b/.test(langs)) { go("hi"); return; }

  /* 2. IP country (cached 30 days). */
  var cached = get("asr-geo-cc"), cachedAt = parseInt(get("asr-geo-at") || "0", 10);
  function route(cc) {
    if (cc === "PK") go("ur");
    else if (ARABIC[cc]) go("ar");
  }
  if (cached && Date.now() - cachedAt < 30 * 864e5) { route(cached); return; }

  fetch("https://get.geojs.io/v1/ip/country.json")
    .then(function (r) { return r.json(); })
    .then(function (j) {
      if (j && j.country && /^[A-Z]{2}$/.test(j.country)) {
        set("asr-geo-cc", j.country); set("asr-geo-at", String(Date.now()));
        route(j.country);
      }
    })
    .catch(function () {});
})();
