"""Section 8: actual Tab/Enter/Escape navigation and focus restoration."""
import asyncio
from playwright.async_api import async_playwright
from common import *
async def main():
    rows=[];errors=[];dialogs=[]
    async with async_playwright() as pw:
        b=await launch(pw);p=await b.new_page(viewport={'width':375,'height':900},reduced_motion='reduce',service_workers='block')
        p.on('pageerror',lambda e:errors.append(str(e)))
        for path in ['index.html','catalog.html','Program.html?id=9797','search.html?q=общага','schedule.html','quiz.html','room.html','campus.html']:
            await p.goto(BASE+path);await settle(p)
            await p.locator('a,button,input,select,textarea,summary,[tabindex]').evaluate_all('es=>es.forEach((e,i)=>e.dataset.auditFocus=i)')
            order=[];seen={}
            for i in range(600):
                await p.keyboard.press('Tab')
                info=await p.evaluate('''()=>{const e=document.activeElement,s=getComputedStyle(e),r=e.getBoundingClientRect();return {unique:e.dataset.auditFocus||'body',tag:e.tagName,id:e.id,name:e.getAttribute('aria-label')||e.textContent.trim().slice(0,70)||e.name,focus:s.outlineStyle!=='none'||s.boxShadow!=='none',rect:{top:r.top,bottom:r.bottom,width:r.width,height:r.height},hidden:!e.getClientRects().length};}''')
                key=info['unique'];seen[key]=seen.get(key,0)+1
                if seen[key]>1:break
                order.append(info)
            rows.append({'page':path,'tabs':len(order),'invisible_focus':[v for v in order if v['tag']!='BODY' and (v['hidden'] or not v['focus'])],'order':order})
        # Test skip navigation using the real first Tab.
        await p.goto(BASE);await p.keyboard.press('Tab');await p.keyboard.press('Enter');skip=await p.evaluate("document.activeElement.id==='main'")
        # Open and close native modal using keyboard only.
        await p.locator('[data-a11y-open]').first.focus();await p.keyboard.press('Enter');await p.keyboard.press('Escape');dialogs.append({'dialog':'accessibility','restored':await p.locator('[data-a11y-open]').first.evaluate('e=>e===document.activeElement')})
        await p.goto(BASE+'catalog.html');await p.locator('[data-compare]').first.focus();await p.keyboard.press('Space');await p.locator('#compare-open').focus();await p.keyboard.press('Enter');await p.keyboard.press('Escape');dialogs.append({'dialog':'comparison','restored':await p.locator('#compare-open').evaluate('e=>e===document.activeElement')})
        # Native range keyboard behavior, not programmatic value assignment.
        await p.goto(BASE);await p.locator('#home-score').focus();await p.keyboard.press('Home');low=await p.locator('#home-score').input_value();await p.keyboard.press('End');high=await p.locator('#home-score').input_value();await p.keyboard.press('ArrowLeft');left=await p.locator('#home-score').input_value();await p.keyboard.press('PageDown');down=await p.locator('#home-score').input_value()
        heading_issues=[]
        for f in PAGES:
            await p.goto(BASE+route(f))
            headings=await p.locator('h1,h2,h3,h4').evaluate_all('es=>es.filter(e=>e.getClientRects().length).map(e=>({level:+e.tagName[1],text:e.textContent.trim()}))');last=0
            for h in headings:
                if h['level']>last+1:heading_issues.append({'page':f,**h})
                last=h['level']
        save('08-heading-order',{'errors':heading_issues})
        await b.close()
    save('08-keyboard',{'pages':rows,'skip_link':skip,'dialogs':dialogs,'slider':{'Home':low,'End':high,'ArrowLeft':left,'PageDown':down},'console':errors,'limitations':['NVDA/VoiceOver and real touchscreen devices are unavailable. Automated keyboard events do not replace a screen-reader user session.']})
asyncio.run(main())
