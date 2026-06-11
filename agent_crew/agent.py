"""Simple (no-tabs) dispatch of a sub-task to one DeepSeek worker.

    python agent.py <agent_id> "the sub-task" --session NAME [--no-env]
    python agent.py <agent_id> - --session NAME      # task from stdin

Uses deepseek-chat. For the live-tabs experience (streamed thinking) use
worker.py + dispatch.py instead. agent_id is one of: coder, designer, ux.
"""

import sys
import os
import argparse
from dotenv import load_dotenv
from openai import OpenAI

import config
from agents import AGENTS
from env_context import build_env_context
import session as sess


def run_agent(agent_id: str, task: str, session: str, include_env: bool) -> str:
    if agent_id not in AGENTS:
        raise SystemExit(f"Unknown agent '{agent_id}'. Choose from: {', '.join(AGENTS)}")

    load_dotenv(config.ENV_PATH)
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("DEEPSEEK_API_KEY not set (check agent_crew/.env).")

    agent = AGENTS[agent_id]
    client = OpenAI(api_key=api_key, base_url=config.DEEPSEEK_BASE_URL)

    sess.append(session, "Claudey -> " + agent["name"], "orchestrator", task)
    turns = sess.load(session)
    dialogue = sess.as_dialogue([t for t in turns if t["role"] != "orchestrator"] or turns)
    env_block = build_env_context() if include_env else "(environment snapshot disabled)"

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

    resp = client.chat.completions.create(
        model=config.CHAT_MODEL,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        temperature=0.7,
        stream=False,
    )
    reply = resp.choices[0].message.content
    sess.append(session, agent["name"], agent_id, reply)
    return reply


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("agent_id")
    p.add_argument("task", help="the sub-task text, or - to read from stdin")
    p.add_argument("--session", required=True)
    p.add_argument("--no-env", action="store_true")
    args = p.parse_args()

    task = sys.stdin.read() if args.task == "-" else args.task
    reply = run_agent(args.agent_id.lower(), task, args.session, not args.no_env)
    print(f"===== {AGENTS[args.agent_id.lower()]['name']} =====\n")
    print(reply)


if __name__ == "__main__":
    main()
