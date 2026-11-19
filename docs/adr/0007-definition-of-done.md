# ADR-0007: Definition of done: failing test first, verify green, QA video

- Status: Accepted
- Date: 2026-11-19
- Deciders: Arslan Asghar

## Context
'Done' claimed by a model is not evidence. Green tests that never failed may test nothing.

## Decision
A task is done only when a test for its acceptance criteria failed before the implementation, every `verify` command passes exactly as configured (for example inside containers), the reviewer approved, and QA recorded the change working.

## Consequences
- + Claims are backed by evidence a reviewer can check.
- − Only as strong as the `verify` commands; weak commands give confident wrong answers.

## Alternatives considered
- Trust the builder's summary.
