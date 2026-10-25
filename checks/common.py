"""Shared audit helpers. Run from the repository root; see checks/README.md."""
import json, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'checks/results'
RESULTS.mkdir(exist_ok=True)
BASE = os.environ.get('CHECK_BASE', 'http://127.0.0.1:4175/').rstrip('/') + '/'
PUBLIC = 'https://gagamix228.github.io/redesign/'
WIDTHS = [320,360,375,390,414,600,768,820,1024,1280,1366,1440,1920,2560]
DATA = json.loads((ROOT/'data/catalogue.json').read_text())
PAGES = [str(p.relative_to(ROOT)) for p in sorted(ROOT.glob('*.html'))+sorted((ROOT/'en').glob('*.html'))]
def route(p):
    return p + {'Program.html':'?id=9797','Institute.html':'?id=0','article.html':'?id=1'}.get(p,'')
def save(name, data):
    (RESULTS/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(name, json.dumps(data,ensure_ascii=False)[:1600],flush=True)
async def launch(pw):
    return await pw.chromium.launch(executable_path=os.environ.get('CHECK_CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
async def settle(p):
    await p.evaluate('document.fonts.ready')
    await p.wait_for_timeout(60)
async def scroll_all(p):
    await p.evaluate('''async()=>{for(let y=0;y<document.documentElement.scrollHeight;y+=600){scrollTo(0,y);await new Promise(r=>setTimeout(r,12));}scrollTo(0,0);}''')
async def axe(p):
    if not await p.evaluate('!!window.axe'):await p.add_script_tag(path=os.environ.get('AXE_PATH',str(ROOT/'checks/vendor/axe.min.js')))
    return await p.evaluate('''async()=>{let r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});return {passes:r.passes.length,violations:r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>({target:n.target,message:n.failureSummary}))}))}}''')
