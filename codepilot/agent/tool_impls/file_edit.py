from __future__ import annotations

import os
import difflib


_undo_stack: list[dict] = []


def edit_file(file_path: str, old_text: str, new_text: str) -> str:
    path = os.path.expanduser(file_path)
    if not os.path.exists(path):
        return f"[오류] 파일이 존재하지 않습니다: {file_path}"

    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return f"[오류] 파일 읽기 실패: {e}"

    if old_text not in content:
        return f"[오류] old_text를 찾을 수 없습니다. 정확한 텍스트를 사용하세요."

    count = content.count(old_text)
    if count > 1:
        return f"[오류] old_text가 {count}번 발견됩니다. 더 구체적인 텍스트를 사용하세요."

    # undo용 백업
    _undo_stack.append({"path": path, "backup": content})

    new_content = content.replace(old_text, new_text, 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    # diff 생성
    old_lines = content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    diff = difflib.unified_diff(old_lines, new_lines, fromfile=file_path, tofile=file_path, lineterm="")
    diff_text = "\n".join(list(diff)[:30])

    return f"편집 완료: {file_path}\n\n{diff_text}"


def undo_last_edit() -> str:
    if not _undo_stack:
        return "되돌릴 편집이 없습니다."

    entry = _undo_stack.pop()
    with open(entry["path"], "w", encoding="utf-8") as f:
        f.write(entry["backup"])
    return f"편집 복원됨: {entry['path']}"
