# ADR-0012: Escalations are one question plus a recommendation

- Status: Accepted
- Date: 2026-11-19
- Deciders: Arslan Asghar

## Context
A human supervising many builders can't absorb a wall of options.

## Decision
The manager asks the human one question at a time, always with its recommended answer, and otherwise stays quiet.

## Consequences
- + Low interruption cost for the human.
- − Some decisions need several rounds.

## Alternatives considered
- Batch all questions into a daily digest: blocks builders for hours.
