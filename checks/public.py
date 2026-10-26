"""Post-publication HTTPS verification with normal certificate validation."""
import concurrent.futures,gzip,hashlib,urllib.request,urllib.error,urllib.parse,asyncio,subprocess
from common import *
def get(path):
    sep='&' if '?' in path else '?';url=PUBLIC+urllib.parse.quote(path,safe='/?=&,%:+')+sep+'audit='+hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest()[:10]
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept-Encoding':'gzip'})
    try:
        with urllib.request.urlopen(req,timeout=25) as r:raw=r.read();status=r.status
    except urllib.error.HTTPError as e:raw=e.read();status=e.code
    if raw[:2]==b'\x1f\x8b':raw=gzip.decompress(raw)
    file=ROOT/(urllib.parse.unquote(urllib.parse.urlsplit(path).path) or 'index.html')
    if status==404 and not file.is_file():file=ROOT/'404.html'
    return {'path':path,'status':status,'matches_local':file.is_file() and raw==file.read_bytes(),'bytes':len(raw)}
async def main():
    crawl=json.loads((RESULTS/'02-links.json').read_text());paths=sorted(set(crawl['pages']+PAGES+['css/site.css','css/evolution.css','css/identity.css','js/app.js','js/motion.js','sw.js','sitemap.xml','robots.txt','assets/apple-touch-icon.png','assets/favicon.svg','assets/favicon-32.png','assets/logo.svg','assets/site-qr.png','docs/urfu-design-project.pdf','docs/urfu-walkthrough-60s.mp4']+['assets/og/'+p.name for p in (ROOT/'assets/og').glob('*.png')]))
    rows=list(concurrent.futures.ThreadPoolExecutor(max_workers=5).map(get,paths));failures=[r for r in rows if r['status']!=200 or not r['matches_local']]
    notfound=get('not-a-page/deep/missing.html');browser={}
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        b=await launch(pw);p=await b.new_page()
        try:await p.goto(PUBLIC,timeout=20000);browser={'status':'opened','heading':await p.locator('h1').inner_text()}
        except Exception as exc:browser={'status':'unavailable','reason':str(exc).splitlines()[0]}
        await b.close()
    save('18-public',{'edition':'03','commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'status':'passed' if not failures and notfound['status']==404 and notfound['matches_local'] else 'failed','url':PUBLIC,'https_checked':len(rows),'results':rows,'failures':failures,'nested_404':notfound,'direct_browser':browser})
if __name__=='__main__':asyncio.run(main())
