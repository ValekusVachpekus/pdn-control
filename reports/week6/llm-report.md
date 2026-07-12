# LLM Usage Report — Assignment 6 / Week 6 (ПДн Контроль)

This report discloses how AI/LLM tools were used during **Week 6** (the customer-transition
sprint: production authentication activation, the customer-handover documentation, the trial
increment `MVP v3 / v1.3.0`, and the customer trial / Sprint Review). AI was used to produce
**drafts**, which the team then reviews, tests, and corrects before they are merged and
integrated. All substantive engineering and product decisions — the transition plan, the
handover level, the release decision, the UAT verdicts, and customer acceptance — remain
original team work.

*Note: The product itself uses an LLM (**Qwen**) for policy-text analysis as a core runtime
feature. This report covers only the AI tooling the **team** used to produce the assignment
deliverables, not the product's runtime LLM.*

## Tools used

The team used **Claude / Claude Code (Anthropic)** for development and documentation tasks
during the sprint. No other AI assistants were used.

## How AI was used per activity

*   **Pre-handover code audit — analysis.** Before the transition meeting, Claude Code was used
    to audit the OAuth path end-to-end across backend and frontend. This surfaced that the
    Yandex/VK backend redirect flow (merged in Sprint 5) was not wired to the SPA — the frontend
    still issued a POST and carried a stale "not implemented" comment, so the login buttons would
    have been dead in production. The finding was recorded on
    [#129](https://github.com/ValekusVachpekus/pdn-control/issues/129); the fix decision and the
    implementation review were the team's.
*   **Frontend OAuth wiring — drafts.** Claude assisted with the frontend change that connected
    the buttons to the real redirect flow (`loginWithProvider` → browser redirect to
    `/oauth/{provider}/start`, handling of the `?oauth=success` / `?oauth_error` return in the
    SPA) delivered in [PR #133](https://github.com/ValekusVachpekus/pdn-control/pull/133). The
    team reviewed, tested, and merged it; the auth/session boundary remains team-owned.
*   **Customer-handover documentation — drafts.** Claude drafted
    [`docs/customer-handover.md`](../../docs/customer-handover.md) (ownership matrix,
    configuration without secret values, run/restore/verify steps, entry points) and
    [`AGENTS.md`](../../AGENTS.md). The ownership split (server, accounts, OAuth apps, DNS,
    repository), the transition level, and the handover facts were provided and confirmed by the
    team.
*   **Transition-meeting preparation — drafts.** Claude drafted the meeting agenda and the
    customer-trial / documentation-review checklist
    ([`reports/week6/transition-meeting-agenda.md`](transition-meeting-agenda.md)) and the
    private call run-sheet. The agenda structure and the questions to the customer were reviewed
    and adjusted by the team.
*   **Reports & documentation — drafts.** Claude drafted the Week 6 report files
    ([`reports/week6/`](.)), including this LLM report, the retrospective, and the reflection,
    from the meeting transcript/summary and the closed Sprint 6 issues. The team edits these for
    accuracy and does not let AI assert results that were not actually produced — UAT outcomes
    and the customer's acceptance are taken from the recorded meeting, not invented.
*   **Roadmap & backlog — drafts.** Claude helped draft the Sprint 6/7 roadmap update and the
    Product Backlog Item bodies (#127, #129, #130, #140). The team set the scope, Story Points,
    priorities, implementers, reviewers, and the Sprint Goal.

## Verification and responsibility

*   **No fabricated evidence:** AI was not used to invent results. The UAT outcomes, the handover
    level (`Deployed or operated on customer side`), and the customer's acceptance are recorded
    only from the actual meeting on 2026-07-11; the outstanding customer-side items (production
    OAuth keys, e-mail DNS) are stated as such, not as completed.
*   **Test quality:** AI-assisted code (the frontend OAuth wiring) was reviewed and exercised
    before merge; the Assignment 4 quality-requirement tests and the documentation link-check
    (Lychee) stay green on each PR. The CI quality gates are unchanged.
*   **Sanitization:** AI tools were never used to process or store customer PII. The meeting
    recording and its transcript are sanitized manually by the team; the private run-sheet,
    exact timecodes, and any credentials are kept out of the public repository.
*   **Ownership:** AI produced drafts as a productivity multiplier; the team verifies, tests,
    and edits everything and holds full responsibility for the transition decisions, the
    handover level, the release, and customer acceptance.
