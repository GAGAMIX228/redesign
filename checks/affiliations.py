"""Verify unique IDs, titles and institute memberships against the live catalogue."""
import datetime,re
from data_audit import fetch,text
from common import *
doc=fetch(DATA['source']);rows=[]
for table in doc.xpath('//table[contains(@class,"edu-programs-list")]'):
    institute=text(table.getprevious())
    for tr in table.xpath('.//tbody/tr'):
        links=tr.xpath('.//a');match=re.search(r'/ru/(\d+)/',links[0].get('href','')) if links else None
        if match:rows.append({'id':match[1],'name':text(links[0]),'institute':institute})
failures=[]
for p in DATA['programs']:
    actual=[r for r in rows if r['id']==p['id']]
    if {r['name'] for r in actual}!={p['name']} or {r['institute'] for r in actual}!=set(p.get('institutes',[p['institute']])):failures.append({'id':p['id'],'live':actual})
save('01-affiliations',{'official_rows':len(rows),'unique_programs':len({r['id'] for r in rows}),'checked':datetime.datetime.now(datetime.timezone.utc).isoformat(),'failures':failures})
