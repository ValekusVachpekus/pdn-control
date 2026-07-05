# User Acceptance Tests (UAT) — ПДн Контроль

User Acceptance Testing verifies, **from the customer's point of view**, that MVP v1 meets
the agreed business acceptance criteria of the relevant user stories. Unlike the automated
[quality requirement tests](./quality-requirement-tests.md) (which check internal quality
attributes), UAT confirms the product is **fit for purpose** for the end user.

- **Product:** ПДн Контроль — technical 152-ФЗ pre-audit service (MVP v1).
- **Acceptor:** the **customer** (product stakeholder), who reviewed and accepted MVP v1 at
  the **Sprint Review on 2026-06-21**
  (see [`reports/week3/customer-review-summary.md`](../reports/week3/customer-review-summary.md)).
- **Build under test:** MVP v1 (full stack via `cd backend && docker compose up`; crawler on
  :8010, PDF microservice on :8020, frontend served by nginx).
- **Overall result:** **5 / 5 Pass** — customer accepted MVP v1.

> **MVP v2 (Sprint 5):** new scenarios for the `MVP v2` increment are maintained in their own
> section, [**MVP v2 (Sprint 5) — new scenarios**](#mvp-v2-sprint-5--new-scenarios), below.
> They were **executed with the customer at the Sprint 5 Review on 2026-07-04 (recorded session)**
> and **passed 2 / 2**; the customer accepted the MVP v2 increment.

### Execution history

| Session date | Build / environment | Acceptor | Result |
|---|---|---|---|
| 2026-06-21 | MVP v1 on the university VM (Sprint Review walkthrough) | Customer | 5 / 5 Pass |
| 2026-06-27 | v1.1.0 on the **customer's own infrastructure** (`pdn.neurolife.tech`), re-run during the Sprint 2 Review | Customer | 5 / 5 Pass |
| 2026-07-04 | `MVP v2` (`v1.2.0`) on `pdn.neurolife.tech`, new scenarios during the Sprint 5 Review (recorded) | Customer | 2 / 2 Pass (UAT-06/07) |

> **2026-06-27 re-run (Sprint 2):** all five scenarios were re-executed by the customer against
> the live deployment on their own infrastructure and passed again
> (see [`reports/week4/customer-review-summary.md`](../reports/week4/customer-review-summary.md)).
> No scenario failed; six **minor UI defects** observed during execution were logged as new
> backlog items and did not block any scenario from passing.
>
> **2026-07-04 (Sprint 5):** the two new MVP v2 scenarios (UAT-06/07), covering the Week 4 UAT
> feedback fixes, were executed by the customer against the live `MVP v2` deployment and passed
> 2 / 2. The customer accepted the MVP v2 increment; no scenario failed. The session was recorded.

Each scenario is written in the standard UAT form: a business goal, the user story and its
acceptance criteria, preconditions, steps, expected result, the observed actual result, and
the **Pass/Fail** verdict.

## Summary

| UAT | User story | Feature | Acceptor | Result |
|---|---|---|---|---|
| [UAT-01](#uat-01--basic-website-scan-produces-a-report) | [US-01](https://github.com/ValekusVachpekus/pdn-control/issues/58) | Basic scan → report | Customer | ✅ Pass |
| [UAT-02](#uat-02--total-potential-fine-is-shown-prominently) | [US-02](https://github.com/ValekusVachpekus/pdn-control/issues/59) | Total potential fine | Customer | ✅ Pass |
| [UAT-03](#uat-03--free-tier-is-limited-paid-tier-unlocks-the-full-report) | [US-05](https://github.com/ValekusVachpekus/pdn-control/issues/62) / [US-06](https://github.com/ValekusVachpekus/pdn-control/issues/63) | Free vs paid gating | Customer | ✅ Pass |
| [UAT-04](#uat-04--full-report-can-be-downloaded-as-pdf) | [US-08](https://github.com/ValekusVachpekus/pdn-control/issues/65) | PDF report download | Customer | ✅ Pass |
| [UAT-05](#uat-05--internal--private-urls-are-refused-anti-ssrf) | [US-12](https://github.com/ValekusVachpekus/pdn-control/issues/69) | Anti-SSRF refusal | Customer | ✅ Pass |

---

## UAT-01 — Basic website scan produces a report

- **User story:** [US-01 — Basic website scan](https://github.com/ValekusVachpekus/pdn-control/issues/58) (Must Have)
- **Business goal:** A small-business owner enters a website URL and receives a 152-ФЗ risk report.

| Field | Value |
|---|---|
| Acceptance criteria | Given a valid public URL, when the user starts a check, the service crawls public pages and returns a report containing a risk score and a list of violations. |
| Preconditions | Stack is running; user is on the landing page; a reachable public test site is available. |
| Steps | 1. Enter a valid public URL in the landing input. 2. Click **«Проверить»**. 3. Wait for the scan to finish (status `done`). 4. Open the report. |
| Expected result | The scan completes with `status=done`; the report screen shows a compliance score (0–100), a risk level, and a list of detected violations with 152-ФЗ article references. |
| **Actual result** | As expected — scan reached `done`, report rendered with score, risk level, and the violations list. |
| **Verdict** | ✅ **Pass** |

---

## UAT-02 — Total potential fine is shown prominently

- **User story:** [US-02 — Total potential fine display](https://github.com/ValekusVachpekus/pdn-control/issues/59) (Must Have)
- **Business goal:** The owner immediately sees the total potential monetary risk (₽), which the customer explicitly asked to be made prominent at the Sprint Review.

| Field | Value |
|---|---|
| Acceptance criteria | The report displays a **total potential fine in rubles**, aggregated from the individual violations' fines. |
| Preconditions | A completed scan of a site with at least one fineable violation (UAT-01 passed). |
| Steps | 1. Open the report from UAT-01. 2. Locate the total potential fine. 3. Cross-check it against the sum of per-violation `fine_rub`. |
| Expected result | A clearly visible total potential fine (₽) is shown near the top of the report; it equals the sum of the per-violation fines. |
| **Actual result** | As expected — total fine shown prominently and consistent with the per-violation sum. Customer confirmed this addressed their Sprint Review request. |
| **Verdict** | ✅ **Pass** |

---

## UAT-03 — Free tier is limited, paid tier unlocks the full report

- **User stories:** [US-05 — Free tier limited check](https://github.com/ValekusVachpekus/pdn-control/issues/62) / [US-06 — Paid tier full analysis](https://github.com/ValekusVachpekus/pdn-control/issues/63) (Must Have)
- **Business goal:** Free users get a teaser; paying users get the full audit (per-report payment).

| Field | Value |
|---|---|
| Acceptance criteria | On the free tier the premium sections (infrastructure, full violations, passed checks, technical appendix, PDF) are blocked behind an unlock overlay; only score, counts, and a short verdict are visible. After payment of a report, the full report is unlocked. |
| Preconditions | A completed scan; user not yet paid for this report. |
| Steps | 1. Open the report on the free tier. 2. Confirm premium blocks are blurred behind «Разблокировать отчёт». 3. Complete payment for the report. 4. Re-open the report. |
| Expected result | Before payment only the score, counts, and short verdict are visible; premium blocks are blurred. After payment the full report (infrastructure, violations, passed checks, appendix, PDF) is unlocked. |
| **Actual result** | As expected — free view limited to score/counts/verdict; after a successful report purchase the premium sections unlocked. |
| **Verdict** | ✅ **Pass** |
| Note | Server-side enforcement of the paid flag is tracked as a hardening item (the unlock must be authoritative on the backend, not the front-end `paid` flag). UAT validates the user-visible behaviour. |

---

## UAT-04 — Full report can be downloaded as PDF

- **User story:** [US-08 — PDF report download](https://github.com/ValekusVachpekus/pdn-control/issues/65) (Should Have)
- **Business goal:** The owner can save / forward a professional PDF audit (for a lawyer, developer, or marketer).

| Field | Value |
|---|---|
| Acceptance criteria | From an unlocked (paid) report the user can download a PDF that contains the score, violations with article references and recommendations, passed checks, and the technical appendix. |
| Preconditions | A paid/unlocked report (UAT-03 passed); PDF microservice running on :8020. |
| Steps | 1. Open an unlocked report. 2. Trigger the PDF download. 3. Open the generated PDF. |
| Expected result | A PDF is produced from the same report JSON (Contract №2) showing scoring, violations (with 152-ФЗ articles, recommendations, fines), passed checks, and the technical appendix (trackers, forms, AI notes). |
| **Actual result** | As expected — PDF generated and contained the scoring, violations, passed checks, and technical appendix consistent with the on-screen report. |
| **Verdict** | ✅ **Pass** |

---

## UAT-05 — Internal / private URLs are refused (anti-SSRF)

- **User story:** [US-12 — Server-side URL validation / anti-SSRF](https://github.com/ValekusVachpekus/pdn-control/issues/69) (Must Have)
- **Business goal:** A submitted URL pointing at internal infrastructure (e.g. cloud metadata) must not be fetched — raised directly by the customer at the Sprint Review.

| Field | Value |
|---|---|
| Acceptance criteria | A scan request whose target resolves to (or redirects to) a private/loopback/link-local/reserved address is refused; the crawler makes no outbound request to that address. |
| Preconditions | Stack is running. |
| Steps | 1. Submit a URL targeting a non-public address (e.g. `http://127.0.0.1`, `http://169.254.169.254`, `http://10.0.0.1`). 2. Submit a URL that redirects to such an address. 3. Observe the service response. |
| Expected result | Each non-public target (direct or via redirect) is refused with no outbound connection to the protected address; the user sees a clear refusal rather than a report. |
| **Actual result** | As expected — direct and redirect-based private targets were refused. Backed by the automated SSRF corpus ([QRT-01](./quality-requirement-tests.md#qrt-01), `crowler/tests/test_ssrf*.py`, 45 passing). |
| **Verdict** | ✅ **Pass** |

---

## MVP v2 (Sprint 5) — new scenarios

These scenarios cover **new or changed user-facing behaviour delivered in `MVP v2`**
(Sprint 5). They were added for the **Week 4 customer-UAT feedback fixes** raised during the
2026-06-27 session
([#99](https://github.com/ValekusVachpekus/pdn-control/issues/99),
[#100](https://github.com/ValekusVachpekus/pdn-control/issues/100),
[#101](https://github.com/ValekusVachpekus/pdn-control/issues/101),
[#102](https://github.com/ValekusVachpekus/pdn-control/issues/102); source:
[`reports/week4/customer-review-summary.md`](../reports/week4/customer-review-summary.md)).

- **Build under test:** `MVP v2` (`v1.2.0`) on the customer's own infrastructure
  (`pdn.neurolife.tech`), after the Sprint 5 deploy.
- **Status:** ✅ **Executed 2026-07-04 — 2 / 2 Pass.** Run with the customer at the **Sprint 5
  Review (recorded session)**; the customer accepted the MVP v2 increment.

| UAT | Source issue | Feature | Acceptor | Result |
|---|---|---|---|---|
| [UAT-06](#uat-06--logged-out-check-routes-to-sign-in-without-a-loading-screen) | [#99](https://github.com/ValekusVachpekus/pdn-control/issues/99) | Logged-out check → sign-in, no loading screen | Customer | ✅ Pass |
| [UAT-07](#uat-07--report-and-history-ui-clarity-fixes) | [#100](https://github.com/ValekusVachpekus/pdn-control/issues/100), [#101](https://github.com/ValekusVachpekus/pdn-control/issues/101), [#102](https://github.com/ValekusVachpekus/pdn-control/issues/102) | Report and history UI clarity | Customer | ✅ Pass |

---

## UAT-06 — Logged-out check routes to sign-in without a loading screen

- **Source:** bug [#99 — loading screen opens on a logged-out check](https://github.com/ValekusVachpekus/pdn-control/issues/99) (Must Have), from the 2026-06-27 customer UAT.
- **Business goal:** A visitor who is not signed in must not be dropped onto a dead "loading" screen; they should be guided to register / sign in.

| Field | Value |
|---|---|
| Acceptance criteria | Given a **logged-out** user, when they start a check, the loading/scanning screen is **not** shown, and the user is routed to registration/login (a clear path to authenticate). |
| Preconditions | `MVP v2` (`v1.2.0`) live on `pdn.neurolife.tech`; user is **logged out**. |
| Steps | 1. Open the site while logged out. 2. Enter a valid public URL in the landing input. 3. Click **«Проверить»**. |
| Expected result | No scanning/loading screen appears; instead the registration/login prompt is shown, giving the user a clear path to authenticate before any check runs. |
| **Actual result** | As expected — the logged-out check no longer opened a loading screen; the user was routed to the sign-in/registration prompt. Executed by the customer at the Sprint 5 Review (recorded, 2026-07-04). |
| **Verdict** | ✅ **Pass** |

---

## UAT-07 — Report and history UI clarity fixes

- **Source:** bugs/tasks [#100](https://github.com/ValekusVachpekus/pdn-control/issues/100), [#101](https://github.com/ValekusVachpekus/pdn-control/issues/101), [#102](https://github.com/ValekusVachpekus/pdn-control/issues/102) (Should Have), from the 2026-06-27 customer UAT.
- **Business goal:** The report and the history must not look empty or show misleading values — three specific clarity defects the customer raised during live testing.

| Field | Value |
|---|---|
| Acceptance criteria | (a) **#100** — on an empty history screen, a prominent **"Новая проверка"** action returns the user to the main page; (b) **#101** — no misleading **"0"** fine is shown for a check that cannot be assessed (the value is hidden, not rendered as zero); (c) **#102** — found forms in **"Точки сбора ПДн"** show their **location** (e.g. «Главная страница» or the page path) and the block is not empty. |
| Preconditions | `MVP v2` (`v1.2.0`) live; a registered, signed-in account; for (a) a fresh/empty history; for (b)/(c) a completed scan of a site that has a form on the **main page** and at least one non-applicable (non-fineable) check. |
| Steps | 1. With an empty history, open **«История»** → confirm the prominent **«Новая проверка»** action and that it returns to the main page. 2. Run a scan of a site with a main-page form. 3. Open the report → confirm no stray **"0"** fine appears for non-applicable checks. 4. Open the technical appendix → confirm **«Точки сбора ПДн»** lists the found form with its location. |
| Expected result | (a) the empty-history "Новая проверка" action is obvious and navigates to the main page; (b) non-applicable checks show no "0" fine; (c) each found form shows a non-empty location label. |
| **Actual result** | As expected on all three — (a) the empty-history «Новая проверка» action was obvious and returned to the main page; (b) no stray «0» fine appeared for non-applicable checks; (c) each found form showed its location in «Точки сбора ПДн». Executed by the customer at the Sprint 5 Review (recorded, 2026-07-04). |
| **Verdict** | ✅ **Pass** |

---

## Sign-off

- **Decision (MVP v1):** MVP v1 **accepted** by the customer at the Sprint Review on 2026-06-21, with
  the follow-up items recorded as new backlog entries (e.g. server-side paid-gate hardening,
  deploy to customer infrastructure / DNS migration — [#88](https://github.com/ValekusVachpekus/pdn-control/issues/88)).
- **Decision (MVP v2):** `MVP v2` (`v1.2.0`) **accepted** by the customer at the Sprint 5 Review on
  2026-07-04 (recorded); UAT-06/07 passed 2 / 2. The customer's only follow-up request was to bring
  social login ([#72](https://github.com/ValekusVachpekus/pdn-control/issues/72)) and domain e-mail
  ([#104](https://github.com/ValekusVachpekus/pdn-control/issues/104)) fully live by providing the
  OAuth `client_id`/`secret` and the SPF/DKIM DNS records — carried into the next Sprint.
- **Traceability:** customer feedback source —
  [`reports/week3/customer-review-summary.md`](../reports/week3/customer-review-summary.md);
  acceptance criteria — the linked user-story issues; internal quality evidence —
  [`docs/quality-requirement-tests.md`](./quality-requirement-tests.md).

## Maintenance

- UAT scenarios are re-run (or re-confirmed) at each Sprint Review against the current build.
- When a user story's acceptance criteria change, update the corresponding UAT here in the
  same PR.
