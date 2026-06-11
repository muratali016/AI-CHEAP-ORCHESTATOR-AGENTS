"""Orchestrator -> worker dispatch. Claudey uses this to hand a sub-task to
a live agent tab and wait for its answer.

    python dispatch.py <agent_id> "the sub-task" --session NAME [--timeout 240]

Writes a task into the agent's inbox (the worker tab picks it up, streams its
thinking, writes the result), then polls the outbox and prints the answer.
Requires that agent's worker.py to be running (open the tabs with start_team).
"""

import os
import sys
import time
import json
import uuid
import argparse

from agents import AGENTS


def main():
    p = argparse.ArgumentParser()
    p.add_argument("agent_id")
    p.add_argument("task", help="sub-task text, or - to read from stdin")
    p.add_argument("--session", required=True)
    p.add_argument("--timeout", type=float, default=240.0)
    args = p.parse_args()

    agent_id = args.agent_id.lower()
    if agent_id not in AGENTS:
        raise SystemExit(f"Unknown agent. Choose from: {', '.join(AGENTS)}")
    task = sys.stdin.read() if args.task == "-" else args.task

    base = os.path.join("runs", args.session)
    inbox = os.path.join(base, "inbox", agent_id)
    outbox = os.path.join(base, "outbox", agent_id)
    os.makedirs(inbox, exist_ok=True)
    os.makedirs(outbox, exist_ok=True)

    tid = uuid.uuid4().hex[:12]
    result_path = os.path.join(outbox, f"{tid}.result.txt")
    tmp = os.path.join(inbox, f"{tid}.task.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"id": tid, "task": task}, f, ensure_ascii=False)
    os.replace(tmp, os.path.join(inbox, f"{tid}.task.json"))  # atomic publish

    deadline = time.time() + args.timeout
    while time.time() < deadline:
        if os.path.exists(result_path):
            time.sleep(0.1)  # let the write settle
            with open(result_path, "r", encoding="utf-8") as f:
                answer = f.read()
            os.remove(result_path)
            print(f"===== {AGENTS[agent_id]['name']} =====\n")
            print(answer)
            return
        time.sleep(0.5)

    raise SystemExit(
        f"Timed out after {args.timeout}s waiting for {agent_id}. "
        f"Is its worker tab running? (start_team)"
    )


if __name__ == "__main__":
    main()
