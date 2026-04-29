"""可视化 Agent。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

# 常见中文字体兼容配置：Windows 通常有 Microsoft YaHei / SimHei；macOS 通常有 Arial Unicode MS。
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

from src.agents.base import BaseAgent
from src.models import AgentResult
from src.utils.file_utils import ensure_dir


class VisualizationAgent(BaseAgent):
    name = "VisualizationAgent"

    def _save(self, path: Path, dpi: int) -> Path:
        plt.tight_layout()
        plt.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close()
        return path

    def run(self, context: dict[str, Any]) -> AgentResult:
        df: pd.DataFrame = context["df"].copy()
        target_col = context["target_col"]
        date_col = context.get("date_col")
        group_cols = context.get("group_cols", [])
        output_dir = Path(context["run_output_dir"])
        assets_dir = ensure_dir(output_dir / "assets")
        dpi = int(context.get("figure_dpi", 160))

        chart_paths: list[str] = []

        if date_col and date_col in df.columns:
            time_df = df.dropna(subset=[date_col]).copy()
            if not time_df.empty:
                time_df[date_col] = pd.to_datetime(time_df[date_col], errors="coerce")
                daily = time_df.groupby(time_df[date_col].dt.date)[target_col].sum().sort_index()
                if not daily.empty:
                    plt.figure(figsize=(10, 4.8))
                    plt.plot(daily.index.astype(str), daily.values, marker="o", linewidth=1.8)
                    plt.xticks(rotation=45, ha="right")
                    plt.title(f"{target_col} Time Trend")
                    plt.xlabel("Date")
                    plt.ylabel(target_col)
                    chart_paths.append(str(self._save(assets_dir / "trend.png", dpi)))

        for col in group_cols[:3]:
            if col in df.columns:
                grouped = df.groupby(col)[target_col].sum().sort_values(ascending=False).head(10)
                if not grouped.empty:
                    plt.figure(figsize=(9, 4.8))
                    plt.bar(grouped.index.astype(str), grouped.values)
                    plt.xticks(rotation=35, ha="right")
                    plt.title(f"Top {col} by {target_col}")
                    plt.xlabel(col)
                    plt.ylabel(target_col)
                    chart_paths.append(str(self._save(assets_dir / f"top_by_{col}.png", dpi)))

        numeric_df = df.select_dtypes(include="number")
        if len(numeric_df.columns) >= 2:
            corr = numeric_df.corr(numeric_only=True)
            plt.figure(figsize=(7, 5.8))
            plt.imshow(corr, aspect="auto")
            plt.colorbar(label="Correlation")
            plt.xticks(range(len(corr.columns)), corr.columns, rotation=45, ha="right")
            plt.yticks(range(len(corr.index)), corr.index)
            plt.title("Numeric Correlation Heatmap")
            chart_paths.append(str(self._save(assets_dir / "correlation_heatmap.png", dpi)))

        context["chart_paths"] = chart_paths
        return AgentResult(self.name, True, f"图表生成完成，共 {len(chart_paths)} 张", {"chart_paths": chart_paths})
