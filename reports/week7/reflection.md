# Reflection — Week 7

> Акцент Week 7: чему научились на follow-up-обслуживании, финальной передаче, фидбеке о
> полезности и финальной доставке `MVP v3` (Assignment 6, Part 12.4).
>
> Draft. Week 7 is the closing sprint: no new product scope — the actual transition, the final
> `MVP v3` (`v1.4.0`) release, and the closing reports. Items that depend on the final customer
> call and the public demo video are finalized after those events.

## Learning points
- **A sprint can legitimately be about closing out, not building.** The customer accepted the
  Week 6 increment (`v1.3.0`) on 2026-07-11 and requested no further features, so the disciplined
  move was to run Sprint 7 strictly as transition, release, and reporting rather than invent scope
  to look busy. The value delivered is a clean ownership transfer and a final release, not new
  functionality — and the roadmap and report say so plainly instead of padding.
- **Repository ownership transfer is a one-way door, so sequencing matters.** Once the GitHub
  repository is transferred to the customer, the team's write access is no longer guaranteed.
  Everything the team must place in the repository — the `v1.4.0` tag, the CHANGELOG entry, the
  final `docs/customer-handover.md`, and the Week 7 reports — has to land *before* the transfer,
  which makes the transfer the last repository action of the course.
- **Honest reporting means leaving explicit TODOs.** The Week 7 report items that depend on the
  not-yet-held call (Sprint Review transcript/summary, UAT re-confirmation, final transition
  status) and on the team's demo video were left as explicit `TODO` rather than pre-filled with
  plausible outcomes. A report is only evidence if it records what actually happened.

## Validated assumptions
- **A no-new-scope transition sprint is acceptable and can be reported honestly.** Assignment 6
  allows the final sprint to be a transition sprint; we stated the absence of new product scope
  directly in [`docs/roadmap.md`](../../docs/roadmap.md) and [`README.md`](README.md) instead of
  manufacturing work.
- **The Week 6 acceptance carries into Week 7.** The handover level
  (`Deployed or operated on customer side`) and the acceptance status recorded at the 2026-07-11
  meeting remain valid; Week 7 only re-requests confirmation on the *current* handover text and
  finalizes the mechanics (repository transfer, release publication).

## Friction and gaps
- **The Sprint 6 action point was not carried through.** The Sprint 6 retrospective committed to
  adding an integration smoke that drives the real OAuth UI redirect path. Sprint 7 had no product
  code, so the smoke was not added; it slipped for a second sprint because it was never scheduled
  as an explicit backlog item. It is recorded here as still open rather than silently dropped.
- **Several report artifacts are blocked on the final call.** The Sprint Review transcript and
  summary, the Week 7 UAT re-confirmation, and the final transition status cannot be written until
  the call is held, so the report ships with those items marked `TODO`.
- **The release depends on a team-produced artifact.** The public sanitized demo video is recorded
  by the team, and its link is required for the `v1.4.0` release notes, so the release cannot be
  cut until that link exists.

## What we would do differently
- **Transfer the repository last, behind a pre-transfer checklist.** Publish the `v1.4.0` tag,
  merge all Week 7 reports and the CHANGELOG entry, and finalize `docs/customer-handover.md`
  *before* initiating the ownership transfer, since write access is not guaranteed afterward.
- **Schedule carried action points explicitly, even in a no-code sprint.** The OAuth UI smoke
  slipped twice because it lived only in a retrospective, not on the board; a carried item needs an
  owner and a place in the sprint or a formal deferral, otherwise it disappears.
- **Update handover status in the same change as the meeting.** The acceptance status and level
  should be written into `docs/customer-handover.md` in the same PR that records the meeting
  outcome, so the customer-facing docs never lag reality (see the drift corrected in Week 7 below).
