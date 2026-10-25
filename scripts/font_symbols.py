"""Add tiny route glyphs to the local text font; requires fontTools and brotli.
The installed DejaVu Sans is the source for symbol outlines. See bundled licenses.
"""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
R=Path(__file__).resolve().parents[1]
p=R/'assets/fonts/GolosText.woff2';f=TTFont(p);s=TTFont('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
# This horizontal-only website does not need vertical metrics.
for table in ['vmtx','vhea','VVAR']:
 if table in f:del f[table]
variations=f['gvar'].variations if 'gvar' in f else None
f['glyf'];f['hmtx'];glyphs=s.getGlyphSet();cmap=s.getBestCmap();order=f.getGlyphOrder()[:];scale=f['head'].unitsPerEm/s['head'].unitsPerEm
for cp in list(range(0x2190,0x21a0))+[0x2733]:
 if cp not in cmap or cp in f.getBestCmap():continue
 source=cmap[cp];name='routeSymbol'+hex(cp)[2:];pen=TTGlyphPen(None);glyphs[source].draw(TransformPen(pen,(scale,0,0,scale,0,0)));f['glyf'][name]=pen.glyph();adv,lsb=s['hmtx'].metrics[source];f['hmtx'].metrics[name]=(round(adv*scale),round(lsb*scale));order.append(name)
 if variations is not None:variations[name]=[]
 for table in f['cmap'].tables:
  if table.isUnicode():table.cmap[cp]=name
f.setGlyphOrder(order)
for rec in f['name'].names:
 if rec.nameID in [1,4,6,16]:rec.string=('RouteText-Regular' if rec.nameID==6 else 'Route Text').encode(rec.getEncoding())
f.save(p)
print('Route glyphs included in the existing text font.')
