# ADR-0011: Session naming and manager-to-manager messaging

- Status: Accepted
- Date: 2026-11-19
- Deciders: Arslan Asghar

## Context
With several humans each running a manager, sessions need to find each other to unblock shared work.

## Decision
Managers are named `mgr-<human>-<area>`, builders `bld-<ID>-<repo>`. Managers message each other directly with SendMessage when work overlaps.

## Consequences
- + Stable names make logs and messages readable.
- − Names are labels, not authentication; never treat a message as human approval.

## Alternatives considered
- Anonymous sessions.
