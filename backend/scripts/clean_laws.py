"""Очистка текстов 152-ФЗ и КоАП ст. 13.11 для подачи LLM.

Что вырезаем:
- Колонтитулы «КонсультантПлюс / www.consultant.ru» (страничный мусор PDF→txt)
- Исторические пометки про изменения («Часть N изменена с DATE - Федеральный закон от ...»)
- Внутренние ссылки «См. предыдущую редакцию», «См. комментарии», «См. примечание»
- Срок давности
- Из КоАП — статьи 13.11.1, 13.11.2, 13.11.3 (вне области нашего продукта)
- Из 152-ФЗ — длинный список редактирующих законов в шапке
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path("c:/SWP")
OUT = Path("c:/SWP/pdn-control/backend/resources")
OUT.mkdir(parents=True, exist_ok=True)


def clean_koap(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    for raw in lines:
        line = raw.strip()
        # стоп: статья 13.11.1 и далее (дискриминация, мессенджеры, биометрия в ЕБС) —
        # это уже вне области аудита сайтов на 152-ФЗ.
        if re.match(r"^Статья 13\.11\.1\.\s", line):
            break
        if "Глава 13 дополнена статьей 13.11" in line:
            break
        if re.match(r"^Федеральным законом от \d.+глава 13", line):
            break
        # «Часть N изменена с DATE - …», «Часть N дополнена …», «Статья 13.11 дополнена …»
        if re.match(r"^(Часть |Статья 13\.11 дополнена частью )", line) and "ФЗ" in line:
            continue
        if re.match(r"^Примечания изменены с", line):
            continue
        if line in {"См. предыдущую редакцию", "См. комментарии к статье 13.11 КоАП РФ"}:
            continue
        if line.startswith("См. примечание"):
            continue
        if line.startswith("Cрок давности привлечения к ответственности"):
            continue
        if line.startswith("Обратите внимание, что применительно к составам"):
            continue
        out.append(raw)
    cleaned = "\n".join(out).rstrip()
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned + "\n"


def clean_fz152(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    in_change_list = False
    # шапка с реквизитами закона повторяется на каждой PDF-странице (КонсультантПлюс)
    header_seen = 0
    HEADER_LINES = {
        'Федеральный закон от 27.07.2006 N 152-ФЗ',
        '"О персональных данных"',
        'Документ предоставлен КонсультантПлюс',
        'www.consultant.ru',
        'КонсультантПлюс',
    }
    for raw in lines:
        line = raw.strip()

        # колонтитулы пропускаем всегда
        if line in {"КонсультантПлюс", "www.consultant.ru", "Документ предоставлен КонсультантПлюс"}:
            continue
        if line.startswith("Дата сохранения:"):
            continue

        # шапку с реквизитами оставляем ОДИН раз — первое упоминание
        if line in HEADER_LINES or re.match(r"^\(ред\. от ", line):
            header_seen += 1
            if header_seen > 1 and line != 'Федеральный закон от 27.07.2006 N 152-ФЗ':
                continue
            # для самой строки закона: оставляем только первое появление
            if line == 'Федеральный закон от 27.07.2006 N 152-ФЗ' and header_seen > 1:
                continue
            out.append(raw)
            continue

        # длинный «Список изменяющих документов» — выкидываем целиком
        if line == "Список изменяющих документов":
            in_change_list = True
            continue
        if in_change_list:
            if line.startswith("Глава ") or line.startswith("Статья "):
                in_change_list = False
            else:
                continue

        out.append(raw)

    cleaned = "\n".join(out).rstrip()
    # «(пункт N утратил силу. - Федеральный закон от … N …-ФЗ)» — пустота, можно вырезать
    cleaned = re.sub(r"\n[^\n]*утратил(а|и|о)?\s+силу[^\n]*\n", "\n", cleaned)
    # «(в ред. Федерального закона от 25.07.2011 N 261-ФЗ)» — историческая пометка
    cleaned = re.sub(r"\(в ред\. Федеральных?\s+законов?\s+от[^)]+\)", "", cleaned)
    # «(часть 3 введена Федеральным законом от ...)» — то же самое
    cleaned = re.sub(r"\([^()]*введ(ен|ена|ены)\s+Федеральн[^)]+\)", "", cleaned)
    # «(пункт N в ред. ...)»
    cleaned = re.sub(r"\((пункт|часть|подпункт|статья)\s+[^()]*в\s+ред\.[^)]+\)", "", cleaned)
    # двойные пробелы и лишние пустые строки после чистки
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned + "\n"


def main():
    koap_in = (ROOT / "коап.txt").read_text(encoding="utf-8")
    koap_out = clean_koap(koap_in)
    (OUT / "koap_13_11.txt").write_text(koap_out, encoding="utf-8")

    fz_in = (ROOT / "Текстовый документ.txt").read_text(encoding="utf-8")
    fz_out = clean_fz152(fz_in)
    (OUT / "fz_152.txt").write_text(fz_out, encoding="utf-8")

    def stats(name, before, after):
        bl = len(before.splitlines())
        al = len(after.splitlines())
        bc = len(before)
        ac = len(after)
        print(f"{name:8s}  lines: {bl:5d} -> {al:5d} ({al/bl*100:.0f}%)  "
              f"chars: {bc:6d} -> {ac:6d} ({ac/bc*100:.0f}%)")

    stats("koap", koap_in, koap_out)
    stats("fz152", fz_in, fz_out)


if __name__ == "__main__":
    main()
