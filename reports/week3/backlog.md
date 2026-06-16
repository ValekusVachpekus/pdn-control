# Week 3 — Product Backlog & Estimation

Assignment 3, Parts 3–4. This is a **Course Task artifact** (reporting/evidence): the
authoritative backlog lives in GitHub Issues + the GitHub Project board. This document
records the backlog snapshot, Story-Point estimation totals, DEEP rationale, the current
Sprint Backlog, and the board setup.

- **Issues (authoritative):** <https://github.com/ValekusVachpekus/pdn-control/issues>
- **User-story index:** [`docs/user-stories.md`](../../docs/user-stories.md)
- **Definition of Done:** [`docs/definition-of-done.md`](../../docs/definition-of-done.md)
- **Sprint 1 milestone:** <https://github.com/ValekusVachpekus/pdn-control/milestone/1>

## 1. Counted Product Backlog (≥15 PBIs)

Won't-Have, Removed and Course-Task issues are **excluded** from the count (Process
Requirements). Story Points use the Modified Fibonacci scale `1, 2, 3, 5, 8, 13, 20, 40, 100`.

| # | PBI | Issue | Type | MoSCoW | SP | Work Status | Sprint |
|---|---|---|---|---|---|---|---|
| 1 | US-12 Server-side URL validation / anti-SSRF | [#69](https://github.com/ValekusVachpekus/pdn-control/issues/69) | User Story | Must | 8 | Ready | Sprint 1 |
| 2 | US-01 Basic website scan | [#58](https://github.com/ValekusVachpekus/pdn-control/issues/58) | User Story | Must | 5 | Done | — |
| 3 | US-02 Total potential fine display | [#59](https://github.com/ValekusVachpekus/pdn-control/issues/59) | User Story | Must | 3 | Done | — |
| 4 | US-03 Detailed list of violations | [#60](https://github.com/ValekusVachpekus/pdn-control/issues/60) | User Story | Must | 5 | Done | — |
| 5 | US-04 Legal article references | [#61](https://github.com/ValekusVachpekus/pdn-control/issues/61) | User Story | Must | 3 | Done | — |
| 6 | US-05 Free tier limited check | [#62](https://github.com/ValekusVachpekus/pdn-control/issues/62) | User Story | Must | 3 | Done | — |
| 7 | US-06 Paid tier full analysis | [#63](https://github.com/ValekusVachpekus/pdn-control/issues/63) | User Story | Must | 8 | Done | — |
| 8 | US-07 Compliance score (0–100) | [#64](https://github.com/ValekusVachpekus/pdn-control/issues/64) | User Story | Must | 5 | Done | — |
| 9 | US-08 PDF report download | [#65](https://github.com/ValekusVachpekus/pdn-control/issues/65) | User Story | Should | 8 | Done | — |
| 10 | Free-report bypass fix | [#54](https://github.com/ValekusVachpekus/pdn-control/issues/54) | Bug | Should | 5 | Ready | Sprint 1 |
| 11 | CI: regression tests (crawler & rule-engine) | [#71](https://github.com/ValekusVachpekus/pdn-control/issues/71) | Task | Should | 5 | To Do | — |
| 12 | Determinism of scan results | [#34](https://github.com/ValekusVachpekus/pdn-control/issues/34) | Bug | Must | 8 | In Progress | Sprint 1 |
| 13 | US-09 Multi-page and JS crawling | [#66](https://github.com/ValekusVachpekus/pdn-control/issues/66) | User Story | Could | 13 | Done | — |
| 14 | US-10 Captcha block notification | [#67](https://github.com/ValekusVachpekus/pdn-control/issues/67) | User Story | Could | 3 | To Do | — |
| 15 | US-13 Scan-finished notification | [#70](https://github.com/ValekusVachpekus/pdn-control/issues/70) | User Story | Could | 5 | To Do | — |
| 16 | Passwordless OTP auth (e-mail) | [#55](https://github.com/ValekusVachpekus/pdn-control/issues/55) | Task | Could | 8 | To Do | — |

**Counted PBIs: 16. Total committed Product Backlog size = 95 Story Points.**

By MoSCoW: Must = 8+5+3+5+3+3+8+5+8 = **48**; Should = 8+5+5 = **18**; Could = 13+3+5+8 = **29**.

> **Work Status snapshot:** the MVP v1 feature stories US-01…US-09 (#58–#66) are already
> implemented and merged into `main`, so they are **Done** (45 SP delivered). Remaining open
> work: Sprint 1 hardening (US-12 #69, #34, #54) plus US-10, US-13, OTP #55 and CI #71.
> Done PBIs still count toward the 15-PBI minimum (only Won't/Removed/Course-Task issues do not).

### Not counted (excluded by Process Requirements)

| PBI | Issue | Type | MoSCoW | SP | Reason |
|---|---|---|---|---|---|
| US-11 Automatic AI code remediation | [#68](https://github.com/ValekusVachpekus/pdn-control/issues/68) | User Story | Won't | 13 | Won't-Have this release (parked, history preserved) |

## 2. Estimation method (Part 4)

Estimated as a team by relative sizing (Planning Poker) on the Modified Fibonacci scale; only
the **final** estimate is recorded on each counted PBI (in the issue body + the Project
`Story Points` field). Anchors: a 3 ≈ a small, well-understood UI/serialization change
(US-02/04/05/10); 8 ≈ external/integration or security-critical work (US-06/08/12, #34);
13 ≈ the hardest item — multi-page JS crawling within budget (US-09). Items the team could
not size confidently were split/clarified before estimating (e.g. the SSRF/determinism work
is tracked as distinct PBIs #69 and #34 rather than one fuzzy "stabilization" item).

## 3. DEEP

- **Detailed appropriately** — near-term/Must-Have and Sprint-1 PBIs carry full descriptions
  + ≥3 testable Gherkin acceptance criteria + roles; lower-priority Could/Won't items are
  intentionally lighter and will be detailed as they approach.
- **Emergent** — the backlog already evolved: US-12/US-13 were added during refinement, three
  existing bugs/tasks (#34/#54/#55) were promoted to full PBIs, and a new CI testing PBI (#71)
  was created from lessons learned about regressions.
- **Estimated** — every counted PBI has a Modified-Fibonacci Story-Point estimate.
- **Prioritized** — all PBIs are MoSCoW-prioritized and ordered (Must → Should → Could →
  Won't), surfaced via the Product Backlog board view sorted by priority.

## 4. Current Sprint Backlog (Sprint 1 — Stabilization / RC hardening)

**Sprint Goal:** make MVP v1 safe to expose publicly and trustworthy — close SSRF, make scan
results deterministic, and stop the free-report bypass.

Each Sprint PBI names one **Implementer** and a different **Reviewer** (Process Requirements;
recorded in the issue body since GitHub issues have no native reviewer field).

| PBI | Issue | SP | Work Status | Implementer | Reviewer |
|---|---|---|---|---|---|
| US-12 Anti-SSRF (server + crawler) | [#69](https://github.com/ValekusVachpekus/pdn-control/issues/69) | 8 | Ready | Airat (`azenlrd`) | Alexandr (`alexzhal1`) |
| Determinism of scan results | [#34](https://github.com/ValekusVachpekus/pdn-control/issues/34) | 8 | In Progress | Alexandr (`alexzhal1`) | Airat (`azenlrd`) |
| Free-report bypass fix | [#54](https://github.com/ValekusVachpekus/pdn-control/issues/54) | 5 | Ready | Alexandr (`alexzhal1`) | Ilia (`ValekusVachpekus`) |

**Sprint committed = 21 Story Points.** Scrum Master / docs: Ksenya (`kskorqueen`).

## 5. GitHub Project board — setup guide

The token used for automation lacks the `project` scope, so the **board is built in the
GitHub web UI**. Steps (do once; field values come from §1):

1. **Create** a new **Project (v2)**, owner `ValekusVachpekus`, e.g. name
   `ПДн Контроль — Product Backlog`.
2. **Custom fields:**
   - **Status** (built-in) → edit options to exactly: `To Do`, `Ready`, `In Progress`,
     `Review`, `Done`.
   - **Type** (single-select): `User Story`, `Bug`, `Task`.
   - **MoSCoW** (single-select): `Must Have`, `Should Have`, `Could Have`, `Won't Have`.
   - **Story Points** (number).
   - (Milestone, Assignee, Labels are native — no need to create.)
3. **Add items:** issues #58–#71, #34, #54, #55 (and #68 US-11 as Won't). Set each item's
   Type / MoSCoW / Story Points / Status from the table in §1.
4. **View 1 — "Product Backlog"** (Table layout): sort by MoSCoW then Story Points; show
   columns Type, Status, Story Points, Assignee, Milestone. Save the view.
5. **View 2 — "Sprint Backlog"** (Board layout): set the board column field to **Status**;
   filter `milestone:"Sprint 1 — Stabilization / RC hardening"`. Save the view.
6. Record the Project URL here once created:
   `Project: <PASTE PROJECT URL>`
