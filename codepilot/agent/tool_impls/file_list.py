from __future__ import annotations

import os


def list_files(path: str = ".", recursive: bool = False) -> str:
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        return f"[오류] 경로가 존재하지 않습니다: {path}"
    if not os.path.isdir(path):
        return f"[오류] 디렉토리가 아닙니다: {path}"

    if recursive:
        return _list_recursive(path, max_depth=3)
    else:
        return _list_flat(path)


def _list_flat(path: str) -> str:
    entries = []
    for entry in sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name)):
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            entries.append(f"  {entry.name}/")
        else:
            size = _format_size(entry.stat().st_size)
            entries.append(f"  {entry.name}  ({size})")

    if not entries:
        return f"{path}: (비어 있음)"
    return f"{path}:\n" + "\n".join(entries)


def _list_recursive(path: str, max_depth: int, current_depth: int = 0, prefix: str = "") -> str:
    if current_depth > max_depth:
        return ""

    lines = []
    try:
        entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name))
    except PermissionError:
        return f"{prefix}[접근 거부]"

    for entry in entries:
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            lines.append(f"{prefix}{entry.name}/")
            sub = _list_recursive(entry.path, max_depth, current_depth + 1, prefix + "  ")
            if sub:
                lines.append(sub)
        else:
            size = _format_size(entry.stat().st_size)
            lines.append(f"{prefix}{entry.name}  ({size})")

    return "\n".join(lines)


def _format_size(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.0f}{unit}" if unit == "B" else f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"
