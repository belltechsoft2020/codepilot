from __future__ import annotations

import os
from codepilot.config import SafetyConfig


def should_confirm(tool_name: str, args: dict, safety: SafetyConfig) -> bool:
    if tool_name == "write_file":
        if safety.confirm_file_write:
            path = os.path.expanduser(args.get("file_path", ""))
            return os.path.exists(path)
        return False

    if tool_name == "edit_file":
        return True

    if tool_name == "run_command":
        cmd = args.get("command", "")
        # 차단 목록 확인
        for blocked in safety.blocked_commands:
            if blocked in cmd:
                return True
        # 위험 키워드 확인
        danger_keywords = ["rm ", "sudo ", "mv ", "chmod ", "chown ", " > ", ">>", "kill "]
        return any(kw in cmd for kw in danger_keywords)

    return False


def is_blocked(tool_name: str, args: dict, safety: SafetyConfig) -> str | None:
    if tool_name == "run_command":
        cmd = args.get("command", "")
        for blocked in safety.blocked_commands:
            if blocked in cmd:
                return f"차단된 명령입니다: {blocked}"
    return None
