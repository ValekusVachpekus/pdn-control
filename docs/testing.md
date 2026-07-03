# Стратегия тестирования и CI-гейт качества

Документ описывает автоматизированное тестирование, контроль покрытия,
дополнительную QA-проверку и правила защиты ветки `main`. Это **поддерживаемый
гейт качества** (Assignment 4, Part 7 & 8, задача #71), который обязаны проходить
все последующие PR, — а не разовое подтверждение.

## Принцип

Тесты разложены по пирамиде и привязаны к компонентам монорепозитория. Быстрые
unit/интеграционные тесты не требуют внешних сервисов и гоняются на каждый PR;
e2e backend поднимает реальный Postgres в CI.

Отдельно защищаем два инварианта стабилизации:

- **anti-SSRF** (US-12 / #69) — краулер не должен ходить во внутренние адреса
  ни напрямую, ни через редирект/DNS-rebinding;
- **детерминизм скана/оценки** (#34) — один и тот же вход даёт один и тот же
  механический результат.

Оба покрыты регрессионными тестами (см. ниже); их падение валит сборку.

## Наборы тестов

| Компонент | Тип | Где | Запуск |
|-----------|-----|-----|--------|
| Crowler | unit + регрессии | [`crowler/tests/`](../crowler/tests/) | `pytest` |
| Backend | unit + интеграция (без БД) | [`backend/tests/`](../backend/tests/) | `pytest --ignore=tests/test_e2e.py` |
| Backend | интеграция (Postgres) | [`backend/tests/test_e2e.py`](../backend/tests/test_e2e.py) | `pytest tests/test_e2e.py` |
| PDFreport | unit + контракт | [`PDFreport/tests/`](../PDFreport/tests/) | `pytest` |
| Frontend | unit (vitest) | [`frontend/test/`](../frontend/test/) | `npm test` |

Ключевые тесты:

- Anti-SSRF: [`crowler/tests/test_ssrf.py`](../crowler/tests/test_ssrf.py),
  [`crowler/tests/test_ssrf_redirect.py`](../crowler/tests/test_ssrf_redirect.py).
- Детерминизм: [`backend/tests/test_determinism.py`](../backend/tests/test_determinism.py)
  (QRT-02), [`backend/tests/test_violation_catalog.py`](../backend/tests/test_violation_catalog.py)
  (идемпотентность правил), детерминизм GeoIP в
  [`crowler/tests/test_geoip.py`](../crowler/tests/test_geoip.py).
- Интеграция «факты парсера → rule-engine → единый отчёт»:
  [`backend/tests/test_integration_pipeline.py`](../backend/tests/test_integration_pipeline.py)
  (без БД/LLM) и [`backend/tests/test_e2e.py`](../backend/tests/test_e2e.py)
  (API на реальном Postgres).
- Канонизация входа LLM-кэша (стабильность ключа):
  [`backend/tests/test_llm_cache.py`](../backend/tests/test_llm_cache.py).
- **MVP v2 (Sprint 5)** — аутентификация (bcrypt + JWT: подпись/подмена/просрочка):
  [`backend/tests/test_auth_service.py`](../backend/tests/test_auth_service.py);
  cookie-нарушения адресованы маркетологу, точки сбора ПДн, разбивка скоринга по
  роли (фидбэк заказчика):
  [`backend/tests/test_mvp_v2_rules.py`](../backend/tests/test_mvp_v2_rules.py);
  адаптер отчёта UI (роли, метки точек сбора):
  [`frontend/test/mapReport.test.js`](../frontend/test/mapReport.test.js).

## Критические модули и порог покрытия

Каждый критический модуль обязан иметь **≥ 30 %** покрытия строк (порог DoD;
может быть повышен по согласованию с TA). Проверяется по-модульно скриптом
[`scripts/check_coverage.py`](../scripts/check_coverage.py) — обычный
`--cov-fail-under` проверяет только агрегат, а нам нужен порог на каждый модуль.

| Модуль | Роль | Порог | Текущее покрытие |
|--------|------|-------|------------------|
| [`crowler/pdn_parser/ssrf.py`](../crowler/pdn_parser/ssrf.py) | anti-SSRF инвариант | 30 % | ~81 % |
| [`crowler/pdn_parser/geoip.py`](../crowler/pdn_parser/geoip.py) | детерминированная страна хостинга | 30 % | ~84 % |
| [`backend/app/services/violation_catalog.py`](../backend/app/services/violation_catalog.py) | rule-engine (механические нарушения) | 30 % | ~74 % |
| [`backend/app/services/llm_cache.py`](../backend/app/services/llm_cache.py) | детерминизм входа LLM | 30 % | ~62 % |
| [`backend/app/services/auth.py`](../backend/app/services/auth.py) | аутентификация MVP v2 (bcrypt + JWT) | 30 % | ~100 % |

«Текущее покрытие» — ориентир на момент заведения гейта; гейт падает только при
просадке ниже порога или если модуль исчез из отчёта (переименование = провал,
чтобы покрытие не «терялось» молча).

## Дополнительная QA-проверка (SAST + аудит зависимостей)

Отдельный статус, не пересекающийся с lint и проверкой ссылок (Lychee):

- **Bandit** (SAST по нашему коду) — **обязательный гейт**, падает на находках
  severity ≥ medium. Под него код уже подчищен: недоверенный XML (sitemap внешних
  сайтов) парсится через `defusedxml` (защита от XXE/billion laughs), намеренный
  bind `0.0.0.0` в контейнере помечен `# nosec B104`.
- **pip-audit** (аудит зависимостей) — **информативно** (`continue-on-error`):
  CVE в транзитивных зависимостях вышестоящих пакетов не блокируют мердж
  продуктовой фичи, но видны в логе.

## Lint / format / type-check

- **`ruff check`** — обязательный lint-гейт (конфиг [`ruff.toml`](../ruff.toml)).
- **`ruff format --check`** — пока **advisory** (`continue-on-error`): полный
  автоформат к кодовой базе ещё не применён, чтобы не плодить шумный диск и
  конфликты с параллельными PR спринта. Включение в обязательные гейты —
  отдельной задачей.
- **type-check (mypy)** — запланирован отдельной задачей (кодовая база ещё не
  типизирована под строгий mypy).

## CI и защита ветки

Workflow [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) запускается на
каждый PR и push в `main`. Job'ы (они же required checks):

`lint`, `crowler`, `backend-unit`, `backend-integration`, `pdfreport`,
`frontend`, `security`. Проверка ссылок живёт отдельно в `Links (Lychee)`.

**Branch protection** на `main` (см. раздел в этом файле / настройки репозитория):
обязательны прохождение перечисленных проверок **и** ревью другого участника
перед мерджем; прямой push в `main` запрещён. Команда включения — в
[CONTRIBUTING.md](../CONTRIBUTING.md) / ниже.

### Включение branch protection (admin)

```bash
gh api -X PUT repos/ValekusVachpekus/pdn-control/branches/main/protection \
  --input - <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["lint","crowler","backend-unit","backend-integration","pdfreport","frontend","security"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": { "required_approving_review_count": 1 },
  "restrictions": null
}
JSON
```

## Локальный прогон

```bash
# Crowler
cd crowler && pip install -r requirements.txt pytest pytest-cov && pytest

# Backend (unit + интеграция без БД)
cd backend && pip install -e .[test] && pytest --ignore=tests/test_e2e.py

# Backend e2e (нужен Postgres на :55432, см. шапку test_e2e.py)
cd backend && pytest tests/test_e2e.py

# PDFreport
cd PDFreport && pip install fastapi "uvicorn[standard]" pytest httpx && pytest

# Frontend
cd frontend && npm ci && npm run build && npm test

# Lint + SAST
ruff check backend/app crowler/pdn_parser PDFreport
bandit -r backend/app crowler/pdn_parser PDFreport --severity-level medium
```
