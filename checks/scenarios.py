"""Section 10 and security input cases. Exercises the real UI and URL states."""
import asyncio,itertools,random,re
from playwright.async_api import async_playwright
from common import *
async def main():
    rows=[];errors=[]
    async with async_playwright() as pw:
        b=await launch(pw);p=await b.new_page(viewport={'width':375,'height':900},reduced_motion='reduce',service_workers='block')
        p.set_default_timeout(5000)
        p.on('pageerror',lambda e:errors.append(str(e)))
        p.on('dialog',lambda d:asyncio.create_task(d.dismiss()))
        async def case(name,fn):
            try:
                detail=await fn();rows.append({'case':name,'status':'passed','evidence':detail})
            except Exception as e:rows.append({'case':name,'status':'failed','reason':str(e)[:400]});print('FAIL',name,str(e)[:180],flush=True)
        for role in ['applicant','student','employee','partner']:
            async def run(role=role):
                await p.goto(BASE);await p.locator('[data-role='+role+']').click();h=await p.locator('h1').inner_text();a=await p.locator('.hero-actions .btn').get_attribute('href');await p.reload();assert await p.locator('[data-role='+role+']').get_attribute('aria-pressed')=='true';return {'headline':h,'primary':a,'remembered':True}
            await case('Role '+role,run)
        for value in ['', '0','150','240','310','999','-5','abc']:
            async def run(value=value):
                await p.goto(BASE+'catalog.html?my='+value);field=p.locator('input[name=my]');invalid=await field.get_attribute('aria-invalid');count=await p.locator('#catalog-list .program-card').count()
                if value in ['310','999','-5']:assert invalid=='true'
                if value=='abc':assert await p.locator('.field-error:visible').count()>0,'Malformed numeric URL was silently discarded'
                return {'count':count,'invalid':invalid}
            await case('Catalog score '+repr(value),run)
        for subject in ['Математика','Русский язык','Информатика','Физика','Обществознание','История','Биология','Химия','Литература','Иностранный язык','География']:
            async def run(subject=subject):
                await p.goto(BASE+'catalog.html');e=p.locator('input[name=ege][value="'+subject+'"]');await e.check();on=await p.locator('#catalog-list .program-card').count();await e.uncheck();assert await p.locator('#catalog-list .program-card').count()==len(DATA['programs']);return {'selected_count':on,'restored':len(DATA['programs'])}
            await case('Subject toggle '+subject,run)
        async def institute():
            await p.goto(BASE+'catalog.html');name='Политехнический институт (филиал) в г. Каменске-Уральском';await p.locator('select[name=institute]').select_option(name);ids=await p.locator('#catalog-list .program-card').evaluate_all('es=>es.map(e=>e.dataset.id)');assert '9812'in ids and '10117'in ids;return ids
        await case('Multi-institute programs remain in branch filters',institute)
        async def compare():
            await p.goto(BASE+'catalog.html');c=p.locator('[data-compare]')
            for i in range(3):await c.nth(i).check()
            await c.nth(3).click();assert not await c.nth(3).is_checked();await p.locator('#compare-open').click();assert await p.locator('#compare-table thead th').count()==4;await p.keyboard.press('Escape');url=await p.evaluate("location.href");await p.goto(url);assert await p.locator('[data-compare]:checked').count()==3;await p.locator('[data-compare]:checked').first.uncheck();await p.locator('#compare-clear').click();assert await p.locator('#compare-bar').is_hidden();return {'limit':3,'shared_url':url}
        await case('Compare add 1/2/3, reject 4, share, remove, clear',compare)
        async def filters():
            await p.goto(BASE+'catalog.html');await p.locator('input[name=budget]').check();await p.locator('select[name=level]').select_option('бакалавриат');await p.locator('input[name=price]').fill('300000');await p.locator('input[name=q]').fill('информатик');url=await p.evaluate("location.href");ids=await p.locator('#catalog-list .program-card').evaluate_all('es=>es.map(e=>e.dataset.id)');await p.goto(url);assert ids==await p.locator('#catalog-list .program-card').evaluate_all('es=>es.map(e=>e.dataset.id)'), 'URL did not restore IDs';await p.locator('button[type=reset]').click();await p.wait_for_function('document.querySelectorAll("#catalog-list .program-card").length === '+str(len(DATA['programs'])));assert await p.locator('#catalog-list .program-card').count()==len(DATA['programs']);return {'filtered':len(ids),'url':url}
        await case('Combined filters, URL restore and reset',filters)
        for q in ['общага','стипуха','пары','приёмка','расписание','ИРИТ','информатика','Информатика','информатеко','ёлка','елка','','я','x'*200,'<script>alert(1)</script>','<img src=x onerror=alert(1)>']:
            async def run(q=q):
                from urllib.parse import quote
                await p.goto(BASE+'search.html?q='+quote(q));count=await p.locator('#search-results .result').count();assert await p.locator('#search-results script,#search-results img').count()==0
                if q in ['общага','стипуха','пары','приёмка','расписание','ИРИТ','информатика','Информатика','информатеко']:assert count>0,'Expected useful result'
                return {'count':count,'message':(await p.locator('#search-count').inner_text())}
            await case('Search '+q[:35],run)
        async def suggestions():
            await p.goto(BASE);e=p.locator('#home-query');
            if not await e.count():e=p.locator('[data-suggest]').first
            await e.fill('общага');await p.keyboard.press('ArrowDown');assert await e.get_attribute('aria-activedescendant');await p.keyboard.press('Escape');assert await e.get_attribute('aria-expanded')=='false';await e.fill('общага ');await p.keyboard.press('ArrowDown');await p.keyboard.press('Enter');await p.wait_for_url('**/campus.html');assert 'campus.html'in p.url;return p.url
        await case('Search suggestions ArrowDown/Esc/Enter',suggestions)
        for group in ['РИ-140944','ри-140944','  ри-140944  ','РИ - 140944','НЕ-123456','']:
            async def run(group=group):
                await p.goto(BASE+'schedule.html?group='+__import__('urllib.parse',fromlist=['quote']).quote(group));text=await p.locator('#schedule-output').inner_text();valid=group.replace(' ','').upper()=='РИ-140944'
                if valid:assert 'Эта группа не найдена'not in text
                else:assert 'Эта группа не найдена' in text
                return text[:100]
            await case('Schedule group '+repr(group),run)
        for room in ['Р-237','р-237','R-237','P-237','Р237',' Р 237 ','Б-237','Р-999','abc','<img src=x onerror=alert(1)>','']:
            async def run(room=room):
                await p.goto(BASE+'room.html?room='+__import__('urllib.parse',fromlist=['quote']).quote(room));text=await p.locator('#room-result').inner_text();assert text.strip()
                if room in ['Р-237','р-237','R-237','P-237','Р237',' Р 237 ']:assert 'Мира, 32'in text
                assert await p.locator('#room-result img,#room-result script').count()==0;return text[:120]
            await case('Room '+repr(room),run)
        sample=random.Random(2026).sample(DATA['programs'],10)+sorted(DATA['programs'],key=lambda x:len(x['name']),reverse=True)[:3]
        for prog in sample:
            async def run(prog=prog):
                await p.goto(BASE+'Program.html?id='+prog['id']);text=await p.locator('#program-content').inner_text();assert prog['name'].lower() in (await p.locator('h1').inner_text()).lower();assert not re.search(r'undefined|NaN|\bnull\b|\[object Object\]',text);return {'id':prog['id'],'name':prog['name']}
            await case('Program '+prog['id'],run)
        for bad in ['','abc','-1','999999','<script>']:
            async def run(bad=bad):
                await p.goto(BASE+'Program.html?id='+bad);assert await p.locator('#program-content .empty').is_visible();return await p.locator('#program-content').inner_text()
            await case('Unknown program '+repr(bad),run)
        for area in sorted({x['area'] for x in DATA['programs']}):
            for priority in ['budget','price','interest']:
                async def run(area=area,priority=priority):
                    await p.goto(BASE+'quiz.html');await p.locator('input[name=area][value="'+area+'"]').check();await p.locator('#quiz-next').click();await p.locator('#quiz-back').click();assert await p.locator('input[name=area]:checked').input_value()==area;await p.locator('#quiz-next').click();await p.locator('#quiz-next').click();await p.locator('input[name=priority][value="'+priority+'"]').check();await p.locator('#quiz-next').click();text=await p.locator('#quiz-results').inner_text();assert text.strip();assert 'области'in text or 'Попробуем шире'in text;return {'cards':await p.locator('#quiz-results .program-card').count()}
                await case('Quiz '+area+'/'+priority,run)
        for f in ['en/index.html','en/catalog.html','en/admission.html','en/contacts.html']:
            async def run(f=f):
                await p.goto(BASE+f);text=await p.locator('body').inner_text();rus=re.findall('[А-Яа-яЁё]+',text);assert not rus,rus;assert await p.locator('.language').get_attribute('href')=='../'+f.split('/')[-1];return {'russian_words':rus,'switch':await p.locator('.language').get_attribute('href')}
            await case('English '+f,run)
        await b.close()
    save('10-scenarios',{'cases':len(rows),'passed':sum(r['status']=='passed' for r in rows),'failures':[r for r in rows if r['status']=='failed'],'results':rows,'console_errors':errors})
asyncio.run(main())
