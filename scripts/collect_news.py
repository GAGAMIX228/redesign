"""Collect public official institute news snippets. Requires lxml; no app dependency."""
from pathlib import Path
from datetime import datetime,timezone
import urllib.request,gzip,json
from lxml import html
R=Path(__file__).resolve().parents[1]
URL='https://rtf.urfu.ru/get-news/ru/?rows=2&cols=3&pid=18511&offset=0'
req=urllib.request.Request(URL,headers={'User-Agent':'Mozilla/5.0','Accept-Encoding':'gzip'})
with urllib.request.urlopen(req,timeout=30) as response:raw=response.read()
if raw[:2]==b'\x1f\x8b':raw=gzip.decompress(raw)
d=html.fromstring(raw.decode('utf-8'));items=[]
clean=lambda e:' '.join(e.text_content().split())
for i,node in enumerate(d.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," news-item ")]')):
 ps=node.xpath('.//*[contains(@class,"snippet")]/p');dates=node.xpath('.//*[contains(@class,"date")]');images=node.xpath('.//img/@src')
 if not ps:continue
 items.append({'id':str(i+1),'title':clean(ps[0]),'text':' '.join(clean(x)for x in ps[1:]if clean(x)),'date':clean(dates[0])if dates else 'Дата не указана','image':images[0]if images else None,'source':URL,'collected':datetime.now(timezone.utc).isoformat()})
(R/'data/news.json').write_text(json.dumps(items,ensure_ascii=False,indent=2));(R/'data/news.js').write_text('window.URFU_NEWS = '+json.dumps(items,ensure_ascii=False)+';')
print('Saved',len(items),'official snippets')
