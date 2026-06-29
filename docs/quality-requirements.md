# Quality Requirements — ПДн Контроль

This document defines the product's measurable **quality requirements (QRs)**. Each QR
follows the quality-scenario format (source → stimulus → environment → artifact →
response → response measure), names the targeted **ISO/IEC 25010** quality
characteristic and sub-characteristic, gives a rationale, lists traceability, and links
to its automated **quality requirement test (QRT)** in
[`docs/quality-requirement-tests.md`](./quality-requirement-tests.md).

Quality requirements are **maintained project assets**. Later work must maintain or
extend them; the linked QRTs run in CI ([#71](https://github.com/ValekusVachpekus/pdn-control/issues/71))
and gate merges per [`docs/definition-of-done.md`](./definition-of-done.md).

Each required QR below uses a **different** ISO/IEC 25010 sub-characteristic.

| ID | ISO/IEC 25010 characteristic | Sub-characteristic | Priority | QRT |
|---|---|---|---|---|
| QR-01 | Security | Confidentiality | Must | [QRT-01](./quality-requirement-tests.md#qrt-01) |
| QR-02 | Reliability | Maturity | Must | [QRT-02](./quality-requirement-tests.md#qrt-02) |
| QR-03 | Functional suitability | Functional correctness | Must | [QRT-03](./quality-requirement-tests.md#qrt-03) |

---

## QR-01 — Crawler confidentiality against SSRF

- **ISO/IEC 25010:** Security → **Confidentiality**
- **Priority:** Must Have

**Quality scenario**

| Element | Value |
|---|---|
| Source | An external user submitting a URL to scan (potentially malicious). |
| Stimulus | A scan request whose target URL resolves to — or redirects to — a private, loopback, link-local, or otherwise non-public IP address (e.g. `127.0.0.1`, `169.254.169.254`, `10.0.0.0/8`, `192.168.0.0/16`). |
| Environment | Production crawler service handling untrusted input. |
| Artifact | Crawler SSRF guard (`crowler/pdn_parser/ssrf.py`) and the crawl pipeline. |
| Response | The crawler refuses the target and makes **no** outbound connection to the non-public address, including after HTTP redirects. |
| **Response measure** | **100%** of attempts to reach private/loopback/link-local/reserved IPs (direct or via redirect) are blocked; **0** outbound requests reach a non-public address across the SSRF test corpus. |

**Rationale.** The crawler fetches attacker-controlled URLs server-side. Without a guard
it could be pointed at internal services or cloud metadata endpoints (`169.254.169.254`),
leaking internal data or credentials. This was raised directly by the customer at the
Sprint Review and fixed under US-12. Confidentiality of internal infrastructure is the
core risk, so the target is zero tolerance.

**Traceability**
- Customer feedback: Sprint Review 2026-06-21 (SSRF concern).
- User story / issues: US-12 ([#69](https://github.com/ValekusVachpekus/pdn-control/issues/69)), PR [#57](https://github.com/ValekusVachpekus/pdn-control/pull/57).
- 152-ФЗ relevance: protects the service operator's own data and third-party systems from unauthorized access.
- QRT: [QRT-01](./quality-requirement-tests.md#qrt-01) — `crowler/tests/test_ssrf.py`, `crowler/tests/test_ssrf_redirect.py`.
- ADR: [ADR-0003 — server-side gating & anti-SSRF boundary](./architecture/adr/0003-server-side-gating-and-ssrf-boundary.md); [ADR-0004 — Caddy/TLS single exposed boundary](./architecture/adr/0004-single-host-compose-caddy-tls.md).

---

## QR-02 — Deterministic scan results

- **ISO/IEC 25010:** Reliability → **Maturity**
- **Priority:** Must Have

**Quality scenario**

| Element | Value |
|---|---|
| Source | A user re-running an audit, or a grader verifying reproducibility. |
| Stimulus | The same crawl input (same site fixture) is processed multiple times. |
| Environment | Backend rule-engine / report pipeline under normal operation. |
| Artifact | Crawl-JSON canonicalization (`crowler/pdn_parser/utils.py`) and mechanical violation detection (`backend/app/services/violation_catalog.py`). |
| Response | Each run produces the **same** canonicalized facts and the **same** set of detected violations. |
| **Response measure** | Across **N = 5** repeated runs over the same fixture, the canonicalized output and the detected-violation set are **identical (0 differences)**. |

**Rationale.** The customer reported that the same site produced different results on
different runs (bug [#34](https://github.com/ValekusVachpekus/pdn-control/issues/34)),
which destroys trust in a compliance report. Volatile fields are stripped during
canonicalization and the deterministic (code-based) detection layer must be idempotent,
so the same input always yields the same verdicts. Note: the LLM analysis layer is
non-deterministic by nature and is therefore excluded from this requirement, which
scopes determinism to the **mechanical / rule-based** facts and violations.

**Traceability**
- Customer feedback: Sprint Review 2026-06-21 (non-deterministic results).
- Issues: bug [#34](https://github.com/ValekusVachpekus/pdn-control/issues/34), canonicalization [#31](https://github.com/ValekusVachpekus/pdn-control/issues/31).
- QRT: [QRT-02](./quality-requirement-tests.md#qrt-02) — idempotency of `detect_mechanical` in `backend/tests/test_violation_catalog.py` plus a canonicalization determinism check.
- ADR: [ADR-0002 — deterministic GeoIP over LLM](./architecture/adr/0002-deterministic-geoip-over-llm.md); [ADR-0001 — deterministic violation catalog guard](./architecture/adr/0001-full-llm-analysis-pipeline.md).

---

## QR-03 — Correct fact-to-violation mapping (rule-engine)

- **ISO/IEC 25010:** Functional suitability → **Functional correctness**
- **Priority:** Must Have

**Quality scenario**

| Element | Value |
|---|---|
| Source | The rule-engine evaluating parser facts against 152-ФЗ rules. |
| Stimulus | A labelled crawl fixture with known expected violations (e.g. a PII form without consent, a foreign tracker, no privacy policy). |
| Environment | Backend deterministic detection layer (no LLM, no DB). |
| Artifact | `backend/app/services/violation_catalog.py` (`detect_mechanical`). |
| Response | The engine emits **exactly** the expected violation IDs and never fabricates an unverifiable violation (e.g. `no_rkn_notification` must not be issued by code; a broken crawl must fail closed to zero violations). |
| **Response measure** | On the labelled fixture set, detected violations match the expected set with **100% precision and 100% recall**; **0** fabricated violations for unverifiable facts; a malformed crawl yields **0** violations. |

**Rationale.** The product's core value is an accurate list of 152-ФЗ violations with
potential fines. A false positive can mean an invented multi-million-ruble fine; a false
negative hides a real risk. The mechanical detector must therefore be provably correct on
known cases and must fail closed rather than fabricate findings from unverifiable facts.

**Traceability**
- Product pipeline: rule-engine fact→violation comparison (see `CLAUDE.md`, Contract №1).
- 152-ФЗ relevance: ст. 9 (consent), ст. 7 (third-party transfer), ст. 18 ч.5 (localization) mapping.
- QRT: [QRT-03](./quality-requirement-tests.md#qrt-03) — `backend/tests/test_violation_catalog.py`.
- ADR: [ADR-0001 — hybrid LLM analysis guarded by a deterministic violation catalog](./architecture/adr/0001-full-llm-analysis-pipeline.md).

---

## Maintenance

- Each QR has at least one automated QRT that runs in CI ([#71](https://github.com/ValekusVachpekus/pdn-control/issues/71)); a failing QRT blocks merge.
- Changing product behaviour that affects a QR requires updating the QR, its QRT, and the relevant fixtures in the same PR.
- New quality-relevant features should add or extend QRs rather than bypass these gates.
