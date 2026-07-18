# Sprint Retrospective — Sprint 7 (Week 7)

> Draft. Sprint 7 carried no new product scope (the customer accepted `v1.3.0` on 2026-07-11 and
> requested no further features); it consists of the actual transition, the final `MVP v3`
> (`v1.4.0`) release, and the closing reports. Items depending on the final call are finalized
> after it.

## What went well
1. **The sprint stayed disciplined with no scope creep.** With the increment already accepted and
   no new features requested, Sprint 7 was run strictly as transition, release, and reporting. The
   absence of new product scope is stated openly in [`docs/roadmap.md`](../../docs/roadmap.md) and
   the [Week 7 report](README.md) rather than padded with invented work.
2. **Customer-facing documentation was brought back to the actual facts.**
   [PR #148](https://github.com/ValekusVachpekus/pdn-control/pull/148) corrected
   [`docs/customer-handover.md`](../../docs/customer-handover.md) and
   [`docs/roadmap.md`](../../docs/roadmap.md), which still read `Not yet accepted` and "OAuth in
   progress" even though the customer had accepted the product on 2026-07-11; the ownership matrix,
   the self-service OAuth-key step, and the verified e-mail domain were updated to the real state.
3. **Quality gates held despite a docs-only sprint.** No product code changed, and the Assignment 4
   CI quality gates (tests, coverage, security scan, lint, Lychee link check) stayed green on every
   PR with branch protection on `main` left intact.

## What did not go well
1. **Documentation had drifted from reality between sprints.** `docs/customer-handover.md` still
   claimed the product was `Not yet accepted` and item 31 of the Week 6 report was still `TODO`
   although the screenshots were already committed. The drift was caught only when auditing the
   docs at the start of Week 7, not when the customer state actually changed on 2026-07-11.
2. **The Sprint 6 action point slipped again.** The commitment to add an integration smoke for the
   real OAuth UI redirect path was not delivered: Sprint 7 had no product code, and the item was
   never placed on the board, so it silently carried over for a second sprint instead of being
   scheduled or formally deferred.

## What we changed compared to the previous Sprint
- **We treated documentation state as something to verify, not assume.** Instead of trusting that
  the docs reflected reality, we audited `docs/customer-handover.md`, `docs/roadmap.md`, and the
  Week 6 report against the recorded 2026-07-11 meeting and corrected the drift in PR #148 — a
  direct response to the "docs lagged the customer state" problem.

## Action points (lessons for post-course / future work)
1. **Keep one source of truth for handover status, updated with the meeting.** The acceptance
   status and handover level must be written into `docs/customer-handover.md` in the same change
   that records the meeting outcome, so customer-facing docs never lag the customer's actual state.
2. **Sequence the repository transfer last, behind a checklist.** Before initiating the ownership
   transfer, confirm the release tag is pushed, all reports are merged, and the CHANGELOG entry is
   closed — because the team's write access to the repository is not guaranteed after the transfer.
3. **Put carried action points on the board, even in a no-code sprint.** The OAuth UI smoke slipped
   twice by living only in a retrospective; a carried item needs an explicit owner and a backlog
   entry, or a recorded decision to defer it, so it cannot disappear between sprints.
