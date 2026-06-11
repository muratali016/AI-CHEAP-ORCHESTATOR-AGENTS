"""Open one live console per agent, each watching for tasks from Claudey.

    python start_team.py <session>

Uses Windows Terminal (wt) tabs if available; otherwise falls back to
separate cmd windows. Leave them open while you work -- each tab streams
that agent's thinking as Claudey hands it sub-tasks.
"""

import os
import sys
import shutil
import subprocess

AGENTS = [("coder", "Coder"), ("designer", "Designer"), ("ux", "UX")]


def main():
    session = sys.argv[1] if len(sys.argv) > 1 else "live"
    proj = os.path.dirname(os.path.abspath(__file__))

    if shutil.which("wt"):
        segments = []
        for i, (aid, title) in enumerate(AGENTS):
            seg = (f'new-tab --title {title} -d "{proj}" '
                   f'cmd /k python worker.py {aid} --session {session}')
            segments.append(seg)
        cmd = "wt " + " ; ".join(segments)
        subprocess.Popen(cmd, shell=True)
        print(f"Opened Windows Terminal with 3 tabs (session: {session}).")
    else:
        for aid, title in AGENTS:
            subprocess.Popen(
                f'start "{title}" cmd /k python worker.py {aid} --session {session}',
                cwd=proj, shell=True,
            )
        print(f"Opened 3 cmd windows (session: {session}).")

    print("Leave them open. Claudey will dispatch tasks to them.")


if __name__ == "__main__":
    main()
