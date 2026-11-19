#!/usr/bin/env python3
"""ADR-0001 / ADR-0007: a PR that touches architecture-sensitive paths must add an ADR.

On `gh pr create`, diff the branch against its base. If any changed file matches
adr.guard_paths and no file under adr.dir was added or changed, block with a hint.
An explicit opt-out is allowed: the PR body's "Deliberately not done" section may say
"No ADR needed: <reason>".
"""
import fnmatch
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (  # noqa: E402
    allow, block, find_config, flag_values, read_hook_input, repo_root, role, split_segments,
)

data = read_hook_input()
if not role() or data.get("tool_name") != "Bash":
    allow()
command = (data.get("tool_input") or {}).get("command", "")
cwd = data.get("cwd") or os.getcwd()
config, config_dir = find_config(cwd)
if not config:
    allow()
adr = config.get("adr") or {}
guard = adr.get("guard_paths") or []
adr_dir = adr.get("dir", "docs/adr").rstrip("/") + "/"
if not guard:
    allow()

for tokens in split_segments(command):
    if os.path.basename(tokens[0]) != "gh" or tokens[1:3] != ["pr", "create"]:
        continue
    args = tokens[3:]
    base = (flag_values(args, "--base", "-B") or [None])[0]
    if not base:
        allow()  # pr_guard reports the missing --base
    body = ""
    for f in flag_values(args, "--body-file", "-F"):
        try:
            body = open(f if os.path.isabs(f) else os.path.join(cwd, f)).read()
        except OSError:
            pass
    if re.search(r"No ADR needed:\s*\S", body, re.I):
        allow()
    root = repo_root(cwd) or cwd
    out = subprocess.run(["git", "-C", cwd, "diff", "--name-only", f"origin/{base}...HEAD"],
                         capture_output=True, text=True, timeout=20)
    if out.returncode != 0:
        allow()  # can't diff (no fetch yet); don't block on our own failure
    changed = [l for l in out.stdout.splitlines() if l]
    # guard paths are relative to the config dir; changed paths are relative to the repo
    rel = os.path.relpath(root, config_dir)
    prefix = "" if rel == "." else rel.rstrip("/") + "/"
    hits = [c for c in changed for g in guard if fnmatch.fnmatch(prefix + c, g) or fnmatch.fnmatch(c, g)]
    has_adr = any(c.startswith(adr_dir) or (prefix + c).startswith(adr_dir) for c in changed)
    if hits and not has_adr:
        block("ADR guard: this PR changes " + ", ".join(sorted(set(hits))[:5])
              + f" but adds no ADR under {adr_dir}. Draft one with /adr, or write "
              "'No ADR needed: <reason>' under 'Deliberately not done'.")

allow()
