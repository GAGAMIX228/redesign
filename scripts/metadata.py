"""Publication metadata, sitemap and owned favicon assets. No runtime dependency."""
import html,json
from pathlib import Path
SITE='https://gagamix228.github.io/redesign/'
def enrich(document,file,en=False):
    path=('en/' if en else '')+file;url=SITE+path;pre='../' if en else ''
    image=SITE+'assets/og/'+('en-' if en else '')+file.replace('.html','.png')
    import re
    document=re.sub(r'(<meta property="og:image" content=")[^"]*(")',lambda m:m[1]+image+m[2],document)
    tags=f'<link rel="canonical" href="{url}"><meta property="og:url" content="{url}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"><link rel="apple-touch-icon" sizes="180x180" href="{pre}assets/apple-touch-icon.png"><link rel="icon" type="image/png" sizes="32x32" href="{pre}assets/favicon-32.png">'
    if file in ['index.html','catalog.html','contacts.html','admission.html']:
        tags+=''.join(f'<link rel="alternate" hreflang="{lang}" href="{SITE+prefix+file}">' for lang,prefix in [('ru',''),('en','en/'),('x-default','')])
    schema={'@context':'https://schema.org','@type':'WebSite','@id':SITE+'#website','url':SITE,'name':'Свой маршрут — конкурсный прототип сайта УрФУ','inLanguage':['ru','en'],'description':'Независимая конкурсная концепция. Не официальный сайт университета.','about':{'@type':'EducationalOrganization','name':'Уральский федеральный университет','url':'https://urfu.ru/'}}
    tags+='<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')+'</script>'
    return document.replace('</head>',tags+'</head>')
def sitemap(root,data,news):
    paths=[str(p.relative_to(root)) for p in sorted(root.glob('*.html'))+sorted((root/'en').glob('*.html')) if p.name not in ['404.html','Program.html','Institute.html','article.html']]
    paths+=['Program.html?id='+p['id'] for p in data['programs']]
    paths+=['Institute.html?id='+str(i) for i in range(len(data['institutes']))]
    paths+=['article.html?id='+n['id'] for n in news]
    (root/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('<url><loc>'+html.escape(SITE+p)+'</loc></url>\n' for p in paths)+'</urlset>\n')
    (root/'robots.txt').write_text('User-agent: *\nAllow: /redesign/\nSitemap: '+SITE+'sitemap.xml\n')
