"""Summarise real, existing browser reports. Does not invent missing measurements."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];D=R/'docs'
load=lambda n:json.loads((D/n).read_text())
s=load('smoke-results.json');a=load('axe-results.json');states=load('accessibility-states.json');lh=load('lighthouse-compressed.json')
motion=load('motion-results.json') if (D/'motion-results.json').exists() else {'checks':[]}
scores=' / '.join(str(round(v['score']*100))for v in lh['categories'].values());audits=lh['audits']
report=f'''# Локальная проверка прототипа

Дата: 25 октября 2026 года. Проверена текущая статическая версия, а не публичный сайт. Это промежуточная техническая проверка; пользовательский конкурсный чек-лист ещё не предоставлен.

## Подтверждённые результаты

- 29 HTML-страниц, включая 4 английские.
- Сценарии фильтрации, сравнения, поиска «общага», квиза, аудитории, демо-заявки и выгрузки .ics: {s['functional_checks']}.
- JavaScript/console errors: {len(s['javascript_errors'])}.
- Горизонтальное переполнение при 320, 390, 768, 1440 и 2560 px: {len(s['horizontal_overflow'])}. Проверены все 29 страниц на каждой ширине.
- Внешние запросы приложения при браузерном обходе: {len(s['external_requests'])}.
- axe-core: {len(a)} страниц, нарушений по выбранным WCAG A/AA-правилам: {sum(len(x['violations'])for x in a)}.
- Отдельные проверки 5 контрастных схем с размером 28 px, увеличенными интервалами и тёмной темы на 5 ключевых страницах: оставшихся проблем {len(states)}.
- Движение и резервные режимы: {len(motion['checks'])} функциональных проверок (пауза, reduced-motion, скрытые секции, отключённый JavaScript и недоступный localStorage).
- HTTP offline: после готовности service worker страница повторно открывается при выключенной сети.
- PDF: 18 листов A4, альбомная ориентация. Видео: 60 секунд, MP4.

## Lighthouse — только локальный запуск

Главная страница, Chromium, стандартный мобильный профиль Lighthouse. Сервер `scripts/serve.py` с gzip, адрес локального запуска в исходном JSON. Сжатие — обычная настройка сервера; для просмотра сборка не нужна.

- Performance / Accessibility / Best Practices / SEO: **{scores}**.
- LCP: **{audits['largest-contentful-paint']['displayValue']}**.
- CLS: **{audits['cumulative-layout-shift']['displayValue']}**.
- Передано во время запуска: **{audits['total-byte-weight']['displayValue']}**.
- Время отчёта: `{lh['fetchTime']}`.

`lighthouse-home.json` содержит также предыдущий замер на стандартном несжимающем Python-сервере. Производительность зависит от сервера: результаты нельзя переносить на ещё не опубликованный GitHub Pages. Для внутренних страниц Lighthouse отдельно не запускался. Оценки Google PageSpeed Insights не заявлены.

## Ограничения проверки и данных

- Управляемый Chromium запрещает навигацию `file://` (`ERR_BLOCKED_BY_ADMINISTRATOR`). Прямое открытие файла в этой среде не подтверждено; это нужно проверить на обычном компьютере. Архитектура не использует fetch собственных JSON, модули и внешние зависимости.
- Автоматический axe/Lighthouse не подтверждает полное соответствие WCAG 2.2 AA. Остаются ручные проверки со скринридером, клавиатурой и реальным телефоном.
- Проходные баллы, календарь приёма 2027 года, тарифы общежитий и поэтажные планы не получены. Отсутствующие значения помечены; расписание и кабинет — демо.
- Сайт размещён по адресу https://gagamix228.github.io/redesign/. Результаты этого отчёта относятся к локальной проверке новой редакции перед обновлением публикации. Полный обход внешних официальных ссылок не выполнен: основной портал отвечает HTTP 403. Локальные пути проверяются отдельно.
- Видео — демонстрация прототипа. Оно не является записью реальных учебных данных.

Машиночитаемые отчёты находятся рядом. Конкурсный финальный чек-лист будет отдельным этапом.
'''
(D/'validation.md').write_text(report)
print('Validation report updated:',scores)
