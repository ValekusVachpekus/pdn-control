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
5. **Merged into protected `main`** — the linked PR is merged into the protected default
   branch. `main` stays releasable.
6. **No known regressions** — the change does not break existing functionality; determinism
   and anti-SSRF invariants still hold.
7. **`CHANGELOG.md` updated if the change is user-visible** — and other affected
   documentation (user-facing/dev docs, contracts, `docs/user-stories.md` status mirror) is
   updated when the change affects it.
8. **Backlog reflects reality** — the issue is closed, and the board Work Status/fields are
   updated to `Done`.

## Notes

- **`Done` is not the same as `merged`**: an item is `Review` while the PR is open; it
  becomes `Done` only after merge into `main` **and** the checklist above.
- Sprint-tracked PBIs additionally require the Implementer/Reviewer roles to be named in the
  issue body (GitHub issues have no native reviewer field).
- This DoD is maintained by the team and may be tightened over time (Emergent).
