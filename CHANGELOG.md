# Changelog

Все значимые изменения проекта документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/),
проект придерживается [Semantic Versioning](https://semver.org/lang/ru/).

## [Unreleased]

### Added

- Корневой `README.md` с описанием проекта, структурой монорепо и инструкциями запуска.
- `CONTRIBUTING.md` с описанием рабочего процесса (ветки, PR, релизы SemVer).
- `.env.example` со списком переменных окружения подсервисов.
- Шаблоны GitHub: PR-шаблон и issue-формы (User Story, задача, баг-репорт).
- CI Lychee для проверки ссылок в Markdown-файлах (на PR и push в `main`).
- Парсер публичных страниц (`crowler/`): формы, cookie, трекеры, политики, реквизиты оператора.
- Микросервис генерации PDF-отчёта (`PDFreport/`) на FastAPI + Typst.
- Веб-интерфейс (`frontend/`): лендинг, экран сканирования, дашборд отчёта, история.
- Аутентификация (e-mail + OAuth Яндекс/ВК) и разовая оплата отчёта (CloudPayments).
- Соответствие 152-ФЗ самого сайта: cookie-баннер с кнопкой «Отклонить», согласие
  на обработку ПДн при регистрации, экран политики.

[Unreleased]: https://github.com/ValekusVachpekus/pdn-control/commits/main
