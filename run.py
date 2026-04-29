"""命令行入口：生成一次数据洞察日报。"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.pipeline import DailyReportPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="多 Agent 协作的自动化数据洞察与日报系统")
    parser.add_argument("--data", required=True, help="CSV 或 Excel 数据文件路径")
    parser.add_argument("--date-col", default=None, help="日期列名，例如 date")
    parser.add_argument("--target", required=True, help="需要重点分析的数值指标列，例如 sales")
    parser.add_argument("--group-cols", nargs="*", default=[], help="分组字段，例如 region product channel")
    parser.add_argument("--output", default="reports", help="日报输出目录，默认 reports")
    parser.add_argument("--report-title", default="自动化数据洞察日报", help="日报标题")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pipeline = DailyReportPipeline(
        data_path=Path(args.data),
        output_dir=Path(args.output),
        date_col=args.date_col,
        target_col=args.target,
        group_cols=args.group_cols,
        report_title=args.report_title,
    )
    result = pipeline.run()
    print("日报生成完成：")
    print(f"Markdown: {result.markdown_path}")
    print(f"HTML    : {result.html_path}")


if __name__ == "__main__":
    main()
