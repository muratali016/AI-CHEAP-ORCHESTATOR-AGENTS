"""Central config + portable paths for the agent crew.

Everything is anchored to THIS folder (agent_crew), so the crew works no
matter what project you drop it into and no matter where you run it from.

- CREW_DIR     : the agent_crew folder itself.
- PROJECT_ROOT : the host project the crew is dropped into (the parent of
                 agent_crew), or override with env var AGENT_CREW_PROJECT_ROOT.
                 This is what the agents become "env aware" of.
- RUNS_DIR     : transcripts + inbox/outbox, kept inside the crew so the whole
                 history travels with the folder.
"""

import os

CREW_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.environ.get("AGENT_CREW_PROJECT_ROOT") or os.path.dirname(CREW_DIR)
RUNS_DIR = os.path.join(CREW_DIR, "runs")
ENV_PATH = os.path.join(CREW_DIR, ".env")

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
CHAT_MODEL = "deepseek-chat"        # used by agent.py (no live tabs)
REASONER_MODEL = "deepseek-reasoner"  # used by worker.py (streams thinking)
