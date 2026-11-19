#!/usr/bin/env bash
# Hook and allocator tests. No dependencies beyond python3, git and bash.
#   bash tests/run.sh
set -uo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
pass=0; fail=0

# --- fixture: an origin repo plus a clone with .orchestra.json -------------------------
git init -q -b main "$T/origin.git" --bare
git clone -q "$T/origin.git" "$T/proj" 2>/dev/null
cd "$T/proj"
git config user.email t@example.com; git config user.name t
git commit -q --allow-empty -m "chore: init"; git push -q origin main
git checkout -q -b feat/AA-0007-old-work && git push -q origin feat/AA-0007-old-work && git checkout -q main
cat > .orchestra.json <<'JSON'
{ "repos": { "app": { "path": ".", "base": "main" } },
  "pr": { "numbering": { "prefix": "AA", "digits": 4 },
          "branch": { "pattern": "{type}/{id}-{slug}", "types": ["feat", "fix"] },
          "body": { "sections": ["Problem", "Change", "Verification", "Demo"] } },
  "adr": { "dir": "docs/adr", "guard_paths": [] } }
JSON
good_body="$T/good.md"
printf '## Problem\nx\n\n## Change\n- y\n\n## Verification\n- 3 passed\n\n## Demo\n<!-- orchestra:demo pending -->\n' > "$good_body"
missing_body="$T/missing.md"; printf '## Problem\nx\n' > "$missing_body"
attrib_body="$T/attrib.md"; { cat "$good_body"; echo; echo "🤖 Generated with Claude Code"; } > "$attrib_body"
nodemo_body="$T/nodemo.md"; printf '## Problem\nx\n\n## Change\n- y\n\n## Verification\n- ok\n\n## Demo\n\n' > "$nodemo_body"

hook_json() { # tool command [agent_id]
  python3 -c 'import json,sys; t,c,a=sys.argv[1],sys.argv[2],sys.argv[3]; k="command" if t=="Bash" else "file_path"; d={"tool_name":t,"tool_input":{k:c},"cwd":sys.argv[4]}; d.update({"agent_id":a} if a else {}); print(json.dumps(d))' "$1" "$2" "${3:-}" "$PWD"
}
check() { # name expected_exit role hook tool command [agent_id]
  local name="$1" want="$2" r="$3" hook="$4" tool="$5" cmd="$6" aid="${7:-}"
  got=$(hook_json "$tool" "$cmd" "$aid" | ORCHESTRA_ROLE="$r" python3 "$HERE/hooks/$hook" 2>/dev/null; echo $?)
  if [ "$got" = "$want" ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: $name (want $want, got $got)"; fi
}

# manager_no_write
check "manager write blocked"            2 manager  manager_no_write.py Write "$PWD/src/app.ts"
check "builder (sub-agent) write ok"     0 manager  manager_no_write.py Write "$PWD/src/app.ts" agent-123
check "manager bookkeeping write ok"     0 manager  manager_no_write.py Write "$PWD/.orchestra/tasks/AA-0008.md"
check "no orchestra role: write ok"      0 ""       manager_no_write.py Write "$PWD/src/app.ts"

# pr_guard: never merge / never push to base
check "gh pr merge blocked"              2 builder pr_guard.py Bash "gh pr merge 12 --squash" a
check "push to base blocked"             2 builder pr_guard.py Bash "git push origin main" a
check "push HEAD:main blocked"           2 builder pr_guard.py Bash "git push origin HEAD:main" a
check "push feature branch ok"           0 builder pr_guard.py Bash "git push -u origin feat/AA-0008-add-health-check" a
check "manager git commit blocked"       2 manager pr_guard.py Bash "git commit -m 'feat(api): x'"
check "no role: merge allowed"           0 ""      pr_guard.py Bash "gh pr merge 12"

# pr_guard: gh pr create
ok="gh pr create --draft --base main --head feat/AA-0008-add-health-check --title 'feat(api): add health check' --body-file $good_body"
check "good pr create ok"                0 builder pr_guard.py Bash "$ok" a
check "missing --head blocked"           2 builder pr_guard.py Bash "gh pr create --base main --body-file $good_body" a
check "wrong base blocked"               2 builder pr_guard.py Bash "gh pr create --base develop --head feat/AA-0008-add-health-check --body-file $good_body" a
check "bad branch name blocked"          2 builder pr_guard.py Bash "gh pr create --base main --head my-branch --body-file $good_body" a
check "one-word slug blocked"            2 builder pr_guard.py Bash "gh pr create --base main --head feat/AA-0008-changes --body-file $good_body" a
check "missing sections blocked"         2 builder pr_guard.py Bash "gh pr create --base main --head feat/AA-0008-add-health-check --body-file $missing_body" a
check "attribution in body blocked"      2 builder pr_guard.py Bash "gh pr create --base main --head feat/AA-0008-add-health-check --body-file $attrib_body" a
check "empty Demo blocked"               2 builder pr_guard.py Bash "gh pr create --base main --head feat/AA-0008-add-health-check --body-file $nodemo_body" a
check "empty Demo ok with --attach"      0 builder pr_guard.py Bash "gh pr create --base main --head feat/AA-0008-add-health-check --body-file $nodemo_body --attach demo.mp4" a

# pr_guard: commits
check "good commit ok"                   0 builder pr_guard.py Bash "git commit -m 'feat(api): add health check endpoint'" a
check "commit with body blocked"         2 builder pr_guard.py Bash "git commit -m 'feat(api): x' -m 'more detail'" a
check "bad commit subject blocked"       2 builder pr_guard.py Bash "git commit -m 'added stuff'" a
check "co-authored-by blocked"           2 builder pr_guard.py Bash "git commit -m 'feat(api): x Co-Authored-By: someone'" a
check "chained: commit ok then merge"    2 builder pr_guard.py Bash "git commit -m 'fix(web): y' && gh pr merge 3" a

# allocator
id1=$(bash "$HERE/scripts/allocate-number.sh" app "$PWD" 2>/dev/null)
id2=$(bash "$HERE/scripts/allocate-number.sh" app "$PWD" 2>/dev/null)
[ "$id1" = "AA-0008" ] && pass=$((pass+1)) || { fail=$((fail+1)); echo "FAIL: allocator first id (got '$id1', want AA-0008)"; }
[ "$id2" = "AA-0009" ] && pass=$((pass+1)) || { fail=$((fail+1)); echo "FAIL: allocator second id (got '$id2', want AA-0009)"; }
bash "$HERE/scripts/allocate-number.sh" nope "$PWD" >/dev/null 2>&1 && { fail=$((fail+1)); echo "FAIL: unknown repo should fail"; } || pass=$((pass+1))

# validate-task.py
good_task="$T/good-task.md"; cat > "$good_task" <<'MD'
## Acceptance criteria
- AC-1: rows show reply time
- AC-2: unreplied rows say awaiting reply
## Test cases
| ID | Covers | Level | Given | When | Then | Video |
|---|---|---|---|---|---|---|
| TC-1 | AC-1 | unit | reply after 2h | format | "replied in 2h" | no |
| TC-2 | AC-2 | e2e | no reply | open inbox | "awaiting reply" | yes |
### Edge and failure cases
| ID | Covers | Level | Given | When | Then | Video |
|---|---|---|---|---|---|---|
| TC-3 | AC-1 | unit | reply before request | format | "awaiting reply" | no |
MD
vt() { python3 "$HERE/scripts/validate-task.py" "$1" >/dev/null 2>&1; echo $?; }
expect() { [ "$2" = "$3" ] && pass=$((pass+1)) || { fail=$((fail+1)); echo "FAIL: $1 (want $3, got $2)"; }; }
expect "valid task passes" "$(vt "$good_task")" 0
grep -v "TC-2" "$good_task" > "$T/t1.md";            expect "uncovered AC fails"      "$(vt "$T/t1.md")" 1
sed '/### Edge/,$d' "$good_task" > "$T/t2.md";        expect "no edge case fails"      "$(vt "$T/t2.md")" 1
sed 's/| unit | reply after 2h |/| unit | |/' "$good_task" > "$T/t3.md"; expect "empty Given fails" "$(vt "$T/t3.md")" 1
sed 's/| e2e |/| smoke |/' "$good_task" > "$T/t4.md"; expect "bad level fails"         "$(vt "$T/t4.md")" 1
{ cat "$good_task"; echo "- AC-3: {criterion}"; } > "$T/t5.md"; expect "placeholder fails" "$(vt "$T/t5.md")" 1

echo "passed: $pass  failed: $fail"
[ "$fail" -eq 0 ]
