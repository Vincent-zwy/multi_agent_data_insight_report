"""通用数据模型。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AgentResult:
    name: str
    success: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineResult:
    markdown_path: Path
    html_path: Path
    context: dict[str, Any]
