# ADR-0002: Deterministic offline GeoIP for hosting country instead of an LLM guess

- **Status:** Accepted
- **Recorded:** 2026-06-29 (Sprint 5) — documents a decision implemented in the Assignment 4 Sprint.
- **Deciders:** product team.
- **Quality requirement(s) addressed:** [QR-02 — Deterministic scan results](../../quality-requirements.md#qr-02--deterministic-scan-results).

## Context

Localization compliance (ст. 18 ч.5 — databases of RU citizens must be hosted in the RF) depends
on the **hosting country** of the scanned site's server. Initially this fact was inferred by the
LLM, which made it non-deterministic and occasionally wrong — the same site could be reported as
hosted in different countries on different runs, exactly the kind of instability the customer
flagged ([#34](https://github.com/ValekusVachpekus/pdn-control/issues/34)).

## Decision

Resolve the server country **deterministically from the IP** using an **offline GeoIP2 (MaxMind)
database** inside the crawler (`crowler/pdn_parser/geoip.py`, [#75](https://github.com/ValekusVachpekus/pdn-control/issues/75)):

- The crawler resolves the target's IP and looks up the country locally (no network call, no LLM).
- It emits `server_country`, a `server_country_source` ("geoip"), and a confidence level.
- **It never fabricates a country:** if the GeoIP DB is missing or the lookup is inconclusive, it
  returns `server_country = None` and the scan still succeeds; the LLM is not used to "guess" it.

## Consequences

- **Positive:** the hosting-country fact is reproducible across runs (serving QR-02), faster (no
  LLM round-trip for it), and honest about uncertainty instead of hallucinating. The localization
  verdict built on top of it becomes stable.
- **Negative / risks:** requires shipping/updating the MaxMind DB in the crawler image
  (`scripts/download_geoip.py`, Dockerfile build step); GeoIP accuracy is bounded by the database
  freshness; `None` results mean localization cannot always be asserted.

## Alternatives considered

- **LLM-inferred country:** rejected — non-deterministic and error-prone, the root cause of the
  instability.
- **Online GeoIP API:** rejected — adds an external dependency and latency to every scan and
  reintroduces a non-reproducible network call; offline DB is deterministic.

## Related

- Code: `crowler/pdn_parser/geoip.py`, `crowler/scripts/download_geoip.py`.
- [QRT-02](../../quality-requirement-tests.md#qrt-02), bug [#34](https://github.com/ValekusVachpekus/pdn-control/issues/34), task [#75](https://github.com/ValekusVachpekus/pdn-control/issues/75).
