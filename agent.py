"""Dispatch a sub-task to a single DeepSeek worker agent, within a shared
session so the agents are aware of each other and of the environment.

Usage:
    python agent.py <agent_id> "the sub-task" --session NAME [--no-env]
    python agent.py <agent_id> - --session NAME      # read task from stdin

agent_id is one of: coder, designer, ux

What each agent sees on every call:
  1. Its fixed role (system prompt).
  2. A live ENVIRONMENT SNAPSHOT of the working dir  -> env aware.
  3. The shared team conversation so far              -> aware of each other.
  4. Its specific sub-task from the orchestrator.

The agent's turn (and the orchestrator's task) are appended to the shared
transcript at runs/<session>/transcript.md so you can read the whole group
conversation.
"""

import sys
import os
import argparse
from dotenv import load_dotenv
from openai import OpenAI

from agents import AGENTS
from env_context import build_env_context
import session as sess

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"


def run_agent(agent_id: str, task: str, session: str, include_env: bool) -> str:
    if agent_id not in AGENTS:
        raise SystemExit(
            f"Unknown agent '{agent_id}'. Choose from: {', '.join(AGENTS)}"
        )

    load_dotenv()
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("DEEPSEEK_API_KEY not set (check your .env file).")

    agent = AGENTS[agent_id]
    client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)

    # Record the orchestrator's instruction to this agent in the shared log.
    sess.append(session, "Orchestrator -> " + agent["name"], "orchestrator", task)

    turns = sess.load(session)
    dialogue = sess.as_dialogue([t for t in turns if t["role"] != "orchestrator"] or turns)

    env_block = build_env_context() if include_env else "(environment snapshot disabled)"

    system = (
        agent["system"]
        + "\n\nYou are part of a team led by an Orchestrator. Other agents on the "
        "team are: " + ", ".join(a["name"] for a in AGENTS.values()) + ". "
        "You can see the shared team conversation and may explicitly build on, "
        "agree with, or push back on what other agents said. Address teammates "
        "by name when you reference their work."
    )

    user = (
        f"{env_block}\n\n"
        f"## SHARED TEAM CONVERSATION SO FAR\n{dialogue}\n\n"
        f"## YOUR TASK FROM THE ORCHESTRATOR\n{task}"
    )

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.7,
        stream=False,
    )
    reply = resp.choices[0].message.content

    sess.append(session, agent["name"], agent_id, reply)
    return reply


def main() -> None:
    p = argparse.ArgumentParser(description="Dispatch a sub-task to a DeepSeek worker.")
    p.add_argument("agent_id")
    p.add_argument("task", help="the sub-task text, or - to read from stdin")
    p.add_argument("--session", required=True, help="shared session name")
    p.add_argument("--no-env", action="store_true", help="skip env snapshot")
    args = p.parse_args()

    task = sys.stdin.read() if args.task == "-" else args.task
    reply = run_agent(args.agent_id.lower(), task, args.session, not args.no_env)

    print(f"===== {AGENTS[args.agent_id.lower()]['name']} =====\n")
    print(reply)


if __name__ == "__main__":
    main()
