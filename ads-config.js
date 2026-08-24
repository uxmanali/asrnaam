/* AsrNaam ad configuration. This is the only file to edit to switch ads on.
 *
 * 1. Get approved by AdSense.
 * 2. Put the publisher ID in `client` below. It is shown in AdSense under
 *    Account -> Settings -> Account information and looks like
 *    ca-pub-1234567890123456.
 * 3. Create two display units in AdSense (Ads -> By ad unit -> Display ads).
 *    Name them something you will recognise, e.g. "in-article" and
 *    "below-content". Each gives you a numeric slot ID. Paste them below.
 * 4. Put the same publisher ID into /ads.txt.
 *
 * Leave `client` empty and the site behaves exactly as it does now: no ad
 * requests, no reserved space, no third-party script.
 */
window.ASR_ADS = {
  client: '',            // e.g. 'ca-pub-1234567890123456'
  slots: {
    inArticle: '',       // numeric slot ID for the unit under the answer block
    belowContent: ''     // numeric slot ID for the unit above the FAQ
  }
};
