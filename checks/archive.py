"""Verify the unpacked review archive served using its own documented server."""
import asyncio
from playwright.async_api import async_playwright
from common import *
async def main():
    base=os.environ.get('ARCHIVE_BASE','http://127.0.0.1:4177/');errors=[];external=[];bad=[]
    async with async_playwright() as pw:
        b=await launch(pw);p=await b.new_page(reduced_motion='reduce');p.on('pageerror',lambda e:errors.append(str(e)));p.on('request',lambda r:external.append(r.url) if r.url.startswith('http') and not r.url.startswith(base) else None);p.on('response',lambda r:bad.append({'url':r.url,'status':r.status}) if r.status>=400 else None)
        for f in PAGES:await p.goto(base+route(f));await settle(p);assert await p.locator('h1').is_visible()
        await p.goto(base);await p.locator('[data-role=student]').click();assert 'ВАШ ДЕНЬ'in await p.locator('h1').inner_text()
        await p.goto(base+'catalog.html?q=информатик');assert await p.locator('#catalog-list .program-card').count()>0
        await p.goto(base+'Program.html?id=10037');assert 'АСТРОНОМИЯ'in (await p.locator('h1').inner_text()).upper()
        await p.goto(base+'search.html?q=общага');assert await p.locator('#search-results .result').count()>0
        await p.goto(base+'schedule.html?day=0');assert await p.locator('.schedule-item').count()==3
        await p.goto(base);await p.locator('[data-offline-save]').click();await p.wait_for_function("document.querySelector('[data-offline-save]').textContent.includes('Обновить')");await p.context.set_offline(True)
        await p.goto(base+'catalog.html');assert await p.locator('#catalog-list .program-card').count()==98
        await p.context.set_offline(False);await b.close()
    path=RESULTS/'15-archive.json';result=json.loads(path.read_text());result.update(http_pages=len(PAGES),errors=errors,external_requests=external,failed_responses=bad,scenarios='roles/catalog/program/search/schedule/offline passed',file_opening='blocked by managed-browser policy; not certified',status='passed' if not(errors or external or bad or result['crc_error'] or result['forbidden_files']) else 'failed');save('15-archive',result)
asyncio.run(main())
