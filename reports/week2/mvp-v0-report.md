# MVP v0 Report — Week 2 (ПДн Контроль)

> MVP v0 is the runnable technical product foundation, evaluated by the TA. It does not
> need to implement a complete user story or reproduce the prototype — it must be
> accessible, runnable, and pass a smoke check.

## Purpose and description

MVP v0 is the end-to-end runnable foundation of **ПДн Контроль**: a React/Vite frontend, a
FastAPI backend with a Playwright-based crawler, an LLM-driven analysis pipeline, and a
Typst-based PDF report generator, wired together behind nginx. Entering a website URL
triggers a scan: the crawler collects facts about the site (forms, cookies, trackers,
policy documents), the backend assigns each detected violation a severity/article/fine
from a deterministic catalog, and the frontend renders the result as a compliance report
with a risk score, total potential fine, and a prioritized list of violations.

## Deployment URL / runnable-artifact link

- **Deployment URL:** http://10.93.26.163:8080/
- **Hosting:** university VM. Accessible from the **Innopolis University network**, where
  the TA can reach it for grading. (A public VPS is not required for Assignment 2; external
  access for the customer's own testing is tracked as a separate product follow-up.)
- **Runnable fallback:** if the VM is unreachable, the product can also be run locally via
  the root README — see [Local setup instructions](#local-setup-instructions) below.

## Public video demonstration

- Video link: [MVP v0 demo (Google Drive, view-only)](https://drive.google.com/file/d/1_ep2iFhQ_XVV5VsKl6w4WUhFH_F__X5i/view?usp=drive_link)

## Relationship to the prototype and proposed MVP v1 stories

- **US-01 (Basic website scan):** implemented end-to-end — the Home screen accepts a URL
  and triggers a real scan through the crawler/backend pipeline.
- **US-02 (Total potential fine display):** implemented — the report screen shows the
  total potential fine (e.g. "до 120 000 ₽") computed from the deterministic violation
  catalog.
- **US-03 (Detailed list of violations):** implemented — the report lists violations
  grouped by severity (critical/warning/info/passed) with human-readable titles.
- **US-04 (Legal article references):** implemented — each violation is tagged with the
  relevant 152-FZ article and KoAP RF fine reference.
- **US-07 (Compliance score):** implemented ahead of schedule — the report shows a 0–100
  risk score alongside the fine, matching the Week 2 customer request to raise it to
  Must Have.
- **US-05 (Free tier limited check):** implemented — the report screen shows a paid/free
  state (e.g. an "Отчёт оплачен" / "report paid" badge); enforcement is currently
  front-end only (see Limitations below).
- **US-08 (PDF Report Download):** implemented — the report screen has a working
  "Скачать PDF" action that generates the report via the PDF microservice.
- **Prototype screens:** the deployed report screen corresponds to the Figma "Report"
  screen referenced in [README.md § Prototype Coverage](README.md#2-prototype-and-interface-artifacts).

## Current limitations, placeholders, and mocks

- The crawler currently scans only the pages it can reach without authentication; some
  violation types (e.g. multi-page/JS-heavy crawling, US-09) are not yet detected on
  every site.
- Email registration is blocked in this environment without a configured SMTP domain.
- The `paid`/`free` tier gating (US-05/US-06) is front-end-only — there is no server-side
  enforcement yet.
- OAuth login providers are stubs (UI present, not wired to real providers).
- Legal texts (privacy policy / terms of service) shown in the app are placeholders, not
  final legal content.

## Local setup instructions

Local setup and run commands live in the root README:
[README.md → "Локальный запуск"](../../README.md#локальный-запуск).

## Repeatable smoke-check scenario

> Web/mobile smoke check: the application opens, primary navigation works, and at least
> one interactive data-flow element is demonstrated (form submission, API call, or state
> change).

**Access instructions:**
Open http://10.93.26.163:8080/ from the Innopolis University network. No login or test
credentials are required to run a scan.

**Steps:**

1. Open <http://10.93.26.163:8080/> in a browser. The "Новая проверка" (New scan) screen
   loads.
2. Enter a website URL (e.g. `neurolife.tech`) into the scan input and start the scan.
3. Wait for the scan to complete and observe the report screen render.

**Expected result:**
The app navigates to the report screen showing a 0–100 risk score, a total potential fine
(e.g. "до 120 000 ₽"), counts of critical/warning/info/passed checks, and an AI-generated
conclusion referencing the audited domain and date — as in
[images/mvp-v0-deployed.png](images/mvp-v0-deployed.png).
