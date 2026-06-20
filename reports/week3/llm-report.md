# LLM Usage Report — Week 3 (ПДн Контроль)

This report discloses how AI/LLM tools were used during Assignment 3. All AI outputs were reviewed, tested, and integrated by team members; all substantive architectural decisions, Sprint Planning, and customer approvals remain original team work.

*Note: The product itself utilizes LLM models (Qwen) for policy text analysis as a core feature. This report covers only the AI tools used by the team to produce the assignment deliverables.*

## Tools used
The team utilized **Claude (Anthropic)** and **ChatGPT (OpenAI)** for development and documentation tasks.

## How AI was used per activity

*   **Documentation & Reporting — Claude/ChatGPT.** Used for drafting the structure of week 3 reports (`reflection.md`, `retrospective.md`, `roadmap.md`) and ensuring they meet the assignment specification. LLMs helped format the LaTeX source for the final PDF submission and provided templates for the Definition of Done.
*   **Frontend Development — ChatGPT.** Used to assist in implementing React components and debugging CSS layout issues in the dashboard. The team provided existing project context, and the AI suggested fixes for responsive design and API integration. All code snippets were reviewed and integrated manually.
*   **Backend & Crawler — Claude.** Used to refine the Playwright crawler logic, specifically for optimizing DOM element selection and handling dynamic page content. AI suggestions for async/await patterns were tested and debugged by the team.
*   **Backlog Refinement — ChatGPT.** Used to verify that our Product Backlog (Issues and Milestones) followed the DEEP (Detailed, Emergent, Estimated, Prioritized) criteria and to check consistency between the Roadmap and Project Board.

## Verification and responsibility
*   **Code Quality:** All AI-generated code was verified by running local smoke-tests (`npm run dev`) and ensuring it passed our manual verification before being committed and merged into `main`.
*   **Sanitization:** AI tools were never used to process or store customer PII (Personal Identifiable Information). All sensitive data (e.g., meeting transcripts, test credentials) was handled manually and sanitized by the team.
*   **Ownership:** The team maintains full responsibility for the architectural choices. AI was used as a productivity multiplier for routine tasks (e.g., formatting Markdown, writing boilerplate code, debugging CSS), while complex logic and business decisions (e.g., MVP scope, MoSCoW prioritization) were made exclusively by the team during Sprint Planning and Customer Review.
