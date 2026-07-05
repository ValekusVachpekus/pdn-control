# Sprint Retrospective — Sprint 5

## What went well
1. **Real authentication landed end-to-end.** The stub login was replaced by a working
   passwordless e-mail OTP flow ([#55](https://github.com/ValekusVachpekus/pdn-control/issues/55))
   and a real Yandex/VK OAuth 2.0 redirect flow
   ([#72](https://github.com/ValekusVachpekus/pdn-control/issues/72), VK via VK ID / PKCE), with
   consent capture (152-ФЗ ст. 9) and an httpOnly session. All 14 Sprint 5 milestone issues were
   closed and CI stayed green on `main`.
2. **Clean UAT acceptance of MVP v2.** The customer executed the new scenarios (UAT-06/07) live on
   their own infrastructure (`pdn.neurolife.tech`) and they passed; the customer accepted the
   increment. Both action points from the Sprint 2 retrospective were carried out beforehand (see
   below), so — unlike Sprint 2 — no UI defects surfaced in front of the stakeholder.
3. **All six Week 4 UAT feedback items were closed in-Sprint.** The customer-raised UI/UX defects
   (#99–#103) were fixed and shipped in the same increment as the customer-feedback response, not
   deferred.
4. **Architecture and process became a maintained asset.** We delivered three architecture views
   (static/dynamic/deployment) + four ADRs (#107–#109), documented the development process, and
   published a hosted docs site (#111) — quality/documentation work delivered as a first-class
   increment, without weakening the Assignment 4 quality gates.

## What did not go well
1. **The OAuth PR broke CI on the way in.** The OAuth change
   ([PR #122](https://github.com/ValekusVachpekus/pdn-control/pull/122)) failed the
   `backend-integration` job because the end-to-end test still asserted the **old login stub**
   (a `501` on `POST /oauth/{provider}`) while the new redirect flow returns different responses.
   The implementation had moved but its e2e test had not, so the regression was caught by CI rather
   than by the author before pushing, and required follow-up commits to realign the assertions with
   the new flow.

## What we changed compared to the previous Sprint
Both action points from the Sprint 2 retrospective were carried out:
1. **Front-end / auth smoke coverage in CI.** We added automated auth tests (bcrypt + JWT — signing,
   tampering, expiry) and rule-engine/report tests, and put `auth.py` under the coverage gate
   ([#110](https://github.com/ValekusVachpekus/pdn-control/issues/110)) — closing the "no automated
   UI/front-end check" gap that let six defects reach the customer in Sprint 2.
2. **Pre-demo dry-run on the production deployment.** We ran a full scan-to-report walkthrough on
   the live customer environment (`pdn.neurolife.tech`) before the Sprint Review, so state-dependent
   UI issues were seen by the team first — and this Sprint the UAT ran clean.

## Action points (process improvements for the next Sprint)
1. **Keep tests in lock-step with the code in the same PR.** When a stub is replaced by a real
   implementation, its e2e/integration assertions must be updated in the *same* commit — add a
   reviewer checklist item "does this PR change an endpoint's contract? update its e2e test" so a
   contract change never lands with a stale test (the root cause of the #122 CI break).
2. **Extend the pre-demo dry-run to the new auth paths.** The Sprint 2 dry-run covered scan→report;
   for the next review also walk the OTP and OAuth login paths on production once the customer's
   credentials/DNS are in place, so the newly-activated auth is exercised before the demo.
