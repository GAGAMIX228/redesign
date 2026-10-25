"""Section 17: PDF bounds, links, QR image and complete MP4 decode/flash analysis."""
import asyncio,subprocess
import numpy as np
import fitz
from PIL import Image,ImageDraw
from playwright.async_api import async_playwright
from common import *
async def main():
    async with async_playwright() as pw:
        b=await launch(pw);p=await b.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce');await p.goto(BASE+'docs/presentation.html');await settle(p)
        bounds=await p.evaluate('''()=>[...document.querySelectorAll('.slide')].flatMap((slide,i)=>{let r=slide.getBoundingClientRect();return [...slide.querySelectorAll('*')].filter(e=>{let x=e.getBoundingClientRect();return x.width&&x.height&&(x.left<r.left-1||x.right>r.right+1||x.top<r.top-1||x.bottom>r.bottom+1)}).map(e=>({slide:i+1,element:e.tagName,class:e.className,text:e.textContent.slice(0,70)}));})''')
        # Exact requested post-fix screenshots, after scrolling every lazy section into view.
        for w in [375,1440]:
            await p.set_viewport_size({'width':w,'height':900})
            for label,path in [('home','index.html'),('catalog','catalog.html'),('program','Program.html?id=9797')]:
                await p.goto(BASE+path);await settle(p);await scroll_all(p);await p.screenshot(path=str(ROOT/'checks/screenshots'/f'{label}-{w}.png'),full_page=False)
        await b.close()
    pdf=fitz.open(ROOT/'docs/urfu-design-project.pdf');outside=[];links=[]
    for i,page in enumerate(pdf):
        for block in page.get_text('blocks'):
            if block[0]<-1 or block[1]<-1 or block[2]>page.rect.width+1 or block[3]>page.rect.height+1:outside.append({'page':i+1,'bounds':block[:4]})
        links += [a.get('uri') for a in page.get_links() if a.get('uri')]
    facts=pdf[16].get_text();pdf_report={'pages':len(pdf),'outside_elements_html':bounds,'outside_text_pdf':outside,'links':links,'has_98_programs':'98 программ'in facts,'has_79_english':'79 английских'in facts,'qr_payload':PUBLIC,'qr_image_present':(ROOT/'assets/site-qr.png').exists()}
    path=ROOT/'docs/urfu-walkthrough-60s.mp4';probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=width,height,codec_name,pix_fmt,r_frame_rate','-of','json',str(path)],text=True))
    raw=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-vf','scale=160:90,format=gray','-f','rawvideo','-'],check=True,capture_output=True).stdout
    frames=np.frombuffer(raw,dtype=np.uint8).reshape(-1,90,160);means=frames.mean(axis=(1,2));delta=np.abs(np.diff(means));bad=np.where(delta>25)[0]
    video={'probe':probe,'decoded_frames':len(frames),'max_adjacent_brightness_change':float(delta.max()),'changes_over_25':[{'time':round(int(i)/25,2),'delta':float(delta[i])} for i in bad],'expected_scene_crossfades_seconds':.5,'compatibility':'H.264, yuv420p, MP4 faststart; actual Windows/Telegram/iPhone player sessions unavailable.'}
    sheet=Image.new('RGB',(960,5*300),'#172321')
    for i,sec in enumerate(range(3,60,6)):
        out=RESULTS/f'video-frame-{sec}.jpg';subprocess.run(['ffmpeg','-y','-v','error','-ss',str(sec),'-i',str(path),'-frames:v','1','-vf','scale=480:270',str(out)],check=True)
        im=Image.open(out);x=(i%2)*480;y=(i//2)*300;sheet.paste(im,(x,y));ImageDraw.Draw(sheet).text((x+12,y+278),str(sec)+' sec',fill='white');out.unlink()
    sheet.save(ROOT/'checks/screenshots/video-contact-sheet.jpg',quality=80)
    save('17-materials',{'pdf':pdf_report,'video':video})
asyncio.run(main())
