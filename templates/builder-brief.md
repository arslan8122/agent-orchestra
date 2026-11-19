# Builder brief: {id}

- **Task:** {title}
- **Repo:** {repo} (`{repo_path}`)
- **Base branch:** `{base}`
- **Branch to create:** `{branch}`
- **Source:** {source}   <!-- text task file or ticket URL -->
- **Depends on / paired with:** {paired}

## Acceptance criteria
{criteria}

## Architecture decisions you must respect
{adr_links}

## Definition of done (ADR-0007)
1. A failing test for the acceptance criteria exists before the implementation.
2. Every `verify` command in `.orchestra.json` passes.
3. Reviewer approved within {review_rounds_max} rounds (else stop and report).
4. QA recorded a video of the change working.
5. A PR is open against `{base}` with every body section filled and the Demo video attached.

Ask the manager (never the human) when blocked. Never merge. Never push to `{base}`.
