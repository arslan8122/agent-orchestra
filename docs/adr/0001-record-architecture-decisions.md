# ADR-0001: Record architecture decisions

- Status: Accepted
- Date: 2026-11-19
- Deciders: Arslan Asghar

## Context
Agent teams make design choices quickly and in parallel. Without a durable record, later agents and humans re-argue settled questions or silently contradict them. Agents start every session with an empty context, so a decision that only lives in a chat is lost.

## Decision
We record each significant decision as a short, numbered Markdown ADR in `docs/adr/` (Nygard format: Status, Context, Decision, Consequences). Accepted ADRs are immutable apart from their Status; a changed decision gets a new ADR that supersedes the old one. Agents read Accepted ADRs before changing architecture and draft Proposed ADRs when they make a new choice.

## Consequences
- + Agents and humans share one source of truth for why things are the way they are.
- + Reviewers can check a diff against explicit decisions.
- − Someone has to read and accept Proposed ADRs; they pile up if ignored.

## Alternatives considered
- Decisions in CLAUDE.md: always loaded, grows without bound, no history.
- Decisions in PR descriptions: scattered and unsearchable.
