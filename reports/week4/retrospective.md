# Sprint Retrospective — Sprint 2

## What went well
1. **Deployment to the customer's own infrastructure.** We moved the service onto the customer's
   server and domain behind Caddy on 443 with a TLS certificate. The customer confirmed during the
   Sprint Review that the migration is fine and accepted the increment.
2. **Quality automation landed as a maintained asset.** We delivered the CI quality gate (required
   jobs, per-module coverage gate, SAST) together with explicit quality requirements and automated
   quality requirement tests (anti-SSRF, determinism, rule-engine correctness).
3. **Determinism via GeoIP.** Replacing the LLM with GeoIP for hosting/IP detection removed a
   source of non-deterministic results and made that part of the audit reproducible.
4. **Clean UAT acceptance.** The customer executed all five UAT scenarios live and they passed
   5 / 5; the Sprint Goal (quality + deployment on their infrastructure) was confirmed as met.

## What did not go well
1. **UI defects reached UAT.** Six small UI/UX issues (loading screen on an unauthenticated check,
   the "New check" button not being discoverable from empty history, a useless "0" fine, empty
   "data collection points" for main-page forms, and the cookie violation addressed to the
   Marketer instead of the Developer) were first spotted by the *customer* during UAT rather than
   by us beforehand. We had no automated UI/front-end smoke check to catch them, so they surfaced
   in front of the stakeholder.

## What we changed compared to the previous Sprint
Both action points from the Sprint 1 retrospective were carried out:
1. **Automated tests in CI.** We added automated/integration tests and wired them into a CI quality
   gate ([#71](https://github.com/ValekusVachpekus/pdn-control/issues/71)), instead of relying on
   manual smoke-checks as in Sprint 1.
2. **Review-buddy workflow.** We assigned a designated reviewer per PBI during planning, which made
   reviews faster and more structured than in the first half of Sprint 1.

## Action points (process improvements for the next Sprint)
1. **Add a front-end UI smoke check before review/demo.** Introduce a minimal automated UI smoke
   test (or a short manual UI checklist run before each Sprint Review) so UI defects are caught by
   the team, not by the customer during UAT.
2. **Pre-demo dry-run on the production deployment.** Do a full scan-to-report walkthrough on the
   live customer environment shortly before the Sprint Review, so state-dependent UI issues
   (empty history, zero values, role labels) are seen and fixed before the meeting.
