"""Shared, original contest identity: a modular У and its route system."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EDITION='03'
PALETTE={'blue':'#2448FF','lime':'#DFFF59','coral':'#FF9876','pink':'#FF92CB','violet':'#C2ABFF','ink':'#1B1931','paper':'#FFFDF7'}
MARK_CONTENT='''<rect class="mark-tile" width="72" height="72" rx="19" fill="#2448FF"/><path class="mark-left" d="M13 16h15l12 19-9 15L13 21Z" fill="#FF9876"/><path class="mark-right" d="M47 16h16L36 61H20Z" fill="#DFFF59"/><path class="mark-step" d="M12 51h12v11H12Z" fill="#FFFDF7"/>'''
MARK='<svg class="brand-mark" viewBox="0 0 72 72" fill="none" aria-hidden="true">'+MARK_CONTENT+'</svg>'
STAR='<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 1v22M1 12h22M4 4l16 16M4 20 20 4" stroke="currentColor" stroke-width="3"/></svg>'
SIGNAL='''<svg viewBox="0 0 180 180" fill="none" aria-hidden="true"><path d="M90 12v156M12 90h156M35 35l110 110M35 145 145 35" stroke="currentColor" stroke-width="25"/><circle cx="90" cy="90" r="20" fill="var(--chapter-bg,var(--paper))"/></svg>'''
CHAPTERS={
 'admission':('01','ВХОД В БУДУЩЕЕ','YOUR NEXT CHAPTER','lime'),
 'catalog':('02','НАЙДИТЕ СВОЁ ДЕЛО','FIND YOUR DIRECTION','lime'),
 'Program':('02','ПРОГРАММА ВАШЕГО БУДУЩЕГО','YOUR DEGREE, YOUR FUTURE','lime'),
 'quiz':('03','НАЧНИТЕ С ИНТЕРЕСА','START WITH CURIOSITY','violet'),
 'institutes':('04','РАЗНЫЕ ЗНАНИЯ. ОБЩИЙ УРФУ.','A WORLD OF KNOWLEDGE','violet'),
 'Institute':('04','ВАША КОМАНДА В УРФУ','YOUR UNIVERSITY COMMUNITY','violet'),
 'student':('05','В РИТМЕ ВАШЕГО ДНЯ','YOUR EVERYDAY UNIVERSITY','blue'),
 'schedule':('05','ВАШ ДЕНЬ ПО ПОЛОЧКАМ','MAKE ROOM FOR YOUR DAY','blue'),
 'account':('05','ЛИЧНОЕ ПРОСТРАНСТВО','YOUR OWN SPACE','blue'),
 'science':('06','ЛЮБОПЫТСТВО МЕНЯЕТ МИР','CURIOSITY CHANGES THINGS','blue'),
 'partners':('06','СОЗДАВАТЬ ВМЕСТЕ','MAKE THINGS TOGETHER','blue'),
 'campus':('07','НОВОЕ МЕСТО. ВАШ ДОМ.','A NEW PLACE TO CALL HOME','coral'),
 'room':('07','ВЫ УЖЕ ПОЧТИ НА МЕСТЕ','YOU ARE ALMOST THERE','coral'),
 'life':('08','БОЛЬШЕ, ЧЕМ УЧЁБА','MORE THAN A DEGREE','pink'),
 'news':('09','УНИВЕРСИТЕТ В ДВИЖЕНИИ','A UNIVERSITY IN MOTION','pink'),
 'article':('09','ИСТОРИИ БОЛЬШОГО УНИВЕРСИТЕТА','STORIES WORTH SHARING','pink'),
 'events':('09','МЕСТО ДЛЯ ВСТРЕЧ','MAKE ROOM FOR CONNECTION','pink'),
 'contacts':('10','ОДИН ВОПРОС — ПЕРВЫЙ ШАГ','ASK. FIND. KEEP GOING.','violet'),
 'search':('10','ВАМ СЮДА ЗА ОТВЕТОМ','YOUR ANSWER STARTS HERE','violet'),
 'about':('11','УРАЛЬСКИЙ ХАРАКТЕР','A SPIRIT THAT MOVES FORWARD','lime'),
 'international':('12','ВАШ УРФУ БЕЗ ГРАНИЦ','YOUR URFU, WITHOUT BORDERS','blue'),
 'concept':('13','САЙТ С ВАШИМ ХАРАКТЕРОМ','BUILT AROUND YOUR NEXT STEP','pink'),
 'style':('13','ЯРКИЙ ЗНАК. СВОЙ МАРШРУТ.','A BOLD MARK. YOUR OWN PATH.','violet'),
 '404':('↗','ДРУГОЙ ПОВОРОТ МАРШРУТА','LET’S FIND YOUR WAY BACK','coral'),
}
def logo(en=False):
    return f'<span class="brand">{MARK}<span class="brand-name"><span class="brand-word">{"UrFU" if en else "УрФУ"}<span class="brand-star" aria-hidden="true">{STAR}</span></span><span class="brand-caption">{"YOUR OWN PATH" if en else "СВОЙ МАРШРУТ"}</span></span><span class="sr-only"> · {"Ural Federal University" if en else "Уральский федеральный университет"}</span></span>'

def write_assets():
    assets=ROOT/'assets'
    (assets/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 72 72">'+MARK_CONTENT+'</svg>')
    # Outlined glyphs keep the downloadable identity independent of installed fonts.
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.varLib.instancer import instantiateVariableFont
    font=instantiateVariableFont(TTFont(assets/'fonts/GolosText.woff2'),{'wght':850});glyphs=font.getGlyphSet();cmap=font.getBestCmap();scale=.061
    paths=[];x=93
    for char in 'УрФУ':
        name=cmap[ord(char)];pen=SVGPathPen(glyphs);glyphs[name].draw(TransformPen(pen,(scale,0,0,-scale,x,55)))
        paths.append(pen.getCommands());x+=font['hmtx'].metrics[name][0]*scale
    word='<path fill="#1B1931" d="'+' '.join(paths)+'"/>'
    caption=[];x=94;scale=.0077
    for char in 'СВОЙ МАРШРУТ':
        name=cmap[ord(char)];pen=SVGPathPen(glyphs);glyphs[name].draw(TransformPen(pen,(scale,0,0,-scale,x,74)))
        caption.append(pen.getCommands());x+=font['hmtx'].metrics[name][0]*scale+.8
    word+='<path fill="#1B1931" d="'+' '.join(caption)+'"/>'
    (assets/'logo.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title" viewBox="0 0 305 78"><title id="title">УрФУ · Свой маршрут — конкурсный знак</title><g transform="translate(0 3)">'+MARK_CONTENT+'</g>'+word+'<path d="M284 11v21m-10.5-10.5h21m-18-7.5 15 15m-15 0 15-15" stroke="#D44F32" stroke-width="4"/></svg>')

if __name__=='__main__':write_assets()
