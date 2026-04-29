"""项目配置。"""

from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass


@dataclass
class AppConfig:
    output_dir: Path = Path("reports")
    max_top_items: int = 10
    anomaly_z_score: float = 2.5
    figure_dpi: int = 160
