"""Sections 2–4 and 14–15: real Chromium interaction and layout matrix."""
import argparse, asyncio, urllib.parse
from playwright.async_api import async_playwright
from common import *
async def main(part):
    errors=[];requests=[];responses=[];failures=[];tested=[]
    async with async_playwright() as pw:
        b=await launch(pw);c=await b.new_context(viewport={'width':1366,'height':900},reduced_motion='reduce',service_workers='block')
        await c.add_init_script("window.__printCount=0;window.print=()=>window.__printCount++;window.alert=()=>window.__alertCount=(window.__alertCount||0)+1;")
        p=await c.new_page()
        p.on('pageerror',lambda e:errors.append({'page':p.url,'type':'exception','message':str(e)}))
        p.on('console',lambda m:errors.append({'page':p.url,'type':m.type,'message':m.text}) if m.type in ['error','warning'] and 'service worker' not in m.text.lower() else None)
        p.on('request',lambda r:requests.append(r.url) if r.url.startswith('http') and not r.url.startswith(BASE) else None)
        p.on('response',lambda r:responses.append({'url':r.url,'status':r.status}) if r.status>=400 else None)
        if part=='buttons':
            buttons=[]
            for f in PAGES:
                await p.goto(BASE+route(f));await settle(p)
                await p.locator('button').evaluate_all('es=>es.forEach((e,i)=>e.dataset.auditButton=i)')
                count=await p.locator('button').count()
                for i in range(count):
                    el=p.locator('[data-audit-button="'+str(i)+'"]')
                    if not await el.count():continue
                    label=(await el.inner_text() or await el.get_attribute('aria-label') or '').strip()
                    row={'page':f,'index':i,'label':label}
                    if not await el.is_visible() or not await el.is_enabled():row['status']='hidden_or_disabled';buttons.append(row);continue
                    before=await p.evaluate('document.body.outerHTML+location.href+window.__printCount')
                    try:
                        await el.click(timeout=2000);await p.wait_for_timeout(80)
                        after=await p.evaluate('document.body.outerHTML+location.href+window.__printCount')
                        row['status']='changed' if before!=after else 'no_change'
                        if row['status']=='no_change':row['reason']='May already be selected/reset. Covered separately by state-specific scenarios.'
                    except Exception as exc:row.update(status='failed',reason=str(exc)[:180])
                    buttons.append(row)
                    # Restore transient modal state so later controls stay reachable.
                    await p.keyboard.press('Escape')
                    await p.evaluate("localStorage.removeItem('urfu:a11y');document.body.removeAttribute('data-a11y');")
                tested.append(f)
            save('02-buttons',{'pages':len(tested),'buttons':buttons,'clicked':sum(x['status'] in ['changed','no_change'] for x in buttons),'failures':[x for x in buttons if x['status']=='failed'],'unexplained':[x for x in buttons if x['status']=='no_change'],'console':errors})
        elif part=='console':
            for f in PAGES:
                await p.goto(BASE+route(f));await settle(p);await scroll_all(p);tested.append(f)
            # Storage getter failures must not abort initialization on any page.
            blocked=await b.new_context(reduced_motion='reduce',service_workers='block')
            await blocked.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw Error('Storage blocked')}})")
            q=await blocked.new_page();q.on('pageerror',lambda e:errors.append({'mode':'storage blocked','message':str(e)}))
            for f in PAGES:await q.goto(BASE+route(f));await settle(q)
            nojs=await b.new_context(java_script_enabled=False,viewport={'width':375,'height':812},service_workers='block');q=await nojs.new_page()
            for f in PAGES:
                await q.goto(BASE+route(f));await settle(q)
                if not await q.locator('main').is_visible() or not await q.locator('h1').is_visible():failures.append({'mode':'no-js','page':f})
            file_status={}
            try:await p.goto((ROOT/'index.html').as_uri());file_status={'status':'opened'}
            except Exception as exc:file_status={'status':'blocked_by_browser_policy','reason':str(exc).splitlines()[0]}
            save('03-console',{'pages':tested,'console':errors,'failed_responses':responses,'external_requests':requests,'fallback_failures':failures,'file':file_status,'cookies':await c.cookies()})
        elif part=='layout':
            from PIL import Image,ImageDraw
            ss=Path('/tmp/urfu-check-screenshots');ss.mkdir(exist_ok=True)
            dimensions=[(w,900) for w in WIDTHS]+[(844,390),(683,450),(342,225)]
            for w,h in dimensions:
                await p.set_viewport_size({'width':w,'height':h});thumbs=[]
                for f in PAGES:
                    await p.goto(BASE+route(f));await settle(p)
                    r=await p.evaluate('''()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,clipped:[...document.querySelectorAll('h1,h2,h3,.btn,output')].filter(e=>{let s=getComputedStyle(e);return !e.closest('.sr-only')&&e.getClientRects().length&&s.overflowX==='hidden'&&e.scrollWidth>e.clientWidth+2}).map(e=>e.textContent.slice(0,80))})''')
                    if r['scroll']>w+1 or r['clipped']:failures.append({'page':f,'viewport':[w,h],**r})
                    path=ss/(f.replace('/','-')+'-'+str(w)+'x'+str(h)+'.jpg')
                    if os.environ.get('CHECK_NO_SCREENSHOTS'):
                        tested.append({'page':f,'viewport':[w,h],'screenshot':str(path)});continue
                    await p.screenshot(path=str(path),full_page=True,type='jpeg',quality=40)
                    im=Image.open(path);im.thumbnail((150,700));thumb=Image.new('RGB',(180,730),'#eeede5');thumb.paste(im,(15,25));ImageDraw.Draw(thumb).text((5,5),f,fill='black');thumbs.append(thumb)
                    tested.append({'page':f,'viewport':[w,h],'screenshot':str(path)})
                if not thumbs:print('Layout',w,h,'issues',len(failures),flush=True);continue
                sheet=Image.new('RGB',(180*8,730*4),'white')
                for i,im in enumerate(thumbs):sheet.paste(im,((i%8)*180,(i//8)*730))
                sheet.save(ROOT/'checks/screenshots'/f'matrix-{w}x{h}.jpg',quality=65)
                print('Layout',w,h,'issues',len(failures),flush=True)
            # Real default font-size setting, not CSS zoom emulation.
            for f in PAGES:
                await p.set_viewport_size({'width':320,'height':900});await p.goto(BASE+route(f));await p.add_style_tag(content='html{font-size:24px!important}')
                if await p.evaluate('document.documentElement.scrollWidth>innerWidth+1'):failures.append({'page':f,'default_font':24,'overflow':True})
            save('04-layout',{'combinations':len(tested),'screenshots':tested,'failures':failures,'note':'683px and 342px viewports test CSS reflow equivalent to 200% and 400% at 1366px; browser toolbar zoom and physical phones unavailable.'})
        await b.close()
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('part',choices=['buttons','console','layout']);asyncio.run(main(a.parse_args().part))
