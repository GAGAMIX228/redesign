"""Measure real compressed response bodies, including explicit offline download."""
import asyncio
from playwright.async_api import async_playwright
from common import *
async def main():
    responses=[]
    async with async_playwright() as pw:
        b=await launch(pw);c=await b.new_context(viewport={'width':375,'height':812},reduced_motion='reduce');p=await c.new_page()
        def response(r):
            if not r.from_service_worker:responses.append({'url':r.url,'bytes':int(r.headers.get('content-length','0'))})
        c.on('response',response);await p.goto(BASE);await settle(p);await p.wait_for_timeout(3000)
        initial=sum(r['bytes'] for r in responses);initial_count=len(responses)
        await scroll_all(p);await p.wait_for_timeout(400);full=sum(r['bytes'] for r in responses)
        await p.locator('[data-offline-save]').click();await p.wait_for_function("document.querySelector('[data-offline-save]').textContent.includes('Обновить')");await p.wait_for_timeout(100);total=sum(r['bytes'] for r in responses)
        await b.close()
    save('09-weight',{'measurement':'Compressed Content-Length response bodies, excluding HTTP headers. First visit, fresh browser storage.','first_screen_3s':initial,'first_screen_requests':initial_count,'home_after_complete_scroll':full,'additional_explicit_offline_download':total-full,'total_with_requested_offline_copy':total,'ordinary_page_below_500_KiB':initial<500*1024,'responses':responses})
asyncio.run(main())
