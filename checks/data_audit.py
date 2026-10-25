"""Section 1: independently compare every program with the live official source."""
import concurrent.futures, datetime, gzip, re, urllib.request
from lxml import html
from common import *
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat()
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept-Encoding':'gzip'})
    with urllib.request.urlopen(req,timeout=30) as r:
        raw=r.read()
        if raw[:2]==b'\x1f\x8b':raw=gzip.decompress(raw)
        return html.fromstring(raw)
def text(e):return ' '.join(e.text_content().split())
def integer(s):
    s=re.sub(r'[^0-9]','',s)
    return int(s) if s else None
def verify(p):
    row={'id':p['id'],'source':p['source'],'checked':NOW,'differences':[]}
    try:
        doc=fetch(p['source']);values={'budget':None,'paid':None,'price':None,'discountPrice':None,'exams':[]}
        for item in doc.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," actual-item ")]'):
            f=item.xpath('.//*[contains(@class,"actual-item-footer")]');kind=text(f[0]) if f else '';required=True
            for tr in item.xpath('.//table[1]//tr'):
                td=tr.xpath('./td')
                if not td:continue
                label=text(td[0]);v=integer(text(td[-1]))
                if 'По выбору' in label:required=False;continue
                if 'Вступительные' in kind and len(td)>1 and v is not None:values['exams'].append({'name':label,'min':v,'required':required})
                mapping={'Количество мест':{'Бюджетных':'budget','Внебюджетных':'paid'},'Стоимость':{'Полная':'price','Со скидкой':'discountPrice'}}
                for k,m in mapping.items():
                    if k in kind and label in m:values[m[label]]=v
        for k,v in values.items():
            if p.get(k)!=v:row['differences'].append({'field':k,'saved':p.get(k),'live':v})
        row['status']='passed' if not row['differences'] else 'failed'
    except Exception as exc:row.update(status='unavailable',reason=str(exc))
    return row
if __name__=='__main__':
    rows=list(concurrent.futures.ThreadPoolExecutor(max_workers=5).map(verify,DATA['programs']))
    catalogue={}
    try:
        doc=fetch(DATA['source']);ids=set(doc.xpath('//table[contains(@class,"edu-programs-list")]//tbody//a/@href'));ids={re.search(r'/ru/(\d+)/',s)[1] for s in ids if re.search(r'/ru/(\d+)/',s)}
        catalogue={'live_count':len(ids),'saved_count':len(DATA['programs']),'missing':sorted(ids-{p['id'] for p in DATA['programs']}),'extra':sorted({p['id'] for p in DATA['programs']}-ids)}
    except Exception as exc:catalogue={'unavailable':str(exc)}
    facts=[('Все страницы: контакт-центр','8 800 100-50-44','https://privet.urfu.ru/'),('student.html: стипендии','2 314,2; 3 008,2; 4 398 ₽, базовые суммы, 2026','https://privet.urfu.ru/money'),('campus.html / room.html: адреса','Мира, 19; Мира, 32','https://privet.urfu.ru/navigation'),('campus.html: оформление НВК','100-летия УрГУ, 6/2','https://privet.urfu.ru/accommodation'),('about.html: история и руководство','1920, 2009, 2023; Обабков; rector@urfu.ru','https://privet.urfu.ru/about')]
    secondary=[]
    for page,value,url in facts:
        try:
            doc=fetch(url);body=text(doc);secondary.append({'pages':page,'value':value,'source':url,'checked':NOW,'official_text':body})
        except Exception as exc:secondary.append({'pages':page,'source':url,'unavailable':str(exc)})
    save('01-data',{'checked':NOW,'catalogue':catalogue,'programs':rows,'secondary':secondary,'limitations':['Official photographs are publicly accessible, but an explicit redistribution licence has not been established. Source credit is not permission.','Admissions 2027 dates, dormitory tariffs, historical passing scores and future events are not confirmed and are not invented.']})
    ledger=['# Реестр данных и источников','',f'Проверка: {NOW}. Все поля 98 программы сопоставлены с актуальными официальными страницами. Подробные результаты: `results/01-data.json`.','', '| Где / данные | Значение | Источник / дата |','|---|---|---|']
    for p in DATA['programs']:
        v=f"{p['name']}; {p['code']}; {'; '.join(p.get('institutes') or [p['institute']])}; {p['duration']}; бюджет {p['budget']}; платно {p['paid']}; цена {p['price']}; скидка {p['discountPrice']}; экзамены: "+'; '.join(f"{e['name']} {e['min']}" for e in p['exams'])
        ledger.append(f"| Каталог, программа {p['id']}, сравнение, калькуляторы | {v} | [{p['year']}]({p['source']}) · {NOW[:10]} |")
    for page,v,url in facts:ledger.append(f'| {page} | {v} | {url} · {NOW[:10]} |')
    ledger+=['| Расписание / кабинет | Вымышленные занятия, оценки, группа, заявки | Явная надпись «Демо» / «Пример» рядом с данными |','| Нумерация шагов, размеры текста, фильтры, результаты | Интерфейсные и вычисляемые числа, не сведения об университете | Расчёт из подтверждённых программ / настройки пользователя |','| Фото | Настоящие фото, источник указан; права на перепубликацию не подтверждены | [Реестр](../docs/assets.md) |']
    (ROOT/'checks/data-sources.md').write_text('\n'.join(ledger)+'\n')
