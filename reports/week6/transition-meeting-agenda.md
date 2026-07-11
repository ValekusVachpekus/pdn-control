# Week 6 — Transition-Readiness Meeting & Customer Trial (agenda + script)

Working agenda for the Week 6 customer meeting. One recorded session is planned to cover
**transition-readiness discussion + customer trial + UAT + Sprint Review** together
(Assignment 6, Part 5.7 and Part 10.8). This file is preparation material; the outcomes
feed [`sprint-review-summary.md`](sprint-review-summary.md),
[`sprint-review-transcript.md`](sprint-review-transcript.md) and the Week 6 report.

## Logistics

- **Date / time:** TBD (before the Week 6 submission, Sunday 2026-07-12).
- **Participants:** the customer (product stakeholder) + the team (Ilya, Airat, Aleksandr).
- **Build under test:** `MVP v3` Week 6 trial (`v1.3.0`) on `https://pdn.neurolife.tech`.
- **Recording:** the session is recorded with the customer's consent; an English transcript
  goes to [`sprint-review-transcript.md`](sprint-review-transcript.md). Ask for recording
  consent at the start. Private exact timecodes for each activity (transition / trial / UAT
  / Sprint Review) go only into the Week 6 Moodle PDF, not the public repository.
- **Precondition to confirm before the meeting:** the customer has provided the production
  OAuth `client_id`/`client_secret` (#129) and applied the SPF/DKIM DNS records (#130); the
  trial is deployed and reachable.

## Agenda (target ~40–50 min)

1. **Intro & recording consent (2 min).** Purpose of the session; confirm recording consent.
2. **Sprint 6 goal & trial increment demo (8 min).** What the Week 6 trial delivers:
   production social login on the customer's keys and real e-mail from the verified domain.
3. **Transition-readiness discussion (12 min)** — cover every point (Part 5.2):
   - Is the product complete enough for transition? Which parts are ready, which still need changes?
   - Is the customer already using the product? If yes, how? If not, why not?
   - Is it already deployed / operated on the customer side? If not, what blocks that?
   - What must happen in Week 7 to complete the transition?
   - How do we increase the chance the product stays useful after final delivery?
4. **Customer-facing documentation review (8 min).** Walk the customer through the doc set
   (checklist below) and capture what is clear, unclear, or missing (Part 3.6, Part 5.3).
5. **Customer trial + UAT execution (12 min).** Let the customer drive the trial independently
   or with minimal guidance (script below); execute the maintained UAT scenarios.
6. **Wrap-up & confirmation (5 min).** Record the handover level, the confirmation status, and
   convert any problems into issues.

## Customer-facing documentation review checklist (Part 3.6)

Ask the customer to review and rate each as clear / unclear / missing:

- [ ] [`README.md`](../../README.md) — is it clear what the product is and how to reach it?
- [ ] [`docs/customer-handover.md`](../../docs/customer-handover.md) — ownership, configuration,
      run/restore/verify steps, entry points, transition status.
- [ ] Current access / run instructions — can they follow them without the team?
- [ ] Deployment / installation instructions (where relevant).
- [ ] Troubleshooting / support notes.
- [ ] Known limitations.

Capture verbatim which parts the customer found clear, unclear, or missing → Week 6 report
item 15 and, where actionable, new issues.

## Customer trial script (independent use, Part 5.4)

Let the customer perform these on `https://pdn.neurolife.tech` with minimal guidance:

1. Open the site; register / sign in.
2. **Production social login (UAT-08):** sign in with Yandex; sign in with VK; confirm both
   return authenticated; first-time registration records the ПДн consent.
3. **Real e-mail login (UAT-09):** request an e-mail login code to a real external mailbox;
   confirm the e-mail arrives from the customer's verified domain and the code signs in.
4. Run a check of a known website; confirm the scan reaches `done` and the report opens.
5. Download the PDF report.
6. (Optional) confirm a scan-finished notification e-mail is received (US-13).

## UAT to execute / re-confirm (Part 9)

- **New (MVP v3 Sprint 6):** UAT-08 (production social login), UAT-09 (real domain e-mail).
  See [`docs/user-acceptance-tests.md`](../../docs/user-acceptance-tests.md).
- **Re-confirm core (as time allows):** UAT-01 (scan → report), UAT-04 (PDF), UAT-05 (anti-SSRF).
- Record for each: Pass / Fail / needs-change, plus the most important feedback points.

## Outcomes to capture (drives the Week 6 report and Part 8)

- **Handover level reached** (Part 8.3): `Ready for independent use` / `Independently used by
  customer` / `Deployed or operated on customer side`.
- **Customer-confirmation status** (Part 8.5): `Accepted` / `Accepted with follow-up items` /
  `Not yet accepted`.
- Did the customer confirm readiness for independent use after Week 7? Did they independently
  use the trial? Is it deployed / operated on their side? (Part 5.5)
- **Feedback → issues:** every product / deployment / documentation / handover problem the
  customer raises becomes a traceable issue or transition action (Part 5.6), assigned to the
  Sprint 7 milestone where it is follow-up work.
- Note anything the customer wants that is out of scope for Week 7.

## Post-meeting artifacts (owners)

- English transcript → [`sprint-review-transcript.md`](sprint-review-transcript.md) (Ilya).
- Sprint Review summary → [`sprint-review-summary.md`](sprint-review-summary.md).
- Fill the `TODO`s in [`README.md`](README.md) (feedback table, doc-review summary, transition
  summary, UAT results, contribution table).
- Update [`docs/customer-handover.md`](../../docs/customer-handover.md) with the confirmed
  handover level and confirmation status.
- New feedback issues on the Sprint 7 milestone; retrospective and reflection after the review.
- Private exact timecodes and access credentials → Week 6 Moodle PDF only.
