from __future__ import annotations

import json
from dataclasses import dataclass

import httpx


@dataclass
class LLMResponse:
    content: str | None = None
    tool_calls: list[dict] | None = None
    usage: dict | None = None


class LLMClient:
    def __init__(self, base_url: str, model: str, max_tokens: int = 8192, temperature: float = 0.3):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.client = httpx.Client(timeout=300.0)

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float | None = None,
    ) -> LLMResponse:
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": temperature if temperature is not None else self.temperature,
        }
        if tools:
            payload["tools"] = tools

        resp = self.client.post(f"{self.base_url}/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()

        choice = data["choices"][0]
        msg = choice["message"]

        tool_calls = None
        if msg.get("tool_calls"):
            tool_calls = []
            for tc in msg["tool_calls"]:
                args = tc["function"]["arguments"]
                if isinstance(args, str):
                    args = json.loads(args)
                tool_calls.append({
                    "id": tc["id"],
                    "name": tc["function"]["name"],
                    "arguments": args,
                })

        return LLMResponse(
            content=msg.get("content"),
            tool_calls=tool_calls,
            usage=data.get("usage"),
        )

    def switch_model(self, model_id: str):
        self.model = model_id

    def close(self):
        self.client.close()
