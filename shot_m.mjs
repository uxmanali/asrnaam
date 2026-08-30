import { chromium } from 'playwright';
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
for(const [u,n] of [['/','home'],['/names/find/','find'],['/ar/names/zainul/','ar-zainul'],['/names/rabia/','rabia']]){
 for(const s of ['light','dark']){
  const ctx=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true,colorScheme:s});
  const p=await ctx.newPage(); await p.goto('http://127.0.0.1:8899'+u,{waitUntil:'networkidle'}); await p.waitForTimeout(600);
  // type into the first search box so we see real typed text
  const inp=await p.$('input[type=search],input[type=text]');
  if(inp){ try{ await inp.fill('Aisha'); }catch(e){} }
  await p.waitForTimeout(300);
  await p.screenshot({path:`/home/claude/m-${n}-${s}.png`});
  await ctx.close();
 }
}
await b.close(); console.log('ok');
