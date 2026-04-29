"""Pipeline Supervisor：统一调度多个 Agent。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.agents.planning_agent import PlanningAgent
from src.agents.data_loader_agent import DataLoaderAgent
from src.agents.data_profiler_agent import DataProfilerAgent
from src.agents.insight_agent import InsightAgent
from src.agents.visualization_agent import VisualizationAgent
from src.agents.report_agent import ReportAgent
from src.config import AppConfig
from src.models import PipelineResult
from src.utils.file_utils import ensure_dir
from src.utils.time_utils import today_str


class DailyReportPipeline:
    """多 Agent 日报流水线。"""

    def __init__(
        self,
        data_path: Path,
        output_dir: Path = Path("reports"),
        date_col: str | None = None,
        target_col: str = "sales",
        group_cols: list[str] | None = None,
        report_title: str = "自动化数据洞察日报",
        config: AppConfig | None = None,
    ) -> None:
        self.config = config or AppConfig(output_dir=output_dir)
        self.context: dict[str, Any] = {
            "data_path": str(data_path),
            "output_dir": str(output_dir),
            "date_col": date_col,
            "target_col": target_col,
            "group_cols": group_cols or [],
            "report_title": report_title,
            "max_top_items": self.config.max_top_items,
            "anomaly_z_score": self.config.anomaly_z_score,
            "figure_dpi": self.config.figure_dpi,
        }
        self.agents = [
            PlanningAgent(),
            DataLoaderAgent(),
            DataProfilerAgent(),
            InsightAgent(),
            VisualizationAgent(),
            ReportAgent(),
        ]

    def run(self) -> PipelineResult:
        run_output_dir = ensure_dir(Path(self.context["output_dir"]) / today_str())
        self.context["run_output_dir"] = str(run_output_dir)
        self.context["agent_logs"] = []

        for agent in self.agents:
            result = agent.run(self.context)
            self.context["agent_logs"].append(result)
            print(f"[{result.name}] {result.message}")
            if not result.success:
                raise RuntimeError(result.message)

        return PipelineResult(
            markdown_path=Path(self.context["markdown_path"]),
            html_path=Path(self.context["html_path"]),
            context=self.context,
        )
