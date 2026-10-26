"""Record real browser scenes and export 60s, Full HD, 25fps with crossfades."""
import asyncio,json,os,shutil,subprocess,time,sys
from pathlib import Path
os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH','/tmp/urfu-playwright')
ff=Path(os.environ['PLAYWRIGHT_BROWSERS_PATH'])/'ffmpeg-1011/ffmpeg-linux';ff.parent.mkdir(parents=True,exist_ok=True)
if not ff.exists():ff.symlink_to(shutil.which('ffmpeg'))
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[1];BASE=os.environ.get('SITE_BASE','http://127.0.0.1:4175/')
SCENES=[('index.html','Свой маршрут · Найти следующий шаг в УрФУ.','intro'),('index.html','Четыре роли — свои быстрые действия.','role'),('index.html','Сумма ЕГЭ: минимумы, а не обещание бюджета.','score'),('catalog.html?budget=1','98 уникальных программ · сравнение по условиям.','compare'),('search.html','«Общага» → общежития. Поиск понимает привычные слова.','search'),('campus.html','Поселение, подтверждённые адреса и личный чек-лист.','campus'),('schedule.html?day=0','Демо-расписание · дни, недели и календарь.','schedule'),('index.html','Контраст, шрифт, интервалы — настройте под себя.','accessibility'),('docs/presentation.html','Мобильная версия · основные сервисы под рукой.','mobile'),('index.html','Свой маршрут · gagamix228.github.io/redesign/','final')]
async def main():
 clips=[];records=[]
 if '--encode-only' in sys.argv:
  records=json.loads((R/'checks/results/video-scenes.json').read_text());clips=[r['clip'] for r in records]
 else:
  wanted=next((x.split('=',1)[1] for x in sys.argv if x.startswith('--scene=')),None)
  previous=json.loads((R/'checks/results/video-scenes.json').read_text()) if wanted else []
  async with async_playwright() as pw:
   b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
   for i,(path,title,kind) in enumerate(SCENES):
    if wanted and kind!=wanted:continue
    c=await b.new_context(viewport={'width':1920,'height':1080},record_video_dir='/tmp/urfu-video-final',record_video_size={'width':1920,'height':1080},reduced_motion='no-preference')
    if kind=='accessibility':await c.add_init_script("localStorage.setItem('urfu:a11y',JSON.stringify({scheme:'blue'}));")
    p=await c.new_page();await p.goto(BASE+path);await p.evaluate('document.fonts.ready');await p.wait_for_timeout(400)
    if kind=='score':await p.locator('.calculator').scroll_into_view_if_needed()
    if kind=='compare':
     await p.locator('[data-compare]').nth(0).check();await p.locator('[data-compare]').nth(1).check();await p.locator('#compare-open').click();await p.wait_for_timeout(350)
    if kind=='campus':await p.locator('.checklist').scroll_into_view_if_needed()
    if kind=='schedule':await p.locator('#schedule-days').scroll_into_view_if_needed()
    if kind=='accessibility':
     await p.locator('[data-a11y-open]').first.click();await p.locator('select[name=scheme]').select_option('blue');await p.wait_for_timeout(350)
    if kind=='mobile':await p.evaluate('''()=>{document.body.innerHTML='<div style="height:100vh;background:#c2abff;display:flex;align-items:center;justify-content:center;gap:100px;color:#1b1931;font-family:Golos,Arial"><img src="screenshots/mobile.png" style="height:800px;border:8px solid #1b1931;border-radius:35px"><div><h1 style="font:600 100px/1 Oswald;margin:0 0 30px">Ваш УрФУ.<br>В вашем<br>телефоне.</h1><p style="font-size:30px">Основные сервисы доступны<br>через нижнюю панель.</p></div></div>';}''')
    await p.evaluate('''text=>{let x=document.createElement('div');x.id='walkthrough-caption';x.textContent=text;Object.assign(x.style,{position:'fixed',bottom:'24px',left:'36px',right:'36px',zIndex:100000,padding:'20px 28px',background:'#1b1931',color:'#fffdf7',font:'600 27px/1.35 Golos,Arial',border:'1px solid #dfff59',borderRadius:'12px',pointerEvents:'none'});(document.querySelector('dialog[open]')||document.body).append(x);let cursor=document.createElement('div');cursor.id='walkthrough-cursor';cursor.innerHTML='<svg width="30" height="36" viewBox="0 0 30 36"><path d="M2 2v28l8-7 6 11 6-3-6-11 11-1Z" fill="white" stroke="#1b1931" stroke-width="2"/></svg>';Object.assign(cursor.style,{position:'fixed',left:'1600px',top:'600px',zIndex:100001,pointerEvents:'none'});cursor.setAttribute('aria-hidden','true');(document.querySelector('dialog[open]')||document.body).append(cursor);document.addEventListener('pointermove',e=>{cursor.style.left=e.clientX+'px';cursor.style.top=e.clientY+'px';});}''',title)
    start=time.monotonic();await p.mouse.move(1600,600);await p.wait_for_timeout(550)
    if kind=='role':await p.locator('[data-role=student]').click()
    if kind=='score':
     box=await p.locator('#home-score').bounding_box();await p.mouse.move(box['x']+box['width']*.45,box['y']+box['height']/2,steps=20);await p.mouse.down();await p.mouse.move(box['x']+box['width']*.9,box['y']+box['height']/2,steps=45);await p.mouse.up()
    if kind=='search':
     await p.locator('#site-query').press_sequentially('общага',delay=140);await p.keyboard.press('Escape');await p.evaluate("scrollTo({top:Math.max(0,scrollY+document.querySelector('#search-count').getBoundingClientRect().top-220),behavior:'smooth'})")
    if kind=='campus':await p.locator('[data-checklist]').nth(0).check();await p.locator('[data-checklist]').nth(1).check()
    if kind=='schedule':await p.locator('[data-day="2"]').click()
    if kind=='accessibility':await p.locator('select[name=size]').select_option('20')
    await p.mouse.move(1570,650,steps=25);await p.wait_for_timeout(max(0,6600-(time.monotonic()-start)*1000));video=p.video;await c.close();clips.append(str(await video.path()));records.append({'scene':i+1,'title':title,'route':path,'clip':clips[-1]});print('Recorded',i+1,kind,flush=True)
   await b.close()
  if wanted:
   changed={r['scene']:r for r in records};records=[changed.get(r['scene'],r) for r in previous];clips=[r['clip'] for r in records]
 (R/'checks/results/video-scenes.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
 cmd=['ffmpeg','-y','-threads','2']
 for clip in clips:cmd+=['-sseof','-6.5','-i',clip]
 filters=[f'[{i}:v]scale=1920:1080,setsar=1,setpts=PTS-STARTPTS,fps=25,settb=AVTB[v{i}]' for i in range(10)];previous='v0'
 for i in range(1,10):
  out='fade'+str(i);filters.append(f'[{previous}][v{i}]xfade=transition=fade:duration=0.5:offset={6*i},fps=25,settb=AVTB[{out}]');previous=out
 filters.append(f'[{previous}]tpad=stop_mode=clone:stop_duration=1[final]')
 cmd+=['-filter_complex_threads','1','-filter_complex',';'.join(filters),'-map','[final]','-t','60','-c:v','libx264','-preset','fast','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart','-an','-threads','2',str(R/'docs/urfu-walkthrough-60s.mp4')]
 with open('/tmp/urfu-video-encode.log','w') as log:subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=log)
 (R/'checks/results/video-scenes.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));print('Saved 60-second Full HD video',flush=True)
if __name__=='__main__':asyncio.run(main())
