from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
files=['./']+[str(p.relative_to(R)) for glob in ['*.html','en/*.html','css/*.css','js/*.js','assets/fonts/*.woff2','assets/images/*.webp','data/programs.js','data/news.js','data/services.js','data/program-details/*.js','assets/*.svg'] for p in R.glob(glob)]
digest=hashlib.sha256()
for item in sorted(p for p in files if p!='./'):
 digest.update(item.encode());digest.update((R/item).read_bytes())
version=digest.hexdigest()[:10]
(R/'sw.js').write_text('''/* Offline shell. Only same-origin GET requests; official external links are never cached. */
const VERSION = 'urfu-'''+version+"';\nconst ASSETS = "+json.dumps(files)+''';
self.addEventListener('install',e=>e.waitUntil(caches.open(VERSION).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('urfu-')&&k!==VERSION).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{
 const url=new URL(e.request.url);if(url.origin!==location.origin||e.request.method!=='GET')return;
 e.respondWith(fetch(e.request).then(r=>{if(r.ok){const copy=r.clone();caches.open(VERSION).then(c=>c.put(e.request,copy));}return r;}).catch(()=>caches.match(e.request).then(r=>r||caches.match(url.pathname).then(r=>r||caches.match('404.html')))));
});
''')
print('Offline assets',len(files),'version',version)
