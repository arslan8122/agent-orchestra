# ADR-0016: Config is JSON and hooks use only the Python standard library

- Status: Accepted
- Date: 2026-11-19
- Deciders: Arslan Asghar

## Context
Hooks run on every tool call in every project. A YAML config would need PyYAML or another runtime that many machines lack, and a failing hook import blocks work.

## Decision
Project config lives in `.orchestra.json`. Hooks are Python 3 scripts using only the standard library; scripts are POSIX shell plus `git`, `gh` and `ffmpeg`.

## Consequences
- + No install step beyond the plugin itself.
- − JSON has no comments; the guide documents each field.

## Alternatives considered
- YAML config.
- Node hooks: not every repo has Node.
