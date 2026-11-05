# Consent configuration record

Recorded 5 Nov 2026 (UTC) from the repository files named below. Each line can be re-checked against the file.

Source: `asr-consent.js` (sets Consent Mode v2 defaults before any Google tag fires; it does not draw a banner).

| Consent state | Region | ad_storage | ad_user_data | ad_personalization | analytics_storage |
|---|---|---|---|---|---|
| Default | EEA, UK, Switzerland (country list in the file, with `wait_for_update: 500`) | denied | denied | denied | denied |
| Default | Everywhere else | denied | denied | denied | granted |

A certified consent platform (Google's own, enabled in AdSense under Privacy and messaging) is expected to call `gtag('consent','update', ...)` where a reader agrees. This record does not confirm that it is enabled; that setting is in the AdSense account and is the owner's.

Vendors and what they receive:

- Google Analytics 4: page views, approximate country, device and browser; the site search term and result count (`asr-search.js`) and the name on a saved card (`asr-share-card.js`) are sent as events.
- Google AdSense: loaded by `asr-ads.js` on pages that carry ad slots; cookies only where the reader has agreed.
- Google Fonts.
- get.geojs.io: country lookup for the language suggestion in `asr-geo-lang.js`; the country code is cached in the browser for 30 days.

The Privacy page (`/privacy/`) describes these states in plain words. Update this record whenever `asr-consent.js` or the vendor list changes.
