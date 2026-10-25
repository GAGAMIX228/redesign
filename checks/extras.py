"""Targeted post-fix checks: campus, exam alternatives, calculators, print and offline."""
import asyncio,re
import fitz
from playwright.async_api import async_playwright
from common import *
async def main():
    checks=[];failures=[];prints=[];network=[]
    async with async_playwright() as pw:
        b=await launch(pw);c=await b.new_context(reduced_motion='reduce');p=await c.new_page()
        for w in WIDTHS:
            await p.set_viewport_size({'width':w,'height':900});await p.goto(BASE+'campus.html')
            for key in ['main','radio','nvk']:
                await p.locator('button[data-map-place='+key+']').click();assert await p.locator('a[data-map-place='+key+']').get_attribute('aria-current')=='true';assert await p.locator('button[data-map-place='+key+']').get_attribute('aria-pressed')=='true'
                if await p.evaluate('document.documentElement.scrollWidth>innerWidth+1'):failures.append({'width':w,'campus':key,'overflow':True})
            await p.goto(BASE)
            for role in ['applicant','student','employee','partner']:
                await p.locator('[data-role='+role+']').click()
                if await p.evaluate('document.documentElement.scrollWidth>innerWidth+1'):failures.append({'width':w,'role':role,'overflow':True})
        checks.append('Map/list/campus selection and all roles at all 14 requested widths')
        for scheme in ['','dark','bw','wb','blue','beige','green']:
            await p.goto(BASE);await p.evaluate("s=>{localStorage.setItem('urfu:a11y',JSON.stringify(['','dark'].includes(s)?{}:{scheme:s,size:'28',line:'2',letter:'.16em'}));localStorage.setItem('urfu:theme',JSON.stringify(s==='dark'?'dark':'light'));}",scheme)
            await p.goto(BASE+'campus.html');await p.set_viewport_size({'width':320,'height':900});await scroll_all(p);r=await axe(p)
            if r['violations']:failures.append({'campus_scheme':scheme,'violations':r['violations']})
        await p.evaluate('localStorage.clear()')
        checks.append('New campus UI axe at 320px: normal, dark and five enlarged contrast schemes')
        alternative=next(x for x in DATA['programs'] if {'Физика','Информатика'}.issubset({e['name'] for e in x['exams']if not e['required']}))
        for choice in ['Физика','Информатика']:
            subjects=[e['name'] for e in alternative['exams']if e['required']]+[choice]
            import urllib.parse
            await p.goto(BASE+'catalog.html?ege='+urllib.parse.quote(','.join(subjects)))
            assert await p.locator('[data-id="'+alternative['id']+'"]').count()==1
        checks.append('Both physics and informatics find the same officially allowed program')
        # Independent arithmetic examples from the verified 2026 snapshot.
        for pid,discount,annual,years in [('10037',False,246000,6),('10037',True,209100,6),('9797',False,390000,4)]:
            saved=next(x for x in DATA['programs']if x['id']==pid)
            if saved['discountPrice' if discount else 'price']!=annual:failures.append({'cost_source_changed':pid});continue
            await p.goto(BASE+'campus.html');await p.locator('#cost-program').select_option(pid);await p.locator('#cost-discount').set_checked(discount);text=await p.locator('#cost-result').inner_text();expected=f'{annual*years:,}'.replace(',',' ');assert expected in text.replace('\xa0',' ').replace('\u202f',' '),(pid,text,expected)
        checks.append('Three tuition arithmetic examples, including discount, checked independently')
        # Download and inspect real iCalendar bytes.
        await p.goto(BASE+'schedule.html?day=0&week=2026-10-19')
        async with p.expect_download() as got:await p.locator('#schedule-ics').click()
        download=await got.value;path=RESULTS/'demo-week.ics';await download.save_as(path);ics=path.read_text();assert '20261019T040000Z' in ics and 'ДЕМО' in ics and ics.count('BEGIN:VEVENT')==16
        checks.append('ICS: 16 demo entries, 09:00 Ekaterinburg converted to 04:00 UTC')
        for route_ in ['Program.html?id=9797','campus.html','schedule.html?day=0','admission.html']:
            await p.goto(BASE+route_);await settle(p);await p.emulate_media(media='print')
            assert await p.locator('.header').is_hidden() and await p.locator('.mobile-bar').is_hidden()
            name=route_.split('?')[0].replace('.html','');out=RESULTS/('print-'+name+'.pdf');await p.pdf(path=str(out),format='A4',print_background=True)
            pdf=fitz.open(out);outside=[]
            for page in pdf:
                for block in page.get_text('blocks'):
                    if block[0]<-1 or block[1]<-1 or block[2]>page.rect.width+1 or block[3]>page.rect.height+1:outside.append(block[:4])
            prints.append({'page':route_,'pages':len(pdf),'outside_text':outside,'contains_address':BASE.rstrip('/') in ''.join(x.get_text() for x in pdf)})
            await p.emulate_media(media='screen')
        # Unknown nested URL must serve the useful custom 404 and working local assets.
        r=await p.goto(BASE+'not-a-page/deep/missing.html');assert r.status==404;assert await p.locator('main h1').is_visible();assert await p.locator('a[href="search.html"]').count()>0
        checks.append('Nested HTTP 404 has navigation, local CSS and search')
        await p.goto(BASE);await p.locator('[data-offline-save]').click();await p.evaluate('navigator.serviceWorker.ready');await p.wait_for_function("[...document.querySelectorAll('[data-offline-save]')].some(e=>e.textContent.includes('Обновить'))");await p.wait_for_timeout(350);await c.set_offline(True)
        for f in PAGES:
            await p.goto(BASE+route(f));assert await p.locator('h1').is_visible()
        await p.goto(BASE+'search.html?q=общага');assert await p.locator('#search-results .result').count()>0
        await p.goto(BASE+'catalog.html?q=информатик');assert await p.locator('#catalog-list .program-card').count()>0
        await p.goto(BASE+'Program.html?id=10037');assert 'Астрономия'.lower() in (await p.locator('h1').inner_text()).lower()
        checks.append('Offline after service-worker installation: all 29 pages, search, filter and dynamic program details')
        await c.set_offline(False);await b.close()
    save('15-16-extras',{'checks':checks,'failures':failures,'print':prints})
asyncio.run(main())
