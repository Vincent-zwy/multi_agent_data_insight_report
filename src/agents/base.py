"""Agent 基类。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.models import AgentResult


class BaseAgent(ABC):
    name = "BaseAgent"

    def log(self, message: str) -> None:
        print(f"[{self.name}] {message}")

    @abstractmethod
    def run(self, context: dict[str, Any]) -> AgentResult:
        raise NotImplementedError
