# LLM Usage Report — Assignment 6 / Week 7 (ПДн Контроль)

This report discloses how AI/LLM tools were used during **Week 7** — the final Sprint of the
course, which carried no new product scope and consisted of the actual transition, the final
`MVP v3` release, and the closing documentation and reporting. AI was used to produce
**drafts**; the team reviews, corrects, and owns them. All substantive decisions — the
transition scope, the handover level, the customer-confirmation status, the release decision,
and the UAT verdicts — remain original team work.

*Note: the product itself uses an LLM (**Qwen**) at runtime to analyse policy texts. This report
covers only the AI tooling the **team** used to produce the assignment deliverables.*

## Tools used

**Claude / Claude Code (Anthropic)** — the same tool as in the previous Sprints. No other AI
assistants were used in Week 7.

## How AI was used per activity

*   **Final-transition meeting preparation — drafts.** Claude drafted
    [`final-transition-agenda.md`](final-transition-agenda.md): the Sprint 7 Review structure,
    the verbatim acceptance question about `docs/customer-handover.md`, the repository-transfer
    item, the UAT re-confirmation script, and the wording of the written confirmation request
    sent to the customer. The team reviewed the agenda and conducted the call itself.
*   **Handover documentation — drafts of factual updates.** Claude updated
    [`docs/customer-handover.md`](../../docs/customer-handover.md) to the actual state after the
    Week 6 meeting (confirmation status, ownership matrix, self-service OAuth keys, verified
    e-mail domain, repository transfer) and [`docs/roadmap.md`](../../docs/roadmap.md) to the
    end-of-course outcome ([PR #148](https://github.com/ValekusVachpekus/pdn-control/pull/148)).
    Every fact written there was supplied by the team from the recorded meeting; AI did not
    decide the handover level or the acceptance status.
*   **Reports — drafts.** Claude drafted the Week 7 report files ([`reports/week7/`](.)),
    including this LLM report, the retrospective, and the reflection, from the actual closed
    issues, merged PRs, and the meeting transcript. Placeholders were left explicitly `TODO`
    until the corresponding event (the call, the release) actually happened, rather than being
    filled with plausible-sounding text.
*   **Release preparation — drafts.** Claude drafted the `CHANGELOG.md` entry for the final
    release and the release notes for `v1.4.0`. The release decision, the version choice
    (`v1.4.0` as the final `MVP v3` delivery above the Week 6 trial `v1.3.0`), and the tag on
    the protected `main` are the team's.
*   **Backlog — drafts.** Claude drafted the body of the Week 7 reporting task
    ([#149](https://github.com/ValekusVachpekus/pdn-control/issues/149)); the Sprint Goal, the
    scope decision (no new features), Story Points, implementer, and reviewer were set by the
    team.

## Verification and responsibility

*   **No fabricated evidence.** Where an outcome did not exist yet, the report says `TODO`
    rather than inventing it. The handover level, the customer-confirmation status, the UAT
    verdicts, and the customer's use of the product are taken only from the recorded meetings
    and the customer's written reply. Items that remain the customer's own responsibility (the
    production OAuth keys) are stated as such, not as delivered.
*   **Quality gates unchanged.** Week 7 changed no product code; the Assignment 4 CI quality
    gates (unit and integration tests, coverage, security scan, lint, link check) stayed green
    on every PR, and branch protection on `main` was not relaxed.
*   **Sanitization.** AI tools were not used to process customer PII. The meeting recording,
    the transcript, the exact timecodes, the access credentials, and the screenshots of the
    customer's confirmation are handled manually and kept out of the public repository — they
    go only into the private Moodle submission.
*   **Ownership.** AI was a drafting multiplier. The team verifies, edits, and holds full
    responsibility for the transition, the release, and the statements made to the customer.
