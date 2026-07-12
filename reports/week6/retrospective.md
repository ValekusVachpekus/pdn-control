# Sprint Retrospective — Sprint 6 (Week 6)

## What went well
1. **The customer accepted MVP v3 and confirmed the handover.** On 2026-07-11 the customer
   executed the trial/UAT scenarios live on their own infrastructure (`pdn.neurolife.tech`),
   accepted the increment, and confirmed the handover level as **deployed and operated on the
   customer side**. The customer stated the product was ready, that they had already used it, and
   that nothing else was required for the handover — and initiated the GitHub repository transfer.
2. **All Sprint 6 milestone issues were closed and CI stayed green.** Production authentication
   ([#129](https://github.com/ValekusVachpekus/pdn-control/issues/129)), production e-mail with
   sender-domain verification ([#130](https://github.com/ValekusVachpekus/pdn-control/issues/130)),
   and the customer-handover / documentation package
   ([#127](https://github.com/ValekusVachpekus/pdn-control/issues/127)) all landed, plus a security
   hardening change binding internal service ports to localhost
   ([PR #137](https://github.com/ValekusVachpekus/pdn-control/pull/137)).
3. **Authentication became functional end-to-end.** With the frontend wired to the backend redirect
   flow (below) and e-mail now sent from a verified domain, Yandex/VK and e-mail-code login work as
   a complete path; only the customer's own production OAuth keys remain to be dropped in, which the
   customer chose to configure themselves.
4. **Handover documentation was delivered as a first-class artifact.** `docs/customer-handover.md`
   and `AGENTS.md` gave the customer an ownership matrix, configuration and run/restore/verify
   steps, and entry points; the customer confirmed the documentation and launch instructions were
   sufficient to operate the product without us.

## What did not go well
1. **The frontend lagged the backend on OAuth.** The Yandex/VK backend redirect flow had been
   merged back in Sprint 5 ([PR #122](https://github.com/ValekusVachpekus/pdn-control/pull/122)),
   but the SPA was never wired to it: `frontend/app/api.js` still issued a `POST` expecting a JSON
   user and carried a stale "OAuth not implemented (501)" comment. In production the "Sign in with
   Yandex/VK" buttons would have been dead despite a backend that reported "done". The gap was only
   found during the pre-handover code audit in Sprint 6 and closed by
   [PR #133](https://github.com/ValekusVachpekus/pdn-control/pull/133) (#129). A feature was treated
   as complete because both halves were merged, even though the two halves were not connected.

## What we changed compared to the previous Sprint
- **We extended pre-demo verification to the auth path.** The Sprint 5 retrospective action point
  was to exercise the login flows before the demo; this Sprint that check was run as a deliberate
  pre-handover audit of the OAuth path, which is exactly what surfaced the dead frontend buttons in
  time to fix them (PR #133) rather than in front of the customer.
- **We activated the customer-side dependencies instead of leaving them dormant.** In Sprint 5,
  social login and domain e-mail were merged but not switchable without customer action; this
  Sprint the e-mail domain verification (#130) was completed and the OAuth wiring finished, leaving
  only the customer's own OAuth keys as an explicit, documented customer step.

## Action points (process improvements for Sprint 7)
1. **Verify features across the front/back seam, not just per half.** "Done" must mean the path
   works end-to-end through the real UI, not that both endpoints exist. Add an integration smoke
   that drives the actual redirect UI path so a wired-but-dead button cannot pass review as done —
   this is the direct root-cause fix for the #129/#133 gap.
2. **Make customer-side activation self-service.** Since the customer will configure the production
   OAuth keys themselves post-handover, keep the activation steps (OAuth `client_id`/`secret`, DNS)
   as an explicit checklist in `docs/customer-handover.md`, so the customer can switch them on
   without the team after final delivery.
