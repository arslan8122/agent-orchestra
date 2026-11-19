# ADR-0008: Every PR includes a video of the change working

- Status: Accepted
- Date: 2026-11-19
- Deciders: Arslan Asghar

## Context
Carson's human-in-the-loop step is watching a video of the feature. Reading a diff doesn't show whether a UI looks or behaves right.

## Decision
QA records a video for every PR: browser recording for UI work, a terminal recording of tests plus a real request for back-end work. PRs open as drafts with a Demo placeholder; `gh pr ready` is blocked until the video is attached.

## Consequences
- + Reviewers see behaviour, not just code.
- − Recording adds minutes per PR.
- − Back-end videos are less informative; exempting them needs a superseding ADR, not a quiet skip.

## Alternatives considered
- Screenshots only.
- UI PRs only.
