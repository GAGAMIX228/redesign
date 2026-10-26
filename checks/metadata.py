"""Sections 12–14: metadata, local OG assets, structured data and sensitive files."""
import collections,re,subprocess
from urllib.parse import urlsplit
from lxml import html
from PIL import Image
from common import *
def main():
    rows=[];titles=[];desc=[];problems=[]
    for f in PAGES:
        p=ROOT/f;d=html.fromstring(p.read_text());title=d.xpath('string(//title)');description=d.xpath('//meta[@name="description"]/@content');titles.append(title);desc.extend(description)
        missing=[label for label,q in [('lang','/html/@lang'),('charset','//meta[@charset]'),('viewport','//meta[@name="viewport"]'),('canonical','//link[@rel="canonical"]'),('apple-icon','//link[@rel="apple-touch-icon"]'),('schema','//script[@type="application/ld+json"]')] if not d.xpath(q)]
        image=d.xpath('//meta[@property="og:image"]/@content');image_path=(ROOT/urlsplit(image[0]).path.split('/redesign/')[-1]) if image and image[0].startswith('https:') else p.parent/(urlsplit(image[0]).path if image else 'missing')
        dimensions=Image.open(image_path).size if image_path.is_file() else None
        if missing or dimensions!=(1200,630):problems.append({'page':f,'missing':missing,'og_dimensions':dimensions})
        for s in d.xpath('//script[@type="application/ld+json"]/text()'):
            try:
                obj=json.loads(s);assert obj.get('@context')=='https://schema.org';assert obj.get('@type')in ['WebSite','EducationalOrganization']
            except Exception as e:problems.append({'page':f,'schema_error':str(e)})
        rows.append({'page':f,'title':title,'description':description,'missing':missing,'og_dimensions':dimensions})
    tracked=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines();secrets=[];junk=[]
    pattern=re.compile(r'(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
    for f in tracked:
        p=ROOT/f
        if p.name in ['.env','.env.local','credentials.json','id_rsa']:junk.append(f)
        if any(x in p.parts for x in ['__pycache__','node_modules','.cache']) or p.suffix in ['.zip','.tmp','.pyc']:junk.append(f)
        if p.is_file() and p.stat().st_size<2_000_000:
            try:
                if pattern.search(p.read_text()):secrets.append(f)
            except UnicodeError:pass
    save('13-metadata-security',{'pages':rows,'failures':problems,'duplicate_titles':[t for t,n in collections.Counter(titles).items()if n>1],'duplicate_descriptions':[t for t,n in collections.Counter(desc).items()if n>1],'secret_files':secrets,'junk_files':junk,'robots':(ROOT/'robots.txt').exists(),'sitemap':(ROOT/'sitemap.xml').exists()})
if __name__=='__main__':main()
