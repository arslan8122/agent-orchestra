---
description: Run the agent orchestra — init | tasks "<text>" | build [tickets…] | plan "<goal>" | tick | status
argument-hint: init | tasks "<one or more tasks>" | build [ticket…] | plan "<goal>" | tick | status
---

Subcommand and arguments: `$ARGUMENTS`

Read `.orchestra.json` and `docs/adr/` first (except for `init`, which creates them). The full
reference is `${CLAUDE_PLUGIN_ROOT}/docs/guide.md`.

## init
Set the project up. Write nothing until all four answers are in.

1. Detect the stack: package.json / pyproject / go.mod / docker-compose, `.gitmodules`
   (each submodule is a candidate repo), Playwright, existing `docs/adr/`,
   `.claude/commands/*pr*.md`.
2. Ask with AskUserQuestion, one call, four questions:
   - **Work source:** "Tickets from a board" or "Text tasks I type (one or many)". If
     tickets: which provider and list, and which status means ready.
   - **PR convention:** if a PR command or CONTRIBUTING file exists, summarise the rules you
     read from it (numbering, branch pattern, per-repo bases, commit format, body sections,
     attribution) and ask to confirm. Otherwise ask for base branch, branch pattern, commit
     format and body sections, defaulting to `templates/orchestra.example.json`.
   - **Video host:** "GitHub attachment via gh --attach (free, not in the repo; needs gh
     2.99+)", "S3-compatible bucket such as Cloudflare R2 free tier", or "Both: gh first,
     bucket as fallback".
   - **Builders at once:** 1, 3 (recommended to start) or 5.
3. Write `.orchestra.json` from the answers (start from `templates/orchestra.example.json`,
   one `repos` entry per repo with its base). A repo whose base you don't know: ask; never
   default to main.
4. Create `docs/adr/` with ADR-0001 to ADR-0017 from `${CLAUDE_PLUGIN_ROOT}/docs/adr/`,
   status **Proposed**, Context rewritten for this project. Add `docs/adr/README.md` index.
5. Add `.orchestra/` to `.gitignore`. Append `templates/claude-md-section.md` to CLAUDE.md.
6. Check the tools: `gh --version` (warn if < 2.99: no `--attach`), `gh auth status`, `ffmpeg`,
   and run each `verify` command once and report the result.
7. Tell the human the next steps: review `.orchestra.json`, `/adr list`, then a dry run with
   one task and `builders.max` 1.

## tasks "<text>"
Only when `work.source` is `text`. The text may hold one task or a list (lines starting with
`-`, `*` or `1.`). Follow the manager's "Work intake" rules: split, choose repos, one question per
ambiguous task with a recommendation, then **plan the test cases** for each task (manager's
"Test cases are planned with the task"), show criteria and test cases together, and after
approval allocate IDs, write `.orchestra/tasks/<ID>.md`, and run `scripts/validate-task.py` on each. Then do `build` for the approved tasks.

## build [ticket…]
Start builders for the given tickets (ticket mode), or for every approved task without a
builder. In ticket mode, plan test cases from the ticket first and get them approved (post
them back to the ticket as a comment when the MCP server allows). Never start a builder for
a task whose record fails `scripts/validate-task.py`. Respect `builders.max` and dependency order. Write a state file per task.

## plan "<goal>"
Break a larger goal into tasks or ticket drafts with acceptance criteria, planned test cases
(Given/When/Then, incl. one edge or failure case each) and dependencies.
Show them for approval. Don't start builders.

## tick
One supervision pass, as in the manager's "Supervision" section. Designed to run under
`/loop <supervision.tick> /orchestrate tick`. Print nothing if nothing needs the human.

## status
Table: ID · repo · stage · review rounds · PR (draft/ready/merged) · blocker · last tick.
