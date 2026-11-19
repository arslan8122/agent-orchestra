# ADR-0017: Test cases are planned with the task, before a builder starts

- Status: Accepted
- Date: 2026-11-19
- Deciders: Arslan Asghar

## Context
ADR-0007 required a failing test first, but left the builder to decide which tests. A builder
that writes both the code and its tests decides what "working" means for itself: it can test
the happy path only, or test its implementation rather than the requirement. The human only
found out at review, after the work was done. Planning tests up front is cheap, and it's the
one point where the human can agree what "done" means before any code exists.

## Decision
During planning (`/orchestrate tasks`, `plan`, or ticket intake) the manager writes, for every
task: acceptance criteria (`AC-n`), test cases (`TC-n`) in Given/When/Then form with the AC
each covers, its level and whether QA's video must show it, at least one edge or failure
case, and an out-of-scope list. The human approves criteria and test cases together.
`scripts/validate-task.py` must pass before a builder starts. Builders implement every planned
case first and see it fail, may add tests but never drop or weaken a planned one, the reviewer
treats a missing planned case as important, QA's video follows the `Video: yes` cases, and
the PR body lists every TC with its result.

## Consequences
- + The human approves what "done" means before code exists, not after.
- + Reviewers and the video map one-to-one onto agreed cases.
- + Edge and failure paths are planned, not left to chance.
- − Planning takes longer and asks more of the human up front.
- − A wrong test case blocks the builder until the record is updated; that's intended.

## Alternatives considered
- Builder chooses its own tests (ADR-0007 alone): fast, but "done" is self-defined.
- A separate test-writer agent after planning: another hand-off with no human checkpoint.
