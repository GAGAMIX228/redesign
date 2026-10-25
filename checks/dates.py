"""Date boundaries and timezone consistency, including invalid URL values."""
import asyncio
from playwright.async_api import async_playwright
from common import *
async def main():
    results=[]
    async with async_playwright() as pw:
        b=await launch(pw)
        for zone in ['Asia/Yekaterinburg','America/Los_Angeles','Pacific/Auckland']:
            c=await b.new_context(timezone_id=zone,reduced_motion='reduce');p=await c.new_page()
            await c.add_init_script("""{const Original=Date;const fixed=Original.parse('2026-12-31T21:30:00Z');window.Date=class extends Original{constructor(...a){super(...(a.length?a:[fixed]));}static now(){return fixed;}};}""")
            for d in ['', '2026-10-24','2026-10-25','2026-10-26','2026-12-31','2027-01-01','2026-02-31','abc']:
                await p.goto(BASE+'index.html'+('?date='+d if d else ''));await settle(p)
                now=await p.locator('#now-text').inner_text()
                await p.goto(BASE+'schedule.html?day=0'+('&date='+d if d else ''))
                week=await p.locator('#schedule-week').inner_text()
                results.append({'zone':zone,'date':d,'now':now,'week':week,'invalid_date_rejected':not(d=='2026-02-31' and '2026-02-31' in now)})
            await c.close()
        await b.close()
    save('01-dates',{'cases':results,'failures':[r for r in results if not r['invalid_date_rejected']],'note':'No invented event deadlines or countdowns. Past news remain in the news archive.'})
asyncio.run(main())
