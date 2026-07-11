# Product Roadmap — ПДн Контроль

This roadmap outlines our Sprint-by-Sprint delivery plan through the end of the course. Detailed task descriptions and real-time progress are tracked in the [Project Board](https://github.com/users/ValekusVachpekus/projects/1). The current Sprint (Assignment 6, Week 6) is inspectable on the board filtered by the [Sprint 6 milestone](https://github.com/ValekusVachpekus/pdn-control/milestone/4).

> **Sprint numbering:** Sprints continue the team's sequential numbering. Assignment 6 spans **Sprint 6** (Week 6) and **Sprint 7** (Week 7); in the assignment text these are referred to as "Sprint 4" and "Sprint 5". The final Sprint 7 increment maps to release `MVP v3`, the final course version. The Sprint milestone (work container) is kept separate from the SemVer release tag.

## Sprint 1: Stabilization & Public Safety (Completed)
*   **Milestone:** [Sprint 1 — Stabilization / RC hardening](https://github.com/ValekusVachpekus/pdn-control/milestone/1)
*   **Dates:** 2026-06-15 — 2026-06-21
*   **Sprint Goal:** Deliver a trustworthy, publicly-safe MVP v1 with protected URL scanning and core reporting.
*   **Focus:** Core infrastructure, SSRF protection, and stabilization of the scan-to-report flow.
*   **Outcome:** MVP v1 released as [`v1.0.0`](https://github.com/ValekusVachpekus/pdn-control/releases/tag/v1.0.0). Scan→report flow live, anti-SSRF enforced, deterministic re-scans, paid-report bypass closed.
*   **Delivered Items:**
    *   [Bug] Free-report bypass fix ([#54](https://github.com/ValekusVachpekus/pdn-control/issues/54))
    *   [Bug] Same results for one website ([#34](https://github.com/ValekusVachpekus/pdn-control/issues/34))
    *   [US-12] Server-side URL validation / anti-SSRF ([#69](https://github.com/ValekusVachpekus/pdn-control/issues/69))
    *   [US-01] Basic website scan ([#58](https://github.com/ValekusVachpekus/pdn-control/issues/58))
    *   [US-02] Total potential fine display ([#59](https://github.com/ValekusVachpekus/pdn-control/issues/59))
    *   [US-03] Detailed list of violations ([#60](https://github.com/ValekusVachpekus/pdn-control/issues/60))
    *   [US-04] Legal article references ([#61](https://github.com/ValekusVachpekus/pdn-control/issues/61))
    *   [US-05] Free tier limited check ([#62](https://github.com/ValekusVachpekus/pdn-control/issues/62))
    *   [US-06] Paid tier full analysis ([#63](https://github.com/ValekusVachpekus/pdn-control/issues/63))
    *   [US-07] Compliance score (0-100) ([#64](https://github.com/ValekusVachpekus/pdn-control/issues/64))
    *   [Task] Implement backend ([#13](https://github.com/ValekusVachpekus/pdn-control/issues/13))
    *   [Task] Make API for checking status in Backend ([#18](https://github.com/ValekusVachpekus/pdn-control/issues/18))

## Sprint 2 — Assignment 4: Quality Automation & Release (Completed)
*   **Milestone:** [Assignment 4 Sprint — Quality automation & release](https://github.com/ValekusVachpekus/pdn-control/milestone/2)
*   **Dates:** 2026-06-22 — 2026-06-28
*   **Sprint Goal:** Turn MVP v1 into a verifiably reliable increment — stand up automated quality gates (defined quality requirements, automated tests with coverage on critical modules, an additional QA check, and branch protection on `main`), then deploy the gated increment and cut release `v1.1.0` so the customer can run user acceptance testing against a trustworthy, internet-accessible build.
*   **Focus:** Risk reduction and quality automation over new features — CI quality gate, deterministic geo-localization, and internet-accessible deployment for UAT.
*   **Planned Items:**
    *   [Task] CI quality gate: unit+integration tests, coverage, additional QA check & branch protection ([#71](https://github.com/ValekusVachpekus/pdn-control/issues/71)) — *Must Have, 8 SP*
    *   [Task] Determine hosting country from IP deterministically (GeoIP), not by LLM guess ([#75](https://github.com/ValekusVachpekus/pdn-control/issues/75)) — *Should Have, 5 SP*
    *   [Task] Move frontend behind Caddy on 443 + TLS certificate (internet-accessible deploy) ([#86](https://github.com/ValekusVachpekus/pdn-control/issues/86)) — *Must Have, 3 SP*
*   **Sprint size:** 16 Story Points.
*   **Outcome:** Increment accepted by the customer at the Week 4 Sprint Review/UAT (5/5 UAT pass). Released as [`v1.1.0`](https://github.com/ValekusVachpekus/pdn-control/releases/tag/v1.1.0). Six minor UI/UX and infra feedback items raised during UAT ([#99–#104](https://github.com/ValekusVachpekus/pdn-control/issues/99)) carried into Sprint 5.

## Sprint 5 — Assignment 5: MVP v2 — Auth & Architecture (Completed)
*   **Milestone:** [Sprint 5 — MVP v2: Auth & Architecture](https://github.com/ValekusVachpekus/pdn-control/milestone/3)
*   **Dates:** 2026-06-29 — 2026-07-05
*   **Maps to release:** `MVP v2` → SemVer `v1.2.0` (milestone kept separate from the release tag).
*   **Sprint Goal:** Deliver `MVP v2` — add real authentication (OAuth Yandex/VK + passwordless e-mail login) and close the UI defects from the Week 4 customer UAT, while documenting the architecture (static/dynamic/deployment views + ADRs) and the development process, without weakening the Assignment 4 quality gates.
*   **Focus:** New onboarding/auth functionality + customer-feedback fixes + maintained architecture, ADR, and development-process documentation, all under the existing CI quality gates.
*   **Planned Items (42 SP):**
    *   *New functionality (Auth & Onboarding):*
        *   [Task] OAuth login via Yandex & VK (redirect flow) ([#72](https://github.com/ValekusVachpekus/pdn-control/issues/72)) — *Must, 8 SP*
        *   [Task] Passwordless OTP e-mail login ([#55](https://github.com/ValekusVachpekus/pdn-control/issues/55)) — *Should, 5 SP*
        *   [Task] Third-party e-mail provider ([#104](https://github.com/ValekusVachpekus/pdn-control/issues/104)) — *Should, 3 SP*
    *   *Customer-feedback fixes (Week 4 UAT):*
        *   [Bug] Loading screen on unauthenticated check ([#99](https://github.com/ValekusVachpekus/pdn-control/issues/99)) — *Must, 2 SP*
        *   [Task] Discoverable "New check" on empty history ([#100](https://github.com/ValekusVachpekus/pdn-control/issues/100)) — *Should, 2 SP*
        *   [Bug] Remove misleading "0" fine ([#101](https://github.com/ValekusVachpekus/pdn-control/issues/101)) — *Should, 1 SP*
        *   [Bug] Label form location in "data collection points" ([#102](https://github.com/ValekusVachpekus/pdn-control/issues/102)) — *Should, 2 SP*
        *   [Bug] Cookie violation → Developer, not Marketer ([#103](https://github.com/ValekusVachpekus/pdn-control/issues/103)) — *Must, 1 SP*
    *   *Architecture, process & quality documentation:*
        *   [Task] Architecture documentation: static/dynamic/deployment views ([#107](https://github.com/ValekusVachpekus/pdn-control/issues/107)) — *Must, 5 SP*
        *   [Task] ≥3 ADRs linked to quality requirements ([#108](https://github.com/ValekusVachpekus/pdn-control/issues/108)) — *Must, 3 SP*
        *   [Task] `development-process.md` (gitGraph + config management) ([#109](https://github.com/ValekusVachpekus/pdn-control/issues/109)) — *Must, 2 SP*
        *   [Task] Extend tests/QA & CI evidence for MVP v2 ([#110](https://github.com/ValekusVachpekus/pdn-control/issues/110)) — *Must, 5 SP*
        *   [Task] Hosted documentation site ([#111](https://github.com/ValekusVachpekus/pdn-control/issues/111)) — *Should, 3 SP*
*   **Sprint size:** 42 Story Points.
*   **Outcome:** `MVP v2` released as [`v1.2.0`](https://github.com/ValekusVachpekus/pdn-control/releases/tag/v1.2.0). Real authentication (OAuth Yandex/VK + passwordless e-mail login) delivered, Week 4 UAT defects closed, architecture (views + ADRs) and development-process documentation maintained under the existing CI gates.

## Sprint 6 — Assignment 6: MVP v3 — Customer transition (Week 6 trial) (Current)
*   **Milestone:** [Sprint 6 — MVP v3: Customer transition](https://github.com/ValekusVachpekus/pdn-control/milestone/4)
*   **Dates:** 2026-07-06 — 2026-07-12
*   **Sprint Goal:** Deliver a stable trial / handover-candidate release (`v1.3.0`) on the customer's own infrastructure — wire production OAuth (Yandex/VK) on the customer's keys and production e-mail sending via the customer's DNS records — and review the customer-facing documentation set for transition readiness.
*   **Focus:** Real transition on the customer side over new features — the product already runs on the customer's server (**https://pdn.neurolife.tech**); Week 6 finalizes production credentials, e-mail/DNS verification, and handover documentation.
*   **Candidate Items:**
    *   [Task] Production OAuth Yandex/VK on the customer's keys ([#72](https://github.com/ValekusVachpekus/pdn-control/issues/72) follow-up)
    *   [Task] Production e-mail sending + sender-domain DNS verification (SPF/DKIM), on top of ([#104](https://github.com/ValekusVachpekus/pdn-control/issues/104))
    *   [Task] Customer-handover documentation + customer-facing documentation review ([`docs/customer-handover.md`](customer-handover.md))
*   **Release target:** Week 6 trial `v1.3.0` on the protected `main`.

## Sprint 7 — Assignment 6: MVP v3 — Final delivery & transition (Week 7)
*   **Milestone:** [Sprint 7 — MVP v3: Final delivery & transition](https://github.com/ValekusVachpekus/pdn-control/milestone/5)
*   **Dates:** 2026-07-13 — 2026-07-19
*   **Maps to release:** `MVP v3` → final SemVer tag (higher precedence than `v1.3.0`).
*   **Sprint Goal:** Complete the transition — finalize OAuth and e-mail on the customer's infrastructure/DNS, resolve Week 6 trial feedback, finalize handover documentation, and deliver the final course version `MVP v3`.
*   **Focus:** Follow-up maintenance, final transition, and final delivery rather than new features — reliability, handover completeness, and closing customer trial feedback.
*   **Expected scope:** Week 6 customer-trial feedback items (to be created after the Week 6 meeting), remaining transition actions, documentation updates, and the public sanitized demo video for `MVP v3`.
*   **End-of-course outcome:** `MVP v3` deployed and operated on the customer's infrastructure, with the reached handover level and customer-confirmation status recorded in [`docs/customer-handover.md`](customer-handover.md) and [`reports/week7/README.md`](../reports/week7/README.md).

## Continuing Quality & Automation Commitments

The quality gates established in the Assignment 4 Sprint are **maintained project assets**, not one-time submission evidence. All later Sprints must keep them passing or replace them with documented, equivalent-or-stronger coverage:

*   **CI quality gate** ([#71](https://github.com/ValekusVachpekus/pdn-control/issues/71)) — unit + integration tests, coverage on critical modules (≥30% line coverage), an additional QA check (security/dependency scan), and lint/format/type checks run on every PR.
*   **Branch protection** on `main` — required passing CI checks and review before merge.
*   **Quality requirements & QRTs** — defined in `docs/quality-requirements.md` and `docs/quality-requirement-tests.md`; each new quality-relevant change must extend or maintain them.
*   **Definition of Done** — `docs/definition-of-done.md` requires acceptance-criteria verification, review, passing CI, relevant automated tests and QRTs, coverage expectations, preserved testing evidence, and a changelog update for user-visible changes.
*   **User acceptance tests** — `docs/user-acceptance-tests.md` keeps ≥3 active end-user-facing scenarios with execution history.

Later PBIs must extend these gates instead of bypassing or disabling them.
