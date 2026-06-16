# Week 3 — Product Backlog & Estimation

Assignment 3, Parts 3–6. **Course Task artifact** (reporting/evidence). The **authoritative
backlog is the GitHub Project board + Issues**; this document only records the summary,
estimation totals, DEEP rationale, and the current Sprint plan — it does not mirror the full
mutable PBI table (that lives on the board, to avoid drift).

- **Project board (authoritative):** <https://github.com/users/ValekusVachpekus/projects/1>
- **Issues:** <https://github.com/ValekusVachpekus/pdn-control/issues>
- **User-story index:** [`docs/user-stories.md`](../../docs/user-stories.md)
- **Definition of Done:** [`docs/definition-of-done.md`](../../docs/definition-of-done.md)
- **Sprint 1 milestone:** <https://github.com/ValekusVachpekus/pdn-control/milestone/1>

## 1. Backlog size & estimation (Parts 3–4)

Counted PBIs (excluding Won't-Have / Removed / Course-Task per Process Requirements): **22**.
Story Points use the Modified Fibonacci scale `1, 2, 3, 5, 8, 13, 20, 40, 100`.

- **Total committed Product Backlog size = 135 Story Points.**
  - Must Have (11 PBIs): **71 SP** — US-01 5, US-02 3, US-03 5, US-04 3, US-05 3, US-06 8,
    US-07 5, US-12 8, #34 8, #13 (backend) 20, #18 (scan-status API) 3.
  - Should Have (5 PBIs): **25 SP** — US-08 8, #54 5, #71 (CI) 5, #28 (tracker detection) 5,
    #31 (cache canon / determinism) 2.
  - Could Have (6 PBIs): **39 SP** — US-09 13, US-10 3, US-13 5, #55 (OTP) 8,
    #72 (OAuth Яндекс/ВК) 8, #50 (scan screen from history) 2.
- **Not counted:** US-11 (#68) Won't-Have, 13 SP — parked, history preserved.

Estimated as a team by relative sizing (Planning Poker); only the final estimate is recorded
on each PBI (Project `Story Points` field + issue body). Items that could not be sized
confidently were split into distinct PBIs (e.g. SSRF #69 vs determinism #34) before estimating.

**Work Status snapshot:** the MVP feature stories US-01…US-09 (#58–#66), US-12 (#69) and the
already-completed supporting tasks #13, #18, #28, #31, #50 are implemented and merged into
`main` → **Done**. Remaining open work is the Sprint 1 hardening set (#34, #54) plus the
backlog items US-10, US-13, OTP #55, CI #71, OAuth #72.

## 2. DEEP

- **Detailed appropriately** — Must-Have / near-term / Sprint PBIs carry full descriptions +
  ≥3 testable Gherkin acceptance criteria + roles; Could/Won't items are intentionally lighter.
- **Emergent** — backlog evolved: US-12/US-13 added during refinement, bugs/tasks #34/#54/#55
  promoted to full PBIs, CI testing PBI #71 created from regression lessons.
- **Estimated** — every counted PBI has a Modified-Fibonacci Story-Point estimate.
- **Prioritized** — all PBIs MoSCoW-prioritized and ordered (Must → Should → Could → Won't),
  surfaced via the Product Backlog board view sorted by priority.

## 3. Definition of Done (Part 5)

Maintained in [`docs/definition-of-done.md`](../../docs/definition-of-done.md). A PBI is `Done`
only when its acceptance criteria **and** the team DoD are both satisfied (AC met, reviewed by
another member, linked PR merged into protected `main`, required checks pass, CHANGELOG updated
if user-visible).

## 4. Sprint Backlog & MVP v1 (Part 6)

**Milestone:** Sprint 1 — Stabilization / RC hardening · **dates:** Mon 2026-06-15 → Sun
2026-06-21 · stored on the milestone (description + due date).

**Sprint Goal:** deliver a trustworthy, publicly-safe MVP v1 — the Must-Have scan→report flow
is live, the crawler cannot be abused for SSRF, re-scanning the same site yields the same
report, and paid report data cannot be unlocked for free. By sprint end MVP v1 is
release-candidate quality.

### 4a. Current Sprint Backlog (Sprint 1)

The **current sprint** delivers the stabilization set. It is a subset of MVP v1 — MVP v1 is
broader (see 4b). OTP auth (#55) and CI (#71) were de-scoped from Sprint 1 and remain in the
Product Backlog.

| Sprint PBI | Issue | Type | SP | Work Status | Implementer | Reviewer |
|---|---|---|---|---|---|---|
| US-12 Server-side URL validation / anti-SSRF | [#69](https://github.com/ValekusVachpekus/pdn-control/issues/69) | User Story | 8 | Done | Airat (`azenlrd`) | Alexandr (`alexzhal1`) |
| Determinism of scan results | [#34](https://github.com/ValekusVachpekus/pdn-control/issues/34) | Bug | 8 | Review (PR #56) | Alexandr (`alexzhal1`) | Airat (`azenlrd`) |
| Free-report bypass fix | [#54](https://github.com/ValekusVachpekus/pdn-control/issues/54) | Bug | 5 | In Progress | Alexandr (`alexzhal1`) | Ilia (`ValekusVachpekus`) |

**Total Sprint commitment = 21 Story Points.** The sprint spans all canonical Work Statuses
(Ready / In Progress / Review / Done). Scrum Master / docs: Ksenya (`kskorqueen`).

### 4b. MVP v1 scope

**MVP v1** = the PBIs marked `MVP version = MVP v1` on the board. It is **not** the same as the
sprint: it also includes already-completed supporting tasks (core backend, scan-status API,
tracker detection, determinism cache, history→scan navigation) that were delivered before this
sprint and are needed for a coherent first release. **All MVP v1 PBIs must be completed,
reviewed, merged into `main` and Done by the Assignment 3 submission.**

| MVP v1 PBI | Issue | Type | SP | Work Status | Implementer (assignee) |
|---|---|---|---|---|---|
| US-12 Server-side URL validation / anti-SSRF | [#69](https://github.com/ValekusVachpekus/pdn-control/issues/69) | User Story | 8 | Done | Airat (`azenlrd`) |
| Determinism of scan results | [#34](https://github.com/ValekusVachpekus/pdn-control/issues/34) | Bug | 8 | Review (PR #56) | Alexandr (`alexzhal1`) |
| Free-report bypass fix | [#54](https://github.com/ValekusVachpekus/pdn-control/issues/54) | Bug | 5 | In Progress | Alexandr (`alexzhal1`) |
| Implement backend (auth/scans/reports/billing) | [#13](https://github.com/ValekusVachpekus/pdn-control/issues/13) | Task | 20 | Done | Alexandr (`alexzhal1`) |
| Scan-status API | [#18](https://github.com/ValekusVachpekus/pdn-control/issues/18) | Task | 3 | Done | Alexandr (`alexzhal1`) |
| Tracker detection on large sites | [#28](https://github.com/ValekusVachpekus/pdn-control/issues/28) | Task | 5 | Done | Airat (`azenlrd`) |
| Cache canon / determinism volatile fields | [#31](https://github.com/ValekusVachpekus/pdn-control/issues/31) | Task | 2 | Done | Alexandr (`alexzhal1`) |
| Scan screen from history | [#50](https://github.com/ValekusVachpekus/pdn-control/issues/50) | Task | 2 | Done | Ilia (`ValekusVachpekus`) |

**MVP v1 total = 53 Story Points** (8 + 8 + 5 + 20 + 3 + 5 + 2 + 2). Of these, 5 are already
Done; only #34 and #54 remain to be merged into `main` by submission.

## 5. Project board structure (Part 3/6)

GitHub Project v2 (Table + Board views) with custom fields:
- **Status** (To Do, Ready, In Progress, Review, Done — canonical Work Status)
- **Type** (User Story, Bug, Task), **MoSCoW** (Must/Should/Could/Won't), **Story Points** (number)
- **MVP version** (MVP v1 / v2 / v3) — group the Table view by this field to show MVP scope
- native Milestone / Assignee / Labels / Linked PRs

Views: **Product Backlog** (Table, sorted by MoSCoW then Story Points) and **Sprint Backlog**
(Board by Status, filtered to the Sprint 1 milestone).
