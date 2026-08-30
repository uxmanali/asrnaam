/* AsrNaam ad configuration. This is the only file to edit to switch ads on.
 *
 * 1. Publisher ID is set. The verification snippet is in the head of every
 *    page and /ads.txt names this seller.
 * 2. Nothing serves yet: slots below are empty, so asr-ads.js stays inert.
 * 3. Create two display units in AdSense (Ads -> By ad unit -> Display ads).
 *    Name them something you will recognise, e.g. "in-article" and
 *    "below-content". Each gives you a numeric slot ID. Paste them below.
 * 4. Put the same publisher ID into /ads.txt.
 *
 * Leave `client` empty and the site behaves exactly as it does now: no ad
 * requests, no reserved space, no third-party script.
 */
window.ASR_ADS = {
  client: 'ca-pub-4856363287006906',
  slots: {
    inArticle: '',       // numeric slot ID for the unit under the answer block
    belowContent: ''     // numeric slot ID for the unit above the FAQ
  }
};
