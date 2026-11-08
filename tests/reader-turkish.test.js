// Run: serve repo root on :8765 (python3 -m http.server 8765), then node tests/reader-turkish.test.js
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  const names = ['Eylül','Yağmur','Çağla','Şule','Işıl','Gökçe'];
  let fail = 0;
  for (const n of names) {
    await p.goto('http://localhost:8765/reader/?name=' + encodeURIComponent(n));
    await p.waitForTimeout(600);
    const inp = await p.inputValue('#reader-input').catch(() => '');
    const txt = await p.innerText('#reader-output').catch(() => '');
    const ok = inp.normalize('NFC') === n && /Turkish letters were read as/.test(txt);
    console.log(ok ? 'PASS' : 'FAIL', n, '| input kept:', inp);
    if (!ok) fail++;
  }
  await b.close(); process.exit(fail ? 1 : 0);
})();
