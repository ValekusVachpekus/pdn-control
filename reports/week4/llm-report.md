# LLM Usage Report — Week 4 (ПДн Контроль)

This report discloses how AI/LLM tools were used during **Assignment 4** (quality
automation & release). AI was used to produce **drafts**, which the team then reviewed,
tested, and corrected before integration. All substantive engineering decisions — the choice
of quality requirements and thresholds, the Sprint plan, the Definition of Done changes, the
release decision, and customer acceptance — remain original team work.

*Note: The product itself uses an LLM (Qwen) for policy-text analysis as a core feature.
This report covers only the AI tooling the **team** used to produce the assignment
deliverables, not the product's runtime LLM.*

## Tools used

The team used **Claude / Claude Code (Anthropic)** for development and documentation tasks
during the sprint. No other AI assistants were used.

## How AI was used per activity

*   **Documentation & reports — drafts.** Claude drafted the structure and wording of the
    sprint documents: quality requirements (`docs/quality-requirements.md`), the QR↔QRT
    mapping (`docs/quality-requirement-tests.md`), the Definition of Done update
    (`docs/definition-of-done.md`), the user acceptance tests
    (`docs/user-acceptance-tests.md`), the roadmap Sprint section, and the week-4 report
    files. The team chose which ISO/IEC 25010 sub-characteristics to target, set the
    measurable thresholds, and edited the drafts for accuracy.
*   **Tests — drafts.** Claude helped write and adjust the automated tests (the determinism
    test `backend/tests/test_determinism.py`, and the SSRF / violation-catalog test work).
    The team ran every test locally and confirmed it passes before committing.
*   **Product code — drafts.** Claude assisted with backend / crawler / frontend code for the
    sprint increment. All suggestions were reviewed, tested, and integrated manually by the
    team.
*   **CI / quality pipeline — drafts.** Claude assisted in drafting the GitHub Actions
    workflow for the test run, coverage reporting, the additional QA check (lint / static
    analysis), and branch protection ([#71](https://github.com/ValekusVachpekus/pdn-control/issues/71)).
    The workflow was reviewed and validated on real PRs by the team.

## Verification and responsibility

*   **Test quality:** Every AI-assisted test was executed locally before commit — the
    quality requirement tests pass (SSRF 45, determinism 3, violation catalog 11), and the
    documentation link-check (Lychee) is green on each PR.
*   **Sanitization:** AI tools were never used to process or store customer PII. Meeting
    transcripts and any sensitive data were handled and sanitized manually by the team.
*   **Ownership:** AI produced drafts as a productivity multiplier; the team verified,
    tested, and edited everything and holds full responsibility for the quality targets, the
    DoD changes, the release decision, and the customer acceptance. The engineering judgement
    (what to measure, what threshold is acceptable, what to ship) was made by the team.
