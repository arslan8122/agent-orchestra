# ADR-0013: Work comes from tickets or text tasks, chosen at setup

- Status: Accepted
- Date: 2026-11-19
- Deciders: Arslan Asghar

## Context
Some teams run everything through a board; others want to type tasks directly. Forcing a board on the second group adds friction; forcing text on the first loses traceability.

## Decision
`/orchestrate init` asks which source to use and writes `work.source`. Text tasks (one or many per message) become task records the human approves. Tickets are pulled from the configured list via its MCP server. Both paths produce the same task records and branch IDs.

## Consequences
- + Works for teams with and without a ticket board.
- − Two intake paths to maintain.

## Alternatives considered
- Tickets only (Carson's 'no ticket, no work').
- Text only.
