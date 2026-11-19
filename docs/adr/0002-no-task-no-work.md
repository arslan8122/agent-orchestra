# ADR-0002: No task, no work; one task = one branch = one PR = one builder

- Status: Accepted
- Date: 2026-11-19
- Deciders: Arslan Asghar

## Context
Parallel agents need a unit of work that is small, independently reviewable and traceable. Work started from a chat message leaves no record of what was asked.

## Decision
Every builder starts from exactly one task record (a ticket, or a text task saved as `.orchestra/tasks/<ID>.md`). One task produces one branch and one PR in one repo. A change spanning repos becomes one task per repo, cross-referenced under 'Paired with'.

## Consequences
- + Every PR traces back to what was asked.
- + Small PRs are reviewable by a human watching one video.
- − Cross-repo features need coordination of several PRs.

## Alternatives considered
- One PR per feature across repos: impossible with submodules or separate repos.
- Tasks without records: nothing to resume from after a crash.
