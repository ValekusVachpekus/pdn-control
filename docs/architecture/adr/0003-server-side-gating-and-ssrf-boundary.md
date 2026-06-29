# ADR-0003: Server-side report gating and an anti-SSRF boundary in the request path

- **Status:** Accepted
- **Recorded:** 2026-06-29 (Sprint 5) — documents a decision implemented since MVP v1 (US-12).
- **Deciders:** product team, after the customer raised both risks at the Sprint Review.
- **Quality requirement(s) addressed:** [QR-01 — Crawler confidentiality against SSRF](../../quality-requirements.md#qr-01--crawler-confidentiality-against-ssrf).

## Context

Two confidentiality risks were identified on MVP v1:

1. **SSRF:** the crawler fetches attacker-controlled URLs server-side and could be pointed at
   internal services or the cloud metadata endpoint (`169.254.169.254`).
2. **Free-tier bypass:** premium report data was originally sent to the frontend and merely
   blurred in CSS, so it could be read via browser "Inspect Element" without paying.

Both are **trust boundaries that must be enforced on the server**, because anything the client
receives or controls cannot be trusted.

## Decision

Enforce both boundaries server-side:

- **Anti-SSRF guard before any crawl.** `POST /api/scans` runs `internal_target_reason` and the
  crawler's own `ssrf` guard rejects targets that resolve — or redirect — to
  private/loopback/link-local/reserved IPs, making **no** outbound connection to them.
- **Server-side payment gating of premium data.** The unified report's premium fields are not sent
  to the frontend until payment is confirmed server-side; the frontend blur is UX only, not the
  access control.

## Consequences

- **Positive:** confidentiality is structural — the SSRF gate is the *first* interaction in the
  scan sequence (see the dynamic view) and premium data never leaves the server unpaid. Directly
  realises QR-01 with a zero-tolerance measure. The gate is centralized and unit-tested
  (including the redirect case).
- **Negative / risks:** the SSRF policy can reject legitimate but unusually-hosted targets; the
  guard must be re-checked after redirects (covered by `test_ssrf_redirect.py`); gating logic must
  stay in the API/worker, never drift into the client.

## Alternatives considered

- **Client-side gating only (blur):** rejected — trivially bypassable, the original bug.
- **Allowlist of scannable domains:** rejected — incompatible with the product (users scan
  arbitrary sites); a deny-by-IP-class guard is the right tool.

## Related

- Code: `backend/app/services/ssrf.py`, `crowler/pdn_parser/ssrf.py`, server-side report gating in `backend/app/routers/reports.py`.
- [QRT-01](../../quality-requirement-tests.md#qrt-01), US-12 [#69](https://github.com/ValekusVachpekus/pdn-control/issues/69), bypass fix [#54](https://github.com/ValekusVachpekus/pdn-control/issues/54).
