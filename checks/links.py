"""BFS of rendered links, query-state pages, anchors and external link checks."""
import asyncio, concurrent.futures, urllib.request, urllib.error, urllib.parse
from playwright.async_api import async_playwright
from common import *
def external(url):
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req,timeout=15) as r:return {'url':url,'status':r.status,'final':r.url}
    except urllib.error.HTTPError as e:return {'url':url,'status':e.code,'classification':'blocked_by_source' if e.code in [401,403,429] else 'broken'}
    except Exception as e:return {'url':url,'status':None,'classification':'unavailable','reason':str(e)}
async def main():
    queue=['index.html'];seen=set();edges=[];failures=[];outside=set();console=[]
    async with async_playwright() as pw:
        b=await launch(pw);p=await b.new_page(reduced_motion='reduce')
        p.on('pageerror',lambda e:console.append(str(e)))
        while queue:
            path=queue.pop(0)
            if path in seen:continue
            seen.add(path)
            response=await p.goto(BASE+path)
            if response.status>=400:failures.append({'page':path,'status':response.status});continue
            await settle(p)
            links=await p.locator('a').evaluate_all('es=>es.map(e=>({href:e.getAttribute("href"),target:e.target,rel:e.rel,text:e.textContent}))')
            ids=await p.locator('[id]').evaluate_all('es=>es.map(e=>e.id)')
            for a in links:
                raw=a['href'];edges.append({'from':path,**a})
                if raw is None or raw.strip() in ['', '#']:failures.append({'page':path,'empty_link':raw});continue
                u=urllib.parse.urlsplit(urllib.parse.urljoin(BASE+path,raw))
                if u.scheme not in ['http','https']:continue
                if not urllib.parse.urlunsplit((u.scheme,u.netloc,'','',''))==urllib.parse.urlunsplit(urllib.parse.urlsplit(BASE)[:2]+('','','')):
                    outside.add(urllib.parse.urlunsplit((u.scheme,u.netloc,u.path,u.query,'')))
                    if a['target']!='_blank' or 'noopener' not in a['rel'].split() or not any(s in a['text'] for s in ['откроется в новой вкладке','opens in a new tab']):failures.append({'page':path,'external_semantics':a})
                    continue
                rel=urllib.parse.urlunsplit(('', '', u.path[len(urllib.parse.urlsplit(BASE).path):],u.query,'')) or 'index.html'
                if not u.path.endswith('.html') and not u.path.endswith('/'):continue
                target=ROOT/urllib.parse.unquote(u.path[len(urllib.parse.urlsplit(BASE).path):])
                if u.fragment:
                    if urllib.parse.urlsplit(path).path==urllib.parse.urlsplit(rel).path:
                        exists=urllib.parse.unquote(u.fragment) in ids
                    else:
                        from lxml import html
                        exists=target.is_file() and bool(html.fromstring(target.read_bytes()).xpath('//*[@id=$id]',id=urllib.parse.unquote(u.fragment)))
                    if not exists:failures.append({'page':path,'missing_anchor':raw})
                if rel not in seen and rel not in queue:queue.append(rel)
            if len(seen)%25==0:print('Crawled',len(seen),flush=True)
        await b.close()
    ext=list(concurrent.futures.ThreadPoolExecutor(max_workers=5).map(external,sorted(outside)))
    save('02-links',{'rendered_pages':len(seen),'pages':sorted(seen),'links_followed':len(edges),'unique_external_links':len(outside),'failures':failures,'console_errors':console,'external':ext,'unreachable_templates':sorted(set(PAGES)-{urllib.parse.urlsplit(s).path for s in seen})})
asyncio.run(main())
