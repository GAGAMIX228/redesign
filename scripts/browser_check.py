"""Local smoke checks. Requires Python Playwright and Chromium; no npm/build needed."""
import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[1]
async def main():
 errors=[];overflow=[];requests=[];limitations=[]
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  page=await browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
  page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
  page.on('request',lambda r:requests.append(r.url) if r.url.startswith('http') and not r.url.startswith('http://127.0.0.1:4173') else None)
  await page.goto('http://127.0.0.1:4173/')
  for y in range(0,6000,700):await page.evaluate('(y)=>scrollTo(0,y)',y);await page.wait_for_timeout(80)
  await page.evaluate('scrollTo(0,0)');await page.screenshot(path='/tmp/urfu-desktop.png',full_page=True)
  await page.set_viewport_size({'width':390,'height':844});await page.screenshot(path='/tmp/urfu-mobile.png')
  for width in [320,390,768,1440,2560]:
   await page.set_viewport_size({'width':width,'height':900})
   for file in sorted(R.glob('*.html'))+sorted((R/'en').glob('*.html')):
    route=str(file.relative_to(R))
    if route=='Program.html':route+='?id=9797'
    if route=='Institute.html':route+='?id=0'
    if route=='article.html':route+='?id=1'
    await page.goto('http://127.0.0.1:4173/'+route)
    wide=await page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
    if wide:
     offenders=await page.evaluate('[...document.querySelectorAll("body *")].filter(x=>x.getBoundingClientRect().right>innerWidth+1&&getComputedStyle(x).position!=="absolute").slice(0,5).map(x=>x.tagName+"."+x.className)');overflow.append([width,file.name,offenders])
  await page.set_viewport_size({'width':1440,'height':1000})
  await page.goto('http://127.0.0.1:4173/catalog.html?ege=math,rus,inf&my=220')
  assert await page.locator('#catalog-list .program-card').count()>0
  await page.locator('input[name=q]').fill('программная инженерия')
  assert await page.locator('#catalog-list .program-card').count()>0
  await page.locator('[data-compare]').first.check();await page.locator('#compare-open').click();assert await page.locator('#compare-dialog').is_visible();await page.keyboard.press('Escape')
  await page.locator('input[name=q]').fill('несуществующаяабракадабра');assert await page.locator('#catalog-empty').is_visible()
  await page.goto('http://127.0.0.1:4173/search.html?q=общага');assert 'Кампус' in await page.locator('#search-results').inner_text()
  await page.goto('http://127.0.0.1:4173/room.html?room=Р-237');assert 'Мира, 32' in await page.locator('#room-result').inner_text()
  await page.goto('http://127.0.0.1:4173/quiz.html');await page.locator('#quiz-next').click();await page.locator('#quiz-next').click();await page.locator('#quiz-next').click();assert await page.locator('#quiz-results').is_visible()
  await page.goto('http://127.0.0.1:4173/schedule.html');assert await page.locator('#schedule-days button').count()==7
  async with page.expect_download() as dl:await page.locator('#schedule-ics').click()
  d=await dl.value;await d.save_as('/tmp/urfu-demo.ics');assert 'BEGIN:VEVENT' in Path('/tmp/urfu-demo.ics').read_text()
  await page.goto('http://127.0.0.1:4173/account.html');await page.locator('#certificate-form button').click();assert 'никуда не отправлена' in await page.locator('#certificate-result').inner_text()
  try:
   await page.goto('file://'+str(R/'index.html'))
   await page.locator('[data-role=student]').click();assert 'ВАШ ДЕНЬ' in await page.locator('#role-heading').inner_text()
   await page.goto('file://'+str(R/'catalog.html')+'?q=информатик');assert await page.locator('#catalog-list .program-card').count()>0
  except Exception as exc:
   if 'ERR_BLOCKED_BY_ADMINISTRATOR' in str(exc):
    limitations.append('The managed Chromium policy blocks file:// navigation; direct file opening could not be browser-tested here.')
    await page.close();page=await browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
   else:raise
  await page.goto('http://127.0.0.1:4173/')
  await page.locator('[data-a11y-open]').first.click();await page.locator('#a11y-form select[name=scheme]').select_option('wb');assert await page.locator('body').get_attribute('data-a11y')=='wb';await page.keyboard.press('Escape')
  await page.evaluate('navigator.serviceWorker.ready');await page.wait_for_timeout(1500);await page.context.set_offline(True);await page.reload();assert await page.locator('#role-heading').inner_text();await page.context.set_offline(False)
  await browser.close()
 report={'javascript_errors':errors,'horizontal_overflow':overflow,'external_requests':requests,'functional_checks':'passed','limitations':limitations}
 (R/'docs/smoke-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
asyncio.run(main())
