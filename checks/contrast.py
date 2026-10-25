"""Extract actual rendered text/background pairs from local axe, including hover."""
import asyncio
from playwright.async_api import async_playwright
from common import *
async def main():
    pairs={};unknown=[]
    async with async_playwright() as pw:
        b=await launch(pw);p=await b.new_page(viewport={'width':1366,'height':900},reduced_motion='reduce',service_workers='block')
        async def collect(label):
            if not await p.evaluate('!!window.axe'):await p.add_script_tag(path=str(ROOT/'checks/vendor/axe.min.js'))
            result=await p.evaluate('''async()=>{const r=await axe.run(document,{runOnly:['color-contrast']});const data=[];for(const group of ['passes','violations'])for(const rule of r[group])for(const n of rule.nodes)for(const check of n.any)if(check.data?.fgColor)data.push({...check.data,target:n.target,passed:group==='passes'});return {data,incomplete:r.incomplete.map(r=>({id:r.id,count:r.nodes.length}))};}''')
            for d in result['data']:
                key=(d['fgColor'],d['bgColor'],d['expectedContrastRatio']);entry=pairs.setdefault(key,{'foreground':key[0],'background':key[1],'required':key[2],'ratio':d['contrastRatio'],'passed':d['passed'],'examples':[]})
                if len(entry['examples'])<3:entry['examples'].append(label+' '+str(d['target']))
            if result['incomplete']:unknown.append({'state':label,'items':result['incomplete']})
        for f in PAGES:
            await p.goto(BASE+route(f));await scroll_all(p);await collect(f)
        for theme in ['dark','bw','wb','blue','beige','green']:
            await p.goto(BASE);await p.evaluate("s=>{localStorage.setItem('urfu:theme',JSON.stringify(s==='dark'?'dark':'light'));localStorage.setItem('urfu:a11y',JSON.stringify(s==='dark'?{}:{scheme:s}));}",theme);await p.reload();await collect(theme)
        await p.evaluate('localStorage.clear()');await p.goto(BASE)
        for selector in ['.hero-actions .btn','[data-role=student]','.shortcut','.text-link','.footer-tools button']:
            await p.locator(selector).first.hover();await collect('hover '+selector)
            await p.locator(selector).first.focus();await collect('focus '+selector)
        await b.close()
    rows=list(pairs.values());save('08-contrast',{'pairs':rows,'incomplete':unknown,'limitations':['Text over images and anti-aliased glyph pixels cannot be fully certified by computed-color extraction. Two-color focus rings use dark ink and cream.']})
    table=['# Контраст фактически отрисованного текста','','Отчёт axe-core. Пары собраны на всех страницах, в темах и при наведении/фокусе ключевых элементов. Иллюстрации и отдельные пиксели сглаживания требуют визуальной проверки.','','| Текст | Фон | Контраст | Требуется | Результат |','|---|---|---|---|---|']
    for r in sorted(rows,key=lambda x:x['ratio']):table.append(f"| {r['foreground']} | {r['background']} | {r['ratio']}:1 | {r['required']} | {'прошло' if r['passed'] else 'ошибка'} |")
    (ROOT/'checks/contrast.md').write_text('\n'.join(table)+'\n')
asyncio.run(main())
