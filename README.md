# centrvietnam.ru

Сайт Центра Туризма (Нячанг). Статический, собирается GitHub Actions из Supabase
(проект `roqmejclibyyjlnxshzu`, таблицы `centr_site_*`) каждые 15 минут и при каждом push.

- `src/template/` — дизайн, админка (`/admin`), скрипты и картинки
- `src/gen.py` — генератор: страницы туров, каталог, подборки, sitemap, llms.txt
- Изменения туров и баннеров делаются в админке `https://centrvietnam.ru/admin/`

Восстановлено 3 ноября 2026 после сбоя хостинга Beget.
