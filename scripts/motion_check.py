"""Functional animation checks: actual motion, global pause and static fallbacks."""
import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[1]
async def main():
 errors=[];clipped=[];checks=[]
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=await b.new_page(viewport={'width':1440,'height':1000},reduced_motion='no-preference')
  p.on('pageerror',lambda e:errors.append(str(e)))
  await p.goto('http://127.0.0.1:4173/');await p.evaluate('document.fonts.ready');await p.wait_for_timeout(1100)
  assert await p.locator('body').get_attribute('data-motion-state')=='on'
  assert await p.locator('.sticker-petals').evaluate("e=>e.getAnimations().some(a=>a.playState==='running')")
  checks.append('Decorative motion is active when allowed')
  for width in [320,390,768,1440,2560]:
   await p.set_viewport_size({'width':width,'height':1000})
   for role in ['applicant','student','employee','partner']:
    await p.locator('[data-role='+role+']').click();await p.wait_for_timeout(200)
    for item in await p.locator('.headline-line').evaluate_all('es=>es.map(e=>({text:e.textContent,clipped:e.scrollWidth>e.clientWidth+1}))'):
     if item['clipped']:clipped.append([width,role,item['text']])
    if await p.evaluate('document.documentElement.scrollWidth>innerWidth+1'):clipped.append([width,role,'page overflow'])
  assert not clipped,clipped;checks.append('All role headlines fit at five screen widths')
  await p.set_viewport_size({'width':1440,'height':1000});await p.locator('[data-role=applicant]').click();await p.evaluate('scrollTo(0,0)');await p.wait_for_timeout(650)
  pause=p.locator('.motion-icon');await pause.click();assert await p.locator('body').get_attribute('data-motion-state')=='off'
  assert await p.locator('.sticker-petals').evaluate("e=>e.getAnimations().every(a=>a.playState!=='running')")
  checks.append('Global pause stops real animation timelines')
  await pause.click();assert await p.locator('body').get_attribute('data-motion-state')=='on'
  await p.emulate_media(reduced_motion='reduce');await p.wait_for_timeout(100);assert await p.locator('body').get_attribute('data-motion-state')=='off';assert await p.locator('h1').is_visible()
  checks.append('Reduced-motion disables effects while leaving content visible')
  await p.emulate_media(reduced_motion='no-preference');await p.wait_for_timeout(100)
  await p.locator('.help-banner').scroll_into_view_if_needed();await p.wait_for_timeout(150)
  assert await p.locator('.sticker-petals').evaluate("e=>e.getAnimations().every(a=>a.playState!=='running')")
  checks.append('Off-screen decorative animation is paused')
  # An enlarged accessibility scheme also switches motion off.
  await p.locator('[data-a11y-open]').first.click();await p.locator('#a11y-form select[name=scheme]').select_option('bw');assert await p.locator('body').get_attribute('data-motion-state')=='off';await p.keyboard.press('Escape')
  checks.append('Accessibility mode disables motion')
  c=await b.new_context(java_script_enabled=False,viewport={'width':390,'height':844});q=await c.new_page();await q.goto('http://127.0.0.1:4173/');assert await q.locator('h1').is_visible();assert await q.locator('.shortcut').count()==6
  checks.append('Primary content and navigation remain visible without JavaScript')
  c2=await b.new_context();await c2.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('Storage disabled by browser')}})");q2=await c2.new_page();q2.on('pageerror',lambda e:errors.append(str(e)));await q2.goto('http://127.0.0.1:4173/');await q2.locator('[data-role=student]').click();assert 'ВАШ ДЕНЬ' in await q2.locator('h1').inner_text()
  checks.append('Blocked local storage does not break roles or initialization')
  await b.close()
 assert not errors,errors
 report={'checks':checks,'javascript_errors':errors,'clipped_content':clipped};(R/'docs/motion-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
asyncio.run(main())
