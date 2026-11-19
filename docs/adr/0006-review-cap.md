# ADR-0006: Review loops are capped at three rounds, then escalate

- Status: Accepted
- Date: 2026-11-19
- Deciders: Arslan Asghar

## Context
Unbounded builder↔reviewer loops burn tokens and can oscillate. Carson caps at three.

## Decision
A builder may request at most `builders.review_rounds_max` (default 3) reviews. Important findings left after the last round go to the manager, then the human.

## Consequences
- + Bounded cost per task.
- + Hard problems reach a human instead of looping.

## Alternatives considered
- No cap.
- Single review: too few for non-trivial changes.
