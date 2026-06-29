# Product Roadmap — ПДн Контроль

This roadmap outlines our Sprint-by-Sprint delivery plan. Detailed task descriptions and real-time progress are tracked in the [Project Board](https://github.com/users/ValekusVachpekus/projects/1). The current Sprint is inspectable on the **Sprint Backlog Assignment 5** view of the board, filtered by the [Sprint 5 milestone](https://github.com/ValekusVachpekus/pdn-control/milestone/3).

> **Sprint numbering:** Sprints are numbered by course week. Sprint 5 is the Assignment 5 increment and maps to release `MVP v2`. The Sprint milestone (work container) is kept separate from the SemVer release tag.

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

## Sprint 5 — Assignment 5: MVP v2 — Auth & Architecture (Current)
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

## Next: Notifications & Customer Infrastructure (Expected next Sprint)
*   **Milestone:** to be created
*   **Sprint Goal:** Finish scan-completion notifications on top of the new e-mail provider and complete the customer-infrastructure/DNS hand-off, maintaining the quality gates.
*   **Candidate Items:**
    *   [US-13] Scan-finished notification (link/email) ([#70](https://github.com/ValekusVachpekus/pdn-control/issues/70)) — builds on the MVP v2 e-mail provider ([#104](https://github.com/ValekusVachpekus/pdn-control/issues/104))
    *   [Task] Complete hosting on the customer's infrastructure + DNS migration ([#88](https://github.com/ValekusVachpekus/pdn-control/issues/88))
*   **Architecture/quality work to continue:** keep `docs/architecture/` (views + ADRs) current as the deployment and auth model evolve; extend QRTs to cover the new auth flows.

## Later: AI Intelligence & Automation (Future)
*   **Sprint Goal:** Implement deep AI analysis of legal texts and improve user retention.
*   **Focus:** LLM-powered policy auditing and automated remediation recommendations.
*   **Candidate Items:**
    *   [US-11] Automatic AI code remediation suggestions (currently Won't-Have; future candidate)
    *   [Task] Deeper LLM policy auditing across documents (cross-document consistency)

## Continuing Quality & Automation Commitments

The quality gates established in the Assignment 4 Sprint are **maintained project assets**, not one-time submission evidence. All later Sprints must keep them passing or replace them with documented, equivalent-or-stronger coverage:

*   **CI quality gate** ([#71](https://github.com/ValekusVachpekus/pdn-control/issues/71)) — unit + integration tests, coverage on critical modules (≥30% line coverage), an additional QA check (security/dependency scan), and lint/format/type checks run on every PR.
*   **Branch protection** on `main` — required passing CI checks and review before merge.
*   **Quality requirements & QRTs** — defined in `docs/quality-requirements.md` and `docs/quality-requirement-tests.md`; each new quality-relevant change must extend or maintain them.
*   **Definition of Done** — `docs/definition-of-done.md` requires acceptance-criteria verification, review, passing CI, relevant automated tests and QRTs, coverage expectations, preserved testing evidence, and a changelog update for user-visible changes.
*   **User acceptance tests** — `docs/user-acceptance-tests.md` keeps ≥3 active end-user-facing scenarios with execution history.

Later PBIs must extend these gates instead of bypassing or disabling them.
