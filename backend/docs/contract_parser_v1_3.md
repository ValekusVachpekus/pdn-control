# ТЗ парсеру: Контракт №1, schema 1.3 — IP сервера

**Адресат:** команда парсера (Айрат Мингазов).
**Зачем:** для оценки соответствия ст. 18 ч. 5 152-ФЗ (локализация БД ПДн
на территории РФ) бэкенду нужно знать, к какому серверу реально подключается
браузер при заходе на сайт. Сейчас LLM в отчёте всегда ставит
`localization_status = "unknown"` — не из чего судить.

## Что добавить

В объект `meta` Контракта №1 — **одно поле**:

| Поле | Тип | Описание |
|---|---|---|
| `server_ip` | `string \| null` | IPv4 или IPv6 адрес, к которому реально подключился Playwright-браузер при загрузке `start_url`. |

**Страну, провайдера и локализацию определяет LLM на бэке** по этому IP —
никакой MaxMind / GeoIP установки на стороне парсера НЕ нужно.

### Bump schema_version

`"schema_version": "1.2"` → `"schema_version": "1.3"`.

## Как получать `server_ip`

**НЕЛЬЗЯ:** делать `socket.gethostbyname(domain)` отдельным запросом. Может
вернуть другой IP, если у домена несколько A-записей или DNS-роутинг подкручен.

**НАДО:** снимать IP реального соединения, выполненного Playwright. Через
CDP-сессию:

```python
# В crawler.py / fetcher.py, где открывается стартовая страница.
# Подписываемся на Network.responseReceived ДО навигации:

async def collect_server_ip(page, start_url: str) -> str | None:
    server_ip = None
    async with page.context.new_cdp_session(page) as cdp:
        await cdp.send("Network.enable")

        def on_response(event):
            nonlocal server_ip
            resp = event.get("response", {})
            # ловим ответ именно на стартовый URL после редиректов
            if resp.get("url", "").startswith(start_url.split("?", 1)[0]) and server_ip is None:
                ip = resp.get("remoteIPAddress")
                if ip:
                    server_ip = ip

        cdp.on("Network.responseReceived", on_response)
        await page.goto(start_url, wait_until="domcontentloaded")
    return server_ip
```

Альтернатива: вытащить из `response.serverAddr` или `Network.requestWillBeSentExtraInfo`,
если так удобнее.

## Edge-cases

| Кейс | `server_ip` |
|---|---|
| Бот-детектор закрыл соединение, `pages_crawled = 0` | `null` |
| Сайт за CDN (Cloudflare, Akamai) | IP CDN-узла — это **не баг**: для 152-ФЗ Cloudflare = обработчик ПДн, и LLM правильно отметит это нарушением |
| IPv6 | `"2606:4700:..."` — норм, LLM понимает оба формата |
| Несколько A-записей (round-robin) | тот IP, к которому реально подключился браузер |
| `localhost` / `127.0.0.1` | вернётся реальный IP бэкенда — норм |

## Пример обновлённого `meta`

```json
{
  "meta": {
    "scan_id": "...",
    "parser_version": "0.3.0",
    "schema_version": "1.3",
    "requested_url": "example.com",
    "start_url": "https://example.com/",
    "base_domain": "example.com",
    "started_at": "2026-06-10T10:00:00Z",
    "finished_at": "2026-06-10T10:00:30Z",
    "duration_ms": 30000,
    "status": "ok",
    "pages_crawled": 5,
    "errors": [],
    "config": { "...": "..." },

    "server_ip": "172.67.198.243"
  }
}
```

## Что произойдёт на бэке, когда поле заполнится

1. [report_builder.py](../app/services/report_builder.py) уже читает `meta.server_ip`
   и кладёт в `infrastructure_and_geo.server_ip`.
2. [llm_analyzer.py](../app/services/llm_analyzer.py) промпт уже инструктирует
   LLM: «определи страну, провайдера и `localization_status` сам по этому IP,
   если можешь; иначе ставь null/unknown».
3. LLM также выпишет отдельный violation по ст. 18 ч. 5 с штрафом до 6 000 000 ₽,
   если сервер вне РФ.
4. PDF-шаблон и фронт уже рендерят IP/страну/хостинг.

Всё ждёт только тебя.

## Acceptance criteria

- [ ] У сайта на росс. хостинге IP вида `5.255.255.x`, `87.250.250.x`,
      `213.180.193.x` (Яндекс) или `185.59.103.x` (Selectel) — попадает в
      `meta.server_ip`, LLM определяет как Россия, локализация compliant.
- [ ] У сайта на Cloudflare IP вида `104.21.x.x`, `172.67.x.x` — попадает в
      `meta.server_ip`, LLM определяет как США, локализация non_compliant,
      появляется отдельное нарушение со штрафом 6 000 000 ₽.
- [ ] При `pages_crawled = 0` поле `null`.
- [ ] `schema_version` стал `"1.3"`.
- [ ] **Никаких новых зависимостей** (MaxMind, geoip2 и т.п.) в парсере не
      требуется — это работа LLM на бэке.
