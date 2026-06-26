# Контракт ответа парсера → бэкенд

Описание JSON, который парсер «ПДн Контроль» отдаёт бэкенду. Живой пример —
[`json_example.txt`](json_example.txt) рядом с этим файлом.

> **Принцип.** Парсер отдаёт **факты**, а не вердикты. Здесь нет риск-скоринга и
> юридических выводов — это работа rule-engine и LLM, которые получают этот JSON
> на вход. Поля `summary` вида `has_*` / `*_without_consent` — наблюдаемые факты
> (есть/нет, сколько), а не оценка соответствия 152-ФЗ.

## Кто что использует

JSON обслуживает трёх потребителей. Это объясняет, почему часть полей дублируется
и почему есть «технические» поля рядом с «текстовыми»:

| Потребитель  | Что берёт |
|--------------|-----------|
| **rule-engine** | счётчики и флаги из `summary`, технические поля форм/cookie |
| **LLM**         | тексты: `consent_checkboxes[].label`, `cookie_banner.text_excerpt`, категории ПДн, флаги |
| **PDF / UI**    | `pages[]` с `evidence` (пруфы «где нашли») |

Кодировка — UTF-8, ключи в `snake_case`. Кириллица не экранируется
(`ensure_ascii=false`).

---

## Верхний уровень

```jsonc
{ "schema_version": "1.4", "meta": {…}, "summary": {…}, "site_identity": {…},
  "policy_documents": [ {…} ], "pages": [ {…} ] }
```

| Поле | Тип | Описание |
|------|-----|----------|
| `schema_version` | string | Версия контракта. Бампается при ломающих изменениях; бэк сверяет на совместимость. |
| `meta` | object | Метаданные скана (см. ниже). |
| `summary` | object | Агрегация и факт-флаги по всему сайту. |
| `site_identity` | object | Реквизиты оператора, извлечённые с сайта (ИНН/ОГРН/название/контакты). |
| `policy_documents` | array | Скачанные тексты политик/согласий/оферт (дедуп по URL). **Вход для LLM.** |
| `pages` | array  | Сырые факты по каждой обойдённой странице. Один объект = одна страница. |

---

## `meta` — метаданные скана

| Поле | Тип | Описание |
|------|-----|----------|
| `scan_id` | string (uuid) | Идентификатор проверки. Задаётся бэком или генерится парсером. Ключ для истории проверок. |
| `parser_version` | string | Версия парсера (`pdn_parser.__version__`). |
| `requested_url` | string | URL ровно как ввёл пользователь (схема не обязательна). |
| `start_url` | string | Нормализованный стартовый URL (со схемой, без фрагмента). |
| `base_domain` | string | Регистрируемый домен сайта; обход ограничен им. |
| `started_at` / `finished_at` | string (ISO-8601, UTC) | Начало/конец обхода. |
| `duration_ms` | number | Длительность обхода, мс. |
| `status` | enum | Итог обхода: `ok` \| `partial` \| `failed` (см. ниже). |
| `config` | object | Фактические параметры обхода: `max_pages`, `max_depth`, `respect_robots`, `headless`, `page_timeout_ms`. |
| `robots_respected` | bool | Учитывался ли `robots.txt`. |
| `pages_requested_limit` | number | Лимит страниц на этот скан (= `config.max_pages`). |
| `pages_crawled` | number | Сколько страниц фактически обойдено. |
| `errors` | array&lt;string&gt; | Ошибки уровня обхода (заблокировано robots, таймаут и т.п.). |
| `server_ip` | string \| null | IP origin'а стартовой страницы — снимается через `Response.server_addr()` Playwright. `null`, если страница не загрузилась. **Введено в schema 1.3.** |
| `server_country` | string \| null | Страна хостинга (ISO-2: `RU`, `US`, …) по `server_ip`, определённая **детерминированно** из offline GeoIP-базы (MaxMind GeoLite2) в парсере, а не «знаниями» LLM. Один и тот же IP всегда даёт одну страну. `null`, если IP пуст/приватный/неопределим или база не подключена — **страну не выдумываем** (цена ложного штрафа по ст. 18 ч. 5 152-ФЗ максимальна). **Введено в schema 1.4.** |
| `server_country_source` | string \| null | Источник `server_country`: `"geoip"` — из локальной базы; `null` — страну определить не удалось. |
| `server_is_cdn` | bool | IP принадлежит **reverse-proxy CDN** (Cloudflare, Fastly, Akamai, CDN77, Edgio, Imperva) по ASN или статическому списку диапазонов. Тогда `server_country` — страна **края CDN**, а не обязательно место хранения ПДн: бэк не должен штрафовать вслепую. **Облачный хостинг (AWS/Azure/GCP) CDN'ом не считается** — у него origin-IP обычно и есть место хранения, иначе реальное нарушение локализации ускользнёт от штрафа. |
| `server_country_confidence` | enum | `high` — страна из базы и это не reverse-proxy CDN (в т.ч. облако-хостинг); `low` — страна из базы, но IP за CDN (origin может быть в другой стране); `unknown` — страну определить не удалось. |
| `hosting_provider` | string \| null | Организация-владелец ASN (если подключена GeoLite2-ASN), иначе имя CDN, иначе `null`. |
| `server_asn` | number \| null | Номер автономной системы (ASN) по `server_ip`, если подключена GeoLite2-ASN; иначе `null`. |

**Значения `status`:**
- `failed` — стартовая страница не загрузилась / `pages_crawled == 0`.
- `partial` — часть страниц с ошибкой, либо упёрлись в лимит при наличии `errors`.
- `ok` — всё загрузилось без ошибок.

---

## `summary` — сводка по сайту

Агрегация фактов со всех страниц + производные флаги. Rule-engine мапит эти поля
на правила почти 1:1.

| Поле | Тип | Описание |
|------|-----|----------|
| `pages_crawled` | number | Дубль `meta.pages_crawled` для удобства. |
| `has_privacy_policy` | bool | Найдена ли где-либо ссылка на политику обработки ПДн. |
| `privacy_policy_urls` | array&lt;string&gt; | Абсолютные URL найденных политик. |
| `has_consent_doc` | bool | Найден ли документ «Согласие на обработку ПДн». |
| `has_cookie_policy` | bool | Найдена ли отдельная cookie-политика. |
| `has_cookie_banner` | bool | Найден ли cookie-баннер хотя бы на одной странице. |
| `cookie_banner_has_reject` | bool | Есть ли у баннера кнопка отказа (а не только «принять»). |
| `tracking_before_consent` | bool | На странице сработали трекеры/выставлены сторонние cookie **до** согласия (баннер есть, но трекеры уже активны). Сильный сигнал нарушения cookie-согласия. |
| `forms_total` | number | Всего форм по сайту. |
| `forms_collecting_pii` | number | Форм, запрашивающих хотя бы одну категорию ПДн. |
| `forms_pii_without_consent` | number | Форм с ПДн, но **без** чекбокса согласия. Типовое нарушение. |
| `forms_with_prechecked_consent` | number | Форм, где согласие проставлено по умолчанию (`pre_checked`). Типовое нарушение. |
| `pii_kinds_collected` | array&lt;enum&gt; | Объединение всех категорий ПДн по сайту (значения — см. `PIIKind`). |
| `cookies_total` | number | Всего уникальных cookie. |
| `third_party_cookies` | number | Из них сторонних. |
| `trackers` | array&lt;object&gt; | Уникальные трекеры по сайту (дедуп по `name`). Элемент: `name`, `category`, `third_party`, `cross_border`, `found_on` (список URL страниц). |
| `tracker_categories` | array&lt;enum&gt; | Удобная выжимка категорий из `trackers` (см. `TrackerCategory`). |
| `has_cross_border_transfer` | bool | Есть ли хотя бы один трекер с `cross_border=true` (передача данных за рубеж, ст. 12). |
| `third_party_domains` | array&lt;string&gt; | Все сторонние домены, к которым обращался сайт. Признак передачи данных третьим лицам. |
| `third_party_domain_count` | number | Длина `third_party_domains`. |

---

## `site_identity` — реквизиты оператора

Извлечённые со страниц (футер, контакты, текст) признаки оператора ПДн. Нужны,
чтобы LLM/юрист мог сверить, совпадает ли оператор в политике с реальным владельцем
сайта, и вообще идентифицирован ли оператор. Извлечение эвристическое (regex),
значения могут быть неполными.

| Поле | Тип | Описание |
|------|-----|----------|
| `legal_name_hints` | array&lt;string&gt; | Строки с признаками юрлица/ИП (ООО, АО, ИП …). |
| `inn` | array&lt;string&gt; | Найденные ИНН (10/12 цифр). |
| `ogrn` | array&lt;string&gt; | Найденные ОГРН/ОГРНИП (13/15 цифр). |
| `contact_emails` | array&lt;string&gt; | Контактные e-mail с сайта. |
| `contact_phones` | array&lt;string&gt; | Контактные телефоны с сайта. |

---

## `policy_documents[]` — тексты документов (для LLM)

Скачанные и очищенные от HTML тексты найденных политик/согласий/оферт. Дедуп
по `url` — каждый документ скачивается и хранится **один раз**, даже если
слинкован с каждой страницы (поэтому тексты тут, а не внутри `pages[].policy_links`).
Это **основной вход для LLM**: модель оценивает полноту юридических формулировок —
указаны ли цели обработки, сроки, передача третьим лицам и т.п.

| Поле | Тип | Описание |
|------|-----|----------|
| `url` | string | Абсолютный URL документа. |
| `kind` | enum | `privacy_policy` \| `consent` \| `cookie_policy` \| `terms`. |
| `fetch_status` | number \| null | HTTP-статус загрузки документа. `null`, если не удалось скачать. |
| `word_count` | number | Число слов в извлечённом тексте. |
| `truncated` | bool | Был ли текст обрезан по лимиту длины. |
| `extracted_text` | string \| null | Полный текст документа, очищенный от HTML. `null`, если используется файловый режим. |
| `text_path` | string \| null | Путь к файлу с текстом (опциональный режим для очень больших документов вместо `extracted_text`). |

> По умолчанию текст inline в `extracted_text`. В файловом режиме
> (`--policy-text-to-files`) `extracted_text = null`, а текст лежит в файле по `text_path`.

---

## `pages[]` — факты по странице

| Поле | Тип | Описание |
|------|-----|----------|
| `url` | string | URL, по которому пошёл обход (нормализованный). |
| `final_url` | string | URL после редиректов. |
| `status` | number \| null | HTTP-статус ответа. `null`, если страница не загрузилась. |
| `title` | string | `<title>` страницы. |
| `depth` | number | Глубина от стартовой страницы (0 = старт). |
| `error` | string \| null | Текст ошибки загрузки; при ошибке остальные поля пустые/дефолтные. |
| `forms` | array | Формы на странице (см. ниже). |
| `cookies` | array | Выставленные cookie (см. ниже). |
| `cookie_banner` | object | Cookie-баннер в DOM (см. ниже). |
| `trackers` | array | Трекеры, найденные на этой странице (см. ниже). |
| `policy_links` | array | Ссылки на политики/согласия (см. ниже). |
| `third_party_domains` | array&lt;string&gt; | Сторонние домены, к которым обращалась именно эта страница. |

### `pages[].forms[]`

| Поле | Тип | Описание |
|------|-----|----------|
| `action` | string \| null | Атрибут `action` формы. |
| `method` | string | `get` / `post`. |
| `fields` | array | Поля формы (см. ниже). |
| `pii_kinds` | array&lt;enum&gt; | Категории ПДн в форме (агрегат по `fields[].pii`). |
| `has_file_upload` | bool | Есть ли загрузка файла (`input[type=file]`). |
| `consent_checkboxes` | array | Чекбоксы, похожие на согласие на обработку ПДн (см. ниже). |
| `policy_links` | array&lt;string&gt; | Ссылки на политику, найденные внутри формы. |

**`forms[].fields[]`**

| Поле | Тип | Описание |
|------|-----|----------|
| `name` | string \| null | Атрибут `name`. |
| `type` | string \| null | Тип поля (`text`, `tel`, `email`, `textarea`…). |
| `required` | bool | Обязательное ли поле. |
| `pii` | enum \| null | Базовая категория ПДн по типу/атрибутам поля (см. `PIIKind`), или `null`. Только надёжные случаи. |
| `label` | string | Видимая подпись поля (label/placeholder). **Вход для LLM** — по ней модель определяет чувствительность данных (здоровье, биометрия и т.п.), парсер этого не угадывает. |

**`forms[].consent_checkboxes[]`**

| Поле | Тип | Описание |
|------|-----|----------|
| `label` | string | Короткая подпись к чекбоксу (до 300 симв.) — для UI. |
| `full_text` | string | Полный текст согласия без обрезки. **Вход для LLM** — оценка полноты формулировки. |
| `pre_checked` | bool | Проставлен ли по умолчанию (нарушение, если да). |
| `links_to_policy` | bool | Есть ли рядом ссылка на политику. |
| `matched_keywords` | array&lt;string&gt; | По каким ключевым словам распознан как согласие. |

### `pages[].cookies[]`

| Поле | Тип | Описание |
|------|-----|----------|
| `name` | string | Имя cookie. |
| `domain` | string | Домен cookie. |
| `third_party` | bool | Сторонний ли домен относительно `base_domain`. |
| `http_only` | bool | Флаг `HttpOnly`. |
| `secure` | bool | Флаг `Secure`. |
| `expires` | number \| null | Unix-время истечения; `null` для сессионных. |

### `pages[].cookie_banner`

| Поле | Тип | Описание |
|------|-----|----------|
| `present` | bool | Найден ли баннер. |
| `full_text` | string | Полный текст баннера без обрезки. **Вход для LLM** — проверка, сказано ли о передаче данных третьим лицам. |
| `text_excerpt` | string | Короткая выдержка (до 400 симв.) — для UI/превью. |
| `has_accept_button` | bool | Есть ли кнопка «принять». |
| `has_reject_button` | bool | Есть ли кнопка «отклонить». |
| `has_settings` | bool | Есть ли «настройки cookie». |
| `matched_keywords` | array&lt;string&gt; | По каким словам распознан баннер. |

### `pages[].trackers[]`

| Поле | Тип | Описание |
|------|-----|----------|
| `name` | string | Название трекера/виджета (напр. «Яндекс.Метрика»). |
| `category` | enum | Категория (см. `TrackerCategory`). |
| `third_party` | bool | Сторонний ли. |
| `cross_border` | bool | Передаёт ли данные за рубеж (иностранный сервис — Google, Facebook, Hotjar …). |
| `evidence` | array&lt;string&gt; | Где обнаружен: `network:<url>`, `src:<url>`, `inline`. Пруф для PDF/дебага; **для LLM не нужно**. |

### `pages[].policy_links[]`

| Поле | Тип | Описание |
|------|-----|----------|
| `url` | string | Абсолютный URL документа. |
| `anchor_text` | string | Текст ссылки. |
| `kind` | enum | `privacy_policy` \| `consent` \| `cookie_policy` \| `terms`. |

---

## Справочник enum-значений

**`PIIKind`** (поля `fields[].pii`, `pii_kinds`, `pii_kinds_collected`):
`email`, `phone`, `name`, `address`, `birthdate`, `passport`, `payment`, `other`.
Спец-категории (здоровье, биометрия) парсер **не** размечает — их определяет
LLM по `fields[].label` и текстам.

**`TrackerCategory`** (`trackers[].category`, `tracker_categories`):
`analytics`, `tag_manager`, `ad_pixel`, `session_replay`, `crm_widget`,
`chat_widget`, `captcha`, `maps`, `social`, `payment`, `cdn`, `other`.

**`policy_links[].kind`:** `privacy_policy`, `consent`, `cookie_policy`, `terms`.

**`meta.status`:** `ok`, `partial`, `failed`.

---

## Заметки для интеграции

- **Дубли сделаны намеренно** для удобства: `summary.pages_crawled`,
  `tracker_categories`, `third_party_domain_count`, а также `third_party_domains`
  на уровне страницы и в `summary`. Бэк может игнорировать ненужные.
- **Для LLM шлите не весь JSON, а проекцию текстов**: `policy_documents[].extracted_text`,
  `consent_checkboxes[].full_text`, `cookie_banner.full_text`, `forms[].fields[].label`
  (по подписям модель сама определит чувствительность данных), плюс контекст —
  `pii_kinds_collected`, `trackers`, `third_party_domains`, флаги `summary`.
  Технические поля (`evidence`, атрибуты cookie, `type`/`required` полей,
  `depth`/`status`, короткие `label`/`text_excerpt`) модели не нужны.
- **Эвристики неточны:** детектор баннера, чекбоксов согласия и категории ПДн
  основаны на ключевых словах — возможны пропуски на нестандартной вёрстке.
- Это предварительный технический аудит, а не гарантия соответствия 152-ФЗ.

> **Тексты для LLM.** Полные тексты документов лежат в `policy_documents`
> (дедуп по URL), формулировки согласий — в `consent_checkboxes[].full_text`,
> текст cookie-баннера — в `cookie_banner.full_text`. Этого достаточно, чтобы
> модель анализировала юридические формулировки, не переходя по ссылкам.
