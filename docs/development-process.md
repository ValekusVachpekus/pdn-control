# Development Process & Configuration Management — ПДн Контроль

This document is the maintained reference for **how the team develops the product** (git
workflow, reviews, Work Status, Definition of Done, traceability) and **how the product is
configured** (environments, configuration files, and secrets). It reflects the rules in
[`CONTRIBUTING.md`](../CONTRIBUTING.md) and the enforcement mechanics in the repository.

## Git workflow

```mermaid
gitGraph
   commit id: "main (protected)"
   branch 109-dev-process
   checkout 109-dev-process
   commit id: "docs: dev-process"
   commit id: "review fixes"
   checkout main
   merge 109-dev-process tag: "PR #x (1 approval)"
   branch 103-cookie-role
   checkout 103-cookie-role
   commit id: "fix: target_role=developer"
   commit id: "add test"
   checkout main
   merge 103-cookie-role tag: "PR #y (1 approval)"
   branch 72-oauth
   checkout 72-oauth
   commit id: "feat: OAuth redirect flow"
   commit id: "tests + changelog"
   checkout main
   merge 72-oauth tag: "PR #z (1 approval)"
   commit id: "release v1.2.0" tag: "v1.2.0"
```

### What the diagram shows

`main` is the single long-lived, **protected** branch. Every change starts as a short-lived
branch created from the related issue, named `<issue-number>-short-description` (e.g.
`72-oauth`). Work happens on that branch as one or more commits; the branch is opened as a Pull
Request that links its issue (`Closes #<n>`), is reviewed and approved by **at least one other**
team member, passes CI, and is then integrated with a **merge commit** (squash and rebase are
disabled, so history is preserved). Releases are tags (`vX.Y.Z`) on a commit of `main`.

### How the team actually uses this workflow

- **One issue → one branch → one focused PR.** Branches are created from the issue page so the
  link is automatic. The author never approves their own PR.
- **Review is mandatory and cross-member.** Each Sprint 5 PBI has a named *implementer* and a
  *different reviewer* (recorded on the issue at Sprint Planning); the reviewer is the required
  approver. This is enforced by branch protection on `main` (required review + required passing
  CI checks before merge), so the rule cannot be bypassed.
- **Acceptance criteria are checked before merge.** The reviewer verifies the issue's acceptance
  criteria and the PR's changelog checklist item, then merges.
- **History is immutable until grading.** PRs, reviews, and tags tied to submitted MVP milestones
  are never force-pushed, rebased away, or deleted — the only exception is purging an accidentally
  committed secret.

### Work Status

Work is tracked on the [GitHub Project board](https://github.com/users/ValekusVachpekus/projects/1)
with a per-Sprint view filtered by milestone. Items move through the board `Status` field:

| Status | Meaning |
|---|---|
| `To Do` / `Ready` | Selected for the Sprint, refined and estimated, not started. |
| `In Progress` | Implementer is actively working on the branch. |
| `Review` | PR open, awaiting the assigned reviewer's approval and CI. |
| `Done` | Merged to `main`, acceptance criteria met, CI green. |

The completion standard for `Done` is defined in [`definition-of-done.md`](definition-of-done.md)
and is the same for every PBI.

### Traceability

Issue → branch (`<issue>-…`) → PR (`Closes #<issue>`) → merge commit on `main` → CHANGELOG entry
(for user-visible changes) → release notes. Each PBI also carries Story Points, MoSCoW priority,
`MVP version`, implementer, and reviewer on the board, so any change can be traced from a backlog
item to the commit and release that delivered it.

## Configuration management

Configuration is split by **what it is** and **how sensitive it is**, and is never hard-coded in
application code.

### Configuration files and where values live

| Layer | Mechanism | Committed? |
|---|---|---|
| Infrastructure wiring (DB/Redis/service URLs, CORS, ports) | Explicit `environment:` in `backend/docker-compose.yml` | ✅ yes — no secrets |
| Application defaults & schema | `app/config.py` (Pydantic settings) | ✅ yes |
| Non-secret example config | `.env.example`, `backend/.env.example` | ✅ yes (templates) |
| **Secrets** (`JWT_SECRET`, `LLM_API_KEY`, `CLOUDPAYMENTS_*`, OAuth & e-mail credentials) | `backend/.env.secret`, loaded via Compose `env_file` (`required: false`) | ❌ **never** |

The split is deliberate: infrastructure addresses are checked in so a clone runs with one command,
while secrets are isolated in `.env.secret` (and local `.env`), which are git-ignored.

### Secrets baseline

- No secrets, keys, real credentials, or personal data are committed. Templates use placeholder
  values in `.env.example`.
- If a secret is ever committed: rotate/revoke it immediately, scrub it from files and history,
  temporarily make the repo private if needed, notify the TA, and document the incident privately.
- The CI security job (Bandit SAST, mandatory gate; `pip-audit` advisory) helps catch insecure
  patterns before merge.

### Environments

- **Local / dev:** `cd backend && docker compose up` brings up the whole stack; internal ports are
  mapped to `localhost` for inspection. The frontend talks to the API in MOCK mode unless wired to
  the real backend.
- **Customer / production:** the same Compose stack on the customer's host, fronted by **Caddy**
  on `:443` with automatic TLS; only `:443` is exposed. See the
  [deployment view](architecture/deployment-view/deployment-diagram.svg).

### CI configuration

CI is configuration-as-code in [`.github/workflows/`](../.github/workflows/): `ci.yml` (lint,
crowler tests, backend unit/integration, PDF, frontend, security) and `lychee.yml` (Markdown link
check). These jobs are required status checks for merging into the protected `main`.

## See also

- [`CONTRIBUTING.md`](../CONTRIBUTING.md) — the authoritative workflow rules.
- [`architecture/README.md`](architecture/README.md) — system structure and ADRs.
- [`definition-of-done.md`](definition-of-done.md) — the completion standard.
- [`testing.md`](testing.md) — test strategy, critical modules, coverage.
