#!/usr/bin/env python3
"""ADR-0003: the manager never writes code.

The manager runs as the main session with ORCHESTRA_ROLE=manager. Builders are
sub-agents of that session; Claude Code includes `agent_id` in hook input for
sub-agent tool calls, so a write WITHOUT agent_id came from the manager itself.
The manager agent's `tools:` list (no Edit/Write) is the primary enforcement;
this hook is the second line of defence.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import allow, block, read_hook_input, role  # noqa: E402

WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}

data = read_hook_input()
if role() != "manager" or data.get("tool_name") not in WRITE_TOOLS:
    allow()
if data.get("agent_id"):
    allow()  # a builder (sub-agent) is writing; that's its job

path = (data.get("tool_input") or {}).get("file_path", "")
# The manager may keep its own bookkeeping under .orchestra/ (tasks, state).
if "/.orchestra/" in path.replace("\\", "/"):
    allow()

block(
    "ADR-0003: the manager never writes code. Record a task and start a builder "
    "for it instead (see /orchestrate build)."
)
