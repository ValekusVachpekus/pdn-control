"""Сигнатуры известных трекеров, метрик, CRM и виджетов.

Используются детектором скриптов/сетевых запросов. Каждая сигнатура
сопоставляется как с доменами сетевых запросов, так и с содержимым тегов
<script> (src и инлайн). Списки заведомо неполные — это MVP, расширяется
по мере появления новых кейсов.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import TrackerCategory


@dataclass(frozen=True)
class Signature:
    name: str
    category: TrackerCategory
    domains: tuple[str, ...] = ()        # подстроки доменов сетевых запросов / src
    js_markers: tuple[str, ...] = ()     # подстроки в инлайн-скриптах
    cross_border: bool = False           # иностранный сервис → передача данных за рубеж (ст. 12)


SIGNATURES: list[Signature] = [
    # --- Аналитика / метрики ---
    Signature("Яндекс.Метрика", TrackerCategory.ANALYTICS,
              domains=("mc.yandex.ru", "mc.yandex.com"),
              js_markers=("ym(", "yandex_metrika", "Ya.Metrika")),
    Signature("Google Analytics", TrackerCategory.ANALYTICS,
              domains=("google-analytics.com", "analytics.google.com"),
              js_markers=("gtag(", "ga(", "GoogleAnalyticsObject"), cross_border=True),
    Signature("Google Tag Manager", TrackerCategory.TAG_MANAGER,
              domains=("googletagmanager.com",),
              js_markers=("googletagmanager.com/gtm.js", "dataLayer"), cross_border=True),
    Signature("Mail.ru / VK Top", TrackerCategory.ANALYTICS,
              domains=("top-fwz1.mail.ru", "top.mail.ru"),
              js_markers=("_tmr", "topmailru")),
    Signature("Hotjar", TrackerCategory.SESSION_REPLAY,
              domains=("static.hotjar.com", "script.hotjar.com"),
              js_markers=("hjid", "hotjar"), cross_border=True),
    Signature("Roistat", TrackerCategory.ANALYTICS,
              domains=("cloud.roistat.com",), js_markers=("roistat",)),
    Signature("Calltouch", TrackerCategory.ANALYTICS,
              domains=("calltouch.ru", "calltracking.ru"), js_markers=("calltouch",)),

    # --- Рекламные пиксели ---
    Signature("Facebook Pixel", TrackerCategory.AD_PIXEL,
              domains=("connect.facebook.net", "facebook.com/tr"),
              js_markers=("fbq(", "fbevents.js"), cross_border=True),
    Signature("VK Pixel / OpenAPI", TrackerCategory.AD_PIXEL,
              domains=("vk.com/js/api/openapi", "ads.vk.com", "userapi.com"),
              js_markers=("VK.Retargeting", "vk_openapi")),
    Signature("Google Ads", TrackerCategory.AD_PIXEL,
              domains=("googleadservices.com", "googlesyndication.com", "doubleclick.net"),
              cross_border=True),
    Signature("Yandex Ads", TrackerCategory.AD_PIXEL,
              domains=("an.yandex.ru", "yandexadexchange.net")),

    # --- CRM / чат-виджеты / квизы ---
    Signature("JivoSite", TrackerCategory.CHAT_WIDGET,
              domains=("code.jivosite.com", "jivo.ru", "jivochat.com"), js_markers=("jivo",)),
    Signature("Битрикс24", TrackerCategory.CRM_WIDGET,
              domains=("bitrix24.ru", "bitrix24.com", "cdn-ru.bitrix24"),
              js_markers=("b24widget", "bitrix24")),
    Signature("amoCRM", TrackerCategory.CRM_WIDGET,
              domains=("amocrm.ru", "amocrm.com"), js_markers=("amo_forms", "amocrm")),
    Signature("Carrot quest", TrackerCategory.CHAT_WIDGET,
              domains=("cdn.carrotquest.io", "carrotquest.io"), js_markers=("carrotquest",)),
    Signature("Talk-Me", TrackerCategory.CHAT_WIDGET,
              domains=("lcab.talk-me.ru", "talk-me.ru"), js_markers=("talkme",)),
    Signature("Envybox", TrackerCategory.CHAT_WIDGET,
              domains=("envybox.io", "envycdn.com"), js_markers=("envybox",)),
    Signature("Marquiz", TrackerCategory.CRM_WIDGET,
              domains=("marquiz.ru", "s.marquiz.ru"), js_markers=("Marquiz",)),

    # --- Капча / карты / соцсети / платежи ---
    Signature("Google reCAPTCHA", TrackerCategory.CAPTCHA,
              domains=("google.com/recaptcha", "gstatic.com/recaptcha"),
              js_markers=("grecaptcha",), cross_border=True),
    Signature("Яндекс.Карты", TrackerCategory.MAPS,
              domains=("api-maps.yandex.ru",), js_markers=("ymaps",)),
    Signature("Google Maps", TrackerCategory.MAPS,
              domains=("maps.googleapis.com", "maps.google.com"), cross_border=True),
    Signature("VK Widgets", TrackerCategory.SOCIAL,
              domains=("vk.com/js/api/openapi",), js_markers=("VK.Widgets",)),
    Signature("ЮKassa / Яндекс.Касса", TrackerCategory.PAYMENT,
              domains=("yookassa.ru", "money.yandex.ru", "yoomoney.ru")),
    Signature("CloudPayments", TrackerCategory.PAYMENT,
              domains=("widget.cloudpayments.ru",), js_markers=("cp.CloudPayments",)),
]


# --- Ключевые слова для эвристик детекторов ---

CONSENT_KEYWORDS: tuple[str, ...] = (
    "согла", "персональн", "обработк", "политик", "152-фз", "152 фз",
    "конфиденциальн", "consent", "agree", "privacy", "i accept",
)

COOKIE_KEYWORDS: tuple[str, ...] = (
    "cookie", "куки", "файлы cookie", "файлов cookie", "использует cookie",
)

ACCEPT_WORDS: tuple[str, ...] = ("приня", "соглас", "ок", "хорошо", "accept", "allow", "got it", "разреш")
REJECT_WORDS: tuple[str, ...] = ("отклон", "отказ", "запрет", "reject", "decline", "deny")
SETTINGS_WORDS: tuple[str, ...] = ("настрой", "настройки cookie", "manage", "settings", "preferences")

POLICY_PATTERNS: dict[str, tuple[str, ...]] = {
    "privacy_policy": ("политик", "обработк персональн", "конфиденциальн", "privacy", "personal-data", "privacy-policy"),
    "consent": ("согласие на обработку", "согласие на обраб", "consent"),
    "cookie_policy": ("cookie", "куки", "cookie-policy"),
    "terms": ("пользовательское соглашение", "оферта", "terms", "условия использования"),
}
