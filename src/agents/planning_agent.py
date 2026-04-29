"""规划 Agent：根据输入参数制定分析计划。"""

from __future__ import annotations

from typing import Any

from src.agents.base import BaseAgent
from src.models import AgentResult


class PlanningAgent(BaseAgent):
    name = "PlanningAgent"

    def run(self, context: dict[str, Any]) -> AgentResult:
        target_col = context.get("target_col")
        date_col = context.get("date_col")
        group_cols = context.get("group_cols", [])

        plan = [
            "读取数据文件并完成字段校验",
            "分析数据规模、字段类型、缺失值和基础统计指标",
            f"围绕核心指标 {target_col} 进行趋势、异常和贡献度分析",
            "自动生成趋势图、分组对比图和相关性图表",
            "汇总结果并生成 Markdown / HTML 日报",
        ]
        if date_col:
            plan.append(f"使用 {date_col} 作为时间序列分析字段")
        if group_cols:
            plan.append(f"使用 {', '.join(group_cols)} 作为分组维度")

        context["analysis_plan"] = plan
        return AgentResult(self.name, True, "分析计划生成完成", {"plan": plan})
