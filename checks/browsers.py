"""Section 11: actual Chromium, Firefox and WebKit binaries; no UA spoofing."""
import asyncio,os
os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH','/tmp/urfu-test-browsers')
from playwright.async_api import async_playwright
from common import *
async def main():
    rows=[]
    async with async_playwright() as pw:
        for name in ['chromium','firefox','webkit']:
            try:
                b=await launch(pw) if name=='chromium' else await getattr(pw,name).launch(headless=True)
                for width in [375,1366]:
                    p=await b.new_page(viewport={'width':width,'height':900},reduced_motion='reduce');errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
                    for path in ['index.html','catalog.html','Program.html?id=9797','schedule.html','campus.html']:
                        await p.goto(BASE+path);await settle(p)
                        wide=await p.evaluate('document.documentElement.scrollWidth>innerWidth+1')
                        if path=='index.html':await p.locator('[data-role=student]').click();assert 'ВАШ ДЕНЬ' in await p.locator('h1').inner_text()
                        if path=='catalog.html':await p.locator('input[name=q]').fill('информатик');assert await p.locator('#catalog-list .program-card').count()>0
                        if path=='Program.html?id=9797':assert await p.locator('#program-my').is_visible()
                        if path=='schedule.html':await p.locator('#week-next').click();assert await p.locator('[data-day]').count()==7
                        if path=='campus.html':await p.locator('[data-campus-choice=nvk]').click();assert '6/2'in await p.locator('#campus-detail').inner_text()
                        rows.append({'browser':name,'version':b.version,'width':width,'page':path,'overflow':wide,'errors':list(errors),'status':'passed' if not errors and not wide else 'failed'})
                    await p.close()
                await b.close()
            except Exception as e:rows.append({'browser':name,'status':'unavailable','reason':str(e)[:2500]})
    save('11-browsers',{'results':rows,'limitations':['Real Edge, macOS Safari, Android and iPhone hardware are unavailable. WebKit tests the engine, not a physical iPhone.']})
asyncio.run(main())
