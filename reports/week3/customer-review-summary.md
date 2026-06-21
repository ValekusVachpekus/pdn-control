# Sprint Review Summary — Sprint 1

**Date:** June 21, 2026

**Participants:**
- **Product Owner Representative:** Customer
- **Scrum Team:** Ksenya Koroleva (Scrum Master), Aleksandr Martiushev (Backend), Airat Mingazov (Backend), Ilia Shchetkov (Frontend), Maksim Shakhrai (QA).

## Artifacts Demonstrated
- **MVP v1 Live Increment:** Functional website deployed on the university VM.
- **Interactive Figma Prototype:** Final MVP v1 interface design.
- **Product Backlog:** Updated board with story points and MoSCoW priorities.

## Scope Reviewed & Implemented Increment
- **Reviewed Scope:** MVP v1 core features (URL scan, fine calculation, legal article references, and anti-SSRF protection).
- **Implemented Increment:** The team demonstrated the functional scan-to-report flow, key security fixes (anti-SSRF validation, deterministic scan results, and secured API for paid reports), and keyboard navigation improvements.

## Approvals & Requested Changes
- **Approvals:** The customer officially approved the MVP v1 scope and the implemented increment.
- **Requested Changes:** The customer requested to increase the visual contrast and prominence of the "Total Fine Amount" display to make it more noticeable to business owners.

## Risks & Action Points
- **Risks:** The transition from the university VM to the new VPS/Domain infrastructure poses a temporary risk of downtime.
- **Action Points:**
    - Redirect DNS to the new production domain (Customer).
    - Port configuration and deployment to the new VPS (Team).
    - Adjust UI design to increase contrast of the fine amount (Frontend).
    - Fix identified bugs #34 and #54 (Backend).

## Resulting Product Backlog/Scope Changes
- **Scope Update:** US-13 (Scan-finished notification) was pulled into the current Sprint as a 'Could Have' priority improvement, which was approved by the customer.
- **Refinement:** No stories were removed; however, the order of UI/UX improvements was adjusted based on customer feedback regarding visual hierarchy.

---
*Note: Explicit written consent for the public MIT-licensed development model was obtained during the meeting.*
