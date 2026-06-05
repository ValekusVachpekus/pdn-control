"""Детектор форм сбора данных и чекбоксов согласия.

Категории ПДн определяются по типу/атрибутам поля только для надёжных случаев
(email, телефон, имя и т.п.) — это структурный факт для rule-engine. Чувствительность
данных (здоровье, биометрия и пр.) парсер НЕ угадывает по ключевым словам: вместо
этого в каждое поле кладётся его текстовая подпись (`label`) и полный текст согласия,
чтобы классификацию делала LLM по полному контексту.
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup, Tag

from ..models import ConsentCheckbox, FormField, FormInfo, PIIKind
from ..signatures import CONSENT_KEYWORDS

# Надёжные эвристики по типу/атрибутам поля (не по «смысловым» ключевым словам).
_PII_RULES: list[tuple[PIIKind, re.Pattern[str]]] = [
    (PIIKind.PASSPORT, re.compile(r"passport|паспорт|снилс|инн", re.I)),
    (PIIKind.PAYMENT, re.compile(r"card|карт|cvv|payment|оплат", re.I)),
    (PIIKind.BIRTHDATE, re.compile(r"birth|рожд|дата рожд", re.I)),
    (PIIKind.ADDRESS, re.compile(r"address|адрес|город|city|индекс", re.I)),
    (PIIKind.NAME, re.compile(r"\bname\b|fio|fname|lname|имя|фамил|отчеств|\bфио\b", re.I)),
]


def _label_text(el: Tag, soup: BeautifulSoup) -> str:
    """Видимая подпись элемента: <label for>, родительский label, placeholder или соседний текст."""
    el_id = el.get("id")
    if el_id:
        label = soup.find("label", attrs={"for": el_id})
        if label:
            return label.get_text(" ", strip=True)
    parent_label = el.find_parent("label")
    if parent_label:
        return parent_label.get_text(" ", strip=True)
    placeholder = el.get("placeholder") or el.get("aria-label")
    if placeholder:
        return str(placeholder)
    parent = el.parent
    if parent:
        return parent.get_text(" ", strip=True)
    return ""


def _field_pii(field: Tag) -> PIIKind | None:
    ftype = (field.get("type") or "").lower()
    haystack = " ".join(
        str(field.get(attr, ""))
        for attr in ("name", "id", "placeholder", "autocomplete", "aria-label", "title")
    )
    if ftype == "email" or re.search(r"e?-?mail|почт", haystack, re.I):
        return PIIKind.EMAIL
    if ftype == "tel" or re.search(r"phone|tel|телефон|моб", haystack, re.I):
        return PIIKind.PHONE
    for kind, pattern in _PII_RULES:
        if pattern.search(haystack):
            return kind
    return None


def _analyze_consent(form: Tag, soup: BeautifulSoup) -> list[ConsentCheckbox]:
    result: list[ConsentCheckbox] = []
    for checkbox in form.find_all("input", attrs={"type": "checkbox"}):
        full_text = _label_text(checkbox, soup)
        low = full_text.lower()
        matched = [kw for kw in CONSENT_KEYWORDS if kw in low]
        if not matched:
            continue
        links_to_policy = bool(
            (checkbox.find_parent("label") or checkbox.parent or form).find("a", href=True)
        )
        result.append(
            ConsentCheckbox(
                label=full_text[:300],
                full_text=full_text,
                pre_checked=checkbox.has_attr("checked"),
                links_to_policy=links_to_policy,
                matched_keywords=matched,
            )
        )
    return result


def detect_forms(soup: BeautifulSoup) -> list[FormInfo]:
    forms: list[FormInfo] = []
    for form in soup.find_all("form"):
        fields: list[FormField] = []
        pii_kinds: set[PIIKind] = set()
        has_file = False

        for el in form.find_all(("input", "textarea", "select")):
            ftype = (el.get("type") or el.name or "").lower()
            if ftype in ("submit", "button", "hidden", "reset", "image"):
                continue
            if ftype == "file":
                has_file = True
            pii = _field_pii(el)
            if pii:
                pii_kinds.add(pii)
            fields.append(
                FormField(
                    name=el.get("name"),
                    type=ftype,
                    required=el.has_attr("required"),
                    pii=pii,
                    label=_label_text(el, soup)[:300],
                )
            )

        policy_links = [
            a["href"] for a in form.find_all("a", href=True)
            if any(kw in (a.get_text() or "").lower() or kw in a["href"].lower()
                   for kw in ("полит", "обработ", "конфиденц", "privacy", "соглас"))
        ]

        forms.append(
            FormInfo(
                action=form.get("action"),
                method=(form.get("method") or "get").lower(),
                fields=fields,
                pii_kinds=sorted(pii_kinds, key=lambda k: k.value),
                has_file_upload=has_file,
                consent_checkboxes=_analyze_consent(form, soup),
                policy_links=policy_links,
            )
        )
    return forms
