# Reflection — Week 6

## Learning points
- **"Done" fails again at the integration seam, not just at customer activation.** Sprint 5
  taught us that a merged feature is not "live" until the customer activates it; Sprint 6 showed
  the same lesson one seam earlier — between our own front and back ends. The OAuth backend
  (merged in Sprint 5) and the OAuth buttons both looked complete, yet the buttons were never
  wired to the flow, so the login path was broken in production
  ([#129](https://github.com/ValekusVachpekus/pdn-control/issues/129) →
  [PR #133](https://github.com/ValekusVachpekus/pdn-control/pull/133)). A feature is done when the
  path works end-to-end, not when both ends exist independently.
- **Handover is decided by operability and ownership, not by a feature checklist.** The customer
  accepted the product because they could use it themselves, the documentation was sufficient to
  run it without us, and the repository transfer could proceed — not because every optional item
  was finished. They explicitly took on the remaining production OAuth keys themselves. Acceptance
  turned on "can the customer run and own this", which is a different bar than "is every feature
  switched on".
- **A verification pass just before a milestone catches what mid-sprint merges miss.** Auditing
  the auth path before the transition meeting caught a production-breaking gap that had survived a
  merge in the previous sprint. Verification concentrated right before delivery is worth the cost.

## Validated assumptions
- **The customer is comfortable owning post-handover activation.** Our plan to hand over with the
  OAuth keys as a documented customer step was validated directly: the customer said to leave the
  login as is and that they would configure the keys themselves, with no further sprints requested.
- **The handover level "deployed and operated on the customer side" is real.** The product runs on
  the customer's own server and domain; the customer confirmed they had already used it and
  considered it ready for handover.
- **The documentation is sufficient for independent operation.** The customer confirmed the README
  and launch instructions were clear, that they could run the service without us, and that the
  technical and legal limitations were understood.

## Friction and gaps
- **Production OAuth keys are not in place at handover.** Yandex/VK login runs on a test
  application until the customer registers the production apps and supplies `client_id`/`secret`;
  this is carried as a documented customer-side step, not a blocker to acceptance.
- **No automated check drives the real OAuth UI path.** The front/back wiring gap reached Sprint 6
  undetected because nothing exercised the actual redirect flow through the SPA; the retrospective
  action point adds an integration smoke for it.
- **The repository transfer is initiated but not yet complete.** The customer provided their
  account and the transfer was started during the review; completing it is Week 7 work.

## Planned response (Week 7)
- **Complete the transition rather than open new scope.** The customer requested no further feature
  iterations, so Week 7 focuses on finishing the handover: complete the GitHub repository transfer,
  close `CHANGELOG [Unreleased]` into the `v1.3.0` release, and record the confirmed handover level
  and acceptance status in [`docs/customer-handover.md`](../../docs/customer-handover.md).
- **Ship the activation checklist for the customer.** Ensure `docs/customer-handover.md` lists the
  exact steps to drop in the production OAuth keys and confirm the e-mail DNS, so the customer can
  switch social login fully on themselves after delivery.
- **Add the OAuth UI integration smoke** from the [retrospective](retrospective.md) so a
  wired-but-dead login path cannot recur.
