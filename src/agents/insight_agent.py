"""洞察挖掘 Agent。"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.agents.base import BaseAgent
from src.models import AgentResult


class InsightAgent(BaseAgent):
    name = "InsightAgent"

    def run(self, context: dict[str, Any]) -> AgentResult:
        df: pd.DataFrame = context["df"].copy()
        target_col = context["target_col"]
        date_col = context.get("date_col")
        group_cols = context.get("group_cols", [])
        anomaly_z_score = context.get("anomaly_z_score", 2.5)

        insights: list[str] = []
        tables: dict[str, Any] = {}

        target = pd.to_numeric(df[target_col], errors="coerce")
        total = target.sum(skipna=True)
        mean = target.mean(skipna=True)
        median = target.median(skipna=True)
        insights.append(f"核心指标 {target_col} 总量为 {total:,.2f}，均值为 {mean:,.2f}，中位数为 {median:,.2f}。")

        if date_col:
            time_df = df.dropna(subset=[date_col]).copy()
            if not time_df.empty:
                time_df[date_col] = pd.to_datetime(time_df[date_col], errors="coerce")
                daily = time_df.groupby(time_df[date_col].dt.date)[target_col].sum().sort_index()
                tables["daily_series"] = daily.reset_index().rename(columns={date_col: "date", target_col: "value"}).to_dict(orient="records")

                if len(daily) >= 2:
                    first_value = daily.iloc[0]
                    last_value = daily.iloc[-1]
                    change = last_value - first_value
                    change_rate = change / first_value if first_value else np.nan
                    if pd.notna(change_rate):
                        direction = "上升" if change >= 0 else "下降"
                        insights.append(
                            f"从 {daily.index[0]} 到 {daily.index[-1]}，{target_col} 由 {first_value:,.2f} {direction}至 {last_value:,.2f}，变化率为 {change_rate:.2%}。"
                        )

                if len(daily) >= 7:
                    rolling = daily.rolling(7).mean()
                    latest_roll = rolling.dropna().iloc[-1]
                    insights.append(f"最近 7 天移动平均值为 {latest_roll:,.2f}，可用于观察短期趋势。")

                std = daily.std()
                if std and not np.isnan(std):
                    z = (daily - daily.mean()) / std
                    anomalies = daily[z.abs() >= anomaly_z_score]
                    if not anomalies.empty:
                        tables["anomalies"] = [
                            {"date": str(idx), "value": float(val), "z_score": float(z.loc[idx])}
                            for idx, val in anomalies.items()
                        ]
                        top_anomaly = anomalies.sort_values(ascending=False).head(1)
                        insights.append(
                            f"检测到 {len(anomalies)} 个异常日期，其中最高异常值出现在 {top_anomaly.index[0]}，数值为 {top_anomaly.iloc[0]:,.2f}。"
                        )
                    else:
                        insights.append("未发现明显超过阈值的时间序列异常点。")

        for col in group_cols:
            if col in df.columns:
                grouped = df.groupby(col)[target_col].sum().sort_values(ascending=False)
                top = grouped.head(10)
                tables[f"top_by_{col}"] = top.reset_index().to_dict(orient="records")
                if not top.empty:
                    top_name = top.index[0]
                    top_val = top.iloc[0]
                    share = top_val / total if total else np.nan
                    if pd.notna(share):
                        insights.append(f"按 {col} 分组时，贡献最高的是 {top_name}，贡献 {target_col} 为 {top_val:,.2f}，占比 {share:.2%}。")

        numeric_df = df.select_dtypes(include="number")
        if len(numeric_df.columns) >= 2 and target_col in numeric_df.columns:
            corr = numeric_df.corr(numeric_only=True)[target_col].drop(labels=[target_col], errors="ignore").dropna()
            if not corr.empty:
                strongest = corr.abs().sort_values(ascending=False).head(3)
                corr_items = []
                for col in strongest.index:
                    corr_items.append({"column": col, "corr": float(corr.loc[col])})
                tables["target_correlations"] = corr_items
                strongest_col = strongest.index[0]
                insights.append(f"与 {target_col} 相关性最强的数值字段是 {strongest_col}，相关系数为 {corr.loc[strongest_col]:.3f}。")

        context["insights"] = insights
        context["insight_tables"] = tables
        return AgentResult(self.name, True, "数据洞察挖掘完成", {"insights": insights, "tables": tables})
