# Публикация в GitHub Pages

Репозиторий: https://github.com/GAGAMIX228/redesign

Сайт загружен в ветку `main`, файлы находятся в корне. Сборка не требуется; `.nojekyll` включён.

1. Откройте https://github.com/GAGAMIX228/redesign/settings/pages.
2. В разделе **Build and deployment** выберите **Source: Deploy from a branch**.
3. Выберите ветку **main** и папку **/ (root)**.
4. Нажмите **Save** и дождитесь публикации GitHub Pages.

Адрес после публикации: https://gagamix228.github.io/redesign/.

Текущая GitHub-интеграция позволяет загрузить файлы, но запрос включения Pages отклонён: `Resource not accessible by integration` (HTTP 403). GitHub Actions также не может автоматически включить Pages со стандартным GITHUB_TOKEN: официальная action `actions/configure-pages@v5` требует отдельные права administration:write и pages:write для такого действия. Передавать токены в чат не нужно — достаточно однократно включить Pages в настройках.

После включения проверьте главную, каталог, поиск «общага» и страницу программы. Обновления ветки main будут публиковаться автоматически.
