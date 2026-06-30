# Assignment 5 — ПДн Контроль (Week 5 Report)

**Project Description:** A specialized web service for preliminary **technical** audits of
small and medium business websites against typical **152-ФЗ** ("On Personal Data") compliance
risks. It provides risk-scoring, violation lists, potential fines, and legal remediation steps.
This week (`MVP v2`) focuses on **authentication & onboarding** (OAuth Yandex/VK + passwordless
e-mail login), **closing the Week 4 customer UAT feedback**, and **maintained architecture, ADR,
and development-process documentation** — all under the Assignment 4 quality gates.

- **License:** [Root MIT LICENSE](https://github.com/ValekusVachpekus/pdn-control/blob/main/LICENSE)
- **Issue Templates:** [.github/ISSUE_TEMPLATE](https://github.com/ValekusVachpekus/pdn-control/tree/main/.github/ISSUE_TEMPLATE)
- **Extended PR Template:** [pull_request_template.md](https://github.com/ValekusVachpekus/pdn-control/blob/main/.github/pull_request_template.md)

Canonical Week 5 public report and submission index. _Sections are filled as Sprint 5 progresses; status fields update from `Planned`/`In Progress` to `Done` as work merges._

---

## Sprint 5 Overview

- **Product Backlog board:** https://github.com/users/ValekusVachpekus/projects/1
- **Sprint Backlog board view:** [Project board — Sprint Backlog Assignment 5 view](https://github.com/users/ValekusVachpekus/projects/1) (filtered by the Sprint 5 milestone)
- **Sprint 5 milestone:** [Sprint 5 — MVP v2: Auth & Architecture](https://github.com/ValekusVachpekus/pdn-control/milestone/3)
- **Sprint dates:** 2026-06-29 — 2026-07-05
- **Maps to release:** `MVP v2` → SemVer `v1.2.0`
- **Total Sprint size:** **42 Story Points** (13 PBIs)

**Sprint Goal:** Deliver `MVP v2` — add real authentication (OAuth Yandex/VK + passwordless
e-mail login) and close the UI defects from the Week 4 customer UAT, while documenting the
architecture (static/dynamic/deployment views + ADRs) and the development process, without
weakening the Assignment 4 quality gates.

**Scope summary:** new auth/onboarding functionality (OAuth [#72](https://github.com/ValekusVachpekus/pdn-control/issues/72),
passwordless OTP [#55](https://github.com/ValekusVachpekus/pdn-control/issues/55), e-mail provider
[#104](https://github.com/ValekusVachpekus/pdn-control/issues/104)); six Week 4 UAT feedback fixes
([#99](https://github.com/ValekusVachpekus/pdn-control/issues/99)–[#104](https://github.com/ValekusVachpekus/pdn-control/issues/104));
maintained architecture/ADR/process documentation and extended tests/QA
([#107](https://github.com/ValekusVachpekus/pdn-control/issues/107)–[#111](https://github.com/ValekusVachpekus/pdn-control/issues/111)).

<!-- TODO Part 7: Summary of delivered MVP v2 changes -->
<!-- TODO Part 7: Link to product access artifact + run instructions -->

---

## Customer Feedback Response (Part 2)

Source of feedback: the **Week 4 Sprint Review / customer-executed UAT on 2026-06-27** against
the deployed `MVP v1` build (`v1.1.0`) — see
[`reports/week4/customer-review-summary.md`](../week4/customer-review-summary.md). The customer
accepted the increment (5/5 UAT pass) and raised six minor UI/UX and infrastructure items during
live testing. All six were accepted into Sprint 5; none were rejected.

| Feedback point | Resulting PBI or issue | Status | Response |
|---|---|---|---|
| Starting a check while logged out is blocked, but the loading screen still opens. | [#99](https://github.com/ValekusVachpekus/pdn-control/issues/99) | Planned (Sprint 5) | Stop the loading screen from showing on an unauthenticated check; route the user to registration/login. |
| From the empty history screen there is no obvious way back to the main page ("New check" not discoverable). | [#100](https://github.com/ValekusVachpekus/pdn-control/issues/100) | Planned (Sprint 5) | Make the "New check" / back-to-main action prominent on the empty-history state. |
| A useless "0" fine is shown when owner-side personal-data checks cannot be assessed. | [#101](https://github.com/ValekusVachpekus/pdn-control/issues/101) | Planned (Sprint 5) | Hide the `0` where the check is not applicable instead of rendering a misleading zero. |
| "Data collection points" looks empty when the forms are on the main page. | [#102](https://github.com/ValekusVachpekus/pdn-control/issues/102) | Planned (Sprint 5) | Label the location (e.g. "Main page") so found forms are not shown as empty. |
| The cookie-banner violation is addressed to the Marketer; it should go to the Developer. | [#103](https://github.com/ValekusVachpekus/pdn-control/issues/103) | Planned (Sprint 5) | Change the violation `target_role` for the cookie-banner rule from `marketer` to `developer`. |
| Use a third-party e-mail provider instead of a local SMTP server on the customer's machine. | [#104](https://github.com/ValekusVachpekus/pdn-control/issues/104) | Planned (Sprint 5) | Integrate a third-party e-mail provider; the team sends the customer the DNS records to add on their side. |

### Feedback not addressed this Sprint

No customer feedback was **rejected**. Every explicit point from the Week 4 review is tracked
above and pulled into Sprint 5. Two **related** items are intentionally deferred beyond `MVP v2`:

- **Scan-finished notification — US-13 ([#70](https://github.com/ValekusVachpekus/pdn-control/issues/70))** — deferred to the next Sprint because it builds on the new third-party e-mail provider ([#104](https://github.com/ValekusVachpekus/pdn-control/issues/104)) delivered in `MVP v2`; sending notifications is only useful once the provider is in place. Not re-raised by the customer at the Week 4 review.
- **DNS cut-over to the customer's domain ([#88](https://github.com/ValekusVachpekus/pdn-control/issues/88))** — the DNS change itself is a **customer-side action**. The team provides configuration and the records to add; the cut-over depends on the customer.

`MVP v2` addresses customer feedback directly: all six Week 4 UAT items are in scope this Sprint.

<!-- =========================================================== -->
<!-- The sections below are scaffolded and filled as Sprint 5    -->
<!-- progresses (Parts 3–14).                                    -->
<!-- =========================================================== -->

## Delivered MVP v2 Changes (Part 7)
<!-- TODO -->

## Maintained Documentation
- [`docs/roadmap.md`](../../docs/roadmap.md)
- [`docs/definition-of-done.md`](../../docs/definition-of-done.md)
- [`docs/testing.md`](../../docs/testing.md)
- [`docs/quality-requirements.md`](../../docs/quality-requirements.md)
- [`docs/quality-requirement-tests.md`](../../docs/quality-requirement-tests.md)
- [`docs/user-acceptance-tests.md`](../../docs/user-acceptance-tests.md)
- [`docs/development-process.md`](../../docs/development-process.md)
- [`docs/architecture/README.md`](../../docs/architecture/README.md)
- Architecture views: [static](../../docs/architecture/static-view/component-diagram.svg) · [dynamic](../../docs/architecture/dynamic-view/scan-sequence.svg) · [deployment](../../docs/architecture/deployment-view/deployment-diagram.svg)
- [ADR directory](../../docs/architecture/adr/)

## Architecture Summary (Parts 4–5)

The product is a set of cooperating services run as one Docker Compose stack behind Caddy/TLS:
a React **frontend**, a FastAPI **backend API**, an async **Celery worker** running the scan
pipeline, a **crawler/parser** (facts, Contract #1), a **PDF** renderer (Typst), **PostgreSQL**,
and **Redis** (queue, LLM cache, progress). It integrates with external systems: the scanned
target site, the LLM API (Qwen), GeoIP, OAuth (Yandex/VK), an e-mail provider, and CloudPayments.
Services are highly cohesive and loosely coupled through two stable JSON contracts and a Redis
queue, which keeps the MVP v2 auth work isolated from the scan pipeline. See
[`docs/architecture/README.md`](../../docs/architecture/README.md) for the static, dynamic, and
deployment views.

**Quality requirements ↔ architecture decisions:** the three quality requirements are each backed
by a recorded ADR — [QR-01 confidentiality](../../docs/quality-requirements.md#qr-01--crawler-confidentiality-against-ssrf)
→ [ADR-0003](../../docs/architecture/adr/0003-server-side-gating-and-ssrf-boundary.md)/[ADR-0004](../../docs/architecture/adr/0004-single-host-compose-caddy-tls.md);
[QR-02 determinism](../../docs/quality-requirements.md#qr-02--deterministic-scan-results)
→ [ADR-0002](../../docs/architecture/adr/0002-deterministic-geoip-over-llm.md)/[ADR-0001](../../docs/architecture/adr/0001-full-llm-analysis-pipeline.md);
[QR-03 correctness](../../docs/quality-requirements.md#qr-03--correct-fact-to-violation-mapping-rule-engine)
→ [ADR-0001](../../docs/architecture/adr/0001-full-llm-analysis-pipeline.md).

## Testing & CI Status (Part 6)
<!-- TODO: testing/CI summary, link to CI pipeline + latest protected-branch run -->

## Release (Part 7)
<!-- TODO: link to SemVer release mapped to MVP v2 + CHANGELOG.md -->

## Demo & UAT (Parts 8, 13)

**User Acceptance Tests:** all scenarios are maintained in
[`docs/user-acceptance-tests.md`](../../docs/user-acceptance-tests.md). For `MVP v2` two new
scenarios were added for the Week 4 customer-UAT feedback fixes:

- [UAT-06](../../docs/user-acceptance-tests.md#uat-06--logged-out-check-routes-to-sign-in-without-a-loading-screen) — logged-out check routes to sign-in without a loading screen ([#99](https://github.com/ValekusVachpekus/pdn-control/issues/99)).
- [UAT-07](../../docs/user-acceptance-tests.md#uat-07--report-and-history-ui-clarity-fixes) — report and history UI clarity fixes ([#100](https://github.com/ValekusVachpekus/pdn-control/issues/100), [#101](https://github.com/ValekusVachpekus/pdn-control/issues/101), [#102](https://github.com/ValekusVachpekus/pdn-control/issues/102)).

> Status: ⏳ **Pending execution** — UAT-06/07 are scheduled to be run with the customer at the
> Sprint 5 Review (recorded session). The public UAT **results summary** is filled in here after
> that session.

<!-- TODO Part 13: public sanitized demo video (<2 min) -->

## Hosted Documentation (Part 11)

The maintained `docs/` are published as a browsable documentation site (MkDocs Material),
built and deployed to GitHub Pages from the protected `main` branch by
[`.github/workflows/docs.yml`](../../.github/workflows/docs.yml).

- **Hosted documentation site:** https://valekusvachpekus.github.io/pdn-control/

The site surfaces the [roadmap](https://valekusvachpekus.github.io/pdn-control/roadmap/),
[architecture overview + views](https://valekusvachpekus.github.io/pdn-control/architecture/),
the [ADRs](https://valekusvachpekus.github.io/pdn-control/architecture/adr/0001-full-llm-analysis-pipeline/),
the [development process](https://valekusvachpekus.github.io/pdn-control/development-process/),
and the quality docs (requirements, requirement tests, testing strategy, Definition of Done).

## Sprint Review & Retrospective (Parts 9–10)
- [Sprint Review summary](sprint-review-summary.md) <!-- TODO -->
- [Reflection](reflection.md) <!-- TODO -->
- [Retrospective](retrospective.md) <!-- TODO -->
- [LLM report](llm-report.md)

## Product Status & Next Steps
<!-- TODO -->

## Contribution Traceability
<!-- TODO Part: team member → issues/PRs/review/testing/architecture/docs -->

## Screenshots
<!-- TODO: Sprint milestone, board view, CI run, release, reviewed PR, hosted docs -->
