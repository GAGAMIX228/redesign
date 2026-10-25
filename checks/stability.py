"""Section 5: layout shifts under load and exhaustive slider/role sizing."""
import asyncio
from playwright.async_api import async_playwright
from common import *
KEY=['index.html','admission.html','catalog.html','Program.html?id=9797','campus.html','schedule.html','search.html?q=общага','concept.html']
async def main():
    loads=[];actions=[];failures=[]
    async with async_playwright() as pw:
        b=await launch(pw)
        for path in KEY:
            c=await b.new_context(viewport={'width':375,'height':812},reduced_motion='reduce',service_workers='block');p=await c.new_page()
            await p.add_init_script("window.__shifts=[];new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__shifts.push({value:e.value,time:e.startTime,sources:e.sources.map(s=>s.node?.tagName+'.'+s.node?.className)});}).observe({type:'layout-shift',buffered:true});")
            cd=await c.new_cdp_session(p);await cd.send('Network.enable');await cd.send('Network.emulateNetworkConditions',{'offline':False,'latency':150,'downloadThroughput':200000,'uploadThroughput':93750});await cd.send('Emulation.setCPUThrottlingRate',{'rate':4})
            await p.goto(BASE+path);await p.wait_for_timeout(1800);await settle(p)
            shifts=await p.evaluate('window.__shifts');cls=sum(e['value'] for e in shifts);loads.append({'page':path,'CLS':cls,'shifts':shifts})
            if cls>=.1:failures.append({'page':path,'CLS':cls})
            await c.close()
        c=await b.new_context(reduced_motion='reduce',service_workers='block');p=await c.new_page()
        for width in [320,375,768,1440]:
            await p.set_viewport_size({'width':width,'height':900});await p.goto(BASE);await settle(p)
            role=[]
            for name in ['applicant','student','employee','partner']:
                await p.locator('[data-role='+name+']').click()
                role.append({'name':name,**await p.evaluate("({height:document.querySelector('.hero').offsetHeight,next:document.querySelector('.now-line').offsetTop})")})
            if len({r['height'] for r in role})>1:failures.append({'width':width,'roles':role})
            await p.locator('[data-role=applicant]').click()
            slider=await p.evaluate('''()=>{let e=document.querySelector('#home-score');let rows=[];for(let v=+e.min;v<=+e.max;v++){e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));rows.push({v,height:document.querySelector('.calc-panel').offsetHeight,result:document.querySelector('#home-score-result').offsetHeight,next:document.querySelector('.route-section').offsetTop});}return rows;}''')
            if len({r['height'] for r in slider})>1:failures.append({'width':width,'slider_min_height':min(r['height'] for r in slider),'slider_max_height':max(r['height'] for r in slider)})
            actions.append({'width':width,'roles':role,'slider_values':len(slider),'slider_heights':sorted({r['height'] for r in slider}),'slider_result_heights':sorted({r['result'] for r in slider})})
        await b.close()
    save('05-stability',{'mobile_slow_network_4x_CPU':loads,'actions':actions,'failures':failures,'note':'Result lists naturally resize after filtering; autocomplete is positioned outside document flow. No invented fixed data.'})
asyncio.run(main())
