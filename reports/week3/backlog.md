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

Counted PBIs (excluding Won't-Have / Removed / Course-Task per Process Requirements): **16**.
Story Points use the Modified Fibonacci scale `1, 2, 3, 5, 8, 13, 20, 40, 100`.

- **Total committed Product Backlog size = 95 Story Points.**
  - Must Have (9 PBIs): **48 SP** — US-01 5, US-02 3, US-03 5, US-04 3, US-05 3, US-06 8,
    US-07 5, US-12 8, #34 8.
  - Should Have (3 PBIs): **18 SP** — US-08 8, #54 5, #71 (CI) 5.
  - Could Have (4 PBIs): **29 SP** — US-09 13, US-10 3, US-13 5, #55 (OTP) 8.
- **Not counted:** US-11 (#68) Won't-Have, 13 SP — parked, history preserved.

Estimated as a team by relative sizing (Planning Poker); only the final estimate is recorded
on each PBI (Project `Story Points` field + issue body). Items that could not be sized
confidently were split into distinct PBIs (e.g. SSRF #69 vs determinism #34) before estimating.

**Work Status snapshot:** the MVP feature stories US-01…US-09 (#58–#66) and US-12 (#69) are
implemented and merged into `main` → **Done**. Remaining open work is the Sprint 1 hardening
set plus US-10, US-13.

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

**MVP v1 scope** = the PBIs marked `MVP version = MVP v1` (the Sprint 1 milestone set). The
only user story is the Must-Have US-12; the rest are required supporting PBIs (Process
Requirements allow technical/testing/bug supporting work in MVP scope). **All MVP v1 PBIs must
be completed, reviewed, merged into `main` and Done by the Assignment 3 submission.**

| Sprint PBI | Issue | Type | SP | Work Status | Implementer | Reviewer |
|---|---|---|---|---|---|---|
| US-12 Server-side URL validation / anti-SSRF | [#69](https://github.com/ValekusVachpekus/pdn-control/issues/69) | User Story | 8 | Done | Airat (`azenlrd`) | Alexandr (`alexzhal1`) |
| Determinism of scan results | [#34](https://github.com/ValekusVachpekus/pdn-control/issues/34) | Bug | 8 | Review (PR #56) | Alexandr (`alexzhal1`) | Airat (`azenlrd`) |
| Free-report bypass fix | [#54](https://github.com/ValekusVachpekus/pdn-control/issues/54) | Bug | 5 | In Progress | Alexandr (`alexzhal1`) | Ilia (`ValekusVachpekus`) |
| Passwordless OTP auth (e-mail) | [#55](https://github.com/ValekusVachpekus/pdn-control/issues/55) | Task | 8 | Ready | — | — |
| CI: regression tests (crawler & rule-engine) | [#71](https://github.com/ValekusVachpekus/pdn-control/issues/71) | Task | 5 | Ready | Airat (`azenlrd`) | Alexandr (`alexzhal1`) |

**Total Sprint commitment = 34 Story Points.** The sprint spans all canonical Work Statuses
(Ready / In Progress / Review / Done). Scrum Master / docs: Ksenya (`kskorqueen`).

## 5. Project board structure (Part 3/6)

GitHub Project v2 (Table + Board views) with custom fields:
- **Status** (To Do, Ready, In Progress, Review, Done — canonical Work Status)
- **Type** (User Story, Bug, Task), **MoSCoW** (Must/Should/Could/Won't), **Story Points** (number)
- **MVP version** (MVP v1 / v2 / v3) — group the Table view by this field to show MVP scope
- native Milestone / Assignee / Labels / Linked PRs

Views: **Product Backlog** (Table, sorted by MoSCoW then Story Points) and **Sprint Backlog**
(Board by Status, filtered to the Sprint 1 milestone).
