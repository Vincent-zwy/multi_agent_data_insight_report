# 多 Agent 协作的自动化数据洞察与日报系统

这是一个可直接上传 GitHub 的 Python 项目，用于从 CSV / Excel 数据中自动完成：

- 数据读取与字段识别
- 数据质量检查
- 关键指标统计
- 趋势、异常、环比、贡献度分析
- 自动生成可视化图表
- 自动输出 Markdown / HTML 日报
- 支持命令行运行、Streamlit 页面运行、定时任务运行

项目采用“多 Agent 协作”架构，将日报生成流程拆分为多个智能处理角色，便于展示系统架构、后续扩展大模型接口或接入数据库。

---

## 1. 项目结构

```text
multi_agent_data_insight_report/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
├── run.py                      # 命令行入口
├── scheduler.py                # 定时日报入口
├── streamlit_app.py            # Web 页面入口
├── sample_data/
│   └── sales_demo.csv          # 示例数据
├── reports/                    # 运行后自动生成日报
├── src/
│   ├── config.py
│   ├── models.py
│   ├── pipeline.py
│   ├── agents/
│   │   ├── base.py
│   │   ├── planning_agent.py
│   │   ├── data_loader_agent.py
│   │   ├── data_profiler_agent.py
│   │   ├── insight_agent.py
│   │   ├── visualization_agent.py
│   │   └── report_agent.py
│   └── utils/
│       ├── file_utils.py
│       └── time_utils.py
└── templates/
    └── daily_report.html.j2
```

---

## 2. 快速开始

### 2.1 创建虚拟环境

```bash
python -m venv .venv
```

Windows：

```bash
.venv\Scripts\activate
```

macOS / Linux：

```bash
source .venv/bin/activate
```

### 2.2 安装依赖

```bash
pip install -r requirements.txt
```

### 2.3 使用示例数据生成日报

```bash
python run.py --data sample_data/sales_demo.csv --date-col date --target sales --group-cols region product
```

运行完成后，会在 `reports/` 目录下生成日报文件，例如：

```text
reports/2026-04-29/daily_report.md
reports/2026-04-29/daily_report.html
reports/2026-04-29/assets/*.png
```

---

## 3. 启动 Web 页面

```bash
streamlit run streamlit_app.py
```

页面支持上传 CSV / Excel 文件，填写日期列、目标指标列、分组字段，然后自动生成日报。

---

## 4. 启动定时日报

每天固定时间自动生成日报：

```bash
python scheduler.py --data sample_data/sales_demo.csv --date-col date --target sales --group-cols region product --hour 9 --minute 0
```

表示每天 09:00 自动运行一次。

---

## 5. Agent 设计说明

本系统由以下 Agent 协作完成自动数据洞察任务：

| Agent | 作用 |
|---|---|
| PlanningAgent | 根据用户参数制定分析任务计划 |
| DataLoaderAgent | 读取 CSV / Excel 数据，并进行基础字段校验 |
| DataProfilerAgent | 分析数据规模、缺失值、字段类型、统计分布 |
| InsightAgent | 挖掘趋势、异常值、贡献度、相关性等洞察 |
| VisualizationAgent | 自动绘制趋势图、分组柱状图、相关性热力图 |
| ReportAgent | 汇总所有 Agent 结果，生成 Markdown / HTML 日报 |
| Pipeline Supervisor | 调度所有 Agent 顺序执行，统一管理上下文 |

---

## 6. 替换自己的数据

你的数据至少建议包含：

- 日期列，例如：`date`
- 数值指标列，例如：`sales`、`revenue`、`cost`、`orders`
- 可选分组列，例如：`region`、`product`、`channel`

运行示例：

```bash
python run.py --data your_data.csv --date-col 日期 --target 销售额 --group-cols 地区 产品
```


MIT License
