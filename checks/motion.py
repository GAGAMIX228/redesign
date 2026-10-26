"""Section 6: compositor properties, actual frames, pause and browser navigation."""
import asyncio, sys
from playwright.async_api import async_playwright
from common import *
async def main():
    result={};issues=[]
    async with async_playwright() as pw:
        b=await launch(pw);c=await b.new_context(viewport={'width':1366,'height':900},reduced_motion='no-preference',service_workers='block');p=await c.new_page()
        await p.goto(BASE);await settle(p);await p.wait_for_timeout(1100)
        properties=await p.evaluate('''()=>{const bad=[];function walk(rules){for(const r of rules){if(r.style){const t=r.style.transitionProperty;const names=t.split(',').map(x=>x.trim());if(names.some(x=>['all','gap','width','height','margin','top','left','background-size'].includes(x)))bad.push({rule:r.cssText.slice(0,200),property:t});}if(r.cssRules)walk(r.cssRules);}}for(const s of document.styleSheets)try{walk(s.cssRules)}catch{}return bad;}''')
        result['layout_property_transitions']=properties
        if properties:issues.append('Layout/paint property transitions found')
        cd=await c.new_cdp_session(p);await cd.send('Emulation.setCPUThrottlingRate',{'rate':4})
        result['scroll_profile']=await p.evaluate('''async()=>{const long=[];const obs=new PerformanceObserver(l=>long.push(...l.getEntries().map(e=>({start:e.startTime,duration:e.duration}))));obs.observe({type:'longtask',buffered:false});let frames=[],previous=performance.now(),start=previous;const end=document.documentElement.scrollHeight-innerHeight;await new Promise(done=>{function step(now){frames.push(now-previous);previous=now;const t=Math.min(1,(now-start)/8000);scrollTo(0,end*t);if(t<1)requestAnimationFrame(step);else done();}requestAnimationFrame(step);});obs.disconnect();frames=frames.slice(2);return {frames:frames.length,p50:frames.sort((a,b)=>a-b)[Math.floor(frames.length*.5)],p95:frames[Math.floor(frames.length*.95)],max:Math.max(...frames),long_tasks:long};}''')
        await cd.send('Emulation.setCPUThrottlingRate',{'rate':1})
        await p.evaluate('scrollTo(0,0)');await p.locator('.motion-icon').click()
        result['pause_stops_loops']=await p.evaluate("[...document.getAnimations()].filter(a=>a.effect?.target?.closest?.('.ticker,.hero-sticker,.hero-spark,.route-ornament')).every(a=>a.playState!=='running')")
        await p.emulate_media(reduced_motion='reduce');result['reduced_motion_state']=await p.locator('body').get_attribute('data-motion-state')
        # Standard browser history and native keyboard scrolling.
        await p.goto(BASE+'catalog.html');await p.evaluate('scrollTo(0,700)');await p.locator('.program-card h3 a').first.click();await p.go_back();await p.wait_for_timeout(150);result['back_url']=p.url;result['back_scroll']=await p.evaluate('scrollY')
        await p.goto(BASE);await p.mouse.click(5,200);await p.keyboard.press('PageDown')
        try:await p.wait_for_function('scrollY>0',timeout=3000);result['native_pagedown']=True
        except:result['native_pagedown']=False;issues.append('Native PageDown did not scroll')
        await p.keyboard.press('End')
        try:await p.wait_for_function('scrollY>1000',timeout=3000);result['native_end']=True
        except:result['native_end']=False;issues.append('Native End did not scroll')
        result['issues']=issues
        await b.close()
    save('06-motion',result)
asyncio.run(main())
