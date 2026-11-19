# ADR-0015: Agents follow the project's existing branch, commit and PR conventions

- Status: Accepted
- Date: 2026-11-19
- Deciders: Arslan Asghar

## Context
A tool that invents its own branch names and PR format creates noise for human reviewers and breaks team tooling. Many teams already document their conventions (for example in a `/open-pr` command).

## Decision
`init` reads the project's convention and writes it to `.orchestra.json`: per-repo bases, `PREFIX-NNNN` numbering, branch pattern, one-line commit format, PR body sections, no attribution. `pr_guard` enforces them on every `git commit`, `git push` and `gh pr create`.

## Consequences
- + Agent PRs look exactly like human PRs.
- − The config must be kept in sync when the convention changes (`/orchestrate init --refresh`).

## Alternatives considered
- A fixed built-in convention.
