"""Section 12: dictionary screening plus explicit Russian plural examples."""
import asyncio,re,sys
sys.path.insert(0,'/tmp/urfu-proofread')
from lxml import html
from common import *
from playwright.async_api import async_playwright
async def main():
    words=set();locations={}
    for f in PAGES:
        doc=html.fromstring((ROOT/f).read_text())
        for x in doc.xpath('//script|//style'):x.drop_tree()
        for w in re.findall(r'[А-Яа-яЁё]+',' '.join(doc.itertext())):
            if len(w)>2 and not w.isupper():words.add(w.lower());locations.setdefault(w.lower(),set()).add(f)
    official=set(re.findall(r'[а-яё]+',' '.join(p['name']+' '+p['institute'] for p in DATA['programs']).lower()))
    unknown=[]
    try:
        import pymorphy3
        morph=pymorphy3.MorphAnalyzer()
        for w in sorted(words-official):
            if not morph.word_is_known(w):unknown.append({'word':w,'pages':sorted(locations[w])})
    except ImportError:unknown=[{'unavailable':'Install pymorphy3 for dictionary screening'}]
    rows=[];numbers=[1,2,3,4,5,11,12,14,21,22,25,101,111];indices=[0,1,1,1,2,2,2,2,0,1,2,0,2]
    async with async_playwright() as pw:
        b=await launch(pw);p=await b.new_page();await p.goto(BASE)
        for forms in [['программа','программы','программ'],['место','места','мест'],['день','дня','дней'],['балл','балла','баллов'],['год','года','лет']]:
            for n,index in zip(numbers,indices):
                actual=await p.evaluate('([n,forms])=>window.plural(n,forms)',[n,forms]);rows.append({'n':n,'word':actual,'expected':forms[index],'passed':actual==forms[index]})
        await b.close()
    save('12-text',{'dictionary_words':len(words),'dictionary_candidates':unknown,'plurals':rows,'note':'Dictionary candidates include proper names, colloquialisms and technical terms; they require editorial review, not automatic replacement. Official program titles retain their source spelling.'})
asyncio.run(main())
