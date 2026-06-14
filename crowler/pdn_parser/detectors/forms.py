"""Детектор форм сбора данных и чекбоксов согласия.

Категории ПДн определяются по типу/атрибутам поля только для надёжных случаев
(email, телефон, имя и т.п.) — это структурный факт для rule-engine. Чувствительность
данных (здоровье, биометрия и пр.) парсер НЕ угадывает по ключевым словам: вместо
этого в каждое поле кладётся его текстовая подпись (`label`) и полный текст согласия,
чтобы классификацию делала LLM по полному контексту.

Снимаются формы двух видов:
  1. классические `<form>`;
  2. «form-like» контейнеры — группы полей + кнопка сабмита БЕЗ обёртки `<form>`.
     Конструкторы лендингов (Tilda, Webflow и т.п.) часто кладут поля просто в
     `<div>`, и без этого мы теряли бы заявки целиком.
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

_SKIP_TYPES = frozenset({"submit", "button", "hidden", "reset", "image"})

# Подсказки в class/id контейнера, что это форма заявки/модалка.
_CONTAINER_HINT = re.compile(
    r"modal|popup|form|feedback|callback|lead|quiz|dialog|window|order|request", re.I
)
# Тексты кнопок-сабмитов form-like контейнера (без явного type=submit).
_SUBMIT_WORDS = (
    "отправ", "оставить заявку", "записаться", "записать", "заказать",
    "получить", "отправить", "send", "submit",
)


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


def _analyze_consent(scope: Tag, soup: BeautifulSoup) -> list[ConsentCheckbox]:
    result: list[ConsentCheckbox] = []
    for checkbox in scope.find_all("input", attrs={"type": "checkbox"}):
        full_text = _label_text(checkbox, soup)
        low = full_text.lower()
        matched = [kw for kw in CONSENT_KEYWORDS if kw in low]
        if not matched:
            continue
        links_to_policy = bool(
            (checkbox.find_parent("label") or checkbox.parent or scope).find("a", href=True)
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


def _policy_links(scope: Tag) -> list[str]:
    return [
        a["href"] for a in scope.find_all("a", href=True)
        if any(kw in (a.get_text() or "").lower() or kw in a["href"].lower()
               for kw in ("полит", "обработ", "конфиденц", "privacy", "соглас"))
    ]


def _build_form(field_els: list[Tag], scope: Tag, soup: BeautifulSoup,
                action: str | None, method: str) -> FormInfo | None:
    """Собирает FormInfo из набора полей. Возвращает None, если полей нет."""
    fields: list[FormField] = []
    pii_kinds: set[PIIKind] = set()
    has_file = False

    for el in field_els:
        ftype = (el.get("type") or el.name or "").lower()
        if ftype in _SKIP_TYPES:
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

    if not fields:
        return None

    return FormInfo(
        action=action,
        method=method,
        fields=fields,
        pii_kinds=sorted(pii_kinds, key=lambda k: k.value),
        has_file_upload=has_file,
        consent_checkboxes=_analyze_consent(scope, soup),
        policy_links=_policy_links(scope),
    )


def _has_submit(scope: Tag) -> bool:
    """Есть ли в контейнере кнопка сабмита (по type или по тексту)."""
    for el in scope.find_all(("button", "input", "a")):
        etype = (el.get("type") or "").lower()
        if etype in ("submit", "button"):
            return True
        if el.name == "button" and not etype:  # <button> по умолчанию submit
            return True
        text = (el.get_text(" ", strip=True) or el.get("value") or "").lower()
        if any(w in text for w in _SUBMIT_WORDS):
            return True
    return False


def _form_container(el: Tag) -> Tag | None:
    """Ближайший вверх контейнер, который выглядит как форма заявки.

    Сначала ищем предка с говорящим class/id (modal/form/popup…), у которого
    есть кнопка сабмита. Если такого нет — ближайший предок с кнопкой сабмита.
    Так одинокий <input> поиска без сабмита не превратится в «форму».
    """
    node: Tag | None = el
    hint_match: Tag | None = None
    for _ in range(8):
        parent = node.parent if node else None
        if not isinstance(parent, Tag) or parent.name in ("body", "html"):
            break
        attrs = " ".join([
            " ".join(parent.get("class") or []),
            parent.get("id") or "",
        ])
        if _CONTAINER_HINT.search(attrs) and _has_submit(parent):
            return parent
        if hint_match is None and _has_submit(parent):
            hint_match = parent
        node = parent
    return hint_match


def _detect_loose_forms(soup: BeautifulSoup) -> list[FormInfo]:
    """Поля сбора ПДн ВНЕ <form>: конструкторы кладут их просто в <div>."""
    loose = [
        el for el in soup.find_all(("input", "textarea", "select"))
        if el.find_parent("form") is None
        and (el.get("type") or el.name or "").lower() not in (_SKIP_TYPES | {"search"})
    ]
    if not loose:
        return []

    # Группируем поля по общему form-like контейнеру.
    groups: dict[int, tuple[Tag, list[Tag]]] = {}
    for el in loose:
        container = _form_container(el)
        if container is None:
            continue
        groups.setdefault(id(container), (container, []))[1].append(el)

    forms: list[FormInfo] = []
    for container, els in groups.values():
        form = _build_form(els, container, soup, action=None,
                           method=(container.get("method") or "post").lower())
        if form is not None:
            forms.append(form)
    return forms


def detect_forms(soup: BeautifulSoup) -> list[FormInfo]:
    forms: list[FormInfo] = []
    for form in soup.find_all("form"):
        built = _build_form(
            form.find_all(("input", "textarea", "select")),
            form, soup,
            action=form.get("action"),
            method=(form.get("method") or "get").lower(),
        )
        if built is not None:
            forms.append(built)

    forms.extend(_detect_loose_forms(soup))
    return forms
