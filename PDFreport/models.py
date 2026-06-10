"""Pydantic-модели входного JSON — Контракт №2 «бэкенд → PDF Report микросервис».

Модели намеренно «мягкие»: `extra="allow"` — бэкенд может прислать дополнительные
поля, не ломая сервис; nullable-поля (организация, гео, URL документа) допускают
`None` (шаблон рендерит их как «—»). Обязательны только те поля, без которых
Typst-шаблон не скомпилируется.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class _Base(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class DocumentMeta(_Base):
    report_id: str
    generated_at: str
    target_url: str
    domain: str
    organization_name: str | None = None
    scan_duration_sec: float | None = None
    pages_scanned: int | None = None
    scanner_version: str | None = None


class Scoring(_Base):
    # None допустимо для отчётов «не удалось проверить» (UNKNOWN risk_level) — в этом
    # случае шаблон Typst скрывает блок оценки рисков.
    overall_score: int | None = None
    risk_level: str = "UNKNOWN"  # CRITICAL|HIGH|MEDIUM|LOW|SAFE|UNKNOWN
    risk_label_ru: str = "—"
    legal_score: int | None = None
    technical_score: int | None = None


class Stats(_Base):
    critical_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    passed_count: int = 0


class PassedCheck(_Base):
    title: str
    detail: str | None = None


class ExecutiveSummary(_Base):
    verdict: str
    # упрощённый вердикт без юр-жаргона для режима «Владелец» во фронте (необязателен)
    verdict_plain: str | None = None
    stats: Stats
    # суммарный потенциальный штраф по КоАП за все нарушения, ₽.
    # Если не прислан — шаблон считает сумму из violations[].fine_rub.
    total_fine_rub: int | None = None
    # пройденные проверки (что на сайте сделано правильно)
    passed_checks: list[PassedCheck] = Field(default_factory=list)


class InfrastructureAndGeo(_Base):
    server_ip: str | None = None
    server_country: str | None = None
    server_country_ru: str | None = None
    hosting_provider: str | None = None
    localization_compliant: bool = False
    localization_note: str | None = None


class Violation(_Base):
    id: str
    severity: str  # critical|warning|info
    article_152fz: str
    title: str
    description: str
    evidence: list[str] = Field(default_factory=list)
    target_role: str  # developer|lawyer|marketer
    recommendation: str
    # потенциальный штраф за это нарушение по КоАП ст. 13.11, ₽ (необязательное)
    fine_rub: int | None = None


class DocumentFound(_Base):
    name: str | None = None
    url: str | None = None
    status: str | None = None


class TrackerItem(_Base):
    name: str
    host: str | None = None
    origin: str | None = None  # "ru" | "foreign"
    kind: str | None = None  # категория: «Аналитика», «Чат-виджет», …


class TrackersSummary(_Base):
    total: int = 0
    russian: int = 0
    foreign: int = 0
    # ключ контракта — "list"; в Python переименовано, чтобы не затенять builtin.
    # Элементы — объекты с деталями трекера (имя/хост/происхождение/категория).
    items: list[TrackerItem] = Field(default_factory=list, alias="list")


class DataCollectionPoint(_Base):
    url: str
    form_name: str | None = None
    fields: list[str] = Field(default_factory=list)


class AiIssue(_Base):
    quote: str  # цитата проблемной формулировки из документа
    article: str | None = None  # «ст. X ч. Y» — статья 152-ФЗ, к которой привязка
    problem: str  # что не так с цитатой
    fix: str | None = None  # что добавить/переписать


class AiNote(_Base):
    doc: str
    verdict: str | None = None  # "good" | "partial" | "bad"
    # Краткое резюме для UI/обратной совместимости (старый шаблон читает text).
    text: str | None = None
    # Новый структурный разбор — все поля опциональны, чтобы старые отчёты
    # (которые в БД лежат без них) не ломались валидацией.
    compliance_score: int | None = None  # 0-100
    summary: str | None = None
    missing_sections: list[str] = Field(default_factory=list)
    issues: list[AiIssue] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)


class TechnicalAppendix(_Base):
    documents_found: list[DocumentFound] = Field(default_factory=list)
    trackers_summary: TrackersSummary = Field(default_factory=TrackersSummary)
    data_collection_points: list[DataCollectionPoint] = Field(default_factory=list)
    # AI-анализ текстов документов (политика, cookie-уведомление, согласие)
    ai_analysis: list[AiNote] = Field(default_factory=list)


class Report(_Base):
    """Корневой объект Контракта №2."""

    document_meta: DocumentMeta
    scoring: Scoring
    executive_summary: ExecutiveSummary
    infrastructure_and_geo: InfrastructureAndGeo
    violations: list[Violation] = Field(default_factory=list)
    technical_appendix: TechnicalAppendix
