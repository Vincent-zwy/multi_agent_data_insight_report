"""定时任务入口：每天自动生成日报。"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler

from src.pipeline import DailyReportPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="定时生成数据洞察日报")
    parser.add_argument("--data", required=True, help="CSV 或 Excel 数据文件路径")
    parser.add_argument("--date-col", default=None, help="日期列名")
    parser.add_argument("--target", required=True, help="重点分析指标列")
    parser.add_argument("--group-cols", nargs="*", default=[], help="分组字段")
    parser.add_argument("--output", default="reports", help="日报输出目录")
    parser.add_argument("--report-title", default="自动化数据洞察日报", help="日报标题")
    parser.add_argument("--hour", type=int, default=9, help="每天运行小时，默认 9")
    parser.add_argument("--minute", type=int, default=0, help="每天运行分钟，默认 0")
    return parser.parse_args()


def build_job(args: argparse.Namespace):
    def job() -> None:
        pipeline = DailyReportPipeline(
            data_path=Path(args.data),
            output_dir=Path(args.output),
            date_col=args.date_col,
            target_col=args.target,
            group_cols=args.group_cols,
            report_title=args.report_title,
        )
        result = pipeline.run()
        print(f"[Scheduler] 日报已生成：{result.html_path}")

    return job


def main() -> None:
    args = parse_args()
    scheduler = BackgroundScheduler()
    scheduler.add_job(build_job(args), trigger="cron", hour=args.hour, minute=args.minute)
    scheduler.start()

    print(f"定时任务已启动：每天 {args.hour:02d}:{args.minute:02d} 自动生成日报。按 Ctrl+C 退出。")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
        print("定时任务已停止。")


if __name__ == "__main__":
    main()
