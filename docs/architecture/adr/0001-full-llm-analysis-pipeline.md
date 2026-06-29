# ADR-0001: Hybrid LLM analysis guarded by a deterministic violation catalog

- **Status:** Accepted
- **Recorded:** 2026-06-29 (Sprint 5) — documents a decision already implemented since MVP v1.
- **Deciders:** product team, at the customer's explicit request.
- **Quality requirement(s) addressed:** [QR-03 — Correct fact-to-violation mapping](../../quality-requirements.md#qr-03--correct-fact-to-violation-mapping-rule-engine) (also supports [QR-02](../../quality-requirements.md#qr-02--deterministic-scan-results)).

## Context

The product must turn crawler **facts** (Contract #1) into a list of 152-ФЗ violations with
articles and potential fines. Two failure modes are unacceptable: **fabricated violations**
(inventing a multi-million-ruble fine the site does not actually incur) and **missed obligations
that require reading natural-language policy text** (where pure pattern-matching is too weak). The
customer explicitly wanted the legal verdicts to come from an LLM analysing the policy/consent/
cookie texts, not from a hand-written rule tree.

## Decision

Use a **hybrid** pipeline rather than either a pure rule-engine or a pure LLM:

1. The **LLM** (`llm_analyzer`) reasons over the extracted policy/consent/cookie texts plus fact
   context and proposes verdicts.
2. A fixed **violation catalog** (`violation_catalog`) owns the canonical title, 152-ФЗ article,
   severity, and fine for each violation type. `report_builder` only emits an LLM-proposed
   violation if `precondition_holds(vtype, crawl)` confirms the underlying crawl fact — otherwise
   the proposal is dropped. Code-verifiable violations are emitted directly by
   `detect_mechanical`.
3. **No degraded fallback:** if the crawl or the LLM call fails, the scan is marked `failed`
   rather than silently returning a partial or guessed report.

## Consequences

- **Positive:** the catalog is a deterministic guardrail that prevents the LLM from fabricating
  fines (directly serving QR-03) and gives stable articles/amounts; the LLM still handles the
  text-understanding the customer asked for. Correctness risk is concentrated at one reviewable
  boundary (`report_builder` + catalog) that the QRTs target.
- **Negative / risks:** every scan depends on a reachable, paid LLM API; LLM latency dominates the
  pipeline (mitigated by the Redis cache, see ADR-0002/QR-02); "fail closed" means a flaky LLM
  surfaces as a failed scan instead of a degraded one.

## Alternatives considered

- **Pure rule-engine:** rejected — cannot judge whether a policy *text* actually declares a
  practice; the customer wanted LLM text analysis.
- **Pure LLM (no catalog):** rejected — non-deterministic articles/fines and a real risk of
  fabricated violations, which QR-03 forbids.

## Related

- Code: `backend/app/services/llm_analyzer.py`, `violation_catalog.py`, `report_builder.py`.
- [Architecture README — static & dynamic views](../README.md).
