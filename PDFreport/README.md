# PDF Report — ПДн Контроль

Микросервис генерации PDF-отчёта из JSON. Рендеринг — через [Typst](https://typst.app).

На вход подаётся JSON по контракту **«бэкенд → PDF Report микросервис» (Контракт №2)**;
на выходе — готовый PDF-отчёт с риск-скорингом, списком нарушений и техническим
приложением.

> Отчёт сознательно содержит дисклеймер: это предварительный технический аудит,
> **не** юридическая гарантия соответствия 152-ФЗ.

## Файлы

| Файл | Назначение |
|------|------------|
| `template.typ` | Шаблон отчёта. Читает данные и рендерит PDF. |
| `example.json` | Пример входного JSON (Контракт №2) для превью/тестов. |
| `.gitignore` | Игнорирует сгенерированные `*.pdf`, `*.png`, `data.json`. |

## Требования

- `typst` ≥ 0.12 (разрабатывалось на 0.14.2).
- Шрифты с кириллицей. Шаблон использует стек `Inter → Liberation Sans → DejaVu Sans`;
  если ни один не установлен, Typst подставит свой дефолтный шрифт (тоже с кириллицей).
  Для фирменного вида установите [Inter](https://rsms.me/inter/).

## Превью на примере

```sh
typst compile --input data=example.json template.typ preview.pdf
# или в картинки:
typst compile --input data=example.json --format png template.typ "page-{n}.png"
```

Откуда берутся данные: шаблон читает путь из `sys.inputs.data`
(`--input data=<path>`), а если он не задан — из `data.json` рядом с шаблоном.
Путь к JSON разрешается относительно `template.typ` либо как абсолютный (в пределах
`--root`, см. ниже).

## Интеграция в микросервис

Typst в целях безопасности не читает файлы вне корня проекта (`--root`). Самый
надёжный паттерн — на каждый запрос создавать рабочую папку, класть туда данные
и компилировать с `--root` на эту папку:

```python
import json, subprocess, tempfile, pathlib, shutil

TEMPLATE = pathlib.Path(__file__).parent / "template.typ"

def render_pdf(report: dict) -> bytes:
    """report — dict по Контракту №2. Возвращает байты PDF."""
    with tempfile.TemporaryDirectory() as tmp:
        job = pathlib.Path(tmp)
        # данные и шаблон — в одном корне
        (job / "data.json").write_text(
            json.dumps(report, ensure_ascii=False), encoding="utf-8"
        )
        shutil.copy(TEMPLATE, job / "template.typ")
        out = job / "report.pdf"
        subprocess.run(
            ["typst", "compile", "--root", str(job),
             str(job / "template.typ"), str(out)],
            check=True, capture_output=True, text=True,
        )
        return out.read_bytes()
```

По умолчанию (без `--input`) шаблон читает `data.json` из своей папки — поэтому в
примере выше дополнительный `--input` не нужен.

## Контракт входного JSON

Полное описание полей — в `CLAUDE.md` проекта (раздел «Контракт №2»). Кратко:

- `document_meta` — метаданные отчёта (`report_id`, `generated_at`, `target_url`,
  `domain`, `organization_name`, `scan_duration_sec`, `pages_scanned`, `scanner_version`).
- `scoring` — `overall_score` (0–100), `risk_level`
  (`CRITICAL|HIGH|MEDIUM|LOW|SAFE`), `risk_label_ru`, `legal_score`, `technical_score`.
- `executive_summary` — `verdict` + `stats`
  (`critical_count`, `warning_count`, `info_count`, `passed_count`).
- `infrastructure_and_geo` — IP/страна/хостинг, `localization_compliant` (bool),
  `localization_note`.
- `violations[]` — `id`, `severity` (`critical|warning|info`), `article_152fz`,
  `title`, `description`, `evidence[]`, `target_role`
  (`developer|lawyer|marketer`), `recommendation`.
- `technical_appendix` — `documents_found[]`, `trackers_summary`
  (`total`/`russian`/`foreign`/`list`), `data_collection_points[]`.

### Устойчивость шаблона

- `null` в полях рендерится как «—».
- Пустой `violations` → блок «Нарушений не выявлено».
- Пустые `documents_found` / `data_collection_points` → текстовая заглушка.
- Неизвестные значения `risk_level` / `severity` / `target_role` не ломают
  компиляцию (есть дефолты).
