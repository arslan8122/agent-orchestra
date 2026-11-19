# Architecture Decision Records

The decisions behind agent-orchestra itself. `/orchestrate init` copies them into your project as
**Proposed**, so you can accept, adapt or supersede each one for your team.

Format: [Michael Nygard's ADR template](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions),
as described by [Martin Fowler](https://martinfowler.com/bliki/ArchitectureDecisionRecord.html).
Accepted ADRs are immutable apart from their Status line.

| ADR | Decision | Status | Date |
|---|---|---|---|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted | 2026-11-19 |
| [0002](0002-no-task-no-work.md) | No task, no work; one task = one branch = one PR = one builder | Accepted | 2026-11-19 |
| [0003](0003-manager-never-writes-code.md) | The manager agent never writes code | Accepted | 2026-11-19 |
| [0004](0004-isolated-builders.md) | Builders run isolated in their own worktrees; humans never address them | Accepted | 2026-11-19 |
| [0005](0005-timer-driven-supervision.md) | Supervision runs on a timer, not at the model's discretion | Accepted | 2026-11-19 |
| [0006](0006-review-cap.md) | Review loops are capped at three rounds, then escalate | Accepted | 2026-11-19 |
| [0007](0007-definition-of-done.md) | Definition of done: failing test first, verify green, QA video | Accepted | 2026-11-19 |
| [0008](0008-video-proof-in-every-pr.md) | Every PR includes a video of the change working | Accepted | 2026-11-19 |
| [0009](0009-never-merge.md) | The system opens PRs and never merges | Accepted | 2026-11-19 |
| [0010](0010-single-number-allocator.md) | One allocator assigns task numbers per repo under a lock | Accepted | 2026-11-19 |
| [0011](0011-session-naming.md) | Session naming and manager-to-manager messaging | Accepted | 2026-11-19 |
| [0012](0012-one-question-escalation.md) | Escalations are one question plus a recommendation | Accepted | 2026-11-19 |
| [0013](0013-work-source-chosen-at-setup.md) | Work comes from tickets or text tasks, chosen at setup | Accepted | 2026-11-19 |
| [0014](0014-proof-hosting-outside-repo.md) | PR videos are hosted outside the repo: gh --attach first, bucket fallback | Accepted | 2026-11-19 |
| [0015](0015-follow-project-conventions.md) | Agents follow the project's existing branch, commit and PR conventions | Accepted | 2026-11-19 |
| [0016](0016-json-config-stdlib-hooks.md) | Config is JSON and hooks use only the Python standard library | Accepted | 2026-11-19 |
