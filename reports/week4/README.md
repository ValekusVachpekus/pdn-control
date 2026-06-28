# Assignment 4 — ПДн Контроль (Week 4 Report)

**Project Description:** A specialized web service for preliminary **technical** audits of
small and medium business websites against typical **152-ФЗ** ("On Personal Data")
compliance risks. It provides risk-scoring, violation lists, potential fines, and legal
remediation steps. This week focused on **quality automation & release**: explicit quality
requirements, automated quality-requirement tests, CI quality gates, an updated Definition of
Done, user acceptance testing, and the v1.1.0 release.

- **License:** [Root MIT LICENSE](https://github.com/ValekusVachpekus/pdn-control/blob/main/LICENSE)
- **Process Requirements:** [Process_Requirements.md](https://gitlab.pg.innopolis.university/search?search=re&nav_source=navbar&project_id=3315&group_id=5842&search_code=true&repository_ref=main)
- **Issue Templates:** [.github/ISSUE_TEMPLATE](https://github.com/ValekusVachpekus/pdn-control/tree/main/.github/ISSUE_TEMPLATE)
- **Extended PR Template:** [pull_request_template.md](https://github.com/ValekusVachpekus/pdn-control/blob/main/.github/pull_request_template.md)

Index for the Week 4 submission. These are **Course Task artifacts** (reporting/evidence);
the live backlog is maintained in GitHub Issues and the Project Board.

## Sprint Planning (Part 1)

- **Roadmap (Sprint-by-Sprint plan):** [docs/roadmap.md](https://github.com/ValekusVachpekus/pdn-control/blob/main/docs/roadmap.md)
- **Sprint Milestone (Assignment 4):** [Milestone #2 — Quality automation & release](https://github.com/ValekusVachpekus/pdn-control/milestone/2) (due 2026-06-28)
- **Product Backlog Board:** [Project #1](https://github.com/users/ValekusVachpekus/projects/1)
- **Sprint Backlog (Assignment 4, filtered by milestone):** [Project board view](https://github.com/users/ValekusVachpekus/projects/1)
- **Planning PR:** [#87 — sprint planning](https://github.com/ValekusVachpekus/pdn-control/pull/87)

**Sprint Goal:** quality + deploy/release. Technical PBIs in the Sprint:

| PBI | Title | SP | Status |
|---|---|---|---|
| [#71](https://github.com/ValekusVachpekus/pdn-control/issues/71) | CI quality gate: tests, coverage, QA check & branch protection | 8 | Done ([#95](https://github.com/ValekusVachpekus/pdn-control/pull/95)) |
| [#75](https://github.com/ValekusVachpekus/pdn-control/issues/75) | Deterministic GeoIP hosting detection | 5 | Done ([#95](https://github.com/ValekusVachpekus/pdn-control/pull/95)) |
| [#86](https://github.com/ValekusVachpekus/pdn-control/issues/86) | Front via Caddy on 443 + TLS | 3 | Done |
| [#88](https://github.com/ValekusVachpekus/pdn-control/issues/88) | Deploy to customer infra + DNS migration | 5 | Done |

## Quality Requirements & Tests (Parts 3–4)

- **Quality Requirements (ISO/IEC 25010):** [docs/quality-requirements.md](https://github.com/ValekusVachpekus/pdn-control/blob/main/docs/quality-requirements.md)
- **Quality Requirement Tests (QR ↔ test mapping):** [docs/quality-requirement-tests.md](https://github.com/ValekusVachpekus/pdn-control/blob/main/docs/quality-requirement-tests.md)
- **QR/QRT PR:** [#89](https://github.com/ValekusVachpekus/pdn-control/pull/89)

| QR | ISO/IEC 25010 | Automated test | Result |
|---|---|---|---|
| [QR-01](https://github.com/ValekusVachpekus/pdn-control/blob/main/docs/quality-requirements.md#qr-01--crawler-confidentiality-against-ssrf) Security/Confidentiality | anti-SSRF | [crowler/tests/test_ssrf.py](https://github.com/ValekusVachpekus/pdn-control/blob/main/crowler/tests/test_ssrf.py), [test_ssrf_redirect.py](https://github.com/ValekusVachpekus/pdn-control/blob/main/crowler/tests/test_ssrf_redirect.py) | 45 passed |
| [QR-02](https://github.com/ValekusVachpekus/pdn-control/blob/main/docs/quality-requirements.md#qr-02--deterministic-scan-results) Reliability/Maturity | determinism | [backend/tests/test_determinism.py](https://github.com/ValekusVachpekus/pdn-control/blob/main/backend/tests/test_determinism.py) | 3 passed |
| [QR-03](https://github.com/ValekusVachpekus/pdn-control/blob/main/docs/quality-requirements.md#qr-03--correct-fact-to-violation-mapping-rule-engine) Functional suitability/Correctness | rule-engine | [backend/tests/test_violation_catalog.py](https://github.com/ValekusVachpekus/pdn-control/blob/main/backend/tests/test_violation_catalog.py) | 11 passed |

## Definition of Done (Part 6)

- **Updated DoD (now includes quality gates):** [docs/definition-of-done.md](https://github.com/ValekusVachpekus/pdn-control/blob/main/docs/definition-of-done.md)
- **DoD PR:** [#90](https://github.com/ValekusVachpekus/pdn-control/pull/90)
- New gates: all QRTs pass, coverage gate, additional QA check (lint/static), branch
  protection (required reviews + required CI checks). CI enforcement wired in
  [#71](https://github.com/ValekusVachpekus/pdn-control/issues/71).

## Testing, Coverage & CI (Parts 5, 7, 8)

- **CI quality-gate issue:** [#71](https://github.com/ValekusVachpekus/pdn-control/issues/71) — **Done** via PR [#95](https://github.com/ValekusVachpekus/pdn-control/pull/95).
- **CI workflow:** [.github/workflows/ci.yml](https://github.com/ValekusVachpekus/pdn-control/blob/main/.github/workflows/ci.yml) — 7 required jobs (lint, crowler, backend-unit, backend-integration, pdfreport, frontend, security).
- **Testing strategy & coverage gate:** [docs/testing.md](https://github.com/ValekusVachpekus/pdn-control/blob/main/docs/testing.md) + per-module gate [scripts/check_coverage.py](https://github.com/ValekusVachpekus/pdn-control/blob/main/scripts/check_coverage.py) (≥ 30 % on critical modules).
- **Additional QA check (SAST):** Bandit (severity ≥ medium) + pip-audit, in the `security` job — distinct from lint and link-check (full write-up below).
- **Branch protection rules:** enforced on `main` via a GitHub **ruleset** (`assignment2-rules`, active): required status checks **and** a required review by another member, plus deletion / non-fast-forward protection. Direct push to `main` is blocked.

  ![Branch protection rules](images/branch-protection.png)
- Increment PRs this Sprint: [#85](https://github.com/ValekusVachpekus/pdn-control/pull/85),
  [#87](https://github.com/ValekusVachpekus/pdn-control/pull/87),
  [#89](https://github.com/ValekusVachpekus/pdn-control/pull/89),
  [#90](https://github.com/ValekusVachpekus/pdn-control/pull/90),
  [#91](https://github.com/ValekusVachpekus/pdn-control/pull/91),
  [#92](https://github.com/ValekusVachpekus/pdn-control/pull/92),
  [#95](https://github.com/ValekusVachpekus/pdn-control/pull/95) (CI gate + GeoIP).

### Unit & integration tests (Parts 20–21)

**Unit tests:**
- Crawler: [`test_ssrf.py`](https://github.com/ValekusVachpekus/pdn-control/blob/main/crowler/tests/test_ssrf.py), [`test_ssrf_redirect.py`](https://github.com/ValekusVachpekus/pdn-control/blob/main/crowler/tests/test_ssrf_redirect.py), [`test_geoip.py`](https://github.com/ValekusVachpekus/pdn-control/blob/main/crowler/tests/test_geoip.py)
- Rule-engine / backend: [`test_violation_catalog.py`](https://github.com/ValekusVachpekus/pdn-control/blob/main/backend/tests/test_violation_catalog.py), [`test_llm_cache.py`](https://github.com/ValekusVachpekus/pdn-control/blob/main/backend/tests/test_llm_cache.py)
- PDF microservice: [`test_models.py`](https://github.com/ValekusVachpekus/pdn-control/blob/main/PDFreport/tests/test_models.py), [`test_renderer.py`](https://github.com/ValekusVachpekus/pdn-control/blob/main/PDFreport/tests/test_renderer.py)
- Frontend: [`mapReport.test.js`](https://github.com/ValekusVachpekus/pdn-control/blob/main/frontend/test/mapReport.test.js), [`smoke.test.jsx`](https://github.com/ValekusVachpekus/pdn-control/blob/main/frontend/test/smoke.test.jsx)

**Integration tests:**
- Backend pipeline (parser → rule-engine → report): [`test_integration_pipeline.py`](https://github.com/ValekusVachpekus/pdn-control/blob/main/backend/tests/test_integration_pipeline.py), [`test_determinism.py`](https://github.com/ValekusVachpekus/pdn-control/blob/main/backend/tests/test_determinism.py)
- Backend API e2e (register/login/scan/report/billing): [`test_e2e.py`](https://github.com/ValekusVachpekus/pdn-control/blob/main/backend/tests/test_e2e.py)
- PDF microservice API: [`test_api.py`](https://github.com/ValekusVachpekus/pdn-control/blob/main/PDFreport/tests/test_api.py)

### Per-module coverage status (Part 19)

Critical modules each gate at **≥ 30 %** line coverage (per-module, enforced by
[`scripts/check_coverage.py`](https://github.com/ValekusVachpekus/pdn-control/blob/main/scripts/check_coverage.py); a renamed/missing module fails the gate so coverage cannot silently disappear). The gate passes on the latest `main` CI run.

| Critical module | Threshold | Current |
|---|---|---|
| `crowler/pdn_parser/ssrf.py` | 30 % | ~81 % |
| `crowler/pdn_parser/geoip.py` | 30 % | ~84 % |
| `backend/app/services/violation_catalog.py` | 30 % | ~73 % |
| `backend/app/services/llm_cache.py` | 30 % | ~62 % |

### Additional QA check — SAST + dependency audit (Part 7.3)

- **Options considered:** SAST of our own code (Bandit), dependency vulnerability audit (pip-audit), secret scanning, and container image scanning.
- **Selected:** **Bandit** (SAST, mandatory gate) + **pip-audit** (dependency audit, advisory), running in the dedicated `security` CI job — deliberately distinct from lint, formatting, type-check, build, unit/integration tests, coverage, the automated QRTs, and the Lychee link-check.
- **QA objective / risk:** catch insecure code patterns (e.g. XXE in untrusted XML, unsafe subprocess/network calls) and known-vulnerable dependencies before they reach `main`.
- **Why it matters here:** the crawler fetches and parses **untrusted third-party content** (external `sitemap.xml`, pages) server-side — exactly the surface where SSRF/XXE-class issues are dangerous. Hardening already done under this gate: untrusted XML is parsed via `defusedxml`; the intentional `0.0.0.0` container bind is annotated `# nosec B104`.
- **Where it runs:** `security` job in [`.github/workflows/ci.yml`](https://github.com/ValekusVachpekus/pdn-control/blob/main/.github/workflows/ci.yml), on every PR and push to `main`; Bandit fails the build on findings of severity ≥ medium.
- **Limitations / deferred:** pip-audit is advisory (`continue-on-error`) so upstream transitive CVEs do not block feature merges but stay visible in the log; `ruff format --check` and `mypy` are not yet mandatory gates (tracked separately). Details: [`docs/testing.md`](https://github.com/ValekusVachpekus/pdn-control/blob/main/docs/testing.md).

## User Acceptance Tests (Part 10)

- **UAT scenarios (5, customer-accepted):** [docs/user-acceptance-tests.md](https://github.com/ValekusVachpekus/pdn-control/blob/main/docs/user-acceptance-tests.md)
- **UAT PR:** [#91](https://github.com/ValekusVachpekus/pdn-control/pull/91)
- Covers: basic scan ([US-01 #58](https://github.com/ValekusVachpekus/pdn-control/issues/58)),
  total fine ([US-02 #59](https://github.com/ValekusVachpekus/pdn-control/issues/59)),
  free/paid gating ([US-05 #62](https://github.com/ValekusVachpekus/pdn-control/issues/62) /
  [US-06 #63](https://github.com/ValekusVachpekus/pdn-control/issues/63)),
  PDF report ([US-08 #65](https://github.com/ValekusVachpekus/pdn-control/issues/65)),
  anti-SSRF ([US-12 #69](https://github.com/ValekusVachpekus/pdn-control/issues/69)).

### UAT execution at the Sprint Review (2026-06-27)

The customer re-executed all five scenarios live against the deployment on **their own
infrastructure** (v1.1.0). **Result: 5 / 5 Pass** — basic scan, total fine, free/paid gating,
PDF download, and anti-SSRF all passed. No scenario failed. Six **minor UI defects** were spotted
during execution; they did not block any scenario and are tracked as the customer-feedback items
below. Full results: [customer-review-summary.md](customer-review-summary.md).

## Customer Feedback Response (Part 2)

Source of feedback: the **Sprint Review with the customer on 2026-06-21** (see
[`reports/week3/customer-review-summary.md`](../week3/customer-review-summary.md) and
[`reports/week3/customer-review-transcript.md`](../week3/customer-review-transcript.md)).
The customer approved the MVP v1 scope and increment, requested one UI change, and decided to
host the service on their own infrastructure.

| Feedback point | Resulting PBI or issue | Status | Response |
|---|---|---|---|
| The "Total Fine" amount should be displayed more prominently as a risk score for business owners. | [#78](https://github.com/ValekusVachpekus/pdn-control/issues/78) | Done | Increased the contrast, font size, and visual weight of the fine amount in the report view so it stands out from the rest of the data. |
| Audit results were non-deterministic (different data for the same site). | [#34](https://github.com/ValekusVachpekus/pdn-control/issues/34) | Done | Canonicalized the crawl JSON (stripped volatile fields) so repeated scans of the same URL yield the same report. |
| Security flaw: full report data was accessible for free via browser "Inspect Element" (blur bypass). | [#54](https://github.com/ValekusVachpekus/pdn-control/issues/54) | Done | Moved data-gating to the API; premium data is not sent to the frontend until payment is confirmed (the blur is now only UX). |
| Security risk: the parser could be pointed at internal APIs (SSRF). | [#69](https://github.com/ValekusVachpekus/pdn-control/issues/69) (US-12, PR [#57](https://github.com/ValekusVachpekus/pdn-control/pull/57)) | Done | Added strict server-side URL validation so the crawler cannot reach internal or private IP ranges, including via redirects. |
| Request for scan-completion notifications (US-13), pulled into the Sprint as a Could-Have. | [#70](https://github.com/ValekusVachpekus/pdn-control/issues/70) | In Progress | Pulled into the Sprint with the customer's approval; implementation is ongoing and the issue is still open (not yet Done). |
| The customer will host the service on their own infrastructure and redirect their domain's DNS. | [#88](https://github.com/ValekusVachpekus/pdn-control/issues/88) | Done | New PBI to prepare deployment config/instructions for the customer's host and assist with DNS migration; builds on the TLS/Caddy deploy ([#86](https://github.com/ValekusVachpekus/pdn-control/issues/86), Done). |

### Feedback not addressed this Sprint

No customer feedback was rejected. Every explicit point from the Sprint Review is tracked
above. Two points are intentionally **not fully closed in the Assignment 4 Sprint**:

- **US-13 scan-finished notification ([#70](https://github.com/ValekusVachpekus/pdn-control/issues/70))** — kept In Progress because the Sprint prioritized quality automation, CI gates, and deployment over new features; it carries into the next Sprint.
- **DNS redirect ([#88](https://github.com/ValekusVachpekus/pdn-control/issues/88))** — the DNS change itself is a **customer-side action**. The team provides the deployment configuration and assistance; the cut-over depends on the customer redirecting their domain.

### New feedback from the Week 4 Sprint Review / UAT (2026-06-27)

Six items raised by the customer during live UAT on the production deployment. All accepted for
the next Sprint (issues to be filed); none were rejected.

| Feedback point | Resulting PBI or issue | Status | Response |
|---|---|---|---|
| Starting a check while logged out is blocked, but the loading screen still opens. | [#99](https://github.com/ValekusVachpekus/pdn-control/issues/99) | Planned (next Sprint) | Stop the loading screen from showing on an unauthenticated check; route the user to registration. |
| From the empty history screen there is no obvious way back to the main page ("New check" not discoverable). | [#100](https://github.com/ValekusVachpekus/pdn-control/issues/100) | Planned (next Sprint) | Make the "New check" / back-to-main action more prominent and intuitive on the empty-history state. |
| A useless "0" fine is shown when owner-side personal-data checks cannot be assessed. | [#101](https://github.com/ValekusVachpekus/pdn-control/issues/101) | Planned (next Sprint) | Hide the `0` value where the check is not applicable instead of rendering a misleading zero. |
| "Data collection points" looks empty when the forms are on the main page. | [#102](https://github.com/ValekusVachpekus/pdn-control/issues/102) | Planned (next Sprint) | Label the location (e.g. "Main page") so found forms are not shown as empty. |
| The cookie-banner violation is addressed to the Marketer; it should go to the Developer. | [#103](https://github.com/ValekusVachpekus/pdn-control/issues/103) | Planned (next Sprint) | Change the violation's `target_role` for the cookie-banner rule from `marketer` to `developer`. |
| Use a third-party email provider instead of a local SMTP server on the customer's machine. | [#104](https://github.com/ValekusVachpekus/pdn-control/issues/104) | Planned (next Sprint) | Integrate a third-party email provider; the team sends the customer the records to add on their side. |

## Release & Deployment (Part 9)

- **Previous SemVer Release:** [v1.0.0 — MVP v1](https://github.com/ValekusVachpekus/pdn-control/releases/tag/v1.0.0)
- **New SemVer Release (this Sprint):** [v1.1.0](https://github.com/ValekusVachpekus/pdn-control/releases/tag/v1.1.0) (maps to Sprint milestone [#2](https://github.com/ValekusVachpekus/pdn-control/milestone/2))
- **Live Deployment (customer/own infra):** [Deployment](https://pdn.neurolife.tech/)
- **Access & Run Instructions:** [Root README.md](https://github.com/ValekusVachpekus/pdn-control/blob/main/README.md)
- **CHANGELOG:** [CHANGELOG.md](https://github.com/ValekusVachpekus/pdn-control/blob/main/CHANGELOG.md)

## Sprint Review, Retrospective & Reflection (Parts 11–13)

The Sprint Review on **2026-06-27** was one recorded session that also covered the
customer-executed UAT (see *User Acceptance Tests* above). The customer accepted the increment
and confirmed the Sprint Goal was met. Transcript publication reuses the consent obtained at the
Week 3 review; exact UAT/Review timecodes are in the private Moodle submission.

- **Customer Review Summary:** [customer-review-summary.md](customer-review-summary.md)
- **Customer Review Transcript (public):** [customer-review-transcript.md](customer-review-transcript.md)
- **Retrospective:** [retrospective.md](retrospective.md)
- **Reflection:** [reflection.md](reflection.md)

## Presentation & Demo (Parts 14–15)

- **Presentation slides:** [Presentation (Google Drive)](https://drive.google.com/file/d/1ALPHK_sTbJmkOFq6Nh6AtnRGcsEMzOAl/view?usp=drive_link)
- **Video Demonstration (< 2 min):** [Demo video (Google Drive)](https://drive.google.com/file/d/1_ep2iFhQ_XVV5VsKl6w4WUhFH_F__X5i/view) — also linked from release [v1.1.0](https://github.com/ValekusVachpekus/pdn-control/releases/tag/v1.1.0).

## LLM Usage (Part 16)

- **LLM Usage Report:** [llm-report.md](llm-report.md)
- **LLM Report PR:** [#92](https://github.com/ValekusVachpekus/pdn-control/pull/92)

## Quality gates going forward (Part 27)

The Assignment 4 tests, CI checks, quality requirement tests, and Definition of Done are
**maintained project assets, not one-time submission evidence**. They keep governing later work:

- The 7 required CI jobs and the `main` ruleset stay enforced — every future PR must pass them
  and be reviewed by another member before merge.
- The automated QRTs (anti-SSRF, determinism, rule-engine correctness) and the per-module
  coverage gate (≥ 30 % on critical modules) remain blocking; a renamed/missing critical module
  fails the gate by design.
- The updated [Definition of Done](https://github.com/ValekusVachpekus/pdn-control/blob/main/docs/definition-of-done.md)
  requires these gates for any PBI to be `Done`. Later PBIs (including the six follow-ups
  [#99–#104](https://github.com/ValekusVachpekus/pdn-control/issues/99)) must **maintain or extend**
  these gates — not bypass or disable them. If the stack, critical modules, or CI change, the QRs,
  tests, and DoD are updated rather than left stale.

## Current product status (Part 38)

- **Released:** [v1.1.0](https://github.com/ValekusVachpekus/pdn-control/releases/tag/v1.1.0),
  deployed and internet-accessible on the **customer's own infrastructure**
  ([pdn.neurolife.tech](https://pdn.neurolife.tech/)).
- **Accepted:** the customer ran all five UAT scenarios live (5 / 5 Pass) and accepted the
  Sprint increment; the Sprint Goal (quality automation + deployment on their infrastructure) was met.
- **Quality:** CI quality gate green on `main`, branch protection active, QRs covered by automated
  QRTs, critical modules above the coverage threshold.
- **Known gaps:** six minor UI/UX and one infra (email) follow-up from UAT are filed
  ([#99–#104](https://github.com/ValekusVachpekus/pdn-control/issues/99)) for the next Sprint;
  US-13 scan-finished notification ([#70](https://github.com/ValekusVachpekus/pdn-control/issues/70))
  is carried over.

## Next steps (Part 39)

- Address the six UAT follow-ups ([#99–#104](https://github.com/ValekusVachpekus/pdn-control/issues/99)):
  fix the UI defects and integrate a third-party email provider.
- Close the front-end UI-testing gap (UI smoke check / pre-demo dry-run) agreed in the
  [retrospective](retrospective.md), so presentation defects are caught before UAT.
- Continue US-13 ([#70](https://github.com/ValekusVachpekus/pdn-control/issues/70)) and the next-Sprint
  roadmap items: social login (Yandex/VK OAuth), CloudPayments, broader JS/SPA crawl coverage
  (see [docs/roadmap.md](https://github.com/ValekusVachpekus/pdn-control/blob/main/docs/roadmap.md)).

## Authoritative Live Sources

- **Sprint Milestone (Assignment 4):** [milestone/2](https://github.com/ValekusVachpekus/pdn-control/milestone/2)
- **Sprint 1 Milestone:** [milestone/1](https://github.com/ValekusVachpekus/pdn-control/milestone/1)
- **Product Backlog Board:** [projects/1](https://github.com/users/ValekusVachpekus/projects/1)
- **User Story Index:** [docs/user-stories.md](https://github.com/ValekusVachpekus/pdn-control/blob/main/docs/user-stories.md)
- **Backlog Summary & Rationale (Week 3):** [reports/week3/backlog.md](https://github.com/ValekusVachpekus/pdn-control/blob/main/reports/week3/backlog.md)

## Contribution Traceability

| Member (GitHub) | Issues Assigned / Created | PRs Created | Review Activity |
|---|---|---|---|
| Ilia Shchetkov (`ValekusVachpekus`) | Created [#88](https://github.com/ValekusVachpekus/pdn-control/issues/88) | [#87](https://github.com/ValekusVachpekus/pdn-control/pull/87), [#89](https://github.com/ValekusVachpekus/pdn-control/pull/89), [#90](https://github.com/ValekusVachpekus/pdn-control/pull/90), [#91](https://github.com/ValekusVachpekus/pdn-control/pull/91), [#92](https://github.com/ValekusVachpekus/pdn-control/pull/92), [#93](https://github.com/ValekusVachpekus/pdn-control/pull/93) | Approved [#85](https://github.com/ValekusVachpekus/pdn-control/pull/85) |
| Ksenya Koroleva (`kskorqueen`) | — | [#85](https://github.com/ValekusVachpekus/pdn-control/pull/85) | Approved [#87](https://github.com/ValekusVachpekus/pdn-control/pull/87), [#89](https://github.com/ValekusVachpekus/pdn-control/pull/89), [#90](https://github.com/ValekusVachpekus/pdn-control/pull/90), [#91](https://github.com/ValekusVachpekus/pdn-control/pull/91), [#92](https://github.com/ValekusVachpekus/pdn-control/pull/92) |
| Airat Mingazov (`azenlrd`) | Assigned [#71](https://github.com/ValekusVachpekus/pdn-control/issues/71), [#75](https://github.com/ValekusVachpekus/pdn-control/issues/75), [#86](https://github.com/ValekusVachpekus/pdn-control/issues/86) | [#95](https://github.com/ValekusVachpekus/pdn-control/pull/95) (CI gate + GeoIP) | — |
| Aleksandr Martiushev (`alexzhal1`) | Assigned [#70](https://github.com/ValekusVachpekus/pdn-control/issues/70); created [#75](https://github.com/ValekusVachpekus/pdn-control/issues/75) | — | — |
| Maksim Shakhrai (`ShakhraiMaksim`) | operated the recording of the Sprint Review / UAT session (2026-06-27) | — | — |

> Source: GitHub issue assignees/authors and PR reviews on the Assignment 4 Sprint
> (milestone [#2](https://github.com/ValekusVachpekus/pdn-control/milestone/2)). The CI gate
> ([#71](https://github.com/ValekusVachpekus/pdn-control/issues/71)) and deterministic GeoIP
> ([#75](https://github.com/ValekusVachpekus/pdn-control/issues/75)) were delivered together in
> PR [#95](https://github.com/ValekusVachpekus/pdn-control/pull/95) — all Sprint technical PBIs
> are now Done.

## Screenshots

Sprint Backlog:

![Sprint Backlog](images/sprint-backlog-1.png)
![Sprint Backlog (filtered by milestone)](images/sprint-backlog-2.png)

Sprint Milestone:

![Sprint Milestone](images/sprint-milestone.png)

Branch Protection:

![Branch protection rules](images/branch-protection.png)

CI quality gate (green):

![CI quality gate green](images/ci.png)

SemVer Release (v1.1.0):

![Release v1.1.0](images/release.png)
