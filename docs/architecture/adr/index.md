# Architecture Decision Records (ADR)

Записи о значимых архитектурных решениях продукта. Каждая ADR фиксирует контекст,
рассмотренные варианты, принятое решение и связанные требования к качеству
([`docs/quality-requirements.md`](../../quality-requirements.md)).

| ADR | Решение | Связанные QR |
|---|---|---|
| [ADR-0001](0001-full-llm-analysis-pipeline.md) | Full-LLM pipeline анализа текстов вместо rule-engine | QR-02, QR-03 |
| [ADR-0002](0002-deterministic-geoip-over-llm.md) | Детерминированный GeoIP вместо LLM для хостинга/IP | QR-02 |
| [ADR-0003](0003-server-side-gating-and-ssrf-boundary.md) | Серверный гейтинг и граница SSRF | QR-01 |
| [ADR-0004](0004-single-host-compose-caddy-tls.md) | Один хост: Docker Compose + Caddy/TLS | QR-01, QR-02 |

Подробнее о том, как решения соотносятся с архитектурой, — в
[обзоре архитектуры](../README.md).
