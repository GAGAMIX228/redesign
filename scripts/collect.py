#!/usr/bin/env python3
"""Official catalogue snapshot. Tool dependency: lxml. Runtime site has no dependencies.
Run: python scripts/collect.py. Never infer absent prices or passing scores.
"""
import argparse, concurrent.futures, datetime, gzip, json, re, urllib.request
from pathlib import Path
from lxml import html
from catalogue_normalize import normalize
ROOT=Path(__file__).resolve().parents[1]
BASE='https://programs.edu.urfu.ru'
URL=BASE+'/ru/?year=2026&lvl=bac&lvl=spc&frm=ft'
STAMP=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(url):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; UrFUPrototype/1.0)','Accept-Encoding':'gzip'})
 with urllib.request.urlopen(req,timeout=35) as r:
  raw=r.read()
  if raw[:2]==b'\x1f\x8b':raw=gzip.decompress(raw)
  return html.fromstring(raw)
def text(el):return ' '.join(el.text_content().split())
def num(s):
 s=re.sub(r'[^\d]','',s)
 return int(s) if s else None
def collect():
 args=argparse.ArgumentParser();args.add_argument('--snapshot',type=Path,help='Explicit previously downloaded official catalogue HTML');opts=args.parse_args();doc=html.parse(str(opts.snapshot)).getroot() if opts.snapshot else read(URL);items=[]
 for table in doc.xpath('//table[contains(@class,"edu-programs-list")]'):
  inst=text(table.getprevious())
  for tr in table.xpath('.//tbody/tr'):
   cells=tr.xpath('./td');links=tr.xpath('.//a')
   if not links or len(cells)<4:continue
   a=links[0];pid=re.search(r'/ru/(\d+)/',a.get('href',''))
   if not pid:continue
   direction=text(cells[2]);code=re.match(r'[\d.]+',direction)
   items.append(dict(id=pid[1],name=text(a),code=code[0] if code else '',institute=inst,level=text(cells[-1]),source=BASE+a.get('href'),year=2026,collected=STAMP))
 def detail(p):
  try:
   doc=read(p['source']);features={}
   for f in doc.xpath('//div[contains(@class,"feature-item")]'):
    h=f.xpath('.//*[contains(@class,"feature-item-header")]');d=f.xpath('.//*[contains(@class,"feature-item-description")]')
    if h and d:features[text(h[0]).rstrip(':')]=text(d[0])
   p['duration']=features.get('Форма и срок обучения','—');p['years']=features.get('Год(ы) набора','—')
   p['description']=[text(x) for x in doc.xpath('//article[contains(@class,"about")]//p') if len(text(x))>40][:5]
   p['exams']=[];p['budget']=p['paid']=p['price']=p['discountPrice']=p['passing']=None
   for item in doc.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," actual-item ")]'):
    footer=item.xpath('.//*[contains(@class,"actual-item-footer")]');kind=text(footer[0]) if footer else ''
    table=item.xpath('.//table');required=True
    for t in table[:1]:
     for tr in t.xpath('.//tr'):
      td=tr.xpath('./td')
      if not td:continue
      label=text(td[0]);v=text(td[-1])
      if 'По выбору' in label:required=False;continue
      if 'Вступительные' in kind and len(td)>1 and num(v) is not None:p['exams'].append({'name':label,'min':num(v),'required':required})
      if 'Количество мест' in kind:
       if label=='Бюджетных':p['budget']=num(v)
       if label=='Внебюджетных':p['paid']=num(v)
      if 'Стоимость' in kind:
       if label=='Полная':p['price']=num(v)
       if label=='Со скидкой':p['discountPrice']=num(v)
   p['head']='; '.join(text(x) for x in doc.xpath('//*[contains(@class,"teachers-name")]')[:1]) or 'Не указан'
   p['englishSource']=p['source'].replace('/ru/','/en/')
   p['area']=('IT и математика' if p['code'].startswith(('01','02','09','10','11')) else 'Инженерия' if p['code'].startswith(('08','12','13','14','15','16','18','20','21','22','23','24','27','28','29')) else 'Естественные науки' if p['code'].startswith(('03','04','05','06')) else 'Общество и экономика' if p['code'].startswith(('37','38','39','40','41','42','43','44')) else 'Гуманитарные науки')
   print(p['id'],p['name'],flush=True)
  except Exception as e:p['error']=str(e);print('ERROR',p['id'],e,flush=True)
  return p
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:items=list(ex.map(detail,items))
 payload={'collected':STAMP,'source':URL,'year':2026,'programs':normalize(items),'institutes':[text(x) for x in doc.xpath('//select[@name="inst"]/option[@value!=""]')]}
 (ROOT/'data/programs.js').write_text('window.URFU_DATA = '+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+';\n')
 (ROOT/'data/catalogue.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2))
 print('Saved',len(items),'programs')
if __name__=='__main__':collect()
