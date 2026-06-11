# 🐉 agent_crew — Claudey + 3 DeepSeek agents, drop-in anywhere

A portable multi-agent crew. **You** are the controller. **Claudey** (Claude
Code) is the orchestrator. Three **DeepSeek** workers do the work:

| Agent | Role |
|-------|------|
| Agent 1 | **Coder** |
| Agent 2 | **Designer** |
| Agent 3 | **UX** |

The agents are **env-aware** (they see the host project's files) and they
**see each other** (one shared transcript per session).

---

## 🚀 Unleash the beasts (in any project)

1. **Copy the whole `agent_crew` folder** into the project you want to work on.
   ```
   your_project/
     └── agent_crew/        <- drop it here
   ```
2. **One-time setup** (only the first time on a machine):
   ```powershell
   cd agent_crew
   pip install -r requirements.txt
   ```
   The `.env` already holds your DeepSeek key (or copy `.env.example` → `.env`
   and paste a key).
3. **Open Claude Code in `your_project`** and tell it:
   > Read `agent_crew/CLAUDEY.md` and be Claudey.
   Then type **`LIVE`** to convene the crew, and give your main task.

That's it. Claudey handles the splitting, dispatching, and assembling. You
review the result at the end.

---

## 🖥️ The two modes

**Live tabs (watch them think)** — each agent gets its own console streaming
its chain-of-thought:
```powershell
python start_team.py mysession     # opens 3 tabs (Coder / Designer / UX)
```
Claudey then dispatches with:
```powershell
python dispatch.py coder "your sub-task" --session mysession
```

**Simple (no tabs)** — quick one-shot, no streaming:
```powershell
python agent.py coder "your sub-task" --session mysession
```

Either way the full group conversation is saved to
`runs/<session>/transcript.md`.

---

## 📂 What's in here

| File | Purpose |
|------|---------|
| `config.py` | Portable paths (finds its own home + the host project) |
| `agents.py` | The 3 agent roles / system prompts |
| `env_context.py` | Builds the host-project snapshot (env-awareness) |
| `session.py` | Shared transcript (how agents see each other) |
| `agent.py` | Simple dispatch (deepseek-chat) |
| `worker.py` | Live tab console (deepseek-reasoner, streams thinking) |
| `dispatch.py` | Claudey → live worker |
| `start_team.py` | Opens the 3 tabs |
| `CLAUDEY.md` | Instructions a fresh Claude reads to become the orchestrator |
| `.env` | Your DeepSeek key (gitignored) |

---

## 🔒 Note
`.env` contains a real API key and is gitignored. If you share this folder,
delete `.env` first (keep `.env.example`) and rotate the key if it leaked.
