# Product Roadmap — ПДн Контроль

This roadmap outlines our Sprint-by-Sprint delivery plan. Detailed task descriptions and real-time progress are tracked in the [Project Board](https://github.com/users/ValekusVachpekus/projects/1/views/1).

## Sprint 1: Stabilization & Public Safety (Current)
*   **Milestone:** [Sprint 1](https://github.com/ValekusVachpekus/pdn-control/milestone/1)
*   **Dates:** 2026-06-15 — 2026-06-21
*   **Sprint Goal:** Deliver a trustworthy, publicly-safe MVP v1 with protected URL scanning and core reporting.
*   **Focus:** Core infrastructure, SSRF protection, and stabilization of the scan-to-report flow.
*   **Planned Items:**
    *   [Bug] Free-report bypass fix ([#54](https://github.com/ValekusVachpekus/pdn-control/issues/54))
    *   [Bug] Same results for one website ([#34](https://github.com/users/ValekusVachpekus/projects/1?pane=issue&itemId=200915642&issue=ValekusVachpekus%7Cpdn-control%7C34))
    *   [US -12] Server-side URL validation / anti-SSRF ([#69](https://github.com/ValekusVachpekus/pdn-control/issues/69))
    *   [CI] Automated regression tests for crawler & rule-engine([#71](https://github.com/ValekusVachpekus/pdn-control/issues/71))
    *   [US -13] Scan-finished notification (link/email)([#70](https://github.com/ValekusVachpekus/pdn-control/issues/70))
    *   [US-01]  Basic website scan ([#58](https://github.com/ValekusVachpekus/pdn-control/issues/58))
    *   [US-02] Total potential fine display ([#59](https://github.com/ValekusVachpekus/pdn-control/issues/59))
    *   [US-03] Detailed list of violations ([#60](https://github.com/ValekusVachpekus/pdn-control/issues/60))
    *   [US-04] Legal article references ([#61](https://github.com/ValekusVachpekus/pdn-control/issues/61))
    *   [US-05] Free tier limited check ([#62](https://github.com/ValekusVachpekus/pdn-control/issues/62))
    *   [US-06] Paid tier full analysis ([#63](https://github.com/ValekusVachpekus/pdn-control/issues/63))
    *   [US-07] Compliance score (0-100) ([#64](https://github.com/ValekusVachpekus/pdn-control/issues/64))
    *   [Task] Implement backend ([#13](https://github.com/users/ValekusVachpekus/projects/1/views/1?pane=issue&itemId=200956657&issue=ValekusVachpekus%7Cpdn-control%7C13))
    *   [Task] Make API for checking status in Backend ([#18](https://github.com/users/ValekusVachpekus/projects/1/views/1?pane=issue&itemId=200956688&issue=ValekusVachpekus%7Cpdn-control%7C18))


## Sprint 2: Enhanced Analysis & Reporting (Near-term)
*   **Milestone:** Sprint 2 (To be created)
*   **Dates:** 2026-06-22 — 2026-06-28
*   **Sprint Goal:** Strengthen authentication, onboarding, and geo-localization accuracy.
*   **Focus:** OAuth login, deterministic GeoIP hosting detection, and passwordless onboarding.
*   **Planned Items:**
    *   [Task]  OAuth login via Yandex & VK (redirect flow) ([#72](https://github.com/ValekusVachpekus/pdn-control/issues/72))
    *   [Task]  Determine hosting country from IP deterministically (GeoIP), not by LLM guess ([#75](https://github.com/ValekusVachpekus/pdn-control/issues/75))
    *   [Task] Passwordless OTP ([#55](https://github.com/ValekusVachpekus/pdn-control/issues/55))
    

## Sprint 3: AI Intelligence & Automation (Future)
*   **Milestone:** Sprint 3 (To be created)
*   **Dates:** 2026-06-29 — 2026-07-05
*   **Sprint Goal:** Implement deep AI analysis of legal texts and improve user retention.
*   **Focus:** LLM-powered policy auditing and automated remediation recommendations.
*   **Planned Items:**
    *   [US-11] Automatic AI code remediation suggestions (currently Won't-Have; future candidate)
    *   [Task] Deeper LLM policy auditing across documents (cross-document consistency)
