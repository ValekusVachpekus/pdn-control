# Week 7 — Final Transition Meeting & Sprint 7 Review (agenda + script)

Working agenda for the Week 7 customer call. One recorded session covers the
**Sprint 7 Review + final transition confirmation + Week 7 UAT re-confirmation**
together (Assignment 6, Part 8, Part 9.4 and Part 10.8). This file is preparation
material; the outcomes feed [`sprint-review-summary.md`](sprint-review-summary.md),
[`sprint-review-transcript.md`](sprint-review-transcript.md),
[`docs/customer-handover.md`](../../docs/customer-handover.md) and the Week 7 report.

Context: the customer already **accepted** the product at the Week 6 meeting (2026-07-11),
UAT 5 / 5 Pass, and requested no further feature iterations
(see [`../week6/sprint-review-summary.md`](../week6/sprint-review-summary.md)). Week 7 is
therefore a **short confirmation call**, not a new demo of new functionality.

## Logistics

- **Date / time:** TBD — to be scheduled before the Week 7 submission (Sprint 7 ends 2026-07-19).
- **Expected duration:** 20–30 min.
- **Participants:** the customer (product stakeholder) + the team.
- **Build under test:** `MVP v3` final (release candidate `v1.4.0`) on `https://pdn.neurolife.tech`.
- **Recording:** ask for recording consent at the start. The sanitized English transcript goes
  to [`sprint-review-transcript.md`](sprint-review-transcript.md); the private recording link and
  the exact per-activity timecodes go **only** into the Week 7 Moodle PDF, not the repository.
- **Preconditions to check before the call:**
  - the site is up and a scan reaches `done` (smoke run);
  - the current [`docs/customer-handover.md`](../../docs/customer-handover.md) has been sent to
    the customer in advance, so they can answer the acceptance question (Part 8.2) informedly;
  - the status of the GitHub repository transfer is known (initiated at Week 6);
  - it is known whether the customer has applied their own production OAuth keys.

## Agenda

1. **Intro and recording consent (2 min).** Purpose: final transition confirmation and the
   Sprint 7 Review. Confirm recording consent.
2. **Sprint 7 Review (8 min)** — cover every point required by Part 10.3:
   - the planned **Sprint 7 Goal**: complete the transition and deliver the final course version
     `MVP v3` (no new features — the customer requested none);
   - **delivered `MVP v3`**: the final release (`v1.4.0`), the finalized handover documentation,
     and the completed transition actions;
   - **resolved and unresolved follow-up items from Week 6**: production OAuth keys (customer
     self-service), e-mail/DNS, GitHub repository transfer;
   - **final transition status and usefulness**: is the product still running and being used?
   - **customer use / deployment / operational status** on their side;
   - **remaining risks and post-course limitations**: no legal guarantee, LLM API key cost and
     availability, crawler heuristics, no team maintenance after the course.
3. **Final transition confirmation (6 min) — Part 8.** Ask the acceptance question below
   explicitly and record the answer verbatim:
   - handover level reached (Part 8.3);
   - customer-confirmation status (Part 8.5);
   - any follow-up items the customer wants recorded.
4. **Repository transfer (4 min).** Finalize the GitHub repository transfer initiated at Week 6:
   confirm the receiving account, execute or schedule the transfer, and agree who owns the
   repository at submission time. Note that public report links must keep working.
5. **Week 7 UAT re-confirmation (5 min).** Re-confirm the customer-critical scenarios against the
   final build (script below).
6. **Wrap-up (3 min).** Restate the recorded handover level, confirmation status, and any
   follow-up actions; agree that the team will send the written confirmation request (below) for
   the record.

## Acceptance question to ask verbatim (Part 8.2)

> "Do you accept the current `docs/customer-handover.md` as sufficient for the reached handover
> level and the current transition scope?"

Record the answer as exactly one of:

- `Accepted`
- `Accepted with follow-up items` (list the items)
- `Not yet accepted` (record what blocks acceptance, and whether the blocker is on the team side,
  the customer side, or external)

## Written confirmation request (for the private evidence)

Send this in writing (messenger or e-mail) with a link to the current `docs/customer-handover.md`,
either before or right after the call. A screenshot of the request and the reply goes into the
**Week 7 Moodle PDF** (item 11) — it must not be committed to the public repository.

Text to send (Russian, as used with the customer):

> Добрый день. Финализируем передачу продукта «ПДн Контроль» по итогам курса.
> Актуальный документ передачи: <ссылка на docs/customer-handover.md>.
> Подтвердите, пожалуйста, письменно:
> 1) принимаете ли вы текущий `docs/customer-handover.md` как достаточный для достигнутого
>    уровня передачи и текущего объёма передачи;
> 2) какой уровень передачи зафиксировать: продукт готов к самостоятельному использованию /
>    вы уже самостоятельно им пользуетесь / он развёрнут и эксплуатируется на вашей стороне;
> 3) остаются ли пункты, которые вы хотите зафиксировать как follow-up.

English translation for the Moodle PDF: a request to confirm in writing (1) whether the current
`docs/customer-handover.md` is accepted as sufficient for the reached handover level and the
current transition scope, (2) which handover level to record, and (3) whether any follow-up items
remain.

If the customer does not reply before submission, the missing response is treated as a **blocker**,
not as implicit acceptance (Part 8.10): the request itself and the absence of a reply go into the
Week 7 Moodle PDF, and `reports/week7/README.md` states `Not yet accepted` with the reason.

## Week 7 UAT re-confirmation script (Part 9.3)

Maintained scenarios: [`docs/user-acceptance-tests.md`](../../docs/user-acceptance-tests.md).
Run against the final build on `https://pdn.neurolife.tech`:

- **UAT-08 — production social login.** At Week 6 this passed on a **test OAuth application**
  because the customer's production keys were not applied yet. If the customer has now applied
  their own `client_id` / `client_secret`, re-run it on the production application and update the
  UAT verdict note. If they have not, record that it remains a customer-side self-service step and
  keep the existing note honest.
- **UAT-09 — login-code e-mail from the verified domain.** Re-confirm a real e-mail still arrives.
- **UAT-01 — scan reaches `done` and the report opens** (core smoke).
- **UAT-04 — PDF report matches the web report** (core smoke).

Record for each: Pass / Fail / needs-change, plus any feedback.

## Outcomes to capture

- **Handover level** (Part 8.3) and **customer-confirmation status** (Part 8.5) — verbatim.
- Final ownership of the **GitHub repository** and the date of transfer.
- Whether the customer is **using** the product, and whether it is **deployed / operated** on
  their side.
- Any follow-up item, limitation, or support expectation the customer names → traceable issue or
  explicit transition action, and an honest row in the Week 7 feedback-response table.
- Anything out of scope for the course — record it as a limitation, not as a promise.

## Recording checklist

- [ ] Recording consent asked and granted at the start of the session.
- [ ] Timecodes noted per activity: Sprint 7 Review / transition confirmation / UAT — these go
      **only** into the Week 7 Moodle PDF (Part 9.4, Part 10.8).
- [ ] Screenshot of the written confirmation request and the customer's reply saved for the
      Moodle PDF.
- [ ] No credentials, private access details, or customer-identifying data end up in the public
      transcript.

## Post-meeting artifacts (owners)

- Sanitized English transcript → [`sprint-review-transcript.md`](sprint-review-transcript.md) (Ilya).
- Sprint Review summary → [`sprint-review-summary.md`](sprint-review-summary.md).
- Final handover level and confirmation status → [`docs/customer-handover.md`](../../docs/customer-handover.md)
  and [`README.md`](README.md) (items 15–18), closing
  [#131](https://github.com/ValekusVachpekus/pdn-control/issues/131).
- UAT verdict notes for UAT-08 / UAT-09 → [`docs/user-acceptance-tests.md`](../../docs/user-acceptance-tests.md).
- New follow-up items (if any) → issues on the
  [Sprint 7 milestone](https://github.com/ValekusVachpekus/pdn-control/milestone/5).
- Private recording link, exact timecodes, access details, and the confirmation screenshot →
  Week 7 Moodle PDF only.
