"""Streamlit 页面入口。"""

from __future__ import annotations

from pathlib import Path
import tempfile

import pandas as pd
import streamlit as st

from src.pipeline import DailyReportPipeline


st.set_page_config(page_title="多 Agent 自动化数据洞察日报系统", layout="wide")
st.title("多 Agent 协作的自动化数据洞察与日报系统")
st.caption("上传 CSV / Excel 数据，自动生成数据洞察、图表和日报。")

uploaded = st.file_uploader("上传数据文件", type=["csv", "xlsx", "xls"])

if uploaded is None:
    st.info("可以先使用项目中的 sample_data/sales_demo.csv 体验命令行运行。")
    st.stop()

suffix = Path(uploaded.name).suffix.lower()
with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
    tmp.write(uploaded.read())
    data_path = Path(tmp.name)

try:
    if suffix == ".csv":
        preview_df = pd.read_csv(data_path)
    else:
        preview_df = pd.read_excel(data_path)
except Exception as exc:
    st.error(f"文件读取失败：{exc}")
    st.stop()

st.subheader("数据预览")
st.dataframe(preview_df.head(20), use_container_width=True)

cols = list(preview_df.columns)
numeric_cols = preview_df.select_dtypes(include="number").columns.tolist()

left, right = st.columns(2)
with left:
    date_col = st.selectbox("日期列", options=[None] + cols, index=0)
    target_col = st.selectbox("重点分析指标列", options=numeric_cols or cols)
with right:
    group_cols = st.multiselect("分组字段", options=[c for c in cols if c != target_col])
    report_title = st.text_input("日报标题", value="自动化数据洞察日报")

if st.button("生成日报", type="primary"):
    pipeline = DailyReportPipeline(
        data_path=data_path,
        output_dir=Path("reports"),
        date_col=date_col,
        target_col=target_col,
        group_cols=group_cols,
        report_title=report_title,
    )
    result = pipeline.run()
    st.success("日报生成完成")

    st.subheader("核心洞察")
    for item in result.context.get("insights", []):
        st.markdown(f"- {item}")

    st.subheader("图表")
    chart_paths = result.context.get("chart_paths", [])
    for chart in chart_paths:
        st.image(chart)

    st.subheader("日报预览")
    st.markdown(result.markdown_path.read_text(encoding="utf-8"))

    st.download_button(
        "下载 Markdown 日报",
        data=result.markdown_path.read_text(encoding="utf-8"),
        file_name="daily_report.md",
        mime="text/markdown",
    )
    st.download_button(
        "下载 HTML 日报",
        data=result.html_path.read_text(encoding="utf-8"),
        file_name="daily_report.html",
        mime="text/html",
    )
