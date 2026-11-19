---
description: Architecture Decision Records — draft | list | accept NNNN | supersede NNNN "<title>"
argument-hint: "<title>" | list | accept NNNN | reject NNNN | supersede NNNN "<title>"
---

Arguments: `$ARGUMENTS`. ADRs live in `adr.dir` from `.orchestra.json` (default `docs/adr`).
File names: `NNNN-kebab-title.md`. Numbers are sequential and never reused. ADR numbers are
separate from task IDs.

- **"<title>"**: draft a new ADR from `${CLAUDE_PLUGIN_ROOT}/templates/adr.md` with the next
  number, status **Proposed**. Fill Context, Decision, Consequences and Alternatives from the
  current conversation and code. Show it; don't accept it yourself.
- **list**: table of number · title · status · date, from the files. Rebuild
  `docs/adr/README.md` (the index) if it's out of date.
- **accept NNNN** / **reject NNNN**: only when the human asks. Change the Status line and the
  date; touch nothing else.
- **supersede NNNN "<title>"**: draft a new ADR whose Context explains what changed. On
  acceptance, set the old one's status to `Superseded by ADR-MMMM` and the new one's to
  `Accepted (supersedes ADR-NNNN)`. Never edit the old ADR's Decision or Consequences.

Rules: Accepted ADRs are immutable apart from their Status line. One decision per ADR. Write
the Decision in the active voice ("Builders branch from origin/<base>").
