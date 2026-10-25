# Итоговые проверки

Чек-лист пользователя сохранён в [checklist.md](checklist.md). Итог: [report.md](report.md). Исходные результаты — [results/](results/), финальные снимки — [screenshots/](screenshots/).

Приложение работает без сборки и зависимостей. Инструменты ниже нужны только для аудита.

1. Python 3.12+, Node 22+ и Chromium. Для Python: `pip install playwright lxml pillow pymupdf numpy pymorphy3 qrcode zxing-cpp`.
2. Запустить из корня: `python scripts/serve.py --port 4175`.
3. По умолчанию проверки открывают локальный сервер на порту 4175. Другой адрес задаётся `CHECK_BASE`. Путь к Chromium — `CHECK_CHROMIUM`; стандартный путь облачной среды `/usr/bin/chromium`. Firefox/WebKit — `python -m playwright install firefox webkit`, с системными библиотеками Playwright.
4. Для Lighthouse: `npm install --prefix /tmp/urfu-audit lighthouse`. При другой установке задать полный путь `LIGHTHOUSE_CLI` к `lighthouse/cli/index.js`. Время и метрики относятся к конкретному запуску и серверу.

Порядок повторного аудита:

```sh
python checks/data_audit.py
python checks/affiliations.py
python checks/dates.py
python checks/links.py
python checks/browser.py buttons
python checks/browser.py console
python checks/browser.py layout
python checks/stability.py
python checks/motion.py
python checks/accessibility.py
python checks/keyboard.py
python checks/contrast.py
python checks/weight.py
python checks/lighthouse.py
python checks/scenarios.py
python checks/quiz_exhaustive.py
python checks/browsers.py
python checks/text.py
python checks/metadata.py
python checks/extras.py
python scripts/presentation.py
python scripts/video.py
python checks/materials.py
python checks/qr.py
python checks/report.py
```

Не запускайте Lighthouse одновременно с другими нагрузочными проверками. `data_audit.py` и `links.py` обращаются к официальным внешним источникам; остальные локальные проверки не требуют сетевых сервисов. Запрос PageSpeed Insights отделён от локальных оценок и может возвращать ограничение квоты.

Полные 493 снимка матрицы сохраняются в `/tmp/urfu-check-screenshots`, контактные листы — в репозитории. `materials.py` сохраняет шесть полных снимков на запрошенных ширинах 375 и 1440 px. Ролик можно повторно кодировать из исходных сцен командой `python scripts/video.py --encode-only`, пока временные видеосцены существуют.

Локальный axe-core 4.14.0 находится в `vendor/`, лицензия MPL-2.0 и сведения о сторонних компонентах приложены. Он не подключён к сайту для посетителей.

Политики облачного браузера, отсутствие физических телефонов и скринридеров не обходятся: такие проверки отмечаются как неподтверждённые. Автоматический отчёт не заменяет ручную проверку WCAG.
