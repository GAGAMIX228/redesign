"""Split an enriched source snapshot and regenerate all ready-to-use site assets."""
from pathlib import Path
import json,runpy
R=Path(__file__).resolve().parents[1]
data=json.loads((R/'data/catalogue.json').read_text());details={}
(R/'data/program-details').mkdir(exist_ok=True)
for p in data['programs']:
 details[p['id']]={'description':p.pop('description',[]),'head':p.pop('head','—')}
 (R/'data/program-details'/(p['id']+'.js')).write_text('window.URFU_DETAILS = '+json.dumps({p['id']:details[p['id']]},ensure_ascii=False,separators=(',',':'))+';')
(R/'data/programs.js').write_text('window.URFU_DATA = '+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';')
runpy.run_path(str(R/'scripts/build.py'))
runpy.run_path(str(R/'scripts/offline.py'))
