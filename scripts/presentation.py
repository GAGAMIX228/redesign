"""Capture actual pages and create an 18-page landscape A4 design proposal.
Tool dependencies: Python Playwright, Pillow; an installed Chromium.
"""
import asyncio,json,re,textwrap
from pathlib import Path
from html import escape as E
from PIL import Image,ImageDraw,ImageFont
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[1];D=R/'docs';S=D/'screenshots';S.mkdir(exist_ok=True)
async def main():
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=await b.new_page(viewport={'width':1440,'height':960},reduced_motion='reduce')
  targets=[('home','index.html'),('catalog','catalog.html?area=IT+%D0%B8+%D0%BC%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B0&budget=1'),('program','Program.html?id=9797'),('search','search.html?q=общага'),('schedule','schedule.html?day=0'),('campus','campus.html'),('accessibility','index.html')]
  for name,route in targets:
   await p.goto('http://127.0.0.1:4173/'+route);await p.evaluate('document.fonts.ready');await p.wait_for_timeout(200)
   if name=='accessibility':await p.locator('[data-a11y-open]').first.click()
   await p.screenshot(path=str(S/(name+'.png')))
  await p.set_viewport_size({'width':390,'height':844});await p.goto('http://127.0.0.1:4173/');await p.evaluate('document.fonts.ready');await p.screenshot(path=str(S/'mobile.png'))
  await p.goto('http://127.0.0.1:4173/catalog.html');await p.screenshot(path=str(S/'mobile-catalog.png'))
  # Build OG images from page titles with locally available typeface, no remote rendering.
  og=R/'assets/og';og.mkdir(exist_ok=True)
  font='/tmp/GolosText.ttf'
  if not Path(font).exists():font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
  big=ImageFont.truetype(font,72);small=ImageFont.truetype(font,26)
  for f in list(R.glob('*.html'))+list((R/'en').glob('*.html')):
   text=f.read_text();title=re.search(r'<title>(.*?)</title>',text)[1].split(' — ')[0];title=re.sub('<[^>]+>',' ',title)
   im=Image.new('RGB',(1200,630),'#07584b');draw=ImageDraw.Draw(im);draw.text((70,48),'УрФУ  /  СВОЙ МАРШРУТ',font=small,fill='#d5f64b');lines=[]
   for word in title.split():
    if lines and draw.textlength(lines[-1]+' '+word,font=big)<1030:lines[-1]+=' '+word
    else:lines.append(word)
   for i,line in enumerate(lines[:4]):draw.text((65,160+i*90),line,font=big,fill='#f6f5ed')
   draw.text((70,560),'Конкурсный прототип · 2026',font=small,fill='#f6f5ed');im.save(og/(('en-' if f.parent.name=='en' else '')+f.stem+'.png'),optimize=True)
  lh={}
  if (D/'lighthouse-compressed.json').exists():
   data=json.loads((D/'lighthouse-compressed.json').read_text());lh={k:round(v['score']*100) for k,v in data['categories'].items()}
  slides=[]
  def add(title,text='',image=None,color='',eyebrow='УРФУ · СВОЙ МАРШРУТ'):
   n=len(slides)+1;body='<div class="copy">'+text+'</div>'
   if image:body='<div class="layout">'+body+'<img src="screenshots/'+image+'.png" alt="Экран работающего прототипа"></div>'
   slides.append(f'<section class="slide {color}"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1>{body}<footer><span>Независимый конкурсный прототип · 25.10.2026</span><span>{n:02d} / 18</span></footer></section>')
  add('СВОЙ<br>МАРШРУТ.','<p class="promise">Университет, в котором легко найти следующий шаг.</p><p>Концепция нового сайта УрФУ.<br>От задач человека — к большому будущему.</p>',color='green')
  add('Что мешает<br>найти ответ.','<p>Официальные сведения размещены на разных ресурсах: портал, каталог программ, навигатор первокурсника, сайты институтов.</p><p>Пользователь начинает с вопроса, а не с названия подразделения.</p><p class="note">Главный портал при сборе вернул HTTP 403. Число ссылок и кликов старого сайта не измерено. Мы не подменяем исследование догадками.</p>')
  add('Четыре принципа.','<div class="principles"><p>01<br><b>Начинать с задачи.</b><br>«Где моя пара?» важнее структуры отдела.</p><p>02<br><b>Говорить честно.</b><br>Источник рядом. Неизвестное — явно.</p><p>03<br><b>Объединять поиск.</b><br>Страницы, программы и службы.</p><p>04<br><b>Быть доступным.</b><br>Телефон, клавиатура и офлайн.</p></div>',color='pink')
  add('Понятная структура.','<div class="principles"><p><b>Поступление</b><br>Маршрут · каталог · квиз</p><p><b>Обучение</b><br>Институты · студенту · расписание</p><p><b>Наука</b><br>Исследования · партнёрам</p><p><b>Жизнь в УрФУ</b><br>Кампус · аудитории · сообщества</p><p><b>Об университете</b><br>История · новости · контакты</p><p><b>Сервисы рядом</b><br>Поиск · доступность · язык · кабинет</p></div>')
  add('Один сайт.<br>Разные маршруты.','<p>Поступаете, учитесь, работаете или представляете партнёра?</p><p>Роль меняет заголовок и быстрые действия главной. Выбор сохраняется на устройстве при разрешённом локальном хранении.</p><p>Сервисы остаются доступны независимо от выбранной роли.</p>',image='home',color='purple')
  add('Ответ ближе.','<div class="principles"><p><b>Программа</b><br>Главная → каталог</p><p><b>Стоимость</b><br>Каталог → программа</p><p><b>Аудитория</b><br>Главная → код корпуса</p><p><b>Расписание</b><br>Нижняя панель → группа</p><p><b>Поселение</b><br>Кампус → чек-лист</p><p><b>Стипендия</b><br>Студенту → поддержка</p><p><b>Служба</b><br>Поиск → контакт</p><p><b>Поделиться</b><br>Каталог → ссылка</p></div><p class="note">Это маршруты прототипа, не сравнительное измерение со старым порталом.</p>')
  add('Первый экран —<br>приглашение к действию.','<p>Крупное обещание. Понятный следующий шаг. Выбор роли и поиск.</p><p>Настоящая фотография УрФУ с указанием источника.</p>',image='home',color='green')
  add('На телефоне —<br>тот же университет.','<div class="phones"><img src="screenshots/mobile.png" alt="Мобильная главная"><img src="screenshots/mobile-catalog.png" alt="Мобильный каталог"><div><p>Нижняя панель из основных сервисов.</p><p>Фильтры, поля и кнопки доступны на узком экране.</p><p>Ширины от 320 px проверяются отдельно.</p></div></div>',color='pink')
  add('Не листать.<br>Подбирать.','<p>Фильтры по предметам, области, институту, уровню, бюджету и цене.</p><p>Сравнение до трёх программ. Подборка сохраняется в адресе страницы.</p>',image='catalog')
  add('Программа<br>без квеста.','<p>Описание, вступительные испытания, места, цена и руководитель — рядом.</p><p>Минимумы не выдаются за проходные баллы. У каждого значения есть официальный источник.</p>',image='program',color='purple')
  add('«Общага» —<br>это общежитие.','<p>Поиск понимает привычные слова: «общага», «стипуха», «пары», «приёмка».</p><p>Синонимы, е/ё и простые опечатки обрабатываются локально, без внешнего ИИ.</p>',image='search')
  add('Полезно<br>каждый день.','<p>Демо-расписание: дни и недели, сохранение группы и файл .ics.</p><p>Код аудитории ведёт к подтверждённому корпусу. Этаж без источника не придумывается.</p>',image='schedule',color='green')
  add('Переезд<br>по шагам.','<p>Поселение, документы, локальный чек-лист и условная схема кампусов.</p><p>Нет приказа с тарифом — нет придуманной цены. Калькулятор считает только известные расходы.</p>',image='campus',color='pink')
  add('Уральский характер.','<div class="palette"><div style="background:#07584b;color:white">Малахит</div><div style="background:#d5f64b">Новый рост</div><div style="background:#f3a6ca">Родонит</div><div style="background:#b9a9ed">Аметист</div><div style="background:#ff956d">Яшма</div></div><p>Знак «У» превращается в маршрут. Грань повторяется в фотографии, стрелках и разделителях.</p><p>Oswald — плакатные заголовки. Golos Text — спокойный интерфейс.</p>')
  add('Настроить<br>под себя.','<p>Пять контрастных схем, размер текста, интервалы, изображения и шрифт.</p><p>Видимый фокус, семантика, подписи полей, диалоги с возвратом фокуса и reduced-motion.</p><p class="note">Полный ручной аудит WCAG 2.2 AA ещё предстоит; автоматический результат не равен сертификации.</p>',image='accessibility',color='purple')
  add('Лёгкий сайт.<br>Без внешних зависимостей.','<p>HTML + CSS + чистый JavaScript. Готовые страницы лежат в репозитории.</p><p>Шрифты, фото и данные локальные. Нет CDN, счётчиков, внешних карт и запросов к собственным JSON.</p><p>Офлайн-кеш работает по HTTP/HTTPS. Прямое file:// предусмотрено архитектурой; управляемый браузер среды блокирует такую проверку.</p>')
  add('Доказательства,<br>а не обещания.','<p><b>101 программа</b> — официальный каталог 2026 года.<br><b>82 английских названия</b> — официальные страницы.</p><p>Локальный Lighthouse: '+(' · '.join(k+': '+str(v) for k,v in lh.items()) if lh else 'результаты в процессе')+'.</p><p>Источники, снимок данных и скрипт сбора приложены. Неполученные сроки 2027 года, проходные баллы и тарифы общежитий отмечены явно.</p><p class="note">Оценки локального запуска не являются PageSpeed Insights публичного сайта.</p>',color='green')
  add('Большое начинается<br>с понятного шага.','<p class="promise">Сначала — проверить задачи с людьми.<br>Потом — подключить официальные данные.<br>Дальше — переносить разделы по одному.</p><p>Сохраняем адреса, доступность и доверие.<br>Свой маршрут. Общий университет.</p>',color='pink')
  html='''<!doctype html><html lang="ru"><meta charset="utf-8"><title>УрФУ · Свой маршрут — дизайн-проект</title><style>@font-face{font-family:Golos;src:url('../assets/fonts/GolosText.woff2')}@font-face{font-family:Oswald;src:url('../assets/fonts/Oswald.woff2')}*{box-sizing:border-box}body{margin:0;color:#172321;background:#f6f5ed;font-family:Golos,Arial,sans-serif}@page{size:A4 landscape;margin:0}.slide{position:relative;width:297mm;height:210mm;padding:14mm 18mm 16mm;break-after:page;overflow:hidden;background:#f6f5ed}.slide:last-child{break-after:auto}.eyebrow{font-size:11px;letter-spacing:.12em;margin-bottom:20px}h1{font:600 65px/1 Oswald,sans-serif;text-transform:uppercase;letter-spacing:-.03em;margin:0 0 30px}p{font-size:20px;line-height:1.5;margin:0 0 18px;max-width:900px}.promise{font-size:29px;max-width:880px}.note{font-size:13px;line-height:1.5}.layout{display:grid;grid-template-columns:.65fr 1fr;gap:28px}.layout p{font-size:17px}.layout>img{width:100%;height:365px;object-fit:cover;object-position:top;border-radius:12px;border:1px solid #17232130}.principles{display:grid;grid-template-columns:1fr 1fr;gap:15px 40px}.principles p{font-size:18px}.palette{display:flex;gap:12px;margin:30px 0}.palette>div{height:150px;flex:1;padding:20px;display:flex;align-items:end;border-radius:12px;font-size:16px}.phones{display:flex;gap:40px;align-items:start}.phones img{height:420px;border:2px solid #172321;border-radius:20px}.phones>div{padding-top:20px}.phones p{font-size:18px}.green{background:#07584b;color:#f6f5ed}.green h1{color:#d5f64b}.pink{background:#f3a6ca}.purple{background:#b9a9ed}footer{position:absolute;bottom:11mm;left:18mm;right:18mm;display:flex;justify-content:space-between;font-size:10px;opacity:.8}</style>'''+''.join(slides)+'</html>'
  (D/'presentation.html').write_text(html)
  await p.goto('http://127.0.0.1:4173/docs/presentation.html');await p.evaluate('document.fonts.ready');await p.pdf(path=str(D/'urfu-design-project.pdf'),print_background=True,prefer_css_page_size=True)
  await b.close()
 print('PDF and 9 actual screenshots generated.')
asyncio.run(main())
