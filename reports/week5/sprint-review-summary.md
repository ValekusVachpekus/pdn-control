# Sprint Review & UAT Summary — Sprint 3

**Date:** 2026-07-04

**Event:** One recorded session covering both customer-executed User Acceptance Testing and the Sprint Review discussion. Exact UAT/Review timecodes are provided privately in the Moodle submission; the public transcript is in `sprint-review-transcript.md`.

**Participants:**
*   **Customer** — product stakeholder / acceptor.
*   **Ilia Shchetkov (ValekusVachpekus)** — Product Owner + Frontend (led the review).
*   **Airat Mingazov (azenlrd)** — Backend.
*   **Aleksandr Martiushev (alexzhal1)** — Backend.
*   **Maksim Shakhrai (ShakhraiMaksim)** — QA (operated the meeting recording).
*   *Absent:* **Ksenya Koroleva (kskorqueen)** — Scrum Master.

---

### Sprint Goal Reviewed
Implement the authentication system (MVP v2: login via code, Yandex ID, VK ID integration) and address all UI/UX feedback items and defects identified during the Sprint 2 Review.

---

### Delivered Increment Demonstrated
*   **Released Increment:** MVP v2 (version 1.2.0).
*   **Authentication & Registration:** "Login by code" fully functional. Backend and UI integration for Yandex ID and VK ID completed (placeholders active awaiting customer API keys).
*   **Infrastructure:** DNS records set up and verified on the customer's domain.
*   **UI/UX Fixes (Addressed Sprint 2 Feedback):**
    *   Prominent "New check" button placed centrally on the screen.
    *   Removed useless "0" fine display from reports to eliminate confusion.
    *   Readdressed cookie banner violations to the **Developer** role (formerly assigned to Marketer).
    *   Improved empty history state with clear navigation back to the main page.
    *   UX quality-of-life fix: automatic retention/saving of the checked website URL.

---

### UAT Results
The customer executed the active UAT scenarios live during the session. **5 / 5 Pass**:

| UAT ID | Feature / Scenario | Result |
| :--- | :--- | :--- |
| **UAT-01** | Full PDF report download & verification | ✅ Pass |
| **UAT-02** | Anti-SSRF refusal (filtering internal IPs / localhost) | ✅ Pass |
| **UAT-03** | Empty history state UX & central action button | ✅ Pass |
| **UAT-04** | Blur gating for free vs. premium report blocks | ✅ Pass |
| **UAT-05** | Login via code functionality & DNS resolution | ✅ Pass |

*No UAT scenario failed. Zero new defects were identified during execution.*

---

### Quality Evidence Discussed
The team presented the automated test suite and quality metrics. The customer confirmed that no additional changes or new quality requirement tests are needed for the automated testing pipeline.

---

### Approvals
*   The customer **accepted the MVP v2 (v1.2.0) increment completely without requested changes or rework**.
*   The customer confirmed that the Sprint Goal was fully achieved (authentication framework deployed + interface fixes closed).

---

### Requested Changes & Customer Action Items
*   **API Keys Delivery (Customer Action):** Customer will register the applications in Yandex ID and VK ID today/tomorrow and provide the API keys to the team.
*   **DNS Records:** Customer confirmed DNS records have already been added on their side.
*   **Next Sprint Objective:** Complete the full authorization and registration lifecycle once keys are applied (Yandex ID, VK ID, Email/Code).

---

### Risks & Action Points
*   **Risk:** Delay in receiving Yandex/VK API keys from the customer could block final integration testing.
*   **Action Point:** Customer to generate and send API keys today or tomorrow; dev team to apply keys and replace temporary error placeholders.

---

### Resulting Product Backlog / Scope Changes
*   **New Priority:** Finalize authentication/registration pipeline (Yandex, VK, Email) as the core focus for Sprint 4.
*   **Scope Closed:** All 6 UI/UX debt items carried over from Sprint 2 have been closed and verified by the customer.
*   **Quality Scope:** No changes requested to CI, test coverage, or security automation.

---
*Note: Recording permission was requested and granted at the start of the session.*
