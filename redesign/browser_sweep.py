import asyncio, sys, json
sys.path.insert(0,'/tmp')
from playwright.async_api import async_playwright
PORT=sys.argv[1]; W=int(sys.argv[2]); paths=open(sys.argv[3]).read().split()
async def one(b, path, out):
    ctx=await b.new_context(viewport={'width':W,'height':844 if W<600 else 900}); pg=await ctx.new_page(); errs=[]
    pg.on('pageerror', lambda e: errs.append(str(e)[:120]))
    await pg.route('**/*', lambda r: r.abort() if 'localhost' not in r.request.url else r.continue_())
    try:
        await pg.goto(f'http://localhost:{PORT}/{path}', wait_until='load', timeout=20000); await pg.wait_for_timeout(250)
        r=await pg.evaluate("""()=>({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth,
          np:!!document.querySelector('.asr-np'),cards:document.querySelectorAll('.np-cards > *').length,
          secs:[...document.querySelectorAll('.asr-np section[id]')].map(s=>s.id).join(','),
          btn:[...document.querySelectorAll('.asr-fav span,.rd-share span')].map(e=>e.textContent).join('|'),
          h1:(document.querySelector('h1')||{}).textContent})""")
    except Exception as e:
        r={'err':str(e)[:100]}
    r['errs']=errs; out[path]=r; await ctx.close()
async def main():
    out={}
    async with async_playwright() as p:
        b=await p.chromium.launch(); sem=asyncio.Semaphore(6)
        async def run(x):
            async with sem: await one(b,x,out)
        await asyncio.gather(*[run(x) for x in paths]); await b.close()
    bad={k:v for k,v in out.items() if v.get('err') or v.get('errs') or v.get('sw',0)>v.get('cw',0)+1 or not v.get('np')}
    import collections
    print(len(out),'pages at',W,'| problems',len(bad)); [print(' ',k,v) for k,v in list(bad.items())[:8]]
    print(' sections:',collections.Counter(v.get('secs') for v in out.values()).most_common(4)); print(' buttons:',collections.Counter(v.get('btn') for v in out.values()).most_common(3)); print(' cards:',collections.Counter(v.get('cards') for v in out.values()).most_common(4))
asyncio.run(main())
