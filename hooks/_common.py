"""Shared helpers for agent-orchestra hooks. Standard library only (ADR-0016)."""
import json
import os
import re
import shlex
import subprocess
import sys

CONFIG_NAME = ".orchestra.json"


def read_hook_input():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def block(message):
    """Exit 2: Claude Code blocks the tool call and shows stderr to the model."""
    print(message, file=sys.stderr)
    sys.exit(2)


def allow():
    sys.exit(0)


def role():
    return os.environ.get("ORCHESTRA_ROLE", "").strip()


def _git(cwd, *args):
    try:
        out = subprocess.run(
            ["git", "-C", cwd, *args], capture_output=True, text=True, timeout=10
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except Exception:
        return ""


def repo_root(cwd):
    """Top level of the checkout containing cwd. For a linked worktree, return the
    main checkout so worktrees map to the same repo entry in the config."""
    top = _git(cwd, "rev-parse", "--show-toplevel")
    if not top:
        return ""
    common = _git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if common and os.path.basename(common) == ".git":
        main = os.path.dirname(common)
        if os.path.isdir(main):
            return os.path.realpath(main)
    return os.path.realpath(top)


def find_config(cwd):
    """Walk up from cwd (and from the main checkout, for worktrees) to .orchestra.json."""
    starts = [os.path.realpath(cwd)]
    root = repo_root(cwd)
    if root:
        starts.append(root)
    for start in starts:
        d = start
        while True:
            p = os.path.join(d, CONFIG_NAME)
            if os.path.isfile(p):
                with open(p) as f:
                    return json.load(f), d
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent
    return None, None


def repo_entry(config, config_dir, cwd):
    """Return (name, entry) for the configured repo that contains cwd, preferring the
    deepest match so a submodule wins over the monorepo root."""
    root = repo_root(cwd) or os.path.realpath(cwd)
    best = (None, None, -1)
    for name, entry in (config.get("repos") or {}).items():
        path = os.path.realpath(os.path.join(config_dir, entry.get("path", ".")))
        if root == path or root.startswith(path + os.sep):
            if len(path) > best[2]:
                best = (name, entry, len(path))
    return best[0], best[1]


def all_bases(config):
    return {e.get("base") for e in (config.get("repos") or {}).values() if e.get("base")}


def current_branch(cwd):
    return _git(cwd, "branch", "--show-current")


def split_segments(command):
    """Split a shell command line into simple-command token lists on && || ; | and
    newlines. Good enough for guard checks; not a full shell parser."""
    parts = re.split(r"&&|\|\||;|\||\n", command)
    segments = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        try:
            tokens = shlex.split(part)
        except ValueError:
            tokens = part.split()
        # drop leading env assignments: FOO=bar cmd ...
        while tokens and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[0]):
            tokens = tokens[1:]
        if tokens:
            segments.append(tokens)
    return segments


def git_subcommand(tokens):
    """For ['git', '-C', 'x', 'push', ...] return ('push', ['...'], cwd_override)."""
    if not tokens or os.path.basename(tokens[0]) != "git":
        return None, [], None
    i, cwd = 1, None
    while i < len(tokens) and tokens[i].startswith("-"):
        if tokens[i] in ("-C", "-c") and i + 1 < len(tokens):
            if tokens[i] == "-C":
                cwd = tokens[i + 1]
            i += 2
        else:
            i += 1
    if i >= len(tokens):
        return None, [], cwd
    return tokens[i], tokens[i + 1:], cwd


def flag_values(args, *names):
    """Values for --flag value / --flag=value / -f value."""
    vals = []
    i = 0
    while i < len(args):
        a = args[i]
        for n in names:
            if a == n and i + 1 < len(args):
                vals.append(args[i + 1])
            elif a.startswith(n + "=") and n.startswith("--"):
                vals.append(a.split("=", 1)[1])
        i += 1
    return vals


ATTRIBUTION = re.compile(r"co-authored-by|generated with|🤖", re.IGNORECASE)
