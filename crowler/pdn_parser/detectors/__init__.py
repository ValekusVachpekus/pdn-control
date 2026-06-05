"""Детекторы фактов на отрендеренной странице.

Каждый детектор получает разобранный DOM (BeautifulSoup) и/или артефакты
загрузки (cookies, сетевые запросы) и возвращает структуры из models.py.
"""

from .cookies import detect_cookie_banner, classify_cookies
from .forms import detect_forms
from .policies import detect_policy_links
from .scripts import detect_trackers

__all__ = [
    "detect_forms",
    "detect_cookie_banner",
    "classify_cookies",
    "detect_trackers",
    "detect_policy_links",
]
