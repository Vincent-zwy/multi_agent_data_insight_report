"""数据读取 Agent。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.agents.base import BaseAgent
from src.models import AgentResult


class DataLoaderAgent(BaseAgent):
    name = "DataLoaderAgent"

    def run(self, context: dict[str, Any]) -> AgentResult:
        data_path = Path(context["data_path"])
        target_col = context["target_col"]
        date_col = context.get("date_col")
        group_cols = context.get("group_cols", [])

        if not data_path.exists():
            raise FileNotFoundError(f"数据文件不存在：{data_path}")

        suffix = data_path.suffix.lower()
        if suffix == ".csv":
            df = pd.read_csv(data_path)
        elif suffix in {".xlsx", ".xls"}:
            df = pd.read_excel(data_path)
        else:
            raise ValueError("仅支持 CSV / Excel 文件")

        if target_col not in df.columns:
            raise ValueError(f"目标指标列不存在：{target_col}")

        if date_col:
            if date_col not in df.columns:
                raise ValueError(f"日期列不存在：{date_col}")
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

        for col in group_cols:
            if col not in df.columns:
                raise ValueError(f"分组字段不存在：{col}")

        df[target_col] = pd.to_numeric(df[target_col], errors="coerce")
        context["df"] = df
        context["columns"] = list(df.columns)

        return AgentResult(
            self.name,
            True,
            f"数据读取完成，共 {len(df)} 行，{len(df.columns)} 列",
            {"shape": df.shape, "columns": list(df.columns)},
        )
