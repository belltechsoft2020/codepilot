from __future__ import annotations

import json
import time
from typing import Callable

from codepilot.llm.client import LLMClient
from codepilot.llm.prompts import SYSTEM_PROMPT, TOOL_DEFINITIONS
from codepilot.agent.tools import ToolRegistry
from codepilot.safety import should_confirm, is_blocked
from codepilot.config import SafetyConfig


class Agent:
    def __init__(
        self,
        llm: LLMClient,
        tools: ToolRegistry,
        safety: SafetyConfig,
        max_iterations: int = 15,
        on_tool_call: Callable[[str, dict], bool] | None = None,
        on_tool_result: Callable[[str, str, float], None] | None = None,
    ):
        self.llm = llm
        self.tools = tools
        self.safety = safety
        self.max_iterations = max_iterations
        self.on_tool_call = on_tool_call
        self.on_tool_result = on_tool_result

    def run(self, user_message: str, history: list[dict] | None = None) -> str:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        for iteration in range(self.max_iterations):
            response = self.llm.chat(messages, tools=TOOL_DEFINITIONS)

            if response.tool_calls:
                assistant_msg = {"role": "assistant", "content": response.content or ""}
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["arguments"], ensure_ascii=False),
                        },
                    }
                    for tc in response.tool_calls
                ]
                messages.append(assistant_msg)

                for tc in response.tool_calls:
                    name = tc["name"]
                    args = tc["arguments"]

                    # 차단 확인
                    blocked = is_blocked(name, args, self.safety)
                    if blocked:
                        result = f"[차단] {blocked}"
                    elif should_confirm(name, args, self.safety) and self.on_tool_call:
                        approved = self.on_tool_call(name, args)
                        if not approved:
                            result = "[사용자가 실행을 거부했습니다]"
                        else:
                            start = time.time()
                            result = self.tools.execute(name, args)
                            elapsed = time.time() - start
                            if self.on_tool_result:
                                self.on_tool_result(name, result, elapsed)
                    else:
                        start = time.time()
                        result = self.tools.execute(name, args)
                        elapsed = time.time() - start
                        if self.on_tool_result:
                            self.on_tool_result(name, result, elapsed)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": result,
                    })
            else:
                return response.content or ""

        return "최대 반복 횟수에 도달했습니다. 질문을 더 구체적으로 해주세요."
