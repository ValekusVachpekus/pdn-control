# ADR-0004: Single-host Docker Compose stack behind Caddy with automatic TLS

- **Status:** Accepted
- **Recorded:** 2026-06-29 (Sprint 5) — documents the deployment decision from the Assignment 4 Sprint.
- **Deciders:** product team, with the customer (who hosts on their own infrastructure).
- **Quality requirement(s) addressed:** [QR-01 — Confidentiality](../../quality-requirements.md#qr-01--crawler-confidentiality-against-ssrf) (TLS + single exposed boundary) and operationally supports [QR-02 — reproducibility](../../quality-requirements.md#qr-02--deterministic-scan-results).

## Context

The product has several runtime parts (API, worker, crawler, PDF service, Postgres, Redis,
frontend). The customer is an SMB that wanted to **host the service on their own VM and point
their domain at it**, and the increment had to be **internet-accessible over TLS** for user
acceptance testing — without the team standing up a Kubernetes cluster or managing certificates by
hand.

## Decision

Deploy the whole product as **one Docker Compose stack on a single host**, fronted by **Caddy** on
`:443`:

- `backend/docker-compose.yml` defines all services; `docker compose up` brings the system up
  reproducibly with pinned images and a `pgdata` volume for durable state.
- **Caddy** is the only internet-facing component; it terminates **automatic TLS** (Let's Encrypt)
  and reverse-proxies static requests to the frontend and `/api/*` to the backend. Internal
  service ports are not exposed publicly (in dev they are mapped to `localhost`).

## Consequences

- **Positive:** trivial for the customer to operate (`docker compose up` on their VM), one network
  boundary to secure, automatic certificate management, and a reproducible environment that
  matches dev. One clear place (Caddy) to terminate TLS and route.
- **Negative / risks:** **single-node** — no horizontal scaling or HA; Postgres and Redis are
  single instances and the `pgdata` volume is the backup/durability boundary; throughput is bound
  by `MAX_CONCURRENT_SCANS` and worker concurrency. Scaling out would require revisiting this ADR.

## Alternatives considered

- **Managed Kubernetes / multi-node:** rejected for an SMB MVP — disproportionate operational cost.
- **Bare-metal processes without containers:** rejected — not reproducible, harder for the
  customer to run and for the team to support.
- **Manual nginx + certbot:** rejected — Caddy gives automatic TLS with far less configuration.

## Related

- Config: `backend/docker-compose.yml`, Caddy reverse proxy ([#86](https://github.com/ValekusVachpekus/pdn-control/issues/86), [#88](https://github.com/ValekusVachpekus/pdn-control/issues/88)).
- [Architecture README — deployment view](../README.md#deployment-view--runtime-topology).
