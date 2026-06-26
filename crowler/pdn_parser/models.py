"""Структуры данных, которые отдаёт парсер (контракт с бэкендом, schema 1.2).

Парсер собирает только факты о сайте. Никаких юридических выводов и скоринга
здесь нет — это работа rule-engine и LLM, которые получают этот объект на вход.
Полное описание контракта — в crowler/CONTRACT.md.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum

SCHEMA_VERSION = "1.4"


class PIIKind(str, Enum):
    """Категория персональных данных, которую запрашивает поле формы."""

    EMAIL = "email"
    PHONE = "phone"
    NAME = "name"
    ADDRESS = "address"
    BIRTHDATE = "birthdate"
    PASSPORT = "passport"
    PAYMENT = "payment"
    OTHER = "other"


class TrackerCategory(str, Enum):
    """Назначение стороннего скрипта/запроса."""

    ANALYTICS = "analytics"
    TAG_MANAGER = "tag_manager"
    AD_PIXEL = "ad_pixel"
    SESSION_REPLAY = "session_replay"
    CRM_WIDGET = "crm_widget"
    CHAT_WIDGET = "chat_widget"
    CAPTCHA = "captcha"
    MAPS = "maps"
    SOCIAL = "social"
    PAYMENT = "payment"
    CDN = "cdn"
    OTHER = "other"


@dataclass
class FormField:
    name: str | None
    type: str | None
    required: bool = False
    pii: PIIKind | None = None
    label: str = ""   # видимая подпись/placeholder поля — контекст для LLM


@dataclass
class ConsentCheckbox:
    """Чекбокс внутри формы, похожий на согласие на обработку ПДн."""

    label: str           # короткая подпись (для UI)
    full_text: str       # полный текст согласия (вход для LLM)
    pre_checked: bool
    links_to_policy: bool
    matched_keywords: list[str] = field(default_factory=list)


@dataclass
class FormInfo:
    action: str | None
    method: str
    fields: list[FormField] = field(default_factory=list)
    pii_kinds: list[PIIKind] = field(default_factory=list)
    has_file_upload: bool = False
    consent_checkboxes: list[ConsentCheckbox] = field(default_factory=list)
    policy_links: list[str] = field(default_factory=list)


@dataclass
class CookieInfo:
    name: str
    domain: str
    third_party: bool
    http_only: bool = False
    secure: bool = False
    expires: float | None = None


@dataclass
class CookieBanner:
    """Признаки cookie-уведомления, найденного в DOM."""

    present: bool
    full_text: str = ""        # полный текст баннера (вход для LLM)
    text_excerpt: str = ""     # короткая выдержка (для UI)
    has_accept_button: bool = False
    has_reject_button: bool = False
    has_settings: bool = False
    matched_keywords: list[str] = field(default_factory=list)


@dataclass
class TrackerHit:
    name: str
    category: TrackerCategory
    third_party: bool
    cross_border: bool = False
    evidence: list[str] = field(default_factory=list)  # где нашли: src/inline/network


@dataclass
class PolicyLink:
    url: str
    anchor_text: str
    kind: str  # privacy_policy | consent | cookie_policy | terms


@dataclass
class PolicyDocument:
    """Скачанный и очищенный текст документа (политика/согласие/оферта)."""

    url: str
    kind: str
    fetch_status: int | None
    word_count: int = 0
    truncated: bool = False
    extracted_text: str | None = None
    text_path: str | None = None


@dataclass
class SiteIdentity:
    """Реквизиты оператора, извлечённые с сайта (эвристически)."""

    legal_name_hints: list[str] = field(default_factory=list)
    inn: list[str] = field(default_factory=list)
    ogrn: list[str] = field(default_factory=list)
    contact_emails: list[str] = field(default_factory=list)
    contact_phones: list[str] = field(default_factory=list)


@dataclass
class PageData:
    """Результат разбора одной страницы."""

    url: str
    final_url: str
    status: int | None
    title: str = ""
    depth: int = 0
    error: str | None = None

    forms: list[FormInfo] = field(default_factory=list)
    cookies: list[CookieInfo] = field(default_factory=list)
    cookie_banner: CookieBanner | None = None
    trackers: list[TrackerHit] = field(default_factory=list)
    policy_links: list[PolicyLink] = field(default_factory=list)
    third_party_domains: list[str] = field(default_factory=list)


@dataclass
class SummaryTracker:
    name: str
    category: TrackerCategory
    third_party: bool
    cross_border: bool
    found_on: list[str] = field(default_factory=list)


@dataclass
class SiteSummary:
    """Агрегация фактов и производные флаги по всему сайту."""

    pages_crawled: int = 0

    has_privacy_policy: bool = False
    privacy_policy_urls: list[str] = field(default_factory=list)
    has_consent_doc: bool = False
    has_cookie_policy: bool = False

    has_cookie_banner: bool = False
    cookie_banner_has_reject: bool = False
    tracking_before_consent: bool = False

    forms_total: int = 0
    forms_collecting_pii: int = 0
    forms_pii_without_consent: int = 0
    forms_with_prechecked_consent: int = 0
    pii_kinds_collected: list[str] = field(default_factory=list)

    cookies_total: int = 0
    third_party_cookies: int = 0

    trackers: list[SummaryTracker] = field(default_factory=list)
    tracker_categories: list[str] = field(default_factory=list)
    has_cross_border_transfer: bool = False
    third_party_domains: list[str] = field(default_factory=list)
    third_party_domain_count: int = 0


@dataclass
class ScanMeta:
    scan_id: str
    parser_version: str
    requested_url: str
    start_url: str
    base_domain: str
    started_at: str
    finished_at: str
    duration_ms: int
    status: str  # ok | partial | failed
    config: dict = field(default_factory=dict)
    robots_respected: bool = True
    pages_requested_limit: int = 0
    pages_crawled: int = 0
    errors: list[str] = field(default_factory=list)
    # IP сервера стартовой страницы (после HTTP-редиректов) — снимается через
    # Playwright Response.server_addr(). Если страница не загрузилась — null.
    server_ip: str | None = None
    # Страна хостинга по server_ip, определённая ДЕТЕРМИНИРОВАННО из offline
    # GeoIP-базы (MaxMind GeoLite2), а не «знаниями» LLM. См. pdn_parser/geoip.py.
    # Введено в schema 1.4. Пустой/приватный/неопределимый IP → server_country=null
    # (страну не выдумываем: цена ложного штрафа по ст. 18 ч. 5 152-ФЗ максимальна).
    server_country: str | None = None          # ISO-2 ("RU", "US", …) или null
    server_country_source: str | None = None   # "geoip" | null
    server_is_cdn: bool = False                 # IP за известным CDN/облаком
    server_country_confidence: str = "unknown"  # "high" | "low" | "unknown"
    hosting_provider: str | None = None         # организация ASN / имя CDN | null
    server_asn: int | None = None               # номер автономной системы | null


@dataclass
class CrawlResult:
    """Полный отчёт парсера — конверт schema 1.2, уходит дальше по пайплайну."""

    meta: ScanMeta
    summary: SiteSummary
    site_identity: SiteIdentity
    policy_documents: list[PolicyDocument] = field(default_factory=list)
    pages: list[PageData] = field(default_factory=list)
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict:
        # Порядок ключей — как в контракте/примере.
        return {
            "schema_version": self.schema_version,
            "meta": asdict(self.meta),
            "summary": asdict(self.summary),
            "site_identity": asdict(self.site_identity),
            "policy_documents": [asdict(d) for d in self.policy_documents],
            "pages": [asdict(p) for p in self.pages],
        }
