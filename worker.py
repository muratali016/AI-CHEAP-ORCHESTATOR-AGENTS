"""A live agent console. Run one of these per agent, each in its own cmd tab.

    python worker.py <agent_id> --session NAME

It sits in a loop watching its inbox for tasks the orchestrator (Claudey)
sends via dispatch.py. When a task arrives it streams the agent's THOUGHT
PROCESS live (DeepSeek reasoner's chain-of-thought, shown dim) followed by
its answer, appends the answer to the shared transcript, and drops the
result in its outbox for the orchestrator to collect.

So you can sit and watch each agent think in its own tab.
"""

import os
import sys
import time
import json
import glob
import argparse

from dotenv import load_dotenv
from openai import OpenAI

from agents import AGENTS
from env_context import build_env_context
import session as sess

BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-reasoner"  # exposes reasoning_content = the live thought process

# ANSI styling (cmd on Win10+/Win11 supports these).
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BOLD = "\033[1m"
RESET = "\033[0m"


def _dirs(session: str, agent_id: str):
    base = os.path.join("runs", session)
    inbox = os.path.join(base, "inbox", agent_id)
    outbox = os.path.join(base, "outbox", agent_id)
    done = os.path.join(base, "processed", agent_id)
    for d in (inbox, outbox, done):
        os.makedirs(d, exist_ok=True)
    return inbox, outbox, done


def _build_messages(agent_id: str, agent: dict, task: str, session: str):
    turns = sess.load(session)
    others = [t for t in turns if t["role"] != "orchestrator"]
    dialogue = sess.as_dialogue(others or turns)
    env_block = build_env_context()

    system = (
        agent["system"]
        + "\n\nYou are part of a team led by an Orchestrator named Claudey. "
        "Other agents are: " + ", ".join(a["name"] for a in AGENTS.values()) + ". "
        "You can see the shared team conversation and may build on, agree with, "
        "or push back on teammates by name."
    )
    user = (
        f"{env_block}\n\n"
        f"## SHARED TEAM CONVERSATION SO FAR\n{dialogue}\n\n"
        f"## YOUR TASK FROM CLAUDEY\n{task}"
    )
    return system, user


def process_task(client, agent_id, agent, task, session):
    sess.append(session, "Claudey -> " + agent["name"], "orchestrator", task)
    system, user = _build_messages(agent_id, agent, task, session)

    print(f"\n{CYAN}{BOLD}{'='*60}{RESET}")
    print(f"{CYAN}{BOLD}NEW TASK from Claudey:{RESET} {task}")
    print(f"{CYAN}{BOLD}{'='*60}{RESET}\n")

    stream = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        stream=True,
    )

    reasoning_parts, answer_parts = [], []
    printed_think_header = printed_answer_header = False

    for chunk in stream:
        delta = chunk.choices[0].delta
        rc = getattr(delta, "reasoning_content", None)
        if rc:
            if not printed_think_header:
                print(f"{YELLOW}--- thinking ---{RESET}")
                printed_think_header = True
            sys.stdout.write(f"{DIM}{rc}{RESET}")
            sys.stdout.flush()
            reasoning_parts.append(rc)
        if delta.content:
            if not printed_answer_header:
                print(f"\n\n{GREEN}--- answer ---{RESET}")
                printed_answer_header = True
            sys.stdout.write(f"{GREEN}{delta.content}{RESET}")
            sys.stdout.flush()
            answer_parts.append(delta.content)

    answer = "".join(answer_parts)
    sess.append(session, agent["name"], agent_id, answer)
    print(f"\n\n{CYAN}--- done, sent back to Claudey ---{RESET}\n")
    return answer


def main():
    p = argparse.ArgumentParser()
    p.add_argument("agent_id")
    p.add_argument("--session", required=True)
    args = p.parse_args()
    agent_id = args.agent_id.lower()
    if agent_id not in AGENTS:
        raise SystemExit(f"Unknown agent. Choose from: {', '.join(AGENTS)}")

    os.system("")  # enable ANSI on Windows
    load_dotenv()
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("DEEPSEEK_API_KEY not set (check .env).")
    client = OpenAI(api_key=api_key, base_url=BASE_URL)
    agent = AGENTS[agent_id]

    inbox, outbox, done = _dirs(args.session, agent_id)
    print(f"{BOLD}{GREEN}{agent['name']} is LIVE{RESET}  (session: {args.session})")
    print(f"{DIM}Watching for tasks from Claudey... leave this tab open.{RESET}")

    while True:
        tasks = sorted(glob.glob(os.path.join(inbox, "*.task.json")))
        for tf in tasks:
            try:
                with open(tf, "r", encoding="utf-8") as f:
                    payload = json.load(f)
            except (OSError, json.JSONDecodeError):
                continue
            tid, task = payload["id"], payload["task"]
            try:
                answer = process_task(client, agent_id, agent, task, args.session)
            except Exception as e:  # keep the tab alive on API errors
                answer = f"[worker error: {e}]"
                print(f"{YELLOW}{answer}{RESET}")
            with open(os.path.join(outbox, f"{tid}.result.txt"), "w", encoding="utf-8") as f:
                f.write(answer)
            os.replace(tf, os.path.join(done, os.path.basename(tf)))
        time.sleep(0.5)


if __name__ == "__main__":
    main()
