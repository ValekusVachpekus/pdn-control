# LLM Usage Report — Assignment 5 (ПДн Контроль)

This report discloses how AI/LLM tools were used during **Assignment 5** (architecture
documentation, development-process & configuration-management documentation, and the `MVP v2`
increment). AI was used to produce **drafts**, which the team then reviews, tests, and corrects
before they are merged and integrated. All substantive engineering and product decisions —
the architecture decisions themselves, the choice of quality requirements and thresholds, the
Sprint plan and scope, the Definition of Done, the release decision, and customer acceptance —
remain original team work.

*Note: The product itself uses an LLM (**Qwen**) for policy-text analysis as a core runtime
feature. This report covers only the AI tooling the **team** used to produce the assignment
deliverables, not the product's runtime LLM.*

## Tools used

The team used **Claude / Claude Code (Anthropic)** for development and documentation tasks
during the sprint. No other AI assistants were used.

## How AI was used per activity

*   **Architecture documentation — drafts.** Claude drafted the structure and prose of the
    maintained architecture artifact ([`docs/architecture/README.md`](../../docs/architecture/README.md))
    and the diagrams-as-code sources for the static (component), dynamic (sequence), and
    deployment views (PlantUML under [`docs/architecture/`](../../docs/architecture/)). The
    team chose the actual architecture views, the components and boundaries to depict, and the
    coupling/cohesion and quality-attribute commentary; the PlantUML sources were rendered to
    SVG and committed alongside the product.
*   **ADRs — drafts.** Claude drafted the four Architecture Decision Records
    ([`docs/architecture/adr/`](../../docs/architecture/adr/)) and their mapping to the
    Assignment 4 quality requirements. The decisions recorded (full-LLM pipeline, deterministic
    GeoIP, server-side gating / SSRF boundary, single-host Compose + Caddy/TLS) were made by the
    team; AI helped capture the context, options, and consequences in the ADR format.
*   **Development process & configuration management — drafts.** Claude drafted
    [`docs/development-process.md`](../../docs/development-process.md), including the Mermaid
    `gitGraph` illustration of the git workflow. The documented workflow reflects how the team
    actually branches, reviews, and releases; the team verified it matches the repository's
    real rules.
*   **Backlog refinement & Sprint planning — drafts.** Claude helped draft Product Backlog Item
    bodies and acceptance criteria for the Sprint 5 issues. The team set the scope, Story Points,
    MoSCoW priorities, implementers, reviewers, and the Sprint Goal.
*   **Customer feedback response — draft.** Claude helped draft the customer-feedback response
    table (Part 2) from the Week 4 review notes; the team confirmed each item and its resolution.
*   **Product code — drafts.** Claude assisted with the `MVP v2` increment: the Week 4 UAT
    feedback fixes to the frontend and the hosted-documentation-site setup (MkDocs configuration
    and the Pages CI workflow). All AI-assisted changes are produced as drafts on issue-linked
    branches and are reviewed, tested, and merged by the team — the front-end auth/`paid` and
    SSRF security boundaries remain team-owned.
*   **Tests — drafts.** Claude helped write and adjust the automated tests for the changed
    areas (e.g. the front-end unit tests for the feedback fixes). The team runs every test
    locally and in CI and confirms it passes before merge.
*   **Reports & documentation — drafts.** Claude drafted the Week 5 report files
    ([`reports/week5/`](.)), including this LLM report and the new `MVP v2` user-acceptance-test
    scenarios in [`docs/user-acceptance-tests.md`](../../docs/user-acceptance-tests.md). The
    team edits these for accuracy and does not let AI assert results that were not actually
    produced (e.g. UAT scenarios not yet executed with the customer are marked **Pending**, not
    Pass).

## Verification and responsibility

*   **Test quality:** Every AI-assisted test is executed locally and in CI before merge; the
    Assignment 4 quality requirement tests and the documentation link-check (Lychee) stay green
    on each PR. The CI quality gates from Assignment 4 are unchanged.
*   **No fabricated evidence:** AI was not used to invent results. UAT outcomes, customer
    acceptance, and review verdicts are recorded only after they actually happen; planned-but-
    not-executed items are labelled as such.
*   **Sanitization:** AI tools were never used to process or store customer PII. Meeting
    recordings, transcripts, and any sensitive data are handled and sanitized manually by the
    team and kept out of the public repository.
*   **Ownership:** AI produced drafts as a productivity multiplier; the team verifies, tests,
    and edits everything and holds full responsibility for the architecture decisions, the
    quality targets, the documented process, the release decision, and customer acceptance. The
    engineering judgement (what to build, what to document, what threshold is acceptable, what
    to ship) was made by the team.
