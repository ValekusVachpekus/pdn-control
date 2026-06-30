# Quality Requirement Tests (QRTs) — ПДн Контроль

This document maps each quality requirement in
[`docs/quality-requirements.md`](./quality-requirements.md) to **at least one automated
test** that verifies its measurable target. Every QRT is a **maintained project asset**:
it is stored in a normal repository test location and runs in CI
([#71](https://github.com/ValekusVachpekus/pdn-control/issues/71)); a failing QRT blocks
merge per [`docs/definition-of-done.md`](./definition-of-done.md).

| QRT | Verifies | Type | Test location | Runs in CI |
|---|---|---|---|---|
| [QRT-01](#qrt-01) | [QR-01](./quality-requirements.md#qr-01--crawler-confidentiality-against-ssrf) (Security / Confidentiality) | Unit | [`crowler/tests/test_ssrf.py`](../crowler/tests/test_ssrf.py), [`crowler/tests/test_ssrf_redirect.py`](../crowler/tests/test_ssrf_redirect.py) | crowler test job (#71) |
| [QRT-02](#qrt-02) | [QR-02](./quality-requirements.md#qr-02--deterministic-scan-results) (Reliability / Maturity) | Unit | [`backend/tests/test_determinism.py`](../backend/tests/test_determinism.py), [`backend/tests/test_violation_catalog.py`](../backend/tests/test_violation_catalog.py) (`test_detect_mechanical_idempotent`) | backend test job (#71) |
| [QRT-03](#qrt-03) | [QR-03](./quality-requirements.md#qr-03--correct-fact-to-violation-mapping-rule-engine) (Functional suitability / Functional correctness) | Unit | [`backend/tests/test_violation_catalog.py`](../backend/tests/test_violation_catalog.py) | backend test job (#71) |

> **CI note.** The CI runner, coverage gate, additional QA check, and branch protection
> that execute these QRTs on every PR are delivered by issue
> [#71](https://github.com/ValekusVachpekus/pdn-control/issues/71). This document defines
> the QR↔test mapping and pass criteria; #71 wires the execution.

---

## QRT-01

- **Verifies:** [QR-01 — Crawler confidentiality against SSRF](./quality-requirements.md#qr-01--crawler-confidentiality-against-ssrf)
- **ISO/IEC 25010:** Security → Confidentiality
- **Evidence type:** Automated unit tests (deterministic; DNS resolver is injected as a fake, no real network).
- **Location:** [`crowler/tests/test_ssrf.py`](../crowler/tests/test_ssrf.py), [`crowler/tests/test_ssrf_redirect.py`](../crowler/tests/test_ssrf_redirect.py)
- **What it checks:** The SSRF guard rejects targets resolving to private, loopback,
  link-local, and reserved IP ranges, **including via HTTP redirects**, and allows public
  addresses.
- **Pass criteria (maps to QR-01 measure):** 100% of non-public targets are blocked; no
  outbound request reaches a non-public address. The test suite passes with zero failures.
- **Run locally:** `cd crowler && uv run pytest tests/test_ssrf.py tests/test_ssrf_redirect.py`

## QRT-02

- **Verifies:** [QR-02 — Deterministic scan results](./quality-requirements.md#qr-02--deterministic-scan-results)
- **ISO/IEC 25010:** Reliability → Maturity
- **Evidence type:** Automated unit tests (pure functions; no Redis/DB/LLM).
- **Location:** [`backend/tests/test_determinism.py`](../backend/tests/test_determinism.py) (added for QR-02), and the existing `test_detect_mechanical_idempotent` in [`backend/tests/test_violation_catalog.py`](../backend/tests/test_violation_catalog.py).
- **What it checks:** `detect_mechanical` produces a **byte-identical** canonicalized
  violation set across **N = 5** repeated runs of the same fixture, yields the same result
  for fresh equal inputs (no hidden global state), and does **not mutate** its input.
- **Pass criteria (maps to QR-02 measure):** Across 5 runs the canonicalized output is
  identical (0 differences); input is unchanged after a call.
- **Scope note:** Determinism is scoped to the mechanical / rule-based layer; the LLM
  analysis layer is non-deterministic by design and excluded by QR-02.
- **Run locally:** `cd backend && uv run pytest tests/test_determinism.py tests/test_violation_catalog.py -k idempotent`

## QRT-03

- **Verifies:** [QR-03 — Correct fact-to-violation mapping](./quality-requirements.md#qr-03--correct-fact-to-violation-mapping-rule-engine)
- **ISO/IEC 25010:** Functional suitability → Functional correctness
- **Evidence type:** Automated unit tests over labelled crawl fixtures (no LLM/DB).
- **Location:** [`backend/tests/test_violation_catalog.py`](../backend/tests/test_violation_catalog.py)
- **What it checks:** On labelled fixtures the engine emits exactly the expected violation
  types (PII form without consent → violation; clean site → zero); never fabricates
  unverifiable violations (`no_rkn_notification` is not emitted by code); a malformed crawl
  fails closed to zero violations; operator-identification suppression works.
- **Pass criteria (maps to QR-03 measure):** Expected-vs-detected violations match with
  100% precision and recall on the fixtures; 0 fabricated violations; malformed crawl → 0.
- **Run locally:** `cd backend && uv run pytest tests/test_violation_catalog.py`

---

## Maintenance

- Each QR has ≥1 automated QRT here; all QRTs run in CI (#71) and gate merges.
- When product behaviour affecting a QR changes, update the QR, this QRT entry, the test,
  and fixtures in the same PR.
- Do not rename or delete these test files without updating this mapping.
