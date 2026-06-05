"""Извлечение реквизитов оператора ПДн со страниц (эвристически, regex).

Нужно, чтобы юрист/LLM мог сверить оператора в политике с реальным владельцем
сайта. Значения могут быть неполными — это подсказки, а не верифицированные данные.
"""

from __future__ import annotations

import re

from .models import SiteIdentity

# ИНН/ОГРН ищем только рядом с меткой, иначе ловятся любые длинные числа.
_INN = re.compile(r"ИНН[:\s]*?(\d{10}|\d{12})", re.I)
_OGRN = re.compile(r"ОГРН(?:ИП)?[:\s]*?(\d{13}|\d{15})", re.I)
_LEGAL_NAME = re.compile(
    r"(?:ООО|ОАО|ЗАО|ПАО|АО)\s+[«\"][^»\"]{2,80}[»\"]"
    r"|ИП\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.\s?[А-ЯЁ]\.",
)
_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE = re.compile(r"(?:\+7|8)[\s\-(]*\d{3}[\s\-)]*\d{3}[\s\-]*\d{2}[\s\-]*\d{2}")


def _uniq(items, limit: int) -> list[str]:
    seen: list[str] = []
    for it in items:
        v = it.strip()
        if v and v not in seen:
            seen.append(v)
        if len(seen) >= limit:
            break
    return seen


def extract_identity(texts: list[str]) -> SiteIdentity:
    """texts — видимый текст обойдённых страниц."""
    blob = "\n".join(texts)
    return SiteIdentity(
        legal_name_hints=_uniq((m.group(0) for m in _LEGAL_NAME.finditer(blob)), 5),
        inn=_uniq((m.group(1) for m in _INN.finditer(blob)), 5),
        ogrn=_uniq((m.group(1) for m in _OGRN.finditer(blob)), 5),
        contact_emails=_uniq(_EMAIL.findall(blob), 10),
        contact_phones=_uniq(_PHONE.findall(blob), 10),
    )
