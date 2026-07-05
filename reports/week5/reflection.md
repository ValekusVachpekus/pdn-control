# Reflection — Week 5

## Learning points
- **"Done" for an integration feature is not the same as "live".** Social login (#72) and domain
  e-mail (#104) were fully implemented and merged, but neither can be switched on without a
  customer-side action — registering the Yandex/VK OAuth apps to supply `client_id`/`secret`, and
  adding the SPF/DKIM DNS records. We learned to state Definition of Done for such features as
  "implemented + documented how to activate", and to carry the activation explicitly as the
  customer's next-Sprint request rather than treating the code merge as the end.
- **A contract change must move its test in the same step.** Replacing the login stub with the real
  OAuth redirect flow broke CI because the e2e test still asserted the old stub's response
  ([#122](https://github.com/ValekusVachpekus/pdn-control/pull/122)). The lesson: when an endpoint's
  behaviour changes, the test that pins that behaviour is part of the same change, not a follow-up.
- **Documenting architecture forces decisions to be named.** Writing the three views and the ADRs
  made us articulate the pipeline as it actually is — hybrid, not "pure LLM": the LLM proposes
  violations but `report_builder` validates each against a fixed `violation_catalog`, and GeoIP is a
  deterministic offline lookup. Capturing this in ADR-0001 turned an implicit design into a
  reviewable, referenceable decision.
- **Carrying out last Sprint's retro actions paid off visibly.** The two Sprint 2 action points
  (CI auth/UI smoke coverage + a pre-demo production dry-run) meant MVP v2's UAT ran clean, in
  contrast to the six defects the customer found in Sprint 2. Retrospective actions are only worth
  writing if the next Sprint actually executes them.

## Validated assumptions
- **Passwordless OTP + social login is acceptable to the customer.** The customer accepted the
  MVP v2 increment (UAT-06/07 pass) and did not request changes to the authentication model; the
  only follow-up is activating the providers with their own credentials/DNS.
- **The Week 4 UI fixes resolved the customer's concerns.** All six defects from the 2026-06-27 UAT
  were fixed and re-checked live; the customer confirmed the report/history are no longer confusing.
- **Maintained architecture/process docs are increment-worthy.** Our assumption that a Sprint mixing
  a real feature (auth) with documentation (views/ADR/process, hosted site) would still be accepted
  as a valuable increment held — the customer approved it.

## Friction and gaps
- **Auth is not yet exercisable in production.** Until the customer registers the OAuth apps and
  adds the e-mail DNS records, social login and domain e-mail cannot be tested against the real
  providers — they run in the merged-but-dormant state.
- **Tests lagged an implementation change once.** The #122 CI break showed our e2e assertions can
  drift from the code within a single PR; addressed by the retrospective action to update contract
  tests in the same commit.
- **US-13 still carried over.** The scan-finished notification
  ([#70](https://github.com/ValekusVachpekus/pdn-control/issues/70)) remained de-prioritised behind
  auth and documentation and is still open.

## Planned response
- **Activate auth in production** once the customer supplies the OAuth `client_id`/`secret` and the
  e-mail SPF/DKIM DNS records (the customer's stated next-Sprint request), then run the OTP/OAuth
  login paths in the pre-demo dry-run.
- **Enforce "contract change ⇒ test change in the same PR"** via the reviewer checklist item added
  in the [retrospective](retrospective.md), so a stale e2e test cannot land again.
- **Pick up US-13** ([#70](https://github.com/ValekusVachpekus/pdn-control/issues/70)) in the next
  Sprint backlog, building the scan-finished notification on the new e-mail provider from #104.
