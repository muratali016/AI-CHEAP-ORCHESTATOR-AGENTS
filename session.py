"""Shared conversation transcript for a multi-agent session.

All agents in a session read the same transcript before they answer and
append their turn to it afterwards. That is what lets them "talk to each
other" -- each agent sees what the orchestrator and the other agents said.

Stored under runs/<session>/ as both transcript.json (machine) and
transcript.md (human-readable, for you to review).
"""

import json
import os
import time
from datetime import datetime

RUNS_DIR = "runs"


def _acquire_lock(lock_path: str, timeout: float = 10.0) -> None:
    """Crude cross-process lock so parallel workers don't corrupt the transcript."""
    start = time.time()
    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return
        except FileExistsError:
            if time.time() - start > timeout:
                try:
                    os.remove(lock_path)  # assume stale
                except OSError:
                    pass
                start = time.time()
            time.sleep(0.05)


def _release_lock(lock_path: str) -> None:
    try:
        os.remove(lock_path)
    except OSError:
        pass


def _session_dir(session: str) -> str:
    return os.path.join(RUNS_DIR, session)


def _json_path(session: str) -> str:
    return os.path.join(_session_dir(session), "transcript.json")


def _md_path(session: str) -> str:
    return os.path.join(_session_dir(session), "transcript.md")


def load(session: str) -> list[dict]:
    path = _json_path(session)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def append(session: str, speaker: str, role: str, content: str) -> None:
    """Add one turn. speaker is a label like 'Orchestrator' or 'Agent 1 - Coder'.
    role is 'orchestrator' or the agent id."""
    os.makedirs(_session_dir(session), exist_ok=True)
    lock_path = os.path.join(_session_dir(session), ".transcript.lock")
    _acquire_lock(lock_path)
    try:
        turns = load(session)
        turns.append(
            {
                "n": len(turns) + 1,
                "speaker": speaker,
                "role": role,
                "content": content,
                "ts": datetime.now().isoformat(timespec="seconds"),
            }
        )
        with open(_json_path(session), "w", encoding="utf-8") as f:
            json.dump(turns, f, ensure_ascii=False, indent=2)
        _write_md(session, turns)
    finally:
        _release_lock(lock_path)


def _write_md(session: str, turns: list[dict]) -> None:
    lines = [f"# Session: {session}", ""]
    for t in turns:
        lines.append(f"### [{t['n']}] {t['speaker']}  _( {t['ts']} )_")
        lines.append("")
        lines.append(t["content"])
        lines.append("")
        lines.append("---")
        lines.append("")
    with open(_md_path(session), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def as_dialogue(turns: list[dict]) -> str:
    """Render the transcript as a readable dialogue block for prompting."""
    if not turns:
        return "(no prior conversation yet)"
    blocks = []
    for t in turns:
        blocks.append(f"[{t['speaker']}]:\n{t['content']}")
    return "\n\n".join(blocks)
