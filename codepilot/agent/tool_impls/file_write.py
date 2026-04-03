from __future__ import annotations

import os


_undo_stack: list[dict] = []


def write_file(file_path: str, content: str) -> str:
    path = os.path.expanduser(file_path)

    # undo용 백업
    backup = None
    if os.path.exists(path):
        with open(path, encoding="utf-8", errors="replace") as f:
            backup = f.read()

    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        return f"[오류] 파일 쓰기 실패: {e}"

    _undo_stack.append({"path": path, "backup": backup})

    line_count = content.count("\n") + (1 if content and not content.endswith("\n") else 0)
    action = "덮어쓰기" if backup is not None else "생성"
    return f"파일 {action} 완료: {file_path} ({line_count}줄)"


def undo_last_write() -> str:
    if not _undo_stack:
        return "되돌릴 변경 사항이 없습니다."

    entry = _undo_stack.pop()
    path = entry["path"]
    backup = entry["backup"]

    if backup is None:
        os.remove(path)
        return f"파일 삭제됨 (생성 취소): {path}"
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(backup)
        return f"파일 복원됨: {path}"
