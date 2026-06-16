# Week 3 — Product Backlog & Estimation

Assignment 3, Parts 3–6. **Course Task artifact** (reporting/evidence). The **authoritative
backlog is the GitHub Project board + Issues**; this document mirrors the board state for the
summary, estimation totals, DEEP rationale, and the current Sprint plan.

- **Project board (authoritative):** <https://github.com/users/ValekusVachpekus/projects/1>
- **Issues:** <https://github.com/ValekusVachpekus/pdn-control/issues>
- **User-story index:** [`docs/user-stories.md`](../../docs/user-stories.md)
- **Definition of Done:** [`docs/definition-of-done.md`](../../docs/definition-of-done.md)
- **Sprint 1 milestone:** <https://github.com/ValekusVachpekus/pdn-control/milestone/1>

## 1. Backlog size & estimation (Parts 3–4)

Counted PBIs on the board (excluding Won't-Have / Removed / Course-Task per Process
Requirements): **18**. Story Points use the Modified Fibonacci scale `1, 2, 3, 5, 8, 13, 20,
40, 100`.

- **Total committed Product Backlog size = 111 Story Points.**
  - Must Have (12 PBIs): **71 SP** — US-01 5, US-02 3, US-03 5, US-04 3, US-05 3, US-06 8,
    US-07 5, US-12 8, #34 (determinism) 8, #54 (free-report fix) 5, #13 (backend) 13,
    #18 (scan-status API) 5.
  - Should Have (5 PBIs): **27 SP** — US-08 8, US-10 3, #28 (tracker detection) 8,
    #31 (cache canon / determinism) 5, #50 (scan screen from history) 3.
  - Could Have (1 PBI): **13 SP** — US-09 13.
- **Not counted:** US-11 (#68) Won't-Have, 13 SP — parked, history preserved.
- **Off-board issues (exist but not on the board, not counted):** OTP #55, US-13 #70,
  CI #71, OAuth #72 — open issues kept for future scope, not currently in the Product Backlog.

Estimated as a team by relative sizing (Planning Poker); only the final estimate is recorded
on each PBI (Project `Story Points` field + issue body). Items that could not be sized
confidently were split into distinct PBIs (e.g. SSRF #69 vs determinism #34) before estimating.

**Work Status snapshot (from the board):** the MVP feature stories US-01…US-10 (#58–#67) and
the supporting tasks #13, #18, #28, #31, #50 are implemented and merged into `main` → **Done**.
Remaining open work is the Sprint 1 hardening set: US-12 #69 (In Progress), #34 (Review),
#54 (In Progress).

## 2. DEEP

- **Detailed appropriately** — Must-Have / near-term / Sprint PBIs carry full descriptions +
  ≥3 testable Gherkin acceptance criteria + roles; lower-priority items are intentionally lighter.
- **Emergent** — backlog evolved: US-12/US-13 added during refinement, bugs/tasks #34/#54
  promoted to full PBIs, already-completed tasks #13/#18/#28/#31/#50 formalized as PBIs, and
  out-of-scope ideas (OTP #55, CI #71, OAuth #72) kept as off-board issues.
- **Estimated** — every counted PBI has a Modified-Fibonacci Story-Point estimate on the board.
- **Prioritized** — all PBIs MoSCoW-prioritized and ordered (Must → Should → Could → Won't),
  surfaced via the Product Backlog board view.

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

### 4a. Current Sprint Backlog (Sprint 1 milestone)

Issues assigned to the Sprint 1 milestone are the selected Sprint Backlog items.

| Sprint PBI | Issue | Type | SP | Work Status | Implementer | Reviewer |
|---|---|---|---|---|---|---|
| US-12 Server-side URL validation / anti-SSRF | [#69](https://github.com/ValekusVachpekus/pdn-control/issues/69) | User Story | 8 | In Progress | Airat (`azenlrd`) | Alexandr (`alexzhal1`) |
| Determinism of scan results | [#34](https://github.com/ValekusVachpekus/pdn-control/issues/34) | Bug | 8 | Review (PR #56) | Alexandr (`alexzhal1`) | Airat (`azenlrd`) |
| Free-report bypass fix | [#54](https://github.com/ValekusVachpekus/pdn-control/issues/54) | Bug | 5 | In Progress | Alexandr (`alexzhal1`) | Ilia (`ValekusVachpekus`) |

**Total Sprint commitment = 21 Story Points.** Scrum Master / docs: Ksenya (`kskorqueen`).

### 4b. MVP v1 scope

**MVP v1** = the PBIs marked `MVP version = MVP v1` on the board. Currently these are the three
Sprint 1 stabilization PBIs below. The already-Done supporting tasks (#13, #18, #28, #31, #50)
are delivered and are candidates for MVP v1 (MVP-version field pending).

| MVP v1 PBI | Issue | Type | SP | Work Status | Implementer (assignee) |
|---|---|---|---|---|---|
| US-12 Server-side URL validation / anti-SSRF | [#69](https://github.com/ValekusVachpekus/pdn-control/issues/69) | User Story | 8 | In Progress | Airat (`azenlrd`) |
| Determinism of scan results | [#34](https://github.com/ValekusVachpekus/pdn-control/issues/34) | Bug | 8 | Review (PR #56) | Alexandr (`alexzhal1`) |
| Free-report bypass fix | [#54](https://github.com/ValekusVachpekus/pdn-control/issues/54) | Bug | 5 | In Progress | Alexandr (`alexzhal1`) |

**MVP v1 total = 21 Story Points** (8 + 8 + 5). **All MVP v1 PBIs must be completed, reviewed,
merged into `main` and Done by the Assignment 3 submission.**

## 5. Project board structure (Part 3/6)

GitHub Project v2 (Table + Board views) with custom fields:
- **Status** (To Do, Ready, In Progress, Review, Done — canonical Work Status)
- **Type** (User Story, Bug, Task), **MoSCoW** (Must/Should/Could/Won't), **Story Points** (number)
- **MVP version** (MVP v1 / v2 / v3) — group the Table view by this field to show MVP scope
- native Milestone / Assignee / Labels / Linked PRs

Views: **Product Backlog** (Table, sorted by MoSCoW) and **Sprint Backlog**
(Board by Status, filtered to the Sprint 1 milestone).
