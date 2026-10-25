import concurrent.futures,json,urllib.request,gzip
from pathlib import Path
from lxml import html
R=Path(__file__).resolve().parents[1];data=json.loads((R/'data/catalogue.json').read_text())
def f(p):
 try:
  req=urllib.request.Request(p['englishSource'],headers={'User-Agent':'Mozilla/5.0','Accept-Encoding':'gzip'})
  with urllib.request.urlopen(req,timeout=20) as r:b=r.read()
  if b[:2]==b'\x1f\x8b':b=gzip.decompress(b)
  d=html.fromstring(b);p['enName']=' '.join(d.xpath('//h1')[0].text_content().split())
  if any('\u0400'<=c<='\u04ff' for c in p['enName']):p['enName']=None
 except Exception:p['enName']=None
 return p
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:data['programs']=list(pool.map(f,data['programs']))
(R/'data/catalogue.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
details={p['id']:{'description':p.pop('description',[]),'head':p.pop('head','—')} for p in data['programs']}
(R/'data/programs.js').write_text('window.URFU_DATA = '+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';')
print('English names',sum(bool(p['enName']) for p in data['programs']))
