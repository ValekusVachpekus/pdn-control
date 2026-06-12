# Assignment 2 — Week 2 Report — ПДн Контроль

**ПДн Контроль** is a web service for preliminary **technical** audits of small and
medium business websites against typical **152-FZ** ("On Personal Data") compliance
risks. It is an MVP and a risk-reduction tool, **not** a legal guarantee.

License: [MIT](../../LICENSE).

> This file is an **index** for the Assignment 2 submission. Substantive content lives
> in the dedicated files linked below.

---

## 1. User stories

- [user-stories.md](user-stories.md) — 11 user stories (US-01 … US-11) with stable IDs,
  MoSCoW priorities, requirement status, and the **Initial proposed MVP v1 scope**
  (US-01 – US-05).

## 2. Prototype and interface artifacts

The product's externally used interface is **graphical** (a web SPA), so the interface
prototype is an interactive Figma prototype. No external API interface is exposed to end
users, therefore `api/openapi.yaml`, `docs/interface.md`, and a Postman collection are
not applicable for this submission.

- **Interactive Figma prototype:**
  [Figma prototype](https://www.figma.com/proto/hzIVCcOBokA8YUqwZKoL0q/Untitled?node-id=3-107&p=f&t=1HviSoUJakE6VTAo-1&scaling=min-zoom&content-scaling=fixed&page-id=0%3A1&starting-point-node-id=3%3A107)
  (publicly viewable, not editable). Covers Home → Report flow, the free-tier
  restriction, and the invalid-URL error state. Mapped user stories: see
  [Prototype Coverage](#prototype-coverage) below.

## 3. MVP v0

- [mvp-v0-report.md](mvp-v0-report.md) — purpose, deployment, video demo, limitations,
  local setup link, and the repeatable smoke-check scenario.
- **Deployment / runnable artifact:** <!-- TODO: replace with the public internet-accessible URL; the internal university-VM address is not reachable from the internet --> _to be published (see mvp-v0-report.md)_.
- **Run instructions:** root [README.md → "Локальный запуск"](../../README.md#локальный-запуск).
- **Public video demonstration (< 2 min):** <!-- TODO: paste the public sanitized video link --> _to be published (see mvp-v0-report.md)_.

## 4. PR/MR workflow

- **PR template:** [.github/pull_request_template.md](../../.github/pull_request_template.md).
- **Reviewed PRs (reviewed by another team member, not self-review):**
  - [PR #19](https://github.com/ValekusVachpekus/pdn-control/pull/19) — frontend bug fixes (page reload, loading screen).
  - [PR #20](https://github.com/ValekusVachpekus/pdn-control/pull/20) — `llm_analyzer.py` update.
  <!-- TODO: confirm each linked PR has a review (approval) by a different team member -->

## 5. Link checking (Lychee)

- **Configuration:** [lychee.toml](../../lychee.toml).
- **Workflow:** [.github/workflows/lychee.yml](../../.github/workflows/lychee.yml).
- **Latest successful run on the protected default branch (`main`):**
  [Lychee workflow runs](https://github.com/ValekusVachpekus/pdn-control/actions/workflows/lychee.yml?query=branch%3Amain+is%3Asuccess)
  <!-- TODO: replace with the permalink to the specific latest successful run -->.

### Excluded Lychee links (justification + manual verification)

The following patterns are excluded in [lychee.toml](../../lychee.toml). Each was visited
manually in a browser before submission to confirm accessibility where applicable:

| Excluded pattern | Reason | Manual check |
|---|---|---|
| `^https?://localhost`, `^https?://127\.0\.0\.1` | Local dev-server addresses from run instructions; do not exist in CI. | N/A — local only |
| `^https?://(host\|backend):\d+` | Docker-internal service hostnames; resolvable only inside Compose. | N/A — internal only |
| `^https://gitlab\.pg\.innopolis\.university` | Behind corporate auth; not reachable anonymously from CI. | Verified accessible when authenticated |

## 6. Screenshots

**Protected default branch settings**

![Protected branch settings](images/protectbranch.jpg)
![Protected branch settings — rules](images/protectbranch1.jpg)

**Example reviewed PR (review by another team member)**

![Reviewed PR — overview](images/PR1.png)
![Reviewed PR — review](images/PR2.png)
![Reviewed PR — approval](images/PR3.png)

**Selected prototype and interface artifacts**

![Figma prototype — report screen](images/figmares.png)
![Figma prototype — report (continued)](images/figmaright.png)
![Figma prototype — error state](images/figmaerror.png)
![Figma prototype — error state (continued)](images/figmaerror1.png)
![Figma prototype — analysis](images/figmaanalisys.png)

**Deployed MVP v0 or runnable artifact**

<!-- TODO: add a PNG screenshot of the deployed/running MVP v0 into images/ and embed it here -->
_To be added once MVP v0 is publicly deployed — see [mvp-v0-report.md](mvp-v0-report.md)._

## 7. Customer review

- **Meeting summary:** [customer-meeting-summary.md](customer-meeting-summary.md).
- **Sanitized English transcript (published with the customer's permission):**
  [customer-meeting-transcript.md](customer-meeting-transcript.md).
- Recording and private instructor sharing were **granted**; the customer also permitted
  **publishing** the sanitized transcript in this repository. Detailed notes
  (`customer-meeting-notes.md`) are therefore **not** used as evidence for this submission.

## 8. Analysis and LLM usage

- **Week 2 analysis:** [analysis.md](analysis.md).
- **LLM usage report:** [llm-report.md](llm-report.md).

---

## Prototype Coverage
The interactive Figma prototype demonstrates the user flow for the following core MVP v1 user stories:
*   **US-01 (Basic website scan):** The Home screen allows users to input a URL.
*   **US-02 & US-03 & US-04 (Fine display, Violations, Legal refs):** The Report screen displays the total fine, a detailed list of violations, and references to FZ-152 articles.
*   **US-05 (Free tier limited check):** The flow includes a restriction that requires upgrading for full details.
*   **Error State:** Demonstrates the system's reaction to an invalid URL.

[Link to interactive Figma prototype](https://www.figma.com/proto/hzIVCcOBokA8YUqwZKoL0q/Untitled?node-id=3-107&p=f&t=1HviSoUJakE6VTAo-1&scaling=min-zoom&content-scaling=fixed&page-id=0%3A1&starting-point-node-id=3%3A107)