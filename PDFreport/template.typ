// ============================================================================
// ПДн Контроль — Typst-шаблон PDF-отчёта
// ----------------------------------------------------------------------------
// Вход: JSON по контракту «бэкенд → PDF Report микросервис» (Контракт №2).
// По умолчанию читает data.json рядом с шаблоном.
// Превью на примере:  typst compile --input data=example.json template.typ preview.pdf
// Прод (микросервис):  пишем data.json в рабочую папку и компилируем (см. README.md).
// ============================================================================

#let data-path = sys.inputs.at("data", default: "data.json")
#let data = json(data-path)

// ---------- справочники цветов и подписей ----------------------------------
#let risk-color = (
  "CRITICAL": rgb("#b3261e"),
  "HIGH": rgb("#d93f0b"),
  "MEDIUM": rgb("#e8a000"),
  "LOW": rgb("#7cb305"),
  "SAFE": rgb("#2e7d32"),
)
#let sev = (
  "critical": (ru: "Критично", color: rgb("#b3261e")),
  "warning": (ru: "Предупреждение", color: rgb("#e8a000")),
  "info": (ru: "Инфо", color: rgb("#1565c0")),
)
#let role-ru = (
  "developer": "Разработчик",
  "lawyer": "Юрист",
  "marketer": "Маркетолог",
)
#let sev-order = ("critical": 0, "warning": 1, "info": 2)
#let ok-green = rgb("#2e7d32")

// ---------- утилиты ----------------------------------------------------------
#let dash(x) = if x == none or x == "" { [—] } else { [#x] }

// группировка по разрядам: 2300000 → "2 300 000" (неразрывные пробелы)
#let group-thousands(n) = {
  let rev = str(n).clusters().rev()
  let parts = ()
  let chunk = ()
  for (i, d) in rev.enumerate() {
    chunk.push(d)
    if calc.rem(i + 1, 3) == 0 { parts.push(chunk.rev().join()); chunk = () }
  }
  if chunk.len() > 0 { parts.push(chunk.rev().join()) }
  parts.rev().join("\u{00A0}")
}
// сумма в рублях с разделителями: 2300000 → "2 300 000 ₽"
#let fmt-rub(n) = group-thousands(n) + "\u{00A0}₽"

#let badge(body, color: luma(90), fg: white) = box(
  fill: color, inset: (x: 6pt, y: 2.5pt), radius: 3pt,
  text(fill: fg, weight: "bold", size: 7.5pt)[#body],
)

// горизонтальный прогресс-бар 0..100
#let bar(value, color) = box(
  width: 100%, height: 11pt, radius: 5.5pt, fill: luma(232),
)[
  #place(left + horizon, box(
    width: calc.min(calc.max(value, 0), 100) * 1%,
    height: 11pt, radius: 5.5pt, fill: color,
  ))
]

// круглый индикатор общего балла
#let gauge(score, color) = box(
  width: 86pt, height: 86pt, radius: 50%, fill: color,
  align(center + horizon, stack(dir: ttb, spacing: 0pt,
    text(fill: white, size: 30pt, weight: "bold")[#score],
    text(fill: white, size: 8pt)[из 100],
  )),
)

// карточка-счётчик
#let stat-card(count, label, color) = box(
  width: 100%, fill: color.lighten(88%), radius: 5pt, inset: 10pt,
  stroke: 0.5pt + color.lighten(45%),
)[
  #text(size: 20pt, weight: "bold", fill: color)[#count]
  #v(-3pt)
  #text(size: 8.5pt)[#label]
]

// заголовок секции
#let sec(title) = {
  v(8pt)
  text(size: 13pt, weight: "bold")[#title]
  v(2pt)
  line(length: 100%, stroke: 0.7pt + luma(200))
  v(5pt)
}

// ---------- настройки документа ---------------------------------------------
#let m = data.document_meta
#let s = data.scoring
#let rc = risk-color.at(s.risk_level, default: luma(100))

#set document(title: "Отчёт ПДн Контроль — " + m.domain)
#set text(font: ("Inter", "Liberation Sans", "DejaVu Sans"), lang: "ru", size: 10pt)
#set page(
  paper: "a4",
  margin: (x: 1.8cm, top: 1.8cm, bottom: 1.8cm),
  footer: context [
    #set text(size: 7.5pt, fill: luma(120))
    #line(length: 100%, stroke: 0.5pt + luma(215))
    #v(2pt)
    #grid(columns: (1fr, auto), align: (left, right),
      [ПДн Контроль — предварительный технический аудит, не является юридической гарантией соответствия 152-ФЗ],
      [#counter(page).display("1") / #counter(page).final().at(0)],
    )
  ],
)

// ============================================================================
// ШАПКА
// ============================================================================
// Если target_url отличается от domain (например, https://example.com/path vs
// example.com) — рисуем обе строки. Иначе только domain, чтобы не было дубля.
#let _show-target-url = m.target_url != none and m.target_url != "" and m.target_url != m.domain

#block(fill: rc, width: 100%, radius: 6pt, inset: 18pt)[
  #text(fill: white, size: 11pt)[Отчёт о проверке сайта на риски нарушения 152-ФЗ]
  #v(5pt)
  #text(fill: white, size: 22pt, weight: "bold")[#m.domain]
  #if _show-target-url [
    #v(2pt)
    #text(fill: white, size: 10pt)[#m.target_url]
  ]
]

// Дата приходит как ISO-8601 (2026-06-09T08:52:57Z). Берём подстроку YYYY-MM-DD HH:MM —
// человекочитаемо и без полной локализации (Typst не умеет parse дат с timezone).
#let _humanize-date(s) = {
  if s == none or s == "" { return "—" }
  let d = if s.contains("T") { s.replace("T", " ") } else { s }
  // Обрезаем секунды и Z: «2026-06-09 08:52:57Z» → «2026-06-09 08:52»
  if d.len() >= 16 { d.slice(0, 16) } else { d }
}

#v(10pt)
#grid(columns: (1fr, 1fr), row-gutter: 5pt, column-gutter: 16pt,
  [*Организация:* #dash(m.organization_name)],
  [*Дата отчёта:* #_humanize-date(m.generated_at)],
  [*Страниц проверено:* #m.pages_scanned],
  [*Длительность скана:* #m.scan_duration_sec с],
  [*ID отчёта:* #raw(m.report_id)],
  [*Версия сканера:* #m.scanner_version],
)

// Если парсер не получил ни одной страницы — рисуем баннер «не удалось проверить»
// и больше ничего не показываем (нет смысла в скоринге и нарушениях).
#let _scan-failed = ("_scan_failed" in data and data._scan_failed) or m.pages_scanned == 0
#if _scan-failed [
  #v(16pt)
  #block(fill: rgb("#fff7ed"), stroke: 1pt + rgb("#f59e0b"), radius: 6pt,
    width: 100%, inset: 14pt)[
    #text(weight: "bold", size: 13pt, fill: rgb("#7c2d12"))[Не удалось проверить сайт]
    #v(6pt)
    #text(size: 10.5pt, fill: rgb("#7c2d12"))[
      Парсер не смог получить страницы сайта. Возможные причины: защита captcha/бот-детектором,
      обязательный JS-рендер, требование авторизации, временная недоступность. Попробуйте
      повторить проверку позже.
    ]
  ]
]
#if not _scan-failed [

// ============================================================================
// ОЦЕНКА РИСКОВ
// ============================================================================
#sec[Оценка рисков]
#grid(columns: (auto, 1fr), column-gutter: 20pt,
  gauge(s.overall_score, rc),
  [
    #text(size: 17pt, weight: "bold", fill: rc)[#s.risk_label_ru]
    #v(1pt)
    #text(size: 9pt, fill: luma(110))[Уровень риска: #s.risk_level]
    #v(9pt)
    #grid(columns: (auto, 1fr, auto), column-gutter: 8pt, row-gutter: 8pt,
      align: (left + horizon, horizon, right + horizon),
      [Юридическая часть], bar(s.legal_score, rgb("#1565c0")), [#s.legal_score],
      [Техническая часть], bar(s.technical_score, rgb("#7b1fa2")), [#s.technical_score],
    )
  ],
)

#v(9pt)
#block(fill: rgb("#fff8e1"), stroke: 0.5pt + rgb("#e8a000"), radius: 4pt, inset: 9pt, width: 100%)[
  #text(size: 8.5pt)[
    #text(weight: "bold")[Оценка и нарушения сформированы AI ]
    на основании 152-ФЗ (ред. от 24.06.2025) и КоАП РФ ст. 13.11 (ред. с 30.05.2025).
    Это предварительный технический аудит, а не юридическое заключение — не заменяет консультацию юриста.
  ]
]

// ============================================================================
// ЗАКЛЮЧЕНИЕ
// ============================================================================
#sec[Заключение]
#block(fill: luma(247), radius: 5pt, inset: 11pt, width: 100%)[
  #text(size: 10pt)[#data.executive_summary.verdict]
]
#v(9pt)
#let st = data.executive_summary.stats
#grid(columns: (1fr,) * 4, column-gutter: 8pt,
  stat-card(st.critical_count, "Критичных", sev.critical.color),
  stat-card(st.warning_count, "Предупреждений", sev.warning.color),
  stat-card(st.info_count, "Информационных", sev.info.color),
  stat-card(st.passed_count, "Пройдено проверок", ok-green),
)

// суммарный потенциальный штраф: берём из executive_summary.total_fine_rub,
// иначе складываем штрафы по отдельным нарушениям.
#let es = data.executive_summary
#let total-fine = if "total_fine_rub" in es and es.total_fine_rub != none {
  es.total_fine_rub
} else {
  (data.violations.map(v =>
    if "fine_rub" in v and v.fine_rub != none { v.fine_rub } else { 0 }
  ) + (0,)).sum()
}
#if total-fine > 0 {
  v(9pt)
  block(
    fill: rgb("#fbe9e7"), stroke: 0.5pt + rgb("#b3261e"),
    radius: 5pt, inset: 11pt, width: 100%,
  )[
    #grid(columns: (1fr, auto), align: (left + horizon, right + horizon),
      [
        #text(size: 9.5pt, weight: "bold")[Потенциальная сумма штрафов]
        #v(-2pt)
        #text(size: 7.5pt, fill: luma(110))[Оценка по КоАП ст. 13.11; не является юридическим расчётом]
      ],
      text(size: 18pt, weight: "bold", fill: rgb("#b3261e"))[#fmt-rub(total-fine)],
    )
  ]
}

// ============================================================================
// ИНФРАСТРУКТУРА И ГЕОЛОКАЦИЯ
// ============================================================================
#sec[Инфраструктура и геолокация]
#let geo = data.infrastructure_and_geo
#table(columns: (auto, 1fr), stroke: 0.5pt + luma(220), inset: 7pt,
  [IP сервера], dash(geo.server_ip),
  [Страна сервера], [#dash(geo.server_country_ru) (#dash(geo.server_country))],
  [Хостинг-провайдер], dash(geo.hosting_provider),
  [Локализация ПДн в РФ (ст. 18 ч. 5)],
  // Tri-state: предпочитаем новый ключ localization_status; падаем на legacy bool,
  // если бэк ещё не апдейтнут.
  {
    let st = if "localization_status" in geo { geo.localization_status }
             else if geo.localization_compliant { "compliant" }
             else { "non_compliant" }
    if st == "compliant" { badge("Соответствует", color: ok-green) }
    else if st == "non_compliant" { badge("Нарушение", color: rgb("#b3261e")) }
    else { badge("Не определено", color: rgb("#b78103")) }
  },
)
#if geo.localization_note != none {
  v(4pt)
  text(size: 9pt, fill: luma(90))[#geo.localization_note]
}

// ============================================================================
// ВЫЯВЛЕННЫЕ НАРУШЕНИЯ
// ============================================================================
#sec[Выявленные нарушения]
#let vs = data.violations
#if vs == none or vs.len() == 0 [
  #block(fill: ok-green.lighten(90%), radius: 4pt, inset: 11pt, width: 100%)[
    #text(fill: ok-green, weight: "bold")[Нарушений не выявлено.]
  ]
] else {
  let sorted = vs.sorted(key: vio => sev-order.at(vio.severity, default: 9))
  for vio in sorted {
    let c = sev.at(vio.severity, default: (ru: vio.severity, color: luma(100))).color
    block(width: 100%, inset: 11pt, radius: 4pt, breakable: true,
      fill: c.lighten(93%), stroke: (left: 3pt + c))[
      #grid(columns: (1fr, auto), align: (left, right + horizon),
        [#badge(sev.at(vio.severity, default: (ru: vio.severity)).ru, color: c) #h(6pt) #text(weight: "bold")[#vio.title]],
        text(size: 8pt, fill: luma(110))[#vio.id],
      )
      #v(5pt)
      #text(size: 9pt)[#vio.description]
      #v(6pt)
      #grid(columns: (auto, 1fr), column-gutter: 6pt, row-gutter: 3pt,
        text(size: 8pt, fill: luma(110))[Статья:],
        text(size: 8pt)[#vio.article_152fz],
        text(size: 8pt, fill: luma(110))[Кому адресовано:],
        badge(role-ru.at(vio.target_role, default: vio.target_role), color: luma(95)),
        ..if "fine_rub" in vio and vio.fine_rub != none {
          (
            text(size: 8pt, fill: luma(110))[Возможный штраф:],
            text(size: 8pt, weight: "bold", fill: rgb("#b3261e"))[до #fmt-rub(vio.fine_rub)],
          )
        } else { () },
      )
      #if vio.evidence != none and vio.evidence.len() > 0 {
        v(5pt)
        text(size: 8pt, fill: luma(110))[Где обнаружено:]
        list(..vio.evidence.map(e => text(size: 8pt)[#raw(e)]))
      }
      #v(5pt)
      #block(fill: white, radius: 3pt, inset: 8pt, width: 100%, stroke: 0.5pt + luma(222))[
        #text(size: 8.5pt, weight: "bold")[Рекомендация. ]
        #text(size: 9pt)[#vio.recommendation]
      ]
    ]
    v(7pt)
  }
}

// ============================================================================
// ПРОЙДЕННЫЕ ПРОВЕРКИ
// ============================================================================
#let passed = es.at("passed_checks", default: ())
#if passed.len() > 0 {
  sec[Пройдено проверок]
  for chk in passed {
    block(width: 100%, inset: 9pt, radius: 4pt, breakable: true,
      fill: ok-green.lighten(94%), stroke: (left: 3pt + ok-green))[
      #text(weight: "bold", size: 9.5pt)[✓ #chk.title]
      #if chk.at("detail", default: none) != none {
        v(2pt)
        text(size: 8.5pt, fill: luma(90))[#chk.detail]
      }
    ]
    v(5pt)
  }
}

// ============================================================================
// ТЕХНИЧЕСКОЕ ПРИЛОЖЕНИЕ
// ============================================================================
#let ta = data.technical_appendix

#sec[Техническое приложение]

#text(weight: "bold", size: 10pt)[Найденные документы]
#v(3pt)
// Сокращаем длинный URL до «host + …/last-segment», чтобы не ломал верстку.
// Полный URL всё равно остаётся в исходном JSON, для чтения в браузере хватает.
#let _short-url(u) = {
  if u == none or u == "" { return "—" }
  let s = str(u)
  if s.len() <= 60 { return s }
  // обрезаем строку, оставляя host и хвост
  let parts = s.split("?")
  let base = parts.at(0)
  if base.len() <= 60 { return base + "?…" }
  base.slice(0, 55) + "…"
}

#if ta.documents_found != none and ta.documents_found.len() > 0 {
  table(columns: (1.3fr, 2fr, 1fr), stroke: 0.5pt + luma(220), inset: 7pt,
    text(weight: "bold")[Документ], text(weight: "bold")[URL], text(weight: "bold")[Статус],
    ..ta.documents_found.map(d => (
      dash(d.name),
      // Кликабельная ссылка (в PDF откроется в браузере), визуально обрезана.
      if d.url == none or d.url == "" { [—] }
      else { text(size: 7.5pt, fill: rgb("#1565c0"))[#link(d.url)[#_short-url(d.url)]] },
      dash(d.status),
    )).flatten()
  )
} else [ #text(size: 9pt, fill: luma(110))[Документы не найдены.] ]

#v(10pt)
#text(weight: "bold", size: 10pt)[Трекеры и сторонние скрипты]
#v(4pt)
#let tr = ta.trackers_summary
#grid(columns: (1fr,) * 3, column-gutter: 8pt,
  stat-card(tr.total, "Всего трекеров", rgb("#1565c0")),
  stat-card(tr.russian, "Российских", ok-green),
  stat-card(tr.foreign, "Зарубежных", rgb("#d93f0b")),
)
#if tr.list != none and tr.list.len() > 0 {
  v(5pt)
  table(columns: (1.4fr, 1fr, 1fr), stroke: 0.5pt + luma(220), inset: 7pt,
    text(weight: "bold")[Трекер], text(weight: "bold")[Категория], text(weight: "bold")[Происхождение],
    ..tr.list.map(t => (
      dash(t.at("name", default: none)),
      dash(t.at("kind", default: none)),
      if t.at("origin", default: none) == "ru" { [Российский] }
      else if t.at("origin", default: none) == "foreign" { text(fill: rgb("#d93f0b"))[Зарубежный] }
      else { [—] },
    )).flatten()
  )
}

#v(10pt)
#text(weight: "bold", size: 10pt)[Точки сбора персональных данных]
#v(3pt)
#if ta.data_collection_points != none and ta.data_collection_points.len() > 0 {
  table(columns: (1.5fr, 1fr, 2fr), stroke: 0.5pt + luma(220), inset: 7pt,
    text(weight: "bold")[Страница], text(weight: "bold")[Форма], text(weight: "bold")[Поля],
    ..ta.data_collection_points.map(p => (
      text(size: 8pt)[#raw(p.url)],
      dash(p.form_name),
      text(size: 9pt)[#p.fields.join(", ")],
    )).flatten()
  )
} else [ #text(size: 9pt, fill: luma(110))[Формы сбора ПДн не обнаружены.] ]

#let ai-verdict = (
  "good": (ru: "OK", color: ok-green),
  "partial": (ru: "Частично", color: rgb("#e8a000")),
  "bad": (ru: "Риск", color: rgb("#b3261e")),
)
#let ai = ta.at("ai_analysis", default: ())
#if ai.len() > 0 {
  v(10pt)
  text(weight: "bold", size: 11pt)[AI-анализ юридических текстов]
  v(2pt)
  text(size: 8.5pt, fill: luma(110))[Разбор политик, согласий и cookie-уведомлений с привязкой к статьям 152-ФЗ]
  v(6pt)
  for note in ai {
    let vd = ai-verdict.at(note.at("verdict", default: ""), default: (ru: "—", color: luma(120)))
    let score = note.at("compliance_score", default: none)
    let summary = note.at("summary", default: none)
    let missing = note.at("missing_sections", default: ())
    let issues  = note.at("issues", default: ())
    let strengths = note.at("strengths", default: ())

    block(width: 100%, inset: 11pt, radius: 5pt, breakable: true,
      fill: luma(250), stroke: 0.5pt + luma(220))[
      // ── Шапка карточки: название документа + вердикт + балл
      #grid(columns: (1fr, auto, auto), column-gutter: 8pt,
        align: (left + horizon, right + horizon, right + horizon),
        text(weight: "bold", size: 10.5pt)[#note.doc],
        badge(vd.ru, color: vd.color),
        if score != none {
          text(size: 8.5pt, fill: luma(110))[Балл: #text(weight: "bold", fill: vd.color)[#score]/100]
        } else []
      )

      // ── Краткое резюме
      #if summary != none and summary != "" [
        #v(5pt)
        #text(size: 9.5pt, fill: luma(60))[#summary]
      ] else if note.at("text", default: none) != none [
        #v(5pt)
        #text(size: 9.5pt, fill: luma(60))[#note.text]
      ]

      // ── Отсутствующие обязательные разделы
      #if missing.len() > 0 [
        #v(8pt)
        #text(weight: "bold", size: 9pt)[Отсутствуют обязательные блоки 152-ФЗ:]
        #v(2pt)
        #for m in missing [
          - #text(size: 8.5pt)[#m]
        ]
      ]

      // ── Конкретные проблемы с цитатами
      #if issues.len() > 0 [
        #v(8pt)
        #text(weight: "bold", size: 9pt)[Конкретные проблемы в тексте:]
        #v(4pt)
        #for is in issues [
          #block(width: 100%, inset: 8pt, radius: 3pt, breakable: true,
            fill: rgb("#fff8e1"), stroke: (left: 2.5pt + rgb("#e8a000")))[
            #if is.at("article", default: "") != "" [
              #text(weight: "bold", size: 8pt, fill: rgb("#7a5b00"))[#is.article]
              #v(2pt)
            ]
            // Цитата — курсив, узкие отступы
            #text(size: 8.5pt, style: "italic", fill: luma(80))[«#is.quote»]
            #v(3pt)
            #text(size: 8.5pt)[#text(weight: "bold")[Проблема: ]#is.problem]
            #if is.at("fix", default: "") != "" [
              #v(2pt)
              #text(size: 8.5pt, fill: rgb("#1565c0"))[#text(weight: "bold")[Как исправить: ]#is.fix]
            ]
          ]
          #v(4pt)
        ]
      ]

      // ── Что сделано хорошо
      #if strengths.len() > 0 [
        #v(6pt)
        #text(weight: "bold", size: 9pt, fill: ok-green)[Что сделано правильно:]
        #v(2pt)
        #for s in strengths [
          - #text(size: 8.5pt)[#s]
        ]
      ]
    ]
    v(8pt)
  }
}

// закрываем блок «не failed»: всё содержимое отчёта рендерится только если парсер не упал
]
