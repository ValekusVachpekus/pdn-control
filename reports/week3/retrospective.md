# Sprint Retrospective — Sprint 1

## What went well
1. **Effective Sprint Planning:** The team successfully broke down the MVP v1 scope into small, manageable issues, which allowed us to maintain a consistent velocity throughout the week.
2. **Interactive Customer Engagement:** The Sprint Review was highly productive. We received clear feedback on the UI (contrast/visibility) and approval of our MVP v1 scope, which gave us a clear direction.
3. **Branching Workflow:** Transitioning to the issue-linked branch workflow (`<issue-number>-short-description`) improved our codebase management and made PR reviews much more structured.

## What did not go well
1. **Technical Instability:** We spent more time than expected debugging scan result determinism (#34), which caused a bottleneck for other tasks.
2. **Review Latency:** In the first half of the week, some Pull Requests were waiting for review for too long, which delayed the merge process and blocked team members.
3. **CI/CD Gaps:** We lacked automated testing for the crawler, meaning bugs were often caught during manual verification rather than by the build system.

## Action points
1. **Automated Testing:** We will implement at least two integration tests for the crawler in the next sprint to reduce reliance on manual smoke-checks.
2. **Review "Buddy System":** To speed up reviews, we will assign a designated reviewer for each PBI during Sprint Planning to ensure PRs are reviewed within 12 hours.
