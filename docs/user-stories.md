# User Stories — Product Backlog Index

This file is a **traceability index** for the user-story backlog. The **GitHub issues are
the authoritative source** for live story content and status; this table only mirrors the
current state for quick traceability. Do not duplicate full mutable story content here.

- **Source:** the active user stories were migrated from the Assignment 2 artifact
  [`reports/week2/user-stories.md`](../reports/week2/user-stories.md), preserving their
  stable IDs (US-01…US-11). That file is kept unchanged as the historical record.
- **Refinement:** US-12 and US-13 were newly discovered during refinement and assigned the
  next free IDs. No stories were split or removed.
- **Requirement status:** `Active` (current product requirement) or `Removed` (no longer a
  current requirement — stable ID preserved, never reused).
- **Work Status** mirrors the current board/issue status: `To Do`, `Ready`, `In Progress`,
  `Review`, `Done`, or `—` for removed stories (canonical meanings per Process Requirements).
- **Sprint** links the sprint milestone when assigned, otherwise `—`.
- Active stories are ordered by MoSCoW priority, then Sprint, then stable ID. Removed
  stories (none currently) would follow all active stories.
- Estimates (Story Points) live on the board and in
  [`reports/week3/backlog.md`](../reports/week3/backlog.md); completion standard:
  [`docs/definition-of-done.md`](definition-of-done.md).

| ID | Short title | MoSCoW priority | Issue | Requirement status | Work Status | Sprint |
|---|---|---|---|---|---|---|
| US-12 | Server-side URL validation / anti-SSRF | Must Have | [#69](https://github.com/ValekusVachpekus/pdn-control/issues/69) | Active | In Progress | [Sprint 1](https://github.com/ValekusVachpekus/pdn-control/milestone/1) |
| US-01 | Basic website scan | Must Have | [#58](https://github.com/ValekusVachpekus/pdn-control/issues/58) | Active | Done | — |
| US-02 | Total potential fine display | Must Have | [#59](https://github.com/ValekusVachpekus/pdn-control/issues/59) | Active | Done | — |
| US-03 | Detailed list of violations | Must Have | [#60](https://github.com/ValekusVachpekus/pdn-control/issues/60) | Active | Done | — |
| US-04 | Legal article references | Must Have | [#61](https://github.com/ValekusVachpekus/pdn-control/issues/61) | Active | Done | — |
| US-05 | Free tier limited check | Must Have | [#62](https://github.com/ValekusVachpekus/pdn-control/issues/62) | Active | Done | — |
| US-06 | Paid tier full analysis | Must Have | [#63](https://github.com/ValekusVachpekus/pdn-control/issues/63) | Active | Done | — |
| US-07 | Compliance score (0–100) | Must Have | [#64](https://github.com/ValekusVachpekus/pdn-control/issues/64) | Active | Done | — |
| US-08 | PDF report download | Should Have | [#65](https://github.com/ValekusVachpekus/pdn-control/issues/65) | Active | Done | — |
| US-10 | Captcha block notification | Should Have | [#67](https://github.com/ValekusVachpekus/pdn-control/issues/67) | Active | Done | — |
| US-09 | Multi-page and JS crawling | Could Have | [#66](https://github.com/ValekusVachpekus/pdn-control/issues/66) | Active | Done | — |
| US-13 | Scan-finished notification (link/email) | Could Have | [#70](https://github.com/ValekusVachpekus/pdn-control/issues/70) | Active | To Do | — |
| US-11 | Automatic AI code remediation | Won't Have | [#68](https://github.com/ValekusVachpekus/pdn-control/issues/68) | Active | — | — |

> Note: US-13 (#70) is an Active user story but is not currently placed on the Product Backlog
> board (kept as an issue only). US-10 (#67) and US-12 (#69) Work Status mirror the board.
