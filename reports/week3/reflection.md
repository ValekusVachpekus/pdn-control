# Week 3 Reflection

## Learning points
- **Backlog Management:** We learned the importance of maintaining a traceable Product Backlog. Migrating from simple markdown stories to GitHub Issues with Story Points and MoSCoW helped us visualize the actual workload.
- **Estimation:** Planning Poker sessions taught us to identify hidden technical risks (e.g., the difference between simple UI changes and backend determinism fixes).
- **Workflow Enforcement:** Working with protected branches and mandatory PR reviews forced us to communicate more clearly. We learned that the "Definition of Done" is not just a formality but a safeguard against regression.
- **MVP Delivery:** We realized that stabilizing the "scan-to-report" flow required much more effort than the initial UI prototype suggested, specifically regarding anti-SSRF measures.

## Validated assumptions
- **Scope Assumption:** Our assumption that the MVP v1 scope (URL scan + violation list) was sufficient to demonstrate business value was confirmed by the customer during the Sprint Review.
- **Technology Choice:** Our initial assumption that Playwright would be enough for the crawler was validated, as it successfully handled dynamic page content, though it required extra effort to stabilize.
- **Monetization Model:** The customer approved the "blurred" free-tier model, confirming our assumption that users need to see the value (violation count) before paying for details.

## Friction and gaps
- **Technical Risks:** We encountered significant issues with scan determinism (different results for the same site), which was a major blocker and required extra effort in Sprint 1.
- **Process Gaps:** We discovered that our CI/CD pipeline lacks automated testing for crawler logic, which led to some "flaky" results during the sprint.

## Planned response
- **Next Sprint Focus:** We will prioritize resolving the deterministic scan results and implementing the PDF export (US-08) to fulfill the Should-Have requirements.
- **Process Improvement:** We will add more specific acceptance criteria to the PR template to avoid superficial reviews.
- **Technical Debt:** We plan to address the remaining bugs identified in Sprint 1 (Issue [#54](https://github.com/ValekusVachpekus/pdn-control/issues/54)) as the very first step of the next Sprint.
- **Documentation:** We will keep our `docs/roadmap.md` updated to reflect the new priority of the tracker detection logic.
