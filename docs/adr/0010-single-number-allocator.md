# ADR-0010: One allocator assigns task numbers per repo under a lock

- Status: Accepted
- Date: 2026-11-19
- Deciders: Arslan Asghar

## Context
Task numbers (`AA-NNNN`) are derived from existing branches. Two builders deriving at once both see the same highest number and claim the same next one.

## Decision
Only `scripts/allocate-number.sh` assigns numbers, one repo at a time under a mkdir lock. It takes the highest number in `git branch -a` and in local claims, adds one, writes a claim file, and the builder pushes its branch immediately.

## Consequences
- + No duplicate numbers, even when allocated seconds apart.
- − Numbers claimed by a builder that crashes before pushing leave a gap; gaps are fine.

## Alternatives considered
- Each builder allocates its own number: races.
- Central counter service: infrastructure for a problem a lock solves.
