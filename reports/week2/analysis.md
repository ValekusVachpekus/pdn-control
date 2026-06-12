# Week 2 Analysis — ПДн Контроль

## Learning points

- **User stories.** Writing stories in the `As a … I want … so that …` form forced us to
  separate the *action* from the *value*. Several early items were phrased as features
  (e.g. "show a 0–100 score") rather than user value; reframing them around the business
  owner's goal (understanding financial risk at a glance) made prioritization much easier.
- **Prioritization (MoSCoW).** Assigning Must/Should/Could/Won't relative to the
  end-of-course scope exposed disagreements we had not noticed: we initially treated the
  0–100 score (US-07) as secondary, while the customer considers it as important as the
  total fine. MoSCoW is a conversation tool, not a fixed label — the customer moved US-07
  from Should to Must in a single sentence.
- **Prototyping.** A clickable Figma prototype communicated the Home → Report flow and the
  free-tier gating far faster than a written description. The customer recognized the
  design immediately ("I saw it last Monday") and gave concrete, actionable feedback
  (make the fine larger and higher-contrast) that text alone would not have produced.
- **Interface design.** Deciding the externally used interface is **graphical** (a web
  SPA) clarified that the crawler/parser and PDF service are *internal* interfaces, not
  things the end user touches. This kept the Assignment 2 interface artifact focused on
  one prototype instead of over-documenting internal APIs.
- **MVP v0 deployment.** Getting a runnable foundation onto a server surfaced an
  environment problem we had not planned for: the university VM is not reachable from the
  internet. "It runs on a machine" is not the same as "the TA and customer can open it."
- **Customer validation.** A short (~18 min) structured review with explicit yes/no
  approval questions was enough to lock down scope, monetization, and the payment
  provider. Preparing the approval questions in advance (`customer-meeting-questions.md`)
  kept the meeting efficient.

## Validated assumptions

- **Confirmed — primary persona is the SMB owner.** We assumed the main user is a small/
  medium business owner; the customer confirmed this is the primary persona.
- **Confirmed — free/paid one-time model.** We assumed a free tier (total fine + number of
  violations only) plus a paid tier (full violation list) with a one-time payment; the
  customer approved this exact split.
- **Confirmed — CloudPayments as the provider.** We were unsure which payment provider to
  target (YooKassa/Stripe/other); the customer fixed it as **CloudPayments** and said we
  do not need to implement the payment system ourselves.
- **Rejected — the fine is more important than the score.** We assumed the total fine
  (US-02) should outrank the 0–100 score (US-07). The customer rejected this: the two must
  carry **equal** priority and be shown side by side. US-07 was raised to Must Have.
- **Confirmed — the university VM deployment is sufficient for grading.** We assumed
  deploying on the university VM would be enough for review. Confirmed for Assignment 2:
  the address (`http://10.93.26.163:8080/`) is reachable from the Innopolis University
  network, where the TA can open it. A public host is *not* required for the assignment.
  External access for the customer's own testing (a product concern raised in the review)
  is a separate follow-up, not a grading blocker.
- **Confirmed-with-dependency — email registration is feasible.** We assumed email/SMTP
  registration is doable; confirmed in principle but **blocked** until the customer
  provides a domain.

## Needs clarification

- **Legal accuracy of the fine calculation (US-02)** — what is the basis: a KoAP range,
  the maximum, or typical practice? One number or a "from–to" range? Pending review by the
  customer's lawyer.
- **152-FZ article references (US-04)** — is the article number enough, or are specific
  parts/clauses and tracking of the latest KoAP amendments required?
- **External access for the customer** — the customer wants to test MVP v0 himself from
  outside the university network; a VPS/domain is to be requested from his contact. This is
  a product follow-up and does not affect Assignment 2 grading (the TA accesses the VM on
  the university network).
- **Domain for SMTP** — required for email registration; to be provided by the customer.
- **Legal texts** — privacy policy and terms of use are placeholders; the customer will
  provide the real text later.
- **Check reliability** — known parser bugs cause some violations to be missed, which
  directly undermines trust in the headline numbers (fine, violation count).

## Planned response

- **US-07 (0–100 score) → Must Have.** Already updated in
  [user-stories.md](user-stories.md). On the result screen the score and the total fine
  are shown together with equal visual emphasis. Affects US-02/US-07 and the prototype's
  Report screen.
- **US-02 visual emphasis.** Make the total fine larger / higher-contrast on the result
  screen (Action point 1; affects US-02 and the prototype).
- **Free-tier scope fixed (US-05/US-06).** Free version shows only the total fine and the
  number of violations; the detailed violation list moves to the paid tier. Reflected in
  [user-stories.md](user-stories.md) notes and the gating in the prototype.
- **Payment (US-06).** Target CloudPayments only; no custom payment system.
- **Deployment.** Keep MVP v0 on the university VM for Assignment 2 grading
  (see [mvp-v0-report.md](mvp-v0-report.md)); arrange external access (VPS/domain) afterwards
  so the customer can self-test. Affects US-01/US-06 delivery for MVP v1.
- **Parser reliability (US-01).** Prioritize fixing the parser/check bugs that cause
  missed violations, since the free-tier value proposition depends on accurate counts.
- **Legal validation (US-02/US-04).** Route the fine calculation and article references
  through the customer's lawyer before treating them as production-correct.
