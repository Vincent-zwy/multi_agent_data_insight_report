"""数据画像 Agent。"""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.agents.base import BaseAgent
from src.models import AgentResult


class DataProfilerAgent(BaseAgent):
    name = "DataProfilerAgent"

    def run(self, context: dict[str, Any]) -> AgentResult:
        df: pd.DataFrame = context["df"]
        target_col = context["target_col"]

        missing = df.isna().sum().sort_values(ascending=False)
        missing_rate = (missing / max(len(df), 1)).round(4)
        dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}

        numeric_df = df.select_dtypes(include="number")
        numeric_summary = numeric_df.describe().T.round(4).to_dict(orient="index") if not numeric_df.empty else {}

        profile = {
            "row_count": int(len(df)),
            "column_count": int(len(df.columns)),
            "dtypes": dtypes,
            "missing_count": missing.astype(int).to_dict(),
            "missing_rate": missing_rate.to_dict(),
            "numeric_summary": numeric_summary,
        }

        target_series = pd.to_numeric(df[target_col], errors="coerce")
        profile["target_summary"] = {
            "sum": float(target_series.sum(skipna=True)),
            "mean": float(target_series.mean(skipna=True)),
            "median": float(target_series.median(skipna=True)),
            "min": float(target_series.min(skipna=True)),
            "max": float(target_series.max(skipna=True)),
            "missing": int(target_series.isna().sum()),
        }

        context["profile"] = profile
        return AgentResult(self.name, True, "数据画像分析完成", {"profile": profile})
