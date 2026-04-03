from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass, field

import yaml


@dataclass
class LLMConfig:
    base_url: str = "http://localhost:8000/v1"
    active_model: str = "30b"
    models: dict = field(default_factory=lambda: {
        "30b": "belltechsoft/Qwen3-Coder-30B-A3B-Instruct",
        "80b": "belltechsoft/Qwen3-Coder-Next",
    })
    max_tokens: int = 8192
    temperature: float = 0.3


@dataclass
class SafetyConfig:
    confirm_file_write: bool = True
    confirm_delete: bool = True
    command_timeout: int = 30
    blocked_commands: list = field(default_factory=lambda: [
        "rm -rf /", "mkfs", "dd if=", ":(){:|:&};:",
    ])


@dataclass
class AgentConfig:
    max_iterations: int = 15


@dataclass
class Config:
    llm: LLMConfig = field(default_factory=LLMConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    working_dir: Path = field(default_factory=Path.cwd)


def load_config(config_path: str | Path | None = None) -> Config:
    if config_path is None:
        for c in [Path.cwd() / "config.yaml", Path(__file__).parent.parent / "config.yaml"]:
            if c.exists():
                config_path = c
                break

    cfg = Config()
    if config_path and Path(config_path).exists():
        with open(config_path) as f:
            raw = yaml.safe_load(f) or {}

        for section_name in ("llm", "safety", "agent"):
            if section_name in raw and isinstance(raw[section_name], dict):
                section_obj = getattr(cfg, section_name)
                for k, v in raw[section_name].items():
                    if hasattr(section_obj, k):
                        setattr(section_obj, k, v)

    return cfg
