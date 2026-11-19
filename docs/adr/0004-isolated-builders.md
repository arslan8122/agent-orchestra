# ADR-0004: Builders run isolated in their own worktrees; humans never address them

- Status: Accepted
- Date: 2026-11-19
- Deciders: Arslan Asghar

## Context
Several builders editing one checkout corrupt each other's work. Humans who talk to builders directly bypass the manager and lose track of 20 parallel threads.

## Decision
Each builder creates its own git worktree in the target repo, branched from `origin/<base>`. Builders are started and spoken to only by the manager; questions go builder → manager → human.

## Consequences
- + No file-level interference between builders.
- + One conversation for the human.
- − Worktrees can still share runtime resources (ports, databases); `builders.max` must respect that.

## Alternatives considered
- Agent-tool worktree isolation: creates the worktree in the top-level repo, which breaks for submodules.
- Cloud sessions per builder: better isolation, not free; supported later via `isolation: cloud`.
