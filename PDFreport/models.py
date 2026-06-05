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
    overall_score: int
    risk_level: str  # CRITICAL|HIGH|MEDIUM|LOW|SAFE — неизвестные значения шаблон не ломают
    risk_label_ru: str
    legal_score: int
    technical_score: int


class Stats(_Base):
    critical_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    passed_count: int = 0


class ExecutiveSummary(_Base):
    verdict: str
    stats: Stats


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


class DocumentFound(_Base):
    name: str | None = None
    url: str | None = None
    status: str | None = None


class TrackersSummary(_Base):
    total: int = 0
    russian: int = 0
    foreign: int = 0
    # ключ контракта — "list"; в Python переименовано, чтобы не затенять builtin
    names: list[str] = Field(default_factory=list, alias="list")


class DataCollectionPoint(_Base):
    url: str
    form_name: str | None = None
    fields: list[str] = Field(default_factory=list)


class TechnicalAppendix(_Base):
    documents_found: list[DocumentFound] = Field(default_factory=list)
    trackers_summary: TrackersSummary = Field(default_factory=TrackersSummary)
    data_collection_points: list[DataCollectionPoint] = Field(default_factory=list)


class Report(_Base):
    """Корневой объект Контракта №2."""

    document_meta: DocumentMeta
    scoring: Scoring
    executive_summary: ExecutiveSummary
    infrastructure_and_geo: InfrastructureAndGeo
    violations: list[Violation] = Field(default_factory=list)
    technical_appendix: TechnicalAppendix
