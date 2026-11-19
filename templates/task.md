# {id}: {title}

- Repo: {repo}
- Source: {source}            <!-- text task entered {date}, or ticket URL -->
- Status: Drafted
- Depends on: {deps}
- Paired with: {paired}

## Original request
> {original_text}

## Acceptance criteria
- AC-1: {criterion}

## Test cases
<!-- Planned with the task and approved by the human BEFORE a builder starts (ADR-0017).
     Every acceptance criterion is covered by at least one test case. The builder writes these
     tests first and sees them fail; QA's video shows the ones marked "video: yes". -->

| ID | Covers | Level | Given | When | Then | Video |
|---|---|---|---|---|---|---|
| TC-1 | AC-1 | unit | {state} | {action} | {expected result} | no |
| TC-2 | AC-1 | e2e | {state} | {action} | {expected result} | yes |

### Edge and failure cases
| ID | Covers | Level | Given | When | Then | Video |
|---|---|---|---|---|---|---|
| TC-3 | AC-1 | integration | {invalid / empty / unauthorised state} | {action} | {error or no-op} | no |

## Out of scope
- {what this task deliberately won't do}

## Notes / answers from the human
