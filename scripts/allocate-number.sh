#!/usr/bin/env bash
# Allocate the next task number (e.g. AA-0031) for ONE configured repo.   ADR-0010
#
#   scripts/allocate-number.sh <repo-name> [config-dir]
#
# Counters are independent per repo. The next number is one above the highest of:
#   - every PREFIX-NNNN in `git branch -a` of that repo (remote branches count as claimed)
#   - every number already claimed locally under .orchestra/claims/<repo>/
# Allocation runs under a per-repo lock, and the claim is written before the lock is
# released, so two tasks allocated seconds apart never get the same number.
set -euo pipefail

repo="${1:?usage: allocate-number.sh <repo-name> [config-dir]}"
root="${2:-$PWD}"
while [ ! -f "$root/.orchestra.json" ] && [ "$root" != "/" ]; do root="$(dirname "$root")"; done
[ -f "$root/.orchestra.json" ] || { echo "no .orchestra.json found" >&2; exit 1; }

read -r path prefix digits < <(python3 - "$root/.orchestra.json" "$repo" <<'PY'
import json, sys
c = json.load(open(sys.argv[1])); r = (c.get("repos") or {}).get(sys.argv[2])
if not r: sys.exit(f"repo '{sys.argv[2]}' is not in .orchestra.json repos; stop and ask")
n = (c.get("pr") or {}).get("numbering") or {}
print(r.get("path", "."), n.get("prefix", "AA"), n.get("digits", 4))
PY
)
repo_dir="$root/$path"
claims="$root/.orchestra/claims/$repo"
lock="$root/.orchestra/locks/$repo.lock"
mkdir -p "$claims" "$(dirname "$lock")"

# portable lock: mkdir is atomic everywhere (macOS has no flock by default)
for _ in $(seq 1 100); do mkdir "$lock" 2>/dev/null && break; sleep 0.1; done
[ -d "$lock" ] || { echo "could not take lock $lock" >&2; exit 1; }
trap 'rmdir "$lock" 2>/dev/null || true' EXIT

git -C "$repo_dir" fetch --quiet --all --prune || { echo "fetch failed in $repo_dir; not allocating" >&2; exit 1; }
remote=$(git -C "$repo_dir" remote get-url origin 2>/dev/null || true)
total=$(git -C "$repo_dir" branch -a | wc -l | tr -d ' ')
re="${prefix}-[0-9]{${digits}}"
top=$( { git -C "$repo_dir" branch -a | grep -oE "$re" || true; ls "$claims" 2>/dev/null | grep -oE "$re" || true; } \
       | sort -u | tail -1)

if [ -z "$top" ]; then
  # Empty result: only start at 1 if the scan itself looks healthy.
  if [ -z "$remote" ] || [ "$total" -eq 0 ]; then
    echo "scan looks broken (remote='$remote', branches=$total); not allocating" >&2; exit 1
  fi
  echo "note: no ${prefix}- branches in $repo ($total branches, $remote); starting at 1" >&2
  n=1
else
  n=$(( 10#${top#${prefix}-} + 1 ))
fi
id=$(printf "%s-%0${digits}d" "$prefix" "$n")
date -u +%Y-%m-%dT%H:%M:%SZ > "$claims/$id"
echo "$id"
