"""报告生成 Agent。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.agents.base import BaseAgent
from src.models import AgentResult
from src.utils.file_utils import write_json
from src.utils.time_utils import now_str


class ReportAgent(BaseAgent):
    name = "ReportAgent"

    def _build_markdown(self, context: dict[str, Any]) -> str:
        title = context.get("report_title", "自动化数据洞察日报")
        profile = context["profile"]
        insights = context.get("insights", [])
        plan = context.get("analysis_plan", [])
        chart_paths = context.get("chart_paths", [])
        tables = context.get("insight_tables", {})

        lines: list[str] = []
        lines.append(f"# {title}")
        lines.append("")
        lines.append(f"生成时间：{now_str()}")
        lines.append("")
        lines.append("## 一、分析任务计划")
        for item in plan:
            lines.append(f"- {item}")

        lines.append("")
        lines.append("## 二、数据概览")
        lines.append(f"- 数据行数：{profile['row_count']}")
        lines.append(f"- 数据列数：{profile['column_count']}")
        target = profile.get("target_summary", {})
        if target:
            lines.append(f"- 核心指标总量：{target.get('sum', 0):,.2f}")
            lines.append(f"- 核心指标均值：{target.get('mean', 0):,.2f}")
            lines.append(f"- 核心指标最大值：{target.get('max', 0):,.2f}")
            lines.append(f"- 核心指标最小值：{target.get('min', 0):,.2f}")

        lines.append("")
        lines.append("## 三、核心洞察")
        if insights:
            for idx, item in enumerate(insights, start=1):
                lines.append(f"{idx}. {item}")
        else:
            lines.append("暂无可输出洞察。")

        lines.append("")
        lines.append("## 四、关键图表")
        if chart_paths:
            for path in chart_paths:
                rel = Path(path).name
                lines.append(f"![{rel}](assets/{rel})")
                lines.append("")
        else:
            lines.append("未生成图表。")

        lines.append("")
        lines.append("## 五、明细表")
        for name, rows in tables.items():
            lines.append(f"### {name}")
            if isinstance(rows, list) and rows:
                headers = list(rows[0].keys())
                lines.append("| " + " | ".join(headers) + " |")
                lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                for row in rows[:10]:
                    lines.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")
            else:
                lines.append("无数据。")
            lines.append("")

        lines.append("## 六、结论与建议")
        lines.append("- 建议重点关注贡献度最高的分组维度，结合业务目标进行资源倾斜。")
        lines.append("- 对异常日期或异常指标进行复盘，判断是业务机会、数据质量问题还是突发风险。")
        lines.append("- 可将本系统接入数据库、邮件或企业微信，实现自动化日报推送。")
        lines.append("")
        return "\n".join(lines)

    def _build_html(self, context: dict[str, Any], markdown_text: str) -> str:
        env = Environment(
            loader=FileSystemLoader("templates"),
            autoescape=select_autoescape(["html", "xml"]),
        )
        template = env.get_template("daily_report.html.j2")
        return template.render(
            title=context.get("report_title", "自动化数据洞察日报"),
            generated_at=now_str(),
            plan=context.get("analysis_plan", []),
            profile=context.get("profile", {}),
            insights=context.get("insights", []),
            chart_paths=["assets/" + Path(p).name for p in context.get("chart_paths", [])],
            tables=context.get("insight_tables", {}),
            markdown_text=markdown_text,
        )

    def run(self, context: dict[str, Any]) -> AgentResult:
        output_dir = Path(context["run_output_dir"])
        markdown_text = self._build_markdown(context)
        html_text = self._build_html(context, markdown_text)

        markdown_path = output_dir / "daily_report.md"
        html_path = output_dir / "daily_report.html"
        profile_path = output_dir / "profile.json"
        insights_path = output_dir / "insights.json"

        markdown_path.write_text(markdown_text, encoding="utf-8")
        html_path.write_text(html_text, encoding="utf-8")
        write_json(profile_path, context.get("profile", {}))
        write_json(insights_path, {"insights": context.get("insights", []), "tables": context.get("insight_tables", {})})

        context["markdown_path"] = markdown_path
        context["html_path"] = html_path

        return AgentResult(
            self.name,
            True,
            "日报生成完成",
            {"markdown_path": str(markdown_path), "html_path": str(html_path)},
        )
