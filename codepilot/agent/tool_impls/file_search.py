from __future__ import annotations

import glob
import subprocess


def search_files(pattern: str, path: str = ".", search_type: str = "content", include: str | None = None) -> str:
    if search_type == "glob":
        return _glob_search(pattern, path)
    else:
        return _grep_search(pattern, path, include)


def _glob_search(pattern: str, path: str) -> str:
    import os
    full_pattern = os.path.join(path, "**", pattern)
    matches = sorted(glob.glob(full_pattern, recursive=True))

    if not matches:
        return f"'{pattern}' 패턴에 일치하는 파일이 없습니다."

    result = matches[:50]
    output = "\n".join(result)
    if len(matches) > 50:
        output += f"\n\n... 외 {len(matches) - 50}개 파일"
    return output


def _grep_search(pattern: str, path: str, include: str | None) -> str:
    cmd = ["grep", "-rn", "--color=never"]
    if include:
        cmd.extend(["--include", include])
    cmd.extend([pattern, path])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        output = result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "[오류] 검색 시간 초과 (15초)"
    except FileNotFoundError:
        return "[오류] grep 명령을 찾을 수 없습니다."

    if not output:
        return f"'{pattern}'에 일치하는 내용이 없습니다."

    lines = output.split("\n")
    if len(lines) > 50:
        return "\n".join(lines[:50]) + f"\n\n... 외 {len(lines) - 50}건"
    return output
