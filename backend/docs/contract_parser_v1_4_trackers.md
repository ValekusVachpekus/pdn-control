# ТЗ парсеру: расширение детекции трекеров (schema 1.4)

**Адресат:** команда парсера (Айрат Мингазов).
**Зачем:** на крупных сайтах (YouTube, VK, Yandex, OK, маркетплейсы) текущий
детектор трекеров возвращает **0 трекеров**, хотя сайты используют десятки
аналитических, рекламных и измерительных скриптов. Причина: детектор считает
трекером только скрипт **с другого домена**, а Google/Yandex/VK
хостят свою аналитику на собственных доменах (`googletagmanager.com`,
`google-analytics.com`, `mc.yandex.ru`, `top-fwz1.mail.ru`).

Это приводит к двум проблемам в нашем продукте:
1. Отчёт по youtube.com показывает «0 трекеров, 0 российских, 0 зарубежных» —
   юзер не верит в качество анализа.
2. LLM на бэке не получает данных о реальной обработке cookie третьих сторон
   и не может выписать корректные нарушения ст. 9 ч. 1 / ст. 7.

## Что добавить / изменить

### 1. Same-organization-трекеры (главное)

Сейчас в `pages[].trackers[]` попадают только скрипты, чей домен **не равен**
`base_domain`. Изменить логику на: попадают все скрипты, чей домен **относится
к известной аналитической / маркетинговой / трекинговой платформе**, даже
если он one-org с базовым доменом.

Например:
- `youtube.com` хостит свой Google Tag Manager, доменом `youtube.com/gtag/...` →
  всё равно классифицируем как `category="tag_manager"`, `name="Google Tag Manager"`.
- `vk.com` загружает свою Top.Mail.Ru с поддомена `top-fwz1.mail.ru` или
  собственного `vk.com/js/...` → `category="analytics"`, `name="VK Pixel"`.
- `yandex.ru` подгружает Я.Метрику с `mc.yandex.ru` → уже работает, но
  если c `metrika.yandex.ru/tag.js` (например) — тоже должна попадать.

### 2. Обновить список сигнатур

В `pdn_parser/signatures.py` (или где у вас живёт детекция) добавить полный
актуальный список платформ:

| Платформа | Сигнатуры (URL/имя/кука) | Категория |
|---|---|---|
| Google Tag Manager | `googletagmanager.com`, `gtag/js`, `gtm.js`, `dataLayer` | `tag_manager` |
| Google Analytics 4 | `google-analytics.com`, `gtag`, `_ga` cookie | `analytics` |
| Google Ads | `googleadservices.com`, `googlesyndication.com`, `doubleclick.net` | `ad_pixel` |
| Facebook Pixel | `connect.facebook.net/en_US/fbevents.js`, `fbq()`, `_fbp` cookie | `ad_pixel` |
| TikTok Pixel | `analytics.tiktok.com`, `ttq.load()` | `ad_pixel` |
| Yandex Metrika | `mc.yandex.ru`, `metrika.yandex.ru`, `_ym_uid` cookie | `analytics` |
| Yandex Direct | `an.yandex.ru/system`, `yandex.ru/ads/system` | `ad_pixel` |
| VK Pixel | `vk.com/rtrg`, `top-fwz1.mail.ru` | `analytics` |
| Top.Mail.Ru | `top.mail.ru/counter`, `top-fwz1.mail.ru` | `analytics` |
| Hotjar | `static.hotjar.com`, `hjid` | `session_replay` |
| Clarity (Microsoft) | `www.clarity.ms`, `clarity()` | `session_replay` |
| Amplitude | `cdn.amplitude.com`, `amplitude.getInstance()` | `analytics` |
| Mixpanel | `cdn.mxpnl.com`, `mixpanel.track()` | `analytics` |
| Bitrix24 chat | `cdn-ru.bitrix24.ru/.../crm`, `Bitrix24` | `crm_widget` |
| amoCRM | `amocrm.ru/sw/install/...`, `AmoCRM` | `crm_widget` |
| Carrot Quest | `carrotquest.io` | `chat_widget` |
| JivoSite | `jivosite.com`, `code.jivosite.com` | `chat_widget` |
| Tawk.to | `embed.tawk.to` | `chat_widget` |
| Intercom | `widget.intercom.io` | `chat_widget` |
| reCAPTCHA (Google) | `www.google.com/recaptcha`, `recaptcha/api.js` | `captcha` |
| hCaptcha | `hcaptcha.com/1/api.js` | `captcha` |
| Cloudflare Turnstile | `challenges.cloudflare.com/turnstile` | `captcha` |
| YouTube embed | `youtube.com/iframe_api`, `youtube-nocookie.com` | `social` |
| VK Open API | `vk.com/js/api/openapi.js` | `social` |
| Google Maps | `maps.googleapis.com`, `maps.gstatic.com` | `maps` |
| Yandex Maps | `api-maps.yandex.ru`, `maps.yandex.ru/api` | `maps` |
| 2GIS Maps | `maps.api.2gis.ru` | `maps` |

### 3. Детекция по cookies (а не только по URL)

Иногда скрипт уже не подгружается (был раньше или закеширован), но cookie
осталась. Если на странице есть **выставленные cookie** характерного имени —
тоже создаём запись в `trackers[]`:

| Cookie | Платформа | Категория |
|---|---|---|
| `_ga`, `_gid`, `_ga_*` | Google Analytics | `analytics` |
| `_gcl_au` | Google Ads | `ad_pixel` |
| `_fbp`, `_fbc` | Facebook Pixel | `ad_pixel` |
| `_ym_uid`, `_ym_d`, `yandexuid` | Yandex Metrika | `analytics` |
| `_ttp` | TikTok Pixel | `ad_pixel` |
| `mailru_o`, `mrcu` | Top.Mail.Ru | `analytics` |
| `_hjSessionUser_*` | Hotjar | `session_replay` |
| `MUID`, `_clck`, `_clsk` | Microsoft Clarity | `session_replay` |
| `intercom-*` | Intercom | `chat_widget` |

В этом случае `evidence` элемента в `trackers[]` — `["cookie:_ga"]`.

### 4. Поле `cross_border` — обновить логику

Сейчас `cross_border` = `true`, если домен трекера зарубежный. Уточнить:

| Платформа | cross_border |
|---|---|
| Google (любые) | true (хостинг США) |
| Facebook / Meta | true |
| TikTok | true |
| Yandex (любые) | false |
| VK / Mail.ru | false |
| Bitrix24 | false |
| Hotjar | true (Финляндия / EU) |
| Microsoft Clarity | true |

Полный mapping держать в `signatures.py` как `dict`.

### 5. Bump schema_version → 1.4 + поле `category` в evidence

Не обязательно, но удобно: в `pages[].trackers[]` уже есть `evidence`-массив —
добавить туда строку с категорией, чтобы LLM мог по ней сразу выписывать
нарушение (например, `"ad_pixel"` → ст. 9 ч. 1 без согласия на маркетинг,
`"session_replay"` → отдельный вопрос про запись сеансов).

## Acceptance criteria

- [ ] Скан `youtube.com` возвращает `pages[].trackers[].length >= 3`
      (минимум: Google Tag Manager, GA4, и/или YouTube embed-API).
- [ ] Скан `vk.com` возвращает Top.Mail.Ru или VK Pixel.
- [ ] Скан `yandex.ru` возвращает Я.Метрику (как и сейчас).
- [ ] Сайт-визитка без аналитики продолжает возвращать `trackers: []`.
- [ ] `schema_version` `"1.4"`.

## Зачем эти поля бэку

LLM на бэке использует `summary.trackers[]` и `summary.has_cross_border_transfer`
для определения нарушений ст. 9 ч. 1 (согласие на cookie третьих сторон),
ст. 7 (передача третьим лицам) и косвенно ст. 18 ч. 5 (локализация). Сейчас
на youtube.com и подобных LLM пишет «трекеры не обнаружены», что неверно
и снижает качество отчёта.

После твоих правок LLM получит конкретные платформы и сможет выписывать
точные нарушения с реальными штрафами 700К-1М ₽ за каждый трекер без согласия.

## Срок

Я бы оценил в 1-2 дня:
- 0.5 дня — обновить `signatures.py` со списком выше;
- 0.5 дня — изменить логику классификации (убрать жёсткий критерий «не базовый домен»);
- 0.5 дня — детекция по cookies;
- 0.5 дня — тесты на 3-5 крупных сайтах + bump schema_version.

Никаких новых зависимостей не требуется — это чистая работа с существующими
detectors.
