#!/usr/bin/env python3
"""Check a task record is ready for a builder (ADR-0002, ADR-0017).

    python3 scripts/validate-task.py .orchestra/tasks/AA-0017.md

Fails (exit 1, reasons on stderr) unless:
  - there is at least one acceptance criterion (AC-n)
  - there is at least one test case row (TC-n) with Covers, Level, Given, When, Then filled
  - every AC is covered by at least one TC
  - at least one TC is an edge or failure case (in the "Edge and failure cases" table)
  - no template placeholders ({...}) are left
The manager runs this before starting a builder; it starts none for a failing record.
"""
import re
import sys

LEVELS = {"unit", "integration", "e2e", "contract", "manual"}
text = open(sys.argv[1]).read()
errors = []

if re.search(r"\{[a-z_ /]+\}", text):
    errors.append("template placeholders like {criterion} are still present")

acs = set(re.findall(r"^\s*-\s*(AC-\d+)\s*:", text, re.M))
if not acs:
    errors.append("no acceptance criteria (lines like '- AC-1: …')")

rows = re.findall(r"^\|\s*(TC-\d+)\s*\|(.*)\|\s*$", text, re.M)
if not rows:
    errors.append("no test cases (rows like '| TC-1 | AC-1 | unit | … |')")
covered = set()
for tc, rest in rows:
    cells = [c.strip() for c in rest.split("|")]
    if len(cells) < 6 or not all(cells[:5]):
        errors.append(f"{tc}: Covers, Level, Given, When and Then must all be filled")
        continue
    if cells[1].lower() not in LEVELS:
        errors.append(f"{tc}: level '{cells[1]}' must be one of {sorted(LEVELS)}")
    covered.update(re.findall(r"AC-\d+", cells[0]))
missing = sorted(acs - covered)
if missing:
    errors.append("acceptance criteria with no test case: " + ", ".join(missing))

edge = text.split("### Edge and failure cases", 1)
if len(edge) < 2 or not re.search(r"^\|\s*TC-\d+", edge[1], re.M):
    errors.append("no edge or failure test case (add one under 'Edge and failure cases')")

if errors:
    print(f"{sys.argv[1]}: not ready for a builder", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print(f"{sys.argv[1]}: ready ({len(acs)} criteria, {len(rows)} test cases)")
