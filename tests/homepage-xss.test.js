const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();let errs=[];p.on('pageerror',e=>errs.push(e.message));
for (const payload of ['<img src=x onerror="window.__x=1">Ali','Ali"><script>window.__x=1</script>',"Ja'far <b>x</b>"]) {
 await p.goto('http://localhost:8765/');await p.evaluate(()=>{window.__x=0});
 await p.fill('#yourName',payload);await p.fill('#fatherName','<img src=x onerror="window.__x=1">');await p.fill('#motherName','Aisha<svg onload="window.__x=1">');
 await p.evaluate(()=>generateReading());await p.waitForTimeout(2200);
 const r=await p.evaluate(()=>({x:window.__x,imgs:document.querySelectorAll('#results img,#results svg,#results script,#results b').length,len:document.getElementById('results').innerText.length}));
 console.log(JSON.stringify(payload),JSON.stringify(r));}
console.log('errors',errs.length,errs.slice(0,2));await b.close();})();
