# MVP v0 Report — Week 2 (ПДн Контроль)

> MVP v0 is the runnable technical product foundation, evaluated by the TA. It does not
> need to implement a complete user story or reproduce the prototype — it must be
> accessible, runnable, and pass a smoke check.
>
> This file is a **skeleton**. Fill every `TODO` before submission.

## Purpose and description

<!-- TODO: 2–4 sentences. What the MVP v0 foundation is and what it demonstrates.
     E.g.: monorepo stack (frontend SPA + crawler/parser + PDF microservice) wired
     together; URL input triggers a scan; a report view renders the result JSON. -->
TODO

## Deployment URL / runnable-artifact link

<!-- TODO: PUBLIC, internet-accessible URL (NOT the internal university-VM address
     http://10.93.26.163:8080/, which is unreachable from the internet and does not
     satisfy Part 4.4). Add a VPS/tunnel URL here, or a runnable-artifact/package link. -->
- Deployment URL: TODO
- Runnable artifact (if not hosted): TODO

## Public video demonstration

<!-- TODO: public, sanitized video, shorter than 2 minutes. -->
- Video link: TODO

## Relationship to the prototype and proposed MVP v1 stories

<!-- TODO: which prototype screens / MVP v1 stories the foundation relates to.
     Reference stable US IDs. Example: US-01 (scan pipeline) is the primary story
     represented by the foundation, even if the end-to-end flow is incomplete. -->
- US-01 (Basic website scan): TODO
- US-02 / US-03 / US-04 (report rendering): TODO
- Prototype screens: TODO

## Current limitations, placeholders, and mocks

<!-- TODO: list honestly. Known items from the customer review:
     - parser/check bugs (some violations not detected);
     - email registration blocked without a domain (SMTP);
     - `paid` gating is front-end-only (no server enforcement yet);
     - OAuth providers are stubs;
     - legal texts (privacy policy / terms) are placeholders. -->
TODO

## Local setup instructions

Local setup and run commands live in the root README:
[README.md → "Локальный запуск"](../../README.md#локальный-запуск).

## Repeatable smoke-check scenario

> Web/mobile smoke check: the application opens, primary navigation works, and at least
> one interactive data-flow element is demonstrated (form submission, API call, or state
> change).

**Access instructions:**
<!-- TODO: how the TA reaches the running product (public URL) and any dedicated
     limited-permission test credentials (NEVER real/production secrets). -->
TODO

**Steps:**
1. <!-- TODO: open the deployment URL --> TODO
2. <!-- TODO: enter a test URL into the scan input and start a scan --> TODO
3. <!-- TODO: observe the scan/report state change --> TODO

**Expected result:**
<!-- TODO: what the TA should see (e.g., scan status transitions, a rendered report or
     report stub with score / fine / violations). -->
TODO
