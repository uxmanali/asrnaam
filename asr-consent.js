/* Consent Mode v2 defaults.
 *
 * Google requires a certified CMP before personalised ads may be served to
 * anyone in the EEA, the UK or Switzerland. A hand-rolled banner does not
 * qualify, so this file does not attempt one. What it does is set the correct
 * default state before any Google tag fires, which is the part that has to be
 * right from the first pageview and cannot be retro-fitted.
 *
 * Denied by default everywhere. Google's own certified CMP (free, enabled in
 * AdSense under Privacy & messaging once the account is approved) will call
 * gtag('consent','update',...) and lift these where the reader agrees.
 *
 * Analytics storage is granted outside those regions only, which keeps the
 * existing Google Analytics measurement working as it does today while
 * remaining conservative where the law is strictest.
 */
(function () {
  'use strict';
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;

  var EEA = ['AT','BE','BG','HR','CY','CZ','DK','EE','FI','FR','DE','GR','HU',
             'IE','IT','LV','LT','LU','MT','NL','PL','PT','RO','SK','SI','ES',
             'SE','IS','LI','NO','GB','CH'];

  gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'denied',
    wait_for_update: 500,
    region: EEA
  });

  gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'granted'
  });
})();
