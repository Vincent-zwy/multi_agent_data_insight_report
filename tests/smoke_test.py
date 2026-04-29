"""最小化冒烟测试。运行方式：python tests/smoke_test.py"""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.pipeline import DailyReportPipeline


def main() -> None:
    pipeline = DailyReportPipeline(
        data_path=Path("sample_data/sales_demo.csv"),
        output_dir=Path("reports"),
        date_col="date",
        target_col="sales",
        group_cols=["region", "product"],
        report_title="测试日报",
    )
    result = pipeline.run()
    assert result.markdown_path.exists()
    assert result.html_path.exists()
    print("smoke test passed")


if __name__ == "__main__":
    main()
