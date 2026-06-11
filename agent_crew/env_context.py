"""Builds a snapshot of the host project so the agents are "env aware".

Scans PROJECT_ROOT (the project the crew was dropped into) and returns the
OS, the directory, the file tree, and the contents of small text files.
"""

import os
import platform

import config

IGNORE_DIRS = {
    ".git", "__pycache__", "runs", "node_modules", ".venv", "venv",
    "dist", "build", ".next", ".idea", ".vscode", "target",
}
IGNORE_FILES = {".env"}
MAX_FILE_BYTES = 8_000
MAX_CONTENT_FILES = 40  # cap so a big host project can't blow up the prompt
TEXT_EXTS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".md", ".txt",
    ".html", ".css", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".sh",
    ".go", ".rs", ".java", ".rb", ".php", ".c", ".cpp", ".h",
}


def _tree(root: str) -> list[str]:
    lines: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in IGNORE_DIRS)
        rel = os.path.relpath(dirpath, root)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        indent = "  " * depth
        if rel != ".":
            lines.append(f"{indent}{os.path.basename(dirpath)}/")
        for fn in sorted(filenames):
            if fn in IGNORE_FILES:
                continue
            full = os.path.join(dirpath, fn)
            try:
                size = os.path.getsize(full)
            except OSError:
                size = 0
            lines.append(f"{indent}  {fn} ({size} B)")
    return lines


def _file_contents(root: str) -> list[str]:
    chunks: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in IGNORE_DIRS)
        for fn in sorted(filenames):
            if len(chunks) >= MAX_CONTENT_FILES:
                return chunks
            if fn in IGNORE_FILES:
                continue
            ext = os.path.splitext(fn)[1].lower()
            if ext not in TEXT_EXTS:
                continue
            full = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(full) > MAX_FILE_BYTES:
                    continue
                with open(full, "r", encoding="utf-8") as f:
                    body = f.read()
            except (OSError, UnicodeDecodeError):
                continue
            rel = os.path.relpath(full, root)
            chunks.append(f"--- {rel} ---\n{body}")
    return chunks


def build_env_context(root: str | None = None, include_contents: bool = True) -> str:
    root = root or config.PROJECT_ROOT
    parts = [
        "## ENVIRONMENT SNAPSHOT (host project)",
        f"OS: {platform.system()} {platform.release()}",
        f"Project root: {root}",
        "",
        "### File tree",
        "\n".join(_tree(root)) or "(empty)",
    ]
    if include_contents:
        contents = _file_contents(root)
        if contents:
            parts += [
                "",
                f"### File contents (up to {MAX_CONTENT_FILES} small text files)",
                "\n\n".join(contents),
            ]
    return "\n".join(parts)


if __name__ == "__main__":
    print(build_env_context())
