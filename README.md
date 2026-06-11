


Example work

https://github.com/user-attachments/assets/f79d7b33-e7a6-4078-bd1f-599cf600fc68




# 🐉 AI Orchestration Crew — Claudey + 3 DeepSeek Agents

A small multi-agent orchestration setup. **You** are the controller. **Claudey**
(Claude Code) is the orchestrator. Three **DeepSeek** worker agents do the work,
each in its own live terminal tab streaming its chain-of-thought:

| Agent | Role |
|-------|------|
| Agent 1 | **Coder** |
| Agent 2 | **Designer** |
| Agent 3 | **UX** |

The agents are **environment-aware** (they see the host project's files) and they
**see each other** through one shared transcript per session — so they genuinely
collaborate (e.g. UX writes a spec → Designer builds it → Coder wires it up).

---

## ✨ Features
- **Orchestrator pattern** — one controller splits a task across specialized agents.
- **Live "thinking" tabs** — each agent runs in its own console streaming the
  DeepSeek *reasoner* chain-of-thought, then its answer.
- **Shared transcript** — agents read each other's turns; full logs in `runs/`.
- **Env-aware** — agents get a live snapshot of the project they're working on.
- **Portable crew** — the [`agent_crew/`](agent_crew/) folder is a self-contained,
  drop-in version you can copy into any project.

## 🎮 Demo built by the crew
[`minecraft_light/index.html`](minecraft_light/index.html) — a lightweight
browser Minecraft clone (Three.js, single file, no build step) the crew designed
and built end-to-end. Just open it in a browser.

---

## 🚀 Setup
```bash
pip install -r requirements.txt        # or: pip install openai python-dotenv
cp .env.example .env                   # then paste your DeepSeek API key
```
Get a DeepSeek key at https://platform.deepseek.com

## 🖥️ Run

**Live tabs (watch them think):**
```bash
python start_team.py mysession         # opens 3 tabs: Coder / Designer / UX
python dispatch.py coder "your sub-task" --session mysession
```

**Simple (no tabs, one-shot):**
```bash
python agent.py coder "your sub-task" --session mysession
```

Either way the full group conversation is saved to `runs/<session>/transcript.md`.

> 💡 The [`agent_crew/`](agent_crew/) folder is the portable, path-independent
> version — copy it into any other project and run it there. See
> [`agent_crew/CLAUDEY.md`](agent_crew/CLAUDEY.md) for how an AI orchestrator
> drives the crew, and [`agent_crew/README.md`](agent_crew/README.md) for details.

---

## 📂 Layout
| Path | Purpose |
|------|---------|
| `agent.py` | Simple one-shot dispatch (deepseek-chat) |
| `worker.py` | Live tab console (deepseek-reasoner, streams thinking) |
| `dispatch.py` | Orchestrator → live worker |
| `start_team.py` | Opens the 3 agent tabs |
| `agents.py` | The 3 agent roles / system prompts |
| `env_context.py` | Builds the project snapshot (env-awareness) |
| `session.py` | Shared transcript (how agents see each other) |
| `agent_crew/` | Portable, drop-in copy of the whole crew |
| `minecraft_light/` | Demo game built by the crew |
| `runs/` | Session transcripts (gitignored) |

---

## 🔒 Security
This repo ships **no API keys**. Your key lives only in a local `.env`, which is
gitignored. Never commit `.env`. If a key is ever exposed, rotate it at
platform.deepseek.com.

## 📝 Requirements
- Python 3.10+
- A DeepSeek API key
- Windows for the live-tabs launcher (`start_team.py` uses Windows Terminal / cmd);
  the core scripts (`agent.py`) are cross-platform.

---

*Built with Claude Code as the orchestrator ("Claudey") and DeepSeek as the workers.*
