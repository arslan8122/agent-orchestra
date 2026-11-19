# ADR-0005: Supervision runs on a timer, not at the model's discretion

- Status: Accepted
- Date: 2026-11-19
- Deciders: Arslan Asghar

## Context
Carson: 'You can't trust your manager agent to do this. It's not deterministic.' A manager left to decide when to check its builders forgets to.

## Decision
`/loop <supervision.tick> /orchestrate tick` (default 15 minutes) drives every check-in. A tick checks every builder, reads PR comments and starts new builders when slots are free.

## Consequences
- + Stuck builders are found within one tick.
- − Ticks cost tokens even when nothing changed; the tick prints nothing unless the human is needed.

## Alternatives considered
- Event-driven only: misses silent failures.
