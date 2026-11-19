# ADR-0009: The system opens PRs and never merges

- Status: Accepted
- Date: 2026-11-19
- Deciders: Arslan Asghar

## Context
Merging is the point where a human takes responsibility for the change. Teams already have review and merge practices that a tool shouldn't bypass.

## Decision
No agent merges. `pr_guard` blocks `gh pr merge` and pushes to any configured base branch; branch protection on GitHub backs it up. The orchestra's job ends when a PR is open, out of draft, with its video.

## Consequences
- + Humans keep control of what lands.
- − Throughput is limited by human review; that's intended.

## Alternatives considered
- Merge manager and merge queue (Carson's setup): more automation than this team wants.
