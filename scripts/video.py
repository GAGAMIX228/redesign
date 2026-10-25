"""Record a real browser walkthrough, then export exactly 60 seconds of MP4.
Requires Python Playwright, Chromium and ffmpeg. No app runtime dependencies.
"""
import asyncio,subprocess,os,shutil
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH","/tmp/urfu-playwright")
# Reuse the trusted system ffmpeg instead of downloading another encoder.

from pathlib import Path
ff=Path(os.environ["PLAYWRIGHT_BROWSERS_PATH"])/"ffmpeg-1011/ffmpeg-linux"
ff.parent.mkdir(parents=True,exist_ok=True)
if not ff.exists():ff.symlink_to(shutil.which("ffmpeg"))
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[1]
async def main():
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  ctx=await b.new_context(viewport={'width':1440,'height':900},record_video_dir='/tmp/urfu-video',record_video_size={'width':1440,'height':900},reduced_motion='no-preference');p=await ctx.new_page()
  async def caption(text):
   await p.evaluate('''text=>{document.getElementById('video-caption')?.remove();const x=document.createElement('div');x.id='video-caption';x.textContent=text;Object.assign(x.style,{position:'fixed',bottom:'20px',left:'20px',right:'20px',zIndex:100000,padding:'18px 24px',background:'#172321',color:'#f6f5ed',font:'600 24px/1.3 Golos,Arial,sans-serif',border:'1px solid #d5f64b',borderRadius:'12px',pointerEvents:'none'});document.body.append(x);}''',text)
  async def go(path,text):
   await p.goto('http://127.0.0.1:4173/'+path);await p.evaluate('document.fonts.ready');await caption(text)
  async def hold(ms=5000):await p.wait_for_timeout(ms)
  await go('index.html','Свой маршрут · Университет, в котором легко найти следующий шаг.');await hold(5000)
  await p.locator('[data-role=student]').click();await caption('Меняем роль — нужные действия оказываются перед вами.');await hold(5000)
  await p.locator('[data-role=applicant]').click();await p.locator('.calculator').scroll_into_view_if_needed();await caption('Сумма ЕГЭ: ориентир по минимумам, а не обещание бюджета.')
  for v in range(120,281,10):await p.locator('#home-score').fill(str(v));await hold(80)
  await hold(4000)
  await go('catalog.html?area=IT+%D0%B8+%D0%BC%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B0&budget=1','Программы по вашим условиям. Сравнение — рядом.');await p.locator('[data-compare]').nth(0).check();await p.locator('[data-compare]').nth(1).check();await p.locator('#compare-open').click();await hold(5500)
  await go('search.html?q=общага','«Общага» → общежития. Поиск понимает привычные слова.');await hold(5500)
  await go('campus.html','Поселение, документы и чек-лист. Без непроверенных цен.');await p.locator('.checklist').scroll_into_view_if_needed();await p.locator('[data-checklist]').nth(0).check();await p.locator('[data-checklist]').nth(1).check();await hold(5500)
  await go('schedule.html?day=0','Демо-расписание: дни, недели и календарь телефона.');await p.locator('#schedule-days').scroll_into_view_if_needed();await p.locator('[data-day="2"]').click();await hold(5500)
  await go('index.html','Настройте сайт под себя: контраст, текст и изображения.');await p.locator('[data-a11y-open]').first.click();await p.locator('select[name=scheme]').select_option('wb');await p.locator('select[name=size]').select_option('20');await hold(5500)
  # Real captured mobile page, placed within the desktop recording canvas.
  await p.locator('#a11y-reset').click();await p.goto('http://127.0.0.1:4173/docs/presentation.html');await p.evaluate('''()=>{document.body.innerHTML='<div style="width:100vw;height:100vh;background:#b9a9ed;display:flex;align-items:center;justify-content:center;gap:80px;padding:30px;color:#172321;font-family:Golos,Arial"><img src="screenshots/mobile.png" style="height:650px;border:8px solid #172321;border-radius:35px"><div style="max-width:550px"><h1 style="font:600 80px/1 Oswald,sans-serif;margin:0 0 30px">Ваш УрФУ.<br>В вашем<br>телефоне.</h1><p style="font-size:25px">Основные сервисы доступны<br>через нижнюю панель.</p></div></div>';}''');await hold(6000)
  await go('index.html','Свой маршрут. Общий университет. Конкурсный прототип УрФУ.');await hold(6000)
  video=p.video;await ctx.close();path=await video.path();await b.close()
  out=R/'docs/urfu-walkthrough-60s.mp4'
  subprocess.run(['ffmpeg','-y','-i',path,'-vf','tpad=stop_mode=clone:stop_duration=60','-t','60','-c:v','libx264','-preset','fast','-crf','25','-pix_fmt','yuv420p','-movflags','+faststart','-an','-threads','2',str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  print('Saved',out)
asyncio.run(main())
