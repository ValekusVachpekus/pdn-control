# Week 7 — Assignment 6 · Sprint 7 (финальный публичный отчёт)

> Каноничный публичный отчёт за Week 7 (Sprint 7 = «Sprint 5» в терминологии задания) и
> **итоговый индекс сдачи Assignment 6**. Легче, чем Week 6: фокус на follow-up, финальной
> передаче и доставке `MVP v3`, без повторения полного контекста проекта.
> Sprint dates: **2026-07-13 — 2026-07-19**.
>
> Статус заполнения: заполнены все пункты, не зависящие от событий. Явными `TODO` остаются
> только пункты, требующие проведённого финального созвона (транскрипт/summary, UAT, итог
> передачи, ответы на фидбек), опубликованного релиза `v1.4.0`, demo-видео команды и
> скриншотов — заполняются по мере наступления.

- **1. Week 6 отчёт (полное evidence Week 6):** [`reports/week6/README.md`](../week6/README.md)

## Бэклог и спринт
- **2. Product Backlog board:** GitHub Projects «доска команды» #1 (элементы с лейблами
  `user story` / `task`); публичный срез — [issues репозитория](https://github.com/ValekusVachpekus/pdn-control/issues),
  трассировка US — [`docs/user-stories.md`](../../docs/user-stories.md).
- **3. Sprint 7 Backlog board:** issues milestone #5 —
  https://github.com/ValekusVachpekus/pdn-control/milestone/5
- **4. Sprint 7 milestone:** https://github.com/ValekusVachpekus/pdn-control/milestone/5
- **5. Sprint Goal / dates / scope:** **Завершить фактическую передачу продукта и выпустить
  финальную версию курса `MVP v3`.** Заказчик принял инкремент Week 6 (`v1.3.0`) на встрече
  2026-07-11 и **новых фич не запросил**, поэтому Sprint 7 намеренно **не содержит нового
  продуктового scope**: это спринт передачи, документации и доставки — финализация
  handover-документации и переноса GitHub-репозитория, получение финального подтверждения
  заказчика, релиз `v1.4.0` и публичное demo-видео. Даты: 2026-07-13 — 2026-07-19.
- **6. Sprint 7 size (SP):** **7 SP** — [#131](https://github.com/ValekusVachpekus/pdn-control/issues/131)
  финализация передачи (2) + [#132](https://github.com/ValekusVachpekus/pdn-control/issues/132)
  релиз `MVP v3` и demo-видео (2) + [#149](https://github.com/ValekusVachpekus/pdn-control/issues/149)
  отчётность Week 7 (3).

## Follow-up и MVP v3
- **7. Сводка follow-up и финальных изменений `MVP v3`:** продуктовый код с `v1.3.0` **не
  менялся** — новых доработок заказчик не запрашивал (инкремент принят на встрече 2026-07-11).
  Sprint 7 закрывает передачу: [`docs/customer-handover.md`](../../docs/customer-handover.md)
  приведён к фактическому состоянию (подтверждение заказчика, self-service боевых OAuth-ключей,
  верифицированный почтовый домен, перенос репозитория), [`docs/roadmap.md`](../../docs/roadmap.md)
  доведён до итога курса, оформлена полная отчётность Week 7. Изменения этого релиза —
  [`CHANGELOG.md`](../../CHANGELOG.md) § `[1.4.0]` (тег проставляется при публикации релиза,
  п. 21).
- **8. Final product access artifact:** https://pdn.neurolife.tech (инфраструктура заказчика).
- **9. Access / run instructions:** [`README.md` § Локальный запуск](../../README.md#локальный-запуск)
  и [`docs/customer-handover.md`](../../docs/customer-handover.md) § «Запуск, восстановление и проверка».

## Документация
- **10. README:** [`README.md`](../../README.md)
- **11. CONTRIBUTING:** [`CONTRIBUTING.md`](../../CONTRIBUTING.md)
- **12. AGENTS:** [`AGENTS.md`](../../AGENTS.md)
- **13. Customer handover:** [`docs/customer-handover.md`](../../docs/customer-handover.md)
- **14. Hosted docs site:** https://valekusvachpekus.github.io/pdn-control/

## Финальная передача
- **15. Итог передачи** (уровень + статус подтверждения): TODO — фиксируется по итогам
  финального созвона Week 7 (агенда: [`final-transition-agenda.md`](final-transition-agenda.md)).
  По состоянию на конец Week 6 достигнут уровень `Deployed or operated on customer side` и
  статус `Accepted` (встреча 2026-07-11); в Week 7 запрашивается подтверждение уже по текущему
  тексту [`docs/customer-handover.md`](../../docs/customer-handover.md).
- **16. Что передано/делегировано:** полная матрица владения —
  [`docs/customer-handover.md`](../../docs/customer-handover.md) § «Что передано, делегировано и
  что осталось у команды». Сервер и домен — у заказчика; продукт развёрнут и работает на его
  инфраструктуре; почтовый домен верифицирован (SPF/DKIM); боевые OAuth-ключи Яндекс/ВК —
  self-service заказчика (задокументированная пошаговая инструкция); перенос GitHub-репозитория
  инициирован 2026-07-11 и финализируется на созвоне Week 7 (#131).
- **17. Остаточные блокеры/лимиты/поддержка/follow-up от заказчика:** TODO (после созвона).
  Известные пост-курсовые ограничения перечислены в
  [`docs/customer-handover.md`](../../docs/customer-handover.md) § «Достаточность документации
  и остаточная поддержка».
- **18. Evidence самостоятельного использования / деплоя на стороне заказчика:** TODO —
  публичная санитизированная сводка. Приватная запись, точные таймкоды и скриншоты переписки —
  только в Week 7 Moodle PDF.
- **19. Таблица ответов на фидбек (Sprint 7):**

  | Фидбек заказчика | Результат (PBI / issue) |
  |---|---|
  | TODO (после созвона Week 7) | TODO |

- **20. Week 7 UAT / customer-trial результаты:** TODO — переподтверждение сценариев из
  [`docs/user-acceptance-tests.md`](../../docs/user-acceptance-tests.md) (UAT-08 на боевых
  OAuth-ключах, если заказчик их подставил; UAT-09; смоук UAT-01 и UAT-04).

## Релиз, демо и Sprint Review
- **21. Final SemVer release → `MVP v3`:** TODO — `v1.4.0` (precedence выше Week 6 trial
  `v1.3.0`), на защищённой `main`.
- **22. CHANGELOG:** [`CHANGELOG.md`](../../CHANGELOG.md)
- **23. Public sanitized demo video (`MVP v3`):** TODO — ссылка (записывает команда).
- **24. Demo Day preparation summary:** TODO — слайды (PDF, приватно в Moodle), пре-записанное
  demo под 2 минуты, распределение слайдов между всеми участниками, репетиция на лабораторной
  Week 7 и тайминг 7 + 7 минут для Week 8.
- **25. Sprint Review transcript/notes:** [`sprint-review-transcript.md`](sprint-review-transcript.md).
- **26. Sprint Review summary:** [`sprint-review-summary.md`](sprint-review-summary.md)
- **27. Reflection:** [`reflection.md`](reflection.md)
- **28. Retrospective:** [`retrospective.md`](retrospective.md)
- **29. LLM report:** [`llm-report.md`](llm-report.md)

## Итоги
- **30. Финальный статус продукта:** TODO (после релиза `v1.4.0` и созвона). Кратко: `MVP v3`
  развёрнут и эксплуатируется на инфраструктуре заказчика (`pdn.neurolife.tech`), принят
  заказчиком на встрече 2026-07-11, quality-гейты Assignment 4 (CI, тесты, покрытие,
  security-скан, branch protection) не ослаблены.
- **31. Contribution traceability:**

  | Участник | Роль | Issues | PR / ревью | Тесты / доки / передача / деплой / Demo Day |
  |---|---|---|---|---|
  | Ilia Shchetkov (`ValekusVachpekus`) | Product Owner / Frontend | #131, #132, #149 | автор #148 | Финализация передачи, handover-документация, roadmap, отчёты Week 7, релиз `v1.4.0` |
  | Aleksandr Martiushev (`alexzhal1`) | Backend | TODO | TODO | TODO |
  | Airat Mingazov (`azenlrd`) | Backend | TODO | ревью #148 | TODO |
  | Ksenya Koroleva (`kskorqueen`) | Scrum Master | TODO | TODO | TODO |
  | Maksim Shakhrai (`ShakhraiMaksim`) | QA | TODO | TODO | TODO |

  > Таблица дозаполняется по факту работ Sprint 7 (созвон, demo-видео, слайды, скриншоты).
  > Вклад указывается честно: если участник не выполнял работ в спринте — это фиксируется прямо.

- **32. Скриншоты** (`images/`): TODO — milestone #5, релиз `v1.4.0`, evidence финального
  деплоя/доступа, пример review-linked PR.
