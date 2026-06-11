"""Open one live console per agent, each watching for tasks from Claudey.

    python start_team.py <session>

Windows Terminal (wt) tabs if available, else separate cmd windows.
Works from anywhere -- paths are anchored to this folder.
"""

import os
import sys
import shutil
import subprocess

import config

AGENTS = [("coder", "Coder"), ("designer", "Designer"), ("ux", "UX")]


def main():
    session = sys.argv[1] if len(sys.argv) > 1 else "live"
    crew = config.CREW_DIR
    worker = os.path.join(crew, "worker.py")
    py = sys.executable or "python"

    if shutil.which("wt"):
        segments = [
            f'new-tab --title {title} -d "{crew}" '
            f'"{py}" "{worker}" {aid} --session {session}'
            for aid, title in AGENTS
        ]
        subprocess.Popen("wt " + " ; ".join(segments), shell=True)
        print(f"Opened Windows Terminal with 3 tabs (session: {session}).")
    else:
        for aid, title in AGENTS:
            subprocess.Popen(
                f'start "{title}" "{py}" "{worker}" {aid} --session {session}',
                cwd=crew, shell=True,
            )
        print(f"Opened 3 cmd windows (session: {session}).")

    print(f"Project the crew is working on: {config.PROJECT_ROOT}")
    print("Leave the tabs open. Claudey will dispatch tasks to them.")


if __name__ == "__main__":
    main()
