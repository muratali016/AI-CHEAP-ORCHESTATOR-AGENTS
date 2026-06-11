"""Shared conversation transcript for a multi-agent session.

All agents in a session read the same transcript before they answer and
append their turn afterwards -- that is how they "talk to each other".
Stored under <crew>/runs/<session>/ as transcript.json + transcript.md.
"""

import json
import os
import time
from datetime import datetime

import config


def _session_dir(session: str) -> str:
    return os.path.join(config.RUNS_DIR, session)


def _json_path(session: str) -> str:
    return os.path.join(_session_dir(session), "transcript.json")


def _md_path(session: str) -> str:
    return os.path.join(_session_dir(session), "transcript.md")


def _acquire_lock(lock_path: str, timeout: float = 10.0) -> None:
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


def load(session: str) -> list[dict]:
    path = _json_path(session)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def append(session: str, speaker: str, role: str, content: str) -> None:
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
    if not turns:
        return "(no prior conversation yet)"
    return "\n\n".join(f"[{t['speaker']}]:\n{t['content']}" for t in turns)
