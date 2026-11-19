# ADR-0003: The manager agent never writes code

- Status: Accepted
- Date: 2026-11-19
- Deciders: Arslan Asghar

## Context
A manager that also codes stops supervising and its context fills with implementation detail. Carson's setup keeps the 'engineer manager' session code-free.

## Decision
The manager plans, delegates, supervises and reports. Its `tools:` list excludes Edit; `hooks/manager_no_write.py` blocks Write/Edit outside `.orchestra/` from the main session, and `hooks/pr_guard.py` blocks the manager from `git commit/push/merge/rebase`.

## Consequences
- + The manager's context stays on coordination, so it can supervise more builders.
- − The manager can still run arbitrary Bash; the guards cover the common paths, not every shell trick.
- − Relies on Claude Code sending `agent_id` for sub-agent tool calls to tell builders from the manager; verify on upgrade.

## Alternatives considered
- Prompt-only rule: models drift under pressure.
- Separate OS user for the manager: too heavy for a plugin.
