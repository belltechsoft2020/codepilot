from __future__ import annotations

import os


def read_file(file_path: str, offset: int = 0, limit: int = 2000) -> str:
    path = os.path.expanduser(file_path)
    if not os.path.exists(path):
        return f"[오류] 파일이 존재하지 않습니다: {file_path}"
    if not os.path.isfile(path):
        return f"[오류] 파일이 아닙니다: {file_path}"

    try:
        with open(path, "rb") as f:
            chunk = f.read(8192)
            if b"\x00" in chunk:
                return f"[바이너리 파일] {file_path} ({os.path.getsize(path):,} bytes)"
    except Exception as e:
        return f"[오류] 파일 읽기 실패: {e}"

    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    total = len(lines)
    selected = lines[offset:offset + limit]

    parts = []
    for i, line in enumerate(selected, start=offset + 1):
        parts.append(f"{i:4d}\t{line.rstrip()}")

    result = "\n".join(parts)
    if offset + limit < total:
        result += f"\n\n... ({total - offset - limit}줄 더 있음, 총 {total}줄)"

    return result
