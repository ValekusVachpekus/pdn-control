# Week 4 Reflection

## Learning points
- **Quality work is a deliverable, not overhead.** A Sprint with fewer new features but explicit
  quality requirements, automated quality requirement tests, a CI quality gate, and an updated
  Definition of Done still produced an increment the customer accepted. Framing the Sprint Goal
  around quality + deployment made that value visible to the stakeholder.
- **Determinism comes from removing the LLM where it is not needed.** Moving hosting/IP detection
  to GeoIP taught us that the cheapest reliability win was taking the model out of a path that only
  needed a lookup, not adding more checks around it.
- **UAT is where the user's mental model meets the product.** Running the scenarios live on the
  customer's own deployment surfaced UI issues (a loading screen on a blocked check, a confusing
  "0" fine, empty "data collection points", a mis-targeted cookie violation) that our automated
  tests did not cover because they were about presentation, not logic.
- **Owning the deployment changes the conversation.** Once the service ran on the customer's server
  and domain, the discussion shifted to concrete operational topics (email delivery, DNS) rather
  than prototypes.

## Validated assumptions
- **Quality-focused Sprint is acceptable to the customer.** Our assumption that we could spend the
  Sprint on quality/automation/deployment instead of new features was confirmed — the customer
  approved the increment and agreed the Sprint Goal was met.
- **GeoIP is sufficient for hosting/localization detection.** Replacing the LLM with GeoIP was
  validated by the deterministic-scan quality requirement test and confirmed acceptable by the
  customer (no requested changes to the checks).
- **Anti-SSRF and the free/paid gating meet expectations.** The customer executed the SSRF and
  free-vs-paid scenarios and confirmed both behave as intended.

## Friction and gaps
- **No front-end UI test coverage.** All six review findings were UI/presentation defects that no
  automated check could catch, so they reached the customer during UAT.
- **Email sending is not wired.** The team decided at the review to use a third-party email
  provider; delivery is blocked on the customer adding the records the team will send.
- **Branch protection depends on a repo admin.** The required-checks/required-review rules on
  `main` are documented but must be applied by a repository admin to be active.
- **US-13 carried over.** The scan-finished notification
  ([#70](https://github.com/ValekusVachpekus/pdn-control/issues/70)) was de-prioritized in favour
  of quality and deployment work and remains open.

## Planned response
- **Fix the six review findings** in the next Sprint as the customer-feedback response (tracked in
  the Customer Feedback Response table of [`reports/week4/README.md`](README.md)).
- **Close the UI-testing gap** by adding a front-end UI smoke check / pre-demo dry-run, as agreed
  in the [retrospective](retrospective.md), so presentation defects are caught before UAT.
- **Wire email** via a third-party provider and send the customer the records to add.
- **Apply branch protection** on `main` (admin action) so the CI quality gate from
  [#71](https://github.com/ValekusVachpekus/pdn-control/issues/71) is enforced, not just configured.
- **Carry US-13** ([#70](https://github.com/ValekusVachpekus/pdn-control/issues/70)) into the next
  Sprint backlog.
