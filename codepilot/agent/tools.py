from __future__ import annotations

from typing import Callable


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable] = {}

    def register(self, name: str, func: Callable):
        self._tools[name] = func

    def execute(self, name: str, arguments: dict) -> str:
        if name not in self._tools:
            return f"[오류] 알 수 없는 도구: {name}"
        try:
            return self._tools[name](**arguments)
        except Exception as e:
            return f"[오류] {name} 실행 실패: {e}"

    def has(self, name: str) -> bool:
        return name in self._tools

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())
