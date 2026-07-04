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
See [**Delivered MVP v2 Changes**](#delivered-mvp-v2-changes-part-7) below for the full summary and
the product-access / run instructions.

---

## Customer Feedback Response (Part 2)

Source of feedback: the **Week 4 Sprint Review / customer-executed UAT on 2026-06-27** against
the deployed `MVP v1` build (`v1.1.0`) — see
[`reports/week4/customer-review-summary.md`](../week4/customer-review-summary.md). The customer
accepted the increment (5/5 UAT pass) and raised six minor UI/UX and infrastructure items during
live testing. All six were accepted into Sprint 5; none were rejected.

| Feedback point | Resulting PBI or issue | Status | Response |
|---|---|---|---|
| Starting a check while logged out is blocked, but the loading screen still opens. | [#99](https://github.com/ValekusVachpekus/pdn-control/issues/99) | Done | Stop the loading screen from showing on an unauthenticated check; route the user to registration/login. |
| From the empty history screen there is no obvious way back to the main page ("New check" not discoverable). | [#100](https://github.com/ValekusVachpekus/pdn-control/issues/100) | Done | Make the "New check" / back-to-main action prominent on the empty-history state. |
| A useless "0" fine is shown when owner-side personal-data checks cannot be assessed. | [#101](https://github.com/ValekusVachpekus/pdn-control/issues/101) | Done | Hide the `0` where the check is not applicable instead of rendering a misleading zero. |
| "Data collection points" looks empty when the forms are on the main page. | [#102](https://github.com/ValekusVachpekus/pdn-control/issues/102) | Done | Label the location (e.g. "Main page") so found forms are not shown as empty. |
| The cookie-banner violation is addressed to the Marketer; it should go to the Developer. | [#103](https://github.com/ValekusVachpekus/pdn-control/issues/103) | Done | Change the violation `target_role` for the cookie-banner rule from `marketer` to `developer`. |
| Use a third-party e-mail provider instead of a local SMTP server on the customer's machine. | [#104](https://github.com/ValekusVachpekus/pdn-control/issues/104) | Done (code); customer DNS pending | Integrated a third-party e-mail provider (Resend), removing the local SMTP server. Delivered and merged; sending real e-mail from the customer's domain still needs the customer to add the SPF/DKIM DNS records we provide. |

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

**Authentication & onboarding (Sprint Goal):**
- **Passwordless e-mail login (OTP)** — two-step sign-in (e-mail → 6-digit code), code stored only as a bcrypt hash, 10-min TTL, attempt limit, rate-limited request that does not reveal account existence ([#55](https://github.com/ValekusVachpekus/pdn-control/issues/55), [PR #119](https://github.com/ValekusVachpekus/pdn-control/pull/119)).
- **Real social login via Yandex & VK (OAuth)** — full authorization-code redirect flow with CSRF `state`, PKCE for VK ID, provider callback that finds/creates/links the account, records 152-ФЗ art. 9 consent on first registration, and sets an httpOnly session cookie. Enabled by setting provider `client_id`/`secret` ([#72](https://github.com/ValekusVachpekus/pdn-control/issues/72), [PR #122](https://github.com/ValekusVachpekus/pdn-control/pull/122)).
- **Third-party e-mail provider (Resend)** — removes the local SMTP server; DEV mode logs the code when no key is set ([#104](https://github.com/ValekusVachpekus/pdn-control/issues/104), [PR #119](https://github.com/ValekusVachpekus/pdn-control/pull/119)).

**Customer UAT feedback fixes (Week 4 → MVP v2):**
- Logged-out check no longer opens a stuck loading screen; routes to sign-in and auto-runs after login ([#99](https://github.com/ValekusVachpekus/pdn-control/issues/99)).
- Prominent "New check" action on the empty-history screen ([#100](https://github.com/ValekusVachpekus/pdn-control/issues/100)).
- Useless "0" fine hidden for non-applicable checks ([#101](https://github.com/ValekusVachpekus/pdn-control/issues/101)).
- "Data collection points" now labels each form's location instead of looking empty ([#102](https://github.com/ValekusVachpekus/pdn-control/issues/102)).
- Cookie-banner violation re-addressed to the **Developer** role instead of the Marketer ([#103](https://github.com/ValekusVachpekus/pdn-control/issues/103), PRs [#113](https://github.com/ValekusVachpekus/pdn-control/pull/113)/[#120](https://github.com/ValekusVachpekus/pdn-control/pull/120)/[#121](https://github.com/ValekusVachpekus/pdn-control/pull/121)).

**Architecture, docs & QA (maintainability):**
- Maintained architecture documentation — static/dynamic/deployment views (PlantUML) + 4 ADRs + development-process doc ([#107](https://github.com/ValekusVachpekus/pdn-control/issues/107)/[#108](https://github.com/ValekusVachpekus/pdn-control/issues/108)/[#109](https://github.com/ValekusVachpekus/pdn-control/issues/109), [PR #112](https://github.com/ValekusVachpekus/pdn-control/pull/112)).
- Hosted documentation site (MkDocs Material → GitHub Pages) ([#111](https://github.com/ValekusVachpekus/pdn-control/issues/111), [PR #114](https://github.com/ValekusVachpekus/pdn-control/pull/114)).
- Extended tests/QA for MVP v2 — auth unit tests + rule-engine/report tests; `auth.py` added to the critical-module coverage gate ([#110](https://github.com/ValekusVachpekus/pdn-control/issues/110), [PR #116](https://github.com/ValekusVachpekus/pdn-control/pull/116)).

**Product access & run instructions:** the increment is deployed on the customer's infrastructure at **https://pdn.neurolife.tech**. Local run: `cd backend && docker compose up` (see the [root README](../../README.md) for setup and environment).

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

All Assignment 4 quality gates stay active and green for the delivered increment. The CI
pipeline runs on every PR and on `main`: `backend-unit`, `backend-integration`, `crowler`,
`frontend`, `pdfreport`, `lint`, `security` (Bandit SAST + dependency audit) and `lychee`
(Markdown link check). `main` is protected — these checks and a review by a different member
are required to merge.

For `MVP v2` the automated verification was extended around the newly important areas:
- **Auth unit tests** — bcrypt password hashing and JWT (signature, tampering, expiry); the
  `auth.py` module was added to the critical-module coverage gate ([#110](https://github.com/ValekusVachpekus/pdn-control/issues/110)).
- **OAuth unit tests** — PKCE S256, authorize-URL building (Yandex without PKCE, VK with
  `code_challenge`/`S256`), provider e-mail parsing, single-use CSRF state ([#72](https://github.com/ValekusVachpekus/pdn-control/issues/72)).
- **Rule-engine / report tests** — cookie violation `target_role`, data-collection points, and
  per-role score breakdown ([#110](https://github.com/ValekusVachpekus/pdn-control/issues/110)).
- The `backend-integration` e2e flow was updated to the real OAuth redirect endpoints.

- **CI pipeline:** [`.github/workflows/ci.yml`](https://github.com/ValekusVachpekus/pdn-control/actions/workflows/ci.yml)
- **Latest protected-default-branch CI run:** [run #28675643650 — ✅ success](https://github.com/ValekusVachpekus/pdn-control/actions/runs/28675643650) (`main`, after the OAuth merge).

## Release (Part 7)

`MVP v2` maps to SemVer **`v1.2.0`**. The [`CHANGELOG.md`](../../CHANGELOG.md) `[1.2.0]` section
is prepared. The tagged GitHub release is cut on the protected `main` branch after the customer
Sprint Review, so it can link the sanitized demo video, this Week 5 report, the [Sprint 5
milestone](https://github.com/ValekusVachpekus/pdn-control/milestone/3), and the run/access
instructions.

- **CHANGELOG:** [`CHANGELOG.md`](../../CHANGELOG.md)
- **SemVer release `v1.2.0`:** _pending — link added once tagged._

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

**Current status:** `MVP v2` is delivered on the protected `main` branch and deployed on the
customer's infrastructure at **https://pdn.neurolife.tech**. All 14 Sprint 5 milestone issues are
closed; CI is green on `main`. The increment adds real authentication (passwordless e-mail OTP +
Yandex/VK OAuth), closes the six Week 4 customer-UAT feedback items, and adds maintained
architecture/ADR/process documentation plus a hosted docs site — without weakening the
Assignment 4 quality gates. Two items need a **customer-side action** to go fully live: registering
the Yandex/VK OAuth apps (to supply `client_id`/`secret`) and adding the SPF/DKIM DNS records for
outbound e-mail.

**Next steps:**
- Run the customer Sprint Review + execute UAT-06/07 (recorded); fill the UAT results, Sprint
  Review summary/notes, retrospective, and reflection.
- Record the public sanitized demo video (< 2 min); tag the **`v1.2.0`** release mapped to `MVP v2`.
- Collect OAuth credentials and the e-mail DNS confirmation from the customer to activate social
  login and domain e-mail in production.
- Next Sprint: scan-finished e-mail notification (US-13, [#70](https://github.com/ValekusVachpekus/pdn-control/issues/70)), building on the new e-mail provider.

## Contribution Traceability

Based on actual PR authorship and recorded PR reviews on GitHub for Sprint 5 (milestone #3).

| Member (GitHub) | Issues implemented | PRs authored | PRs reviewed | Testing / QA | Architecture / Docs |
|---|---|---|---|---|---|
| Ilia Shchetkov (`ValekusVachpekus`) | #99, #100, #101, #102, #107 | [#112](https://github.com/ValekusVachpekus/pdn-control/pull/112), [#113](https://github.com/ValekusVachpekus/pdn-control/pull/113), [#114](https://github.com/ValekusVachpekus/pdn-control/pull/114), [#115](https://github.com/ValekusVachpekus/pdn-control/pull/115) | #116, #121, #122 | UI feedback-fix verification | Architecture views + 4 ADR + dev-process (#107–#109); hosted docs site (#111); Week 5 UAT scenarios + LLM report |
| Aleksandr Martiushev (`alexzhal1`) | #55, #72, #103, #104 | [#119](https://github.com/ValekusVachpekus/pdn-control/pull/119), [#120](https://github.com/ValekusVachpekus/pdn-control/pull/120), [#121](https://github.com/ValekusVachpekus/pdn-control/pull/121), [#122](https://github.com/ValekusVachpekus/pdn-control/pull/122) | #113, #114, #115 | Auth (OTP + OAuth) implementation | E-mail provider integration; auth backend |
| Airat Mingazov (`azenlrd`) | #110 | [#116](https://github.com/ValekusVachpekus/pdn-control/pull/116) | #119, #120 | Auth + rule-engine/report tests; `auth.py` added to coverage gate | `docs/testing.md` / QRT updates |
| Ksenya Koroleva (`kskorqueen`) | — | [#118](https://github.com/ValekusVachpekus/pdn-control/pull/118) | #112 | — | Week 5 report contributions and report images; reviewed architecture/process docs (#112) |
| Maksim Shakhrai (`ShakhraiMaksim`) | _to confirm_ | — | — | — | _to confirm_ |

> ⚠️ **`ShakhraiMaksim`'s Sprint 5 contribution is still to be confirmed** — to be filled with his
> actual work before submission.

## Screenshots
<!-- TODO: Sprint milestone, board view, CI run, release, reviewed PR, hosted docs -->
