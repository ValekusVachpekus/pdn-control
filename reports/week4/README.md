## Customer Feedback Response

Source of feedback: the **Sprint Review with the customer on 2026-06-21** (see
[`reports/week3/customer-review-summary.md`](../week3/customer-review-summary.md) and
[`reports/week3/customer-review-transcript.md`](../week3/customer-review-transcript.md)).
The customer approved the MVP v1 scope and increment, requested one UI change, and
decided to host the service on their own infrastructure.

| Feedback point | Resulting PBI or issue | Status | Response |
|---|---|---|---|
| The "Total Fine" amount should be displayed more prominently as a risk score for business owners. | [#78](https://github.com/ValekusVachpekus/pdn-control/issues/78) | Done | Increased the contrast, font size, and visual weight of the fine amount in the report view so it stands out from the rest of the data. |
| Audit results were non-deterministic (different data for the same site). | [#34](https://github.com/ValekusVachpekus/pdn-control/issues/34) | Done | Canonicalized the crawl JSON (stripped volatile fields) so repeated scans of the same URL yield the same report. |
| Security flaw: full report data was accessible for free via browser "Inspect Element" (blur bypass). | [#54](https://github.com/ValekusVachpekus/pdn-control/issues/54) | Done | Moved data-gating to the API; premium data is not sent to the frontend until payment is confirmed (the blur is now only UX). |
| Security risk: the parser could be pointed at internal APIs (SSRF). | [#69](https://github.com/ValekusVachpekus/pdn-control/issues/69) (US-12, PR [#57](https://github.com/ValekusVachpekus/pdn-control/pull/57)) | Done | Added strict server-side URL validation so the crawler cannot reach internal or private IP ranges, including via redirects. |
| Request for scan-completion notifications (US-13), pulled into the Sprint as a Could-Have. | [#70](https://github.com/ValekusVachpekus/pdn-control/issues/70) | In Progress | Pulled into the Sprint with the customer's approval; implementation is ongoing and the issue is still open (not yet Done). |
| The customer will host the service on their own infrastructure and redirect their domain's DNS. | [#88](https://github.com/ValekusVachpekus/pdn-control/issues/88) | To Do (next Sprint) | New PBI to prepare deployment config/instructions for the customer's host and assist with DNS migration; builds on the TLS/Caddy deploy ([#86](https://github.com/ValekusVachpekus/pdn-control/issues/86), Done). |

### Feedback not addressed this Sprint

No customer feedback was rejected. Every explicit point from the Sprint Review is
tracked above. Two points are intentionally **not fully closed in the Assignment 4
Sprint**:

- **US-13 scan-finished notification ([#70](https://github.com/ValekusVachpekus/pdn-control/issues/70))** — kept In Progress because the Sprint prioritized quality automation, CI gates, and deployment over new features; it carries into the next Sprint.
- **DNS redirect ([#88](https://github.com/ValekusVachpekus/pdn-control/issues/88))** — the DNS change itself is a **customer-side action**. The team provides the deployment configuration and assistance; the cut-over depends on the customer redirecting their domain.
