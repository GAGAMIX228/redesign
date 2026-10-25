"""All 30,720 answer sets through the actual result renderer, against official data."""
import asyncio,itertools
from playwright.async_api import async_playwright
from common import *
async def main():
    errors=[]
    async with async_playwright() as pw:
        b=await launch(pw);p=await b.new_page(reduced_motion='reduce',service_workers='block');p.on('pageerror',lambda e:errors.append(str(e)))
        await p.goto(BASE+'quiz.html');await p.locator('#quiz-next').click();await p.locator('#quiz-next').click()
        areas=await p.locator('input[name=area]').evaluate_all('es=>es.map(e=>e.value)');subjects=await p.locator('#quiz-form input[name=ege]').evaluate_all('es=>es.map(e=>e.value)');priorities=await p.locator('input[name=priority]').evaluate_all('es=>es.map(e=>e.value)')
        reference=[]
        for area in areas:
            for mask in range(1<<len(subjects)):
                chosen={s for i,s in enumerate(subjects) if mask&(1<<i)}
                eligible=[]
                for prog in DATA['programs']:
                    if prog['area']!=area:continue
                    exams=prog['exams'];mandatory={e['name'] for e in exams if e['required']};alternatives={e['name'] for e in exams if not e['required']}
                    if chosen and (not exams or not mandatory.issubset(chosen) or alternatives and not alternatives.intersection(chosen)):continue
                    eligible.append(prog)
                for priority in priorities:
                    selected=eligible[:]
                    if priority=='budget':selected=sorted((x for x in selected if (x['budget'] or 0)>0),key=lambda x:-x['budget'])
                    if priority=='price':selected.sort(key=lambda x:x['price'] if x['price'] is not None else float('inf'))
                    reference.append({'area':area,'mask':mask,'priority':priority,'count':len(selected),'ids':[x['id']for x in selected[:6]]})
        await p.expose_function('quizProgress',lambda n:print('Quiz answer sets',n,flush=True))
        result=await p.evaluate(r'''async rows=>{const f=document.querySelector('#quiz-form'),inputs=[...f.querySelectorAll('[name=ege]')],root=document.querySelector('#quiz-results'),failures=[];let tested=0;for(const row of rows){f.querySelectorAll('[name=area]').forEach(e=>e.checked=e.value===row.area);f.querySelectorAll('[name=priority]').forEach(e=>e.checked=e.value===row.priority);inputs.forEach((e,i)=>e.checked=!!(row.mask&(1<<i)));f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));const ids=[...root.querySelectorAll('.program-card')].map(e=>e.dataset.id);const count=Number(root.querySelector(':scope > p')?.textContent.match(/^(\d+)/)?.[1]||0);if(count!==row.count||JSON.stringify(ids)!==JSON.stringify(row.ids)||(!count&&!root.textContent.includes('Попробуем шире'))||/undefined|NaN|\[object Object\]/.test(root.textContent))failures.push({...row,actual:ids,actualCount:count});tested++;if(tested%256===0){await new Promise(r=>setTimeout(r,0));if(tested%2048===0)await window.quizProgress(tested);}}return {tested,failures};}''',reference)
        await b.close()
    save('10-quiz-exhaustive',{'answer_sets':len(reference),'method':'All results through real form submit handler; all 3 steps/back separately covered by the 97 UI scenarios. Expected results independently computed from the official snapshot.','console_errors':errors,**result})
asyncio.run(main())
