# LLM Usage Report — Week 4 (ПДн Контроль)

This report discloses how AI/LLM tools were used during **Assignment 4** (quality
automation & release). All AI outputs were reviewed, tested, and integrated by team members;
all substantive engineering decisions — the choice of quality requirements, the Sprint plan,
the Definition of Done changes, and customer acceptance — remain original team work.

*Note: The product itself uses an LLM (Qwen) for policy-text analysis as a core feature.
This report covers only the AI tools the **team** used to produce the assignment
deliverables, not the product's runtime LLM.*

## Tools used

The team used **Claude (Anthropic)** and **ChatGPT (OpenAI)** for development and
documentation tasks during the sprint.

## How AI was used per activity

*   **Quality requirements & tests (Part 3–4) — Claude.** Used to help phrase the three
    quality requirements in the ISO/IEC 25010 quality-scenario format
    (source → stimulus → response measure) and to draft the QR↔QRT mapping. The team chose
    which sub-characteristics to target (Confidentiality, Maturity, Functional correctness)
    and set the measurable thresholds. AI assisted in writing the determinism test
    (`backend/tests/test_determinism.py`); the team ran it locally to confirm it passes.
*   **Definition of Done (Part 6) — Claude.** Used to fold the new quality gates (QRT pass,
    coverage gate, additional QA check, branch protection) into `docs/definition-of-done.md`
    consistently with the existing checklist wording.
*   **User Acceptance Tests (Part 10) — Claude/ChatGPT.** Used to structure
    `docs/user-acceptance-tests.md` into standard UAT scenarios (acceptance criteria,
    steps, expected/actual result, verdict). The actual acceptance and customer feedback
    came from the real Sprint Review with the customer.
*   **CI / quality pipeline (Part 7–8) — ChatGPT.** Used to assist the developer in drafting
    the GitHub Actions workflow for the unit/integration test run, coverage reporting, and an
    additional QA check (lint/static analysis). All workflow YAML was reviewed and validated
    on real PRs by the team.
*   **Sprint & backlog admin (Part 1) — Claude.** Used to draft the roadmap Sprint section
    and to keep the GitHub issues, milestone, and project board consistent. Story Points,
    priorities, and people assignments were decided by the team.
*   **Reports & documentation — Claude/ChatGPT.** Used to draft and format the week-4 report
    structure (Sprint Review, retrospective, reflection) and to check the deliverables
    against the assignment specification.

## Verification and responsibility

*   **Test quality:** Every AI-assisted test was executed locally before commit — the
    quality requirement tests pass (SSRF 45, determinism 3, violation catalog 11), and the
    documentation link-check (Lychee) is green on each PR.
*   **Sanitization:** AI tools were never used to process or store customer PII. Meeting
    transcripts and any sensitive data were handled and sanitized manually by the team.
*   **Ownership:** The team holds full responsibility for the quality targets, the DoD
    changes, the release decision, and the customer acceptance. AI was a productivity
    multiplier for routine drafting, formatting, and boilerplate; the engineering judgement
    (what to measure, what threshold is acceptable, what to ship) was made by the team.
