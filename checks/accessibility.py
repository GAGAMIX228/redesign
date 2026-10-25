"""Section 7: WCAG A/AA in all templates and interactive/color states."""
import asyncio
from playwright.async_api import async_playwright
from common import *
async def main():
    rows=[]
    async with async_playwright() as pw:
        b=await launch(pw);p=await b.new_page(reduced_motion='reduce',service_workers='block')
        async def check(label):
            await settle(p);r=await axe(p);wide=await p.evaluate('document.documentElement.scrollWidth>innerWidth+1');rows.append({'state':label,'overflow':wide,**r})
            if r['violations'] or wide:print('ISSUE',label,[(x['id'],len(x['nodes']))for x in r['violations']],wide,flush=True)
        for w in [375,1366]:
            await p.set_viewport_size({'width':w,'height':900})
            for f in PAGES:
                await p.goto(BASE+route(f));await scroll_all(p);await check(f'{w}/{f}/top')
                await p.evaluate('scrollTo(0,(document.documentElement.scrollHeight-innerHeight)/2)');await check(f'{w}/{f}/middle')
            print('Axe templates complete',w,flush=True)
        for scheme in ['bw','wb','blue','beige','green','dark']:
            await p.set_viewport_size({'width':320,'height':900})
            await p.goto(BASE)
            await p.evaluate("s=>{localStorage.setItem('urfu:a11y',JSON.stringify(s==='dark'?{}:{scheme:s,size:'28',line:'2',letter:'.16em'}));localStorage.setItem('urfu:theme',JSON.stringify(s==='dark'?'dark':'light'));}",scheme)
            for f in PAGES:
                await p.goto(BASE+route(f));await scroll_all(p);await check(scheme+'/'+f)
            print('Axe scheme complete',scheme,flush=True)
        await p.evaluate('localStorage.clear()')
        for w in [375,1366]:
            await p.set_viewport_size({'width':w,'height':900});await p.goto(BASE)
            if w==375:await p.locator('.menu-toggle').click()
            else:await p.locator('.nav-group summary').first.click()
            await check(f'menu-open/{w}')
            await p.keyboard.press('Escape');await p.locator('[data-a11y-open]').first.click();await check(f'a11y-dialog/{w}');await p.keyboard.press('Escape')
            await p.goto(BASE+'catalog.html');await p.locator('[data-compare]').nth(0).check();await p.locator('[data-compare]').nth(1).check();await p.locator('#compare-open').click();await check(f'comparison/{w}');await p.keyboard.press('Escape')
            await p.locator('input[name=q]').fill('абракадабра');await check(f'empty-catalog/{w}')
            await p.locator('input[name=my]').fill('-5');await check(f'invalid-number/{w}')
            await p.goto(BASE+'search.html?q=общага');await check(f'search-results/{w}')
            await p.goto(BASE+'quiz.html')
            for step in range(3):
                await check(f'quiz-step-{step+1}/{w}');await p.locator('#quiz-next').click()
            await check(f'quiz-result/{w}')
        await b.close()
    save('07-accessibility',{'axe_version':'4.14.0','runs':len(rows),'results':rows,'violations':sum(len(r['violations']) for r in rows),'overflow_states':[r['state'] for r in rows if r['overflow']]})
asyncio.run(main())
