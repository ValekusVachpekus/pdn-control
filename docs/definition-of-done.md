# Definition of Done

The shared minimum completion standard for work in this repository. A PBI may be moved to
Work Status **`Done`** only when **both** its issue-specific acceptance criteria **and**
every item below are satisfied (per Process Requirements).

## Done checklist

A PBI is **Done** when:

1. **Acceptance criteria met** — every acceptance criterion in the issue is satisfied and
   demonstrably true.
2. **Implemented behind a linked PR** — the change is delivered via a pull request linked to
   the issue (default implementation evidence). Named deliverables (design/API/deploy/docs
   artifacts) are attached when a PR alone is not obvious evidence.
3. **Reviewed by the named reviewer** — the PR is reviewed and approved by the issue's
   **Reviewer** (a different person from the **Implementer**), who confirms it is ready to
   complete.
4. **Tests green** — relevant automated tests exist and pass in CI; no failing checks on the
   PR. New behavior is covered by tests where practical.
5. **Quality gates pass** — the CI pipeline ([#71](https://github.com/ValekusVachpekus/pdn-control/issues/71))
   is green on the PR, specifically:
   - all **Quality Requirement Tests** ([`docs/quality-requirement-tests.md`](./quality-requirement-tests.md))
     for affected requirements pass — no QR may regress;
   - the **coverage gate** is met (coverage does not drop below the agreed threshold);
   - the **additional QA check** (lint / static analysis) reports no new violations.
6. **Quality requirements maintained** — if the change touches a behaviour covered by a
   [quality requirement](./quality-requirements.md), the QR, its QRT, and the relevant
   fixtures are updated in the **same** PR; no QR is silently weakened.
7. **Merged into protected `main`** — the linked PR is merged into the protected default
   branch via the enforced branch-protection rules (required reviews + required CI checks).
   `main` stays releasable.
8. **No known regressions** — the change does not break existing functionality; determinism
   (QR-02) and anti-SSRF (QR-01) invariants still hold.
9. **`CHANGELOG.md` updated if the change is user-visible** — and other affected
   documentation (user-facing/dev docs, contracts, `docs/user-stories.md` status mirror) is
   updated when the change affects it.
10. **Backlog reflects reality** — the issue is closed, and the board Work Status/fields are
    updated to `Done`.

## Notes

- **`Done` is not the same as `merged`**: an item is `Review` while the PR is open; it
  becomes `Done` only after merge into `main` **and** the checklist above.
- Sprint-tracked PBIs additionally require the Implementer/Reviewer roles to be named in the
  issue body (GitHub issues have no native reviewer field).
- **Quality gates (items 5–6)** were added in the Assignment 4 sprint together with the
  [quality requirements](./quality-requirements.md) and their
  [tests](./quality-requirement-tests.md); the CI wiring that enforces them
  (test run, coverage gate, additional QA check, branch protection) is delivered by
  [#71](https://github.com/ValekusVachpekus/pdn-control/issues/71). Until #71 merges, items 5
  and 7 are satisfied manually (QRTs run locally, review approved) and become automatic once
  the pipeline is live.
- This DoD is maintained by the team and may be tightened over time (Emergent).
