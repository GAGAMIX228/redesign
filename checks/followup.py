"""Regression checks for clipboard denial, nested dialogs and replaced animation targets."""
import asyncio
from playwright.async_api import async_playwright
from common import BASE, PAGES, route, launch, settle, axe, save

CLIPBOARD = """mode=>{
 window.auditCopied=[];
 Object.defineProperty(navigator,'clipboard',{configurable:true,value:mode==='missing'?undefined:{
  writeText:async text=>{if(mode==='denied')throw new DOMException('Denied','NotAllowedError');auditCopied.push(text);}
 }});
}"""
OBSERVERS = """(()=>{
 const Native=IntersectionObserver;window.auditObservers=[];
 window.IntersectionObserver=class extends Native{
  constructor(callback,options){super(callback,options);this.targets=new Set();auditObservers.push(this);}
  observe(el){this.targets.add(el);super.observe(el);}
  unobserve(el){this.targets.delete(el);super.unobserve(el);}
  disconnect(){this.targets.clear();super.disconnect();}
 };
})();"""

async def main():
    cases=[];errors=[];accessibility=[];tracking=[]
    async with async_playwright() as pw:
        b=await launch(pw)
        for width in (375,1440):
            p=await b.new_page(viewport={'width':width,'height':900},service_workers='block')
            p.on('pageerror',lambda e:errors.append(str(e)))
            for mode in ('denied','missing','allowed'):
                await p.goto(BASE+'catalog.html?compare=9797,10037&my=180')
                await p.evaluate(CLIPBOARD,mode)
                opener=p.locator('[data-share]').first
                await opener.click()
                if mode=='allowed':
                    assert await p.evaluate('auditCopied[0]===location.href')
                    assert not await p.locator('#share-dialog').count()
                    cases.append({'width':width,'clipboard':mode,'copied_exact_url':True})
                    continue
                dialog=p.get_by_role('dialog',name='Скопируйте ссылку',exact=True)
                await dialog.wait_for(state='visible')
                assert await dialog.locator('input').input_value()==p.url
                assert await dialog.locator('input').evaluate('e=>e===document.activeElement&&e.selectionStart===0&&e.selectionEnd===e.value.length')
                # Native dialogs may pass Tab to browser chrome, never to page content behind them.
                for key in ('Tab','Tab','Shift+Tab','Shift+Tab'):
                    await p.keyboard.press(key)
                    assert await dialog.evaluate('e=>!document.hasFocus()||e.contains(document.activeElement)')
                result=await axe(p)
                accessibility.append({'width':width,'clipboard':mode,**result})
                assert not result['violations']
                await p.keyboard.press('Escape')
                await dialog.wait_for(state='hidden')
                assert await opener.evaluate('e=>e===document.activeElement')
                assert await p.evaluate("document.body.style.overflow===''")
                # Reopened dialogs also close by clicking their backdrop.
                await opener.click()
                await p.mouse.click(2,2)
                await dialog.wait_for(state='hidden')
                assert await opener.evaluate('e=>e===document.activeElement')
                cases.append({'width':width,'clipboard':mode,'url_and_selection':True,'tab_keeps_background_inert':True,'escape_restores_focus':True,'backdrop_closes':True})
            # Closing a sharing dialog keeps comparison open and the page locked.
            await p.evaluate(CLIPBOARD,'denied')
            await p.locator('#compare-open').click()
            compare=p.get_by_role('dialog',name='Сравнение программ',exact=True)
            await compare.wait_for(state='visible')
            nested_opener=compare.locator('[data-share]')
            await nested_opener.click()
            dialog=p.get_by_role('dialog',name='Скопируйте ссылку',exact=True)
            await dialog.wait_for(state='visible')
            await p.keyboard.press('Escape')
            await dialog.wait_for(state='hidden')
            assert await compare.is_visible()
            assert await p.evaluate("document.body.style.overflow==='hidden'")
            assert await nested_opener.evaluate('e=>e===document.activeElement')
            await p.keyboard.press('Escape')
            await compare.wait_for(state='hidden')
            assert await p.evaluate("document.body.style.overflow===''")
            assert await p.locator('#compare-open').evaluate('e=>e===document.activeElement')
            # Rapid repeated calls must not leave an extra scroll lock behind.
            await p.evaluate("document.body.style.overflow='auto';const b=document.querySelector('[data-share]');b.click();b.click();")
            await dialog.wait_for(state='visible')
            await p.keyboard.press('Escape')
            await dialog.wait_for(state='hidden')
            assert await p.evaluate("document.body.style.overflow==='auto'")
            cases.append({'width':width,'nested_dialog_focus_and_scroll':True,'repeated_open_restores_original_overflow':True})
            await p.close()
        p=await b.new_page(viewport={'width':1440,'height':900},service_workers='block')
        p.on('pageerror',lambda e:errors.append(str(e)))
        await p.add_init_script(OBSERVERS)
        await p.goto(BASE+'catalog.html')
        query=p.locator('#catalog-filters input[name=q]')
        for i in range(120):
            await query.fill('инф' if i%2 else 'технолог')
            await p.wait_for_timeout(35)
        await p.wait_for_timeout(100)
        observers=await p.evaluate('auditObservers.map(o=>({observed:o.targets.size,detached:[...o.targets].filter(e=>!e.isConnected).length}))')
        assert all(o['detached']==0 for o in observers)
        tracking.append({'filter_changes':120,'observers':observers,'detached_targets':0})
        await p.locator('[data-motion-toggle]').first.click()
        await p.wait_for_timeout(60)
        assert await p.evaluate("document.body.dataset.motionState==='off'")
        await query.fill('технолог')
        await p.wait_for_timeout(100)
        assert await p.locator('#catalog-list .program-card').count()>0
        await p.locator('[data-motion-toggle]').first.click()
        await p.emulate_media(reduced_motion='reduce')
        await p.wait_for_timeout(60)
        assert await p.evaluate("document.body.dataset.motionState==='off'")
        tracking.append({'motion_pause_and_reduced_motion':True,'content_still_visible':True})
        # Shared dialog code must initialise without errors on every page.
        for f in PAGES:
            await p.goto(BASE+route(f));await settle(p)
            opener=p.locator('[data-a11y-open]').first
            await opener.click()
            await p.keyboard.press('Escape')
            assert await opener.evaluate('e=>e===document.activeElement')
        await b.close()
    assert not errors,errors
    save('19-followup',{'status':'passed','sharing':cases,'axe':accessibility,'animation_tracking':tracking,'shared_dialog_pages':len(PAGES),'console_errors':errors,'limitations':['Clipboard outcomes are simulated to exercise permission fallbacks; no clipboard permission or browser policy was bypassed. Direct file navigation remains unverified.']})

asyncio.run(main())
