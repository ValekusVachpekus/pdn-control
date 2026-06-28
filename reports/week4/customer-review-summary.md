# Sprint Review & UAT Summary — Sprint 2

**Date:** 2026-06-27

**Event:** One recorded session covering **both** customer-executed User Acceptance Testing
**and** the Sprint Review discussion. Exact UAT/Review timecodes are provided privately in the
Moodle submission; the public transcript is in
[`customer-review-transcript.md`](customer-review-transcript.md).

**Participants:**
- **Customer** — product stakeholder / acceptor.
- **Ilia Shchetkov** (`ValekusVachpekus`) — Product Owner + Frontend (led the review).
- **Airat Mingazov** (`azenlrd`) — Backend.
- **Aleksandr Martiushev** (`alexzhal1`) — Backend.
- **Maksim Shakhrai** (`ShakhraiMaksim`) — QA (operated the meeting recording).
- **Absent:** Ksenya Koroleva (`kskorqueen`) — Scrum Master.

## Sprint Goal Reviewed
Improve product quality and deploy the service on the customer's own infrastructure: quality
requirements + automated quality requirement tests, CI quality gates, an updated Definition of
Done, more deterministic checks (GeoIP instead of the LLM for hosting/IP detection), and a
TLS-secured deployment on the customer's server and domain.

## Delivered Increment Demonstrated
- **Live service on customer infrastructure** behind Caddy on 443 with a TLS certificate
  ([#86](https://github.com/ValekusVachpekus/pdn-control/issues/86),
  [#88](https://github.com/ValekusVachpekus/pdn-control/issues/88)).
- **Deterministic GeoIP hosting/IP detection** replacing the LLM in that path
  ([#75](https://github.com/ValekusVachpekus/pdn-control/issues/75)).
- **CI quality gate** — required jobs, per-module coverage gate, SAST (Bandit + pip-audit),
  branch protection ([#71](https://github.com/ValekusVachpekus/pdn-control/issues/71)).
- **Quality requirements & automated QRTs** (anti-SSRF, determinism, rule-engine correctness).
- **Released increment** [v1.1.0](https://github.com/ValekusVachpekus/pdn-control/releases/tag/v1.1.0).

## UAT Results
The customer executed the active UAT scenarios live during the session. **5 / 5 Pass:**

| UAT | Feature | Result |
|---|---|---|
| [UAT-01](../../docs/user-acceptance-tests.md#uat-01--basic-website-scan-produces-a-report) | Basic scan → report | ✅ Pass |
| [UAT-02](../../docs/user-acceptance-tests.md#uat-02--total-potential-fine-is-shown-prominently) | Total potential fine | ✅ Pass |
| [UAT-03](../../docs/user-acceptance-tests.md#uat-03--free-tier-is-limited-paid-tier-unlocks-the-full-report) | Free vs paid gating | ✅ Pass |
| [UAT-04](../../docs/user-acceptance-tests.md#uat-04--full-report-can-be-downloaded-as-pdf) | PDF report download | ✅ Pass |
| [UAT-05](../../docs/user-acceptance-tests.md#uat-05--internal--private-urls-are-refused-anti-ssrf) | Anti-SSRF refusal | ✅ Pass |

No UAT scenario failed. Several **minor UI defects** were observed during execution (see
*Requested Changes* below); they did not block any scenario from passing.

## Quality Evidence Discussed
The team walked the customer through the quality requirements, the automated quality requirement
tests, the CI pipeline, and the Definition of Done. The customer confirmed that **no changes** to
the CI, quality requirements, or quality requirement tests are needed.

## Approvals
- The customer **accepted the Sprint increment** and confirmed the **Sprint Goal was reached**
  (quality improvement + deployment on their infrastructure).
- The customer confirmed the **migration to their infrastructure and domain** is fine.

## Requested Changes (Customer Feedback)
All raised during live testing; the customer confirmed they were captured correctly.

1. **Check without registration** — starting a check while logged out is correctly blocked, but
   the loading screen still opens; fix the flow so it does not show loading.
2. **"New check" button discoverability** — from the empty history screen there is no obvious way
   back to the main page; make the "New check" action more intuitive.
3. **Useless "0" fine** — remove the `0` shown when the owner-side personal-data checks cannot be
   assessed; it confuses the reader.
4. **Empty "data collection points"** — when forms are on the main page the block looks empty;
   label the location (e.g. "Main page") instead of leaving it blank.
5. **Cookie violation target role** — the cookie-banner violation is addressed to the *Marketer*;
   it should be addressed to the *Developer*.
6. **Email delivery** — the team may use a third-party email provider instead of a local SMTP
   server on the customer's machine; the customer will add whatever records the team sends.

## Risks & Action Points
- **Email sending** depends on the customer adding the provider records the team sends → the team
  prepares and sends the provider details; the customer adds them.
- **Action:** track the six feedback items above as backlog items for the next Sprint (see the
  Customer Feedback Response table in [`reports/week4/README.md`](README.md)).

## Resulting Product Backlog / Scope Changes
- Six new UI/UX and infrastructure backlog items added from this review (items 1–6 above).
- No items removed; no changes requested to the quality model, CI, or test scope.
- US-13 scan-finished notification ([#70](https://github.com/ValekusVachpekus/pdn-control/issues/70))
  remains carried over — not raised again by the customer.

---
*Note: Recording permission was requested and granted at the start of the session. Public
publication of the transcript reuses the consent obtained at the Week 3 Sprint Review.*
