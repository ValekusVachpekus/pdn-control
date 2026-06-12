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

- **Deployment URL:** http://10.93.26.163:8080/
- **Hosting:** university VM. Accessible from the **Innopolis University network**, where
  the TA can reach it for grading. (A public VPS is not required for Assignment 2; external
  access for the customer's own testing is tracked as a separate product follow-up.)
  <!-- TODO: if the TA needs VPN/on-campus instructions to reach the university network, state them here. -->
- **Runnable fallback:** if the VM is unreachable, the product can also be run locally via
  the root README — see [Local setup instructions](#local-setup-instructions) below.

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
Open http://10.93.26.163:8080/ from the Innopolis University network.
<!-- TODO: add any dedicated limited-permission test credentials if login is required
     (NEVER real/production secrets), and VPN/on-campus access notes if needed. -->

**Steps:**
1. <!-- TODO: open the deployment URL --> TODO
2. <!-- TODO: enter a test URL into the scan input and start a scan --> TODO
3. <!-- TODO: observe the scan/report state change --> TODO

**Expected result:**
<!-- TODO: what the TA should see (e.g., scan status transitions, a rendered report or
     report stub with score / fine / violations). -->
TODO
