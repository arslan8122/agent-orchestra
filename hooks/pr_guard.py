#!/usr/bin/env python3
"""Guards every git/gh command an orchestra session runs.

ADR-0009  the system never merges: blocks `gh pr merge` and pushes to a base branch.
ADR-0015  PRs follow the project's convention: --base/--head present, base matches the
          repo's configured base, branch matches the pattern, body has every section,
          one-line commit subjects in the configured format, no attribution.
ADR-0008  a PR may only leave draft (`gh pr ready`) once its Demo video is attached.

Active only when ORCHESTRA_ROLE is set and a .orchestra.json is found, so a person's
ordinary Claude Code session in the same repo is unaffected.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (  # noqa: E402
    ATTRIBUTION, all_bases, allow, block, current_branch, find_config,
    flag_values, git_subcommand, read_hook_input, repo_entry, role, split_segments,
)

DEMO_PENDING = "<!-- orchestra:demo pending -->"

data = read_hook_input()
if not role() or data.get("tool_name") != "Bash":
    allow()
command = (data.get("tool_input") or {}).get("command", "")
cwd = data.get("cwd") or os.getcwd()
config, config_dir = find_config(cwd)
if not config:
    allow()

pr = config.get("pr") or {}
numbering = pr.get("numbering") or {}
prefix = numbering.get("prefix", "AA")
digits = int(numbering.get("digits", 4))
types = (pr.get("branch") or {}).get("types", ["feat", "fix"])
pattern = (pr.get("branch") or {}).get("pattern", "{type}/{id}-{slug}")
sections = (pr.get("body") or {}).get("sections", [])
commit_re = re.compile((pr.get("commit") or {}).get(
    "pattern", r"^(feat|fix|docs|chore|refactor|test|perf|build|ci)(\([a-z0-9._/-]+\))?: \S.*$"))
bases = all_bases(config)


def branch_regex(entry):
    allowed = [entry["branch_type"]] if entry and entry.get("branch_type") else types
    rx = re.escape(pattern)
    rx = rx.replace(re.escape("{type}"), "(?:" + "|".join(map(re.escape, allowed)) + ")")
    rx = rx.replace(re.escape("{id}"), re.escape(prefix) + r"-\d{" + str(digits) + "}")
    rx = rx.replace(re.escape("{slug}"), r"[a-z0-9]+(?:-[a-z0-9]+){1,4}")
    return re.compile("^" + rx + "$")


def read_body(args):
    for f in flag_values(args, "--body-file", "-F"):
        try:
            with open(f if os.path.isabs(f) else os.path.join(cwd, f)) as fh:
                return fh.read()
        except OSError:
            block(f"pr-guard: can't read --body-file {f}")
    vals = flag_values(args, "--body", "-b")
    return vals[0] if vals else None


def check_body(body, has_attach):
    missing = [s for s in sections
               if not re.search(r"^##\s+" + re.escape(s) + r"\s*$", body, re.M)]
    if missing:
        block("ADR-0015: PR body is missing section(s): " + ", ".join(missing)
              + ". Fill templates/pr-body.md.")
    if ATTRIBUTION.search(body):
        block("ADR-0015: no attribution in PR bodies (Co-Authored-By / 'Generated with').")
    if "Demo" in sections:
        m = re.search(r"^##\s+Demo\s*$(.*?)(?=^##\s|\Z)", body, re.M | re.S)
        demo = m.group(1) if m else ""
        if not (has_attach or DEMO_PENDING in demo or re.search(r"https?://", demo)):
            block("ADR-0008: the Demo section needs the video. Leave the placeholder "
                  f"'{DEMO_PENDING}' and open as --draft; scripts/upload-proof.sh fills it.")


for tokens in split_segments(command):
    head = os.path.basename(tokens[0])

    # ---- gh ----------------------------------------------------------------
    if head == "gh" and len(tokens) >= 3 and tokens[1] == "pr":
        sub, args = tokens[2], tokens[3:]
        if sub == "merge":
            block("ADR-0009: the orchestra never merges. A human merges in GitHub.")
        if sub == "create":
            base = (flag_values(args, "--base", "-B") or [None])[0]
            headb = (flag_values(args, "--head", "-H") or [None])[0]
            if not base or not headb:
                block("ADR-0015: gh pr create needs explicit --base and --head.")
            name, entry = repo_entry(config, config_dir, cwd)
            if not entry:
                block("ADR-0015: this repo isn't in .orchestra.json `repos`; "
                      "stop and ask which base it uses. Never fall back to main.")
            if base != entry.get("base"):
                block(f"ADR-0015: {name} PRs target '{entry.get('base')}', not '{base}'.")
            if not branch_regex(entry).match(headb):
                block(f"ADR-0015: branch '{headb}' doesn't match '{pattern}' "
                      f"({prefix}-{'N' * digits}, 2-5 word kebab slug).")
            title = (flag_values(args, "--title", "-t") or [""])[0]
            if ATTRIBUTION.search(title):
                block("ADR-0015: no attribution in PR titles.")
            body = read_body(args)
            if body is None:
                block("ADR-0015: pass the body with --body-file (filled templates/pr-body.md).")
            check_body(body, "--attach" in args)
        if sub == "ready":
            target = next((a for a in args if not a.startswith("-")), "")
            try:
                out = subprocess.run(["gh", "pr", "view", *( [target] if target else []),
                                      "--json", "body", "-q", ".body"],
                                     capture_output=True, text=True, timeout=20, cwd=cwd)
                if out.returncode == 0 and DEMO_PENDING in out.stdout:
                    block("ADR-0008: Demo video not attached yet. Run scripts/upload-proof.sh first.")
            except subprocess.TimeoutExpired:
                pass
        continue

    # ---- git ---------------------------------------------------------------
    sub, args, cdir = git_subcommand(tokens)
    if not sub:
        continue
    gcwd = cdir if cdir and os.path.isabs(cdir) else os.path.join(cwd, cdir) if cdir else cwd

    if role() == "manager" and not data.get("agent_id") and sub in ("commit", "push", "merge", "rebase", "cherry-pick"):
        block(f"ADR-0003: the manager doesn't run `git {sub}`. Builders own their branches.")

    if sub == "push":
        positional = [a for a in args if not a.startswith("-")]
        refspecs = positional[1:]
        targets = [r.split(":", 1)[1] if ":" in r else r for r in refspecs]
        if not targets:
            targets = [current_branch(gcwd)]
        targets = [t.replace("refs/heads/", "").lstrip("+") for t in targets if t]
        hit = [t for t in targets if t in bases]
        if hit:
            block(f"ADR-0009: never push to a base branch ({', '.join(hit)}). "
                  "Push your feature branch and open a PR.")

    if sub == "commit":
        if "--amend" in args and "--no-edit" in args:
            continue
        msgs = flag_values(args, "-m", "--message")
        files = flag_values(args, "-F", "--file")
        if files:
            try:
                with open(files[0] if os.path.isabs(files[0]) else os.path.join(gcwd, files[0])) as fh:
                    msgs = [fh.read().rstrip("\n")]
            except OSError:
                block(f"pr-guard: can't read commit message file {files[0]}")
        if not msgs:
            block("ADR-0015: commit with -m '<type>(<scope>): <summary>' (one line).")
        if len(msgs) > 1 or "\n" in msgs[0].strip():
            block("ADR-0015: commit messages are one line, no body. Details go in the PR.")
        if ATTRIBUTION.search(msgs[0]):
            block("ADR-0015: no attribution in commits (no Co-Authored-By trailer).")
        if not commit_re.match(msgs[0].strip()):
            block(f"ADR-0015: commit subject '{msgs[0]}' doesn't match {commit_re.pattern}")

allow()
