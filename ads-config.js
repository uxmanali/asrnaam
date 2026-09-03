/* AsrNaam ad configuration. This is the only file to edit to switch ads on.
 *
 * 1. Publisher ID is set. The verification snippet is in the head of every
 *    page and /ads.txt names this seller.
 * 2. Both display units exist and are live. Ads serve.
 * 3. To stop all ads immediately, blank `client` below and deploy. The site
 *    then renders exactly as it did before AdSense: no ad requests, no
 *    reserved space, no third-party script. Blanking a single slot removes
 *    only that placement.
 * 4. /ads.txt names this publisher. If AdSense ever generates a different
 *    line at Sites -> asrnaam.com -> ads.txt, theirs wins.
 */
window.ASR_ADS = {
  client: 'ca-pub-4856363287006906',
  slots: {
    inArticle: '6326035469',       // display unit 'in-article', created 2026-09-01
    belowContent: '7237943255'     // display unit 'below-content', created 2026-09-01
  }
};
