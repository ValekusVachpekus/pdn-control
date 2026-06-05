"""Агрегация фактов по сайту в SiteSummary.

Чистая функция над списком PageData — без сети и Playwright, легко тестируется.
Все поля — наблюдаемые факты и производные флаги, не юридические выводы.
"""

from __future__ import annotations

from .models import PageData, SiteSummary, SummaryTracker


def _page_tracking_before_consent(page: PageData) -> bool:
    """Баннер на странице есть, но трекеры/сторонние cookie уже активны при загрузке.

    Парсер грузит страницу в чистом контексте и снимает состояние ДО клика по
    баннеру — значит наличие трекеров/сторонних cookie при present-баннере и есть
    отслеживание без согласия.
    """
    banner = page.cookie_banner
    if not banner or not banner.present:
        return False
    has_third_party_cookie = any(c.third_party for c in page.cookies)
    return bool(page.trackers) or has_third_party_cookie


def build_summary(pages: list[PageData]) -> SiteSummary:
    s = SiteSummary(pages_crawled=len(pages))

    privacy_urls: list[str] = []
    pii_kinds: set[str] = set()
    tracker_map: dict[str, SummaryTracker] = {}
    third_party_domains: set[str] = set()
    cookies_seen: set[tuple[str, str]] = set()  # (name, domain) для дедупа

    for page in pages:
        if page.error:
            continue

        # --- Политики / документы ---
        for link in page.policy_links:
            if link.kind == "privacy_policy":
                privacy_urls.append(link.url)
                s.has_privacy_policy = True
            elif link.kind == "consent":
                s.has_consent_doc = True
            elif link.kind == "cookie_policy":
                s.has_cookie_policy = True

        # --- Cookie-баннер ---
        if page.cookie_banner and page.cookie_banner.present:
            s.has_cookie_banner = True
            if page.cookie_banner.has_reject_button:
                s.cookie_banner_has_reject = True
        if _page_tracking_before_consent(page):
            s.tracking_before_consent = True

        # --- Формы ---
        for form in page.forms:
            s.forms_total += 1
            if form.pii_kinds:
                s.forms_collecting_pii += 1
                if not form.consent_checkboxes:
                    s.forms_pii_without_consent += 1
            if any(cb.pre_checked for cb in form.consent_checkboxes):
                s.forms_with_prechecked_consent += 1
            for kind in form.pii_kinds:
                pii_kinds.add(kind.value)

        # --- Cookie ---
        for c in page.cookies:
            key = (c.name, c.domain)
            if key in cookies_seen:
                continue
            cookies_seen.add(key)
            s.cookies_total += 1
            if c.third_party:
                s.third_party_cookies += 1

        # --- Трекеры (дедуп по имени, копим страницы в found_on) ---
        for t in page.trackers:
            st = tracker_map.get(t.name)
            if st is None:
                tracker_map[t.name] = SummaryTracker(
                    name=t.name, category=t.category, third_party=t.third_party,
                    cross_border=t.cross_border, found_on=[page.url],
                )
            elif page.url not in st.found_on:
                st.found_on.append(page.url)

        third_party_domains.update(page.third_party_domains)

    s.privacy_policy_urls = sorted(set(privacy_urls))
    s.pii_kinds_collected = sorted(pii_kinds)
    s.trackers = list(tracker_map.values())
    s.tracker_categories = sorted({t.category.value for t in s.trackers})
    s.has_cross_border_transfer = any(t.cross_border for t in s.trackers)
    s.third_party_domains = sorted(third_party_domains)
    s.third_party_domain_count = len(s.third_party_domains)
    return s
