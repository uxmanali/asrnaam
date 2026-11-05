// Reader regression test (DA-2.5). Run from the repo root with: python3 -m http.server 8765 & node tests/reader-parser.test.js
// Uses Playwright. Checks: multi-word names read every word, doubled letters in Arabic script are not an error, no console errors.
const { chromium } = require('playwright');
const cases = [ ['Rahman', 6], ['Abdul Rahman', null], ['Hassan', null], ['محمد', null], ['الله', null] ];
(async () => {
  const b = await chromium.launch(); const p = await b.newPage(); const errs = [];
  p.on('pageerror', e => errs.push(String(e)));
  let fail = 0; const counts = {};
  for (const [name] of cases) {
    await p.goto('http://localhost:8765/reader/?name=' + encodeURIComponent(name) + '&t=' + Date.now());
    await p.waitForSelector('.qf-row', { timeout: 8000 });
    const n = await p.evaluate(() => { const r = [...document.querySelectorAll('.qf-row')].find(x => /Letters/.test(x.textContent)); return r ? parseInt(r.querySelector('.qf-value').textContent, 10) : -1; });
    counts[name] = n; console.log(name, n);
  }
  if (!(counts['Abdul Rahman'] > counts['Rahman'])) { console.log('FAIL: multi-word name not fully read'); fail++; }
  if (!(counts['الله'] >= 4)) { console.log('FAIL: repeated Arabic letters not preserved (Allah)'); fail++; }
  if (!(counts['Hassan'] >= 4)) { console.log('NOTE: Hassan reads', counts['Hassan'], 'letters'); }
  if (errs.length) { console.log('FAIL: page errors', errs); fail++; }
  await b.close(); process.exit(fail ? 1 : 0);
})();
