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
#block(fill: rc, width: 100%, radius: 6pt, inset: 18pt)[
  #text(fill: white, size: 11pt)[Отчёт о проверке сайта на риски нарушения 152-ФЗ]
  #v(5pt)
  #text(fill: white, size: 22pt, weight: "bold")[#m.domain]
  #v(2pt)
  #text(fill: white, size: 10pt)[#m.target_url]
]

#v(10pt)
#grid(columns: (1fr, 1fr), row-gutter: 5pt, column-gutter: 16pt,
  [*Организация:* #dash(m.organization_name)],
  [*Дата отчёта:* #m.generated_at],
  [*Страниц проверено:* #m.pages_scanned],
  [*Длительность скана:* #m.scan_duration_sec с],
  [*ID отчёта:* #raw(m.report_id)],
  [*Версия сканера:* #m.scanner_version],
)

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
    #text(weight: "bold")[Важно. ]
    Это предварительный технический аудит сайта, а не юридическое заключение.
    Отчёт не гарантирует полное соответствие 152-ФЗ и не заменяет консультацию юриста.
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
  if geo.localization_compliant { badge("Соответствует", color: ok-green) }
  else { badge("Нарушение", color: rgb("#b3261e")) },
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
// ТЕХНИЧЕСКОЕ ПРИЛОЖЕНИЕ
// ============================================================================
#let ta = data.technical_appendix

#sec[Техническое приложение]

#text(weight: "bold", size: 10pt)[Найденные документы]
#v(3pt)
#if ta.documents_found != none and ta.documents_found.len() > 0 {
  table(columns: (1.3fr, 2fr, 1.2fr), stroke: 0.5pt + luma(220), inset: 7pt,
    text(weight: "bold")[Документ], text(weight: "bold")[URL], text(weight: "bold")[Статус],
    ..ta.documents_found.map(d => (
      dash(d.name), text(size: 8pt)[#dash(d.url)], dash(d.status),
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
  text(size: 9pt)[#tr.list.join(", ")]
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
