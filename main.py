import os
from src.data_processing.loader import (
    load_dataset,
    summarize_sales_by_region_year,
    summarize_models_by_region_year,
    explore_key_drivers_of_sales,
    summarize_models_by_year,
    xgboost_key_drivers,
)
from src.config import DATASET_PATH, get_run_report_dir
from src.llm.agent import LLMReportAgent
from src.llm.utils import Spinner
from src.reporting.markdown_builder import build_markdown_report


# Provide the path to the Excel dataset
dataset_dir = DATASET_PATH

# Get an experiment run folder
experiment_dir = get_run_report_dir()
figures_dir = os.path.join(experiment_dir, "figures")

# Load data
df = load_dataset(dataset_dir)

# Preprocess data
sales_summary = summarize_sales_by_region_year(
    df, os.path.join(experiment_dir, "sales_summary.json")
)

model_by_year_summary = summarize_models_by_year(
    df, os.path.join(experiment_dir, "models_by_year_summary.json")
)

model_by_region_summary = summarize_models_by_region_year(
    df, os.path.join(experiment_dir, "models_by_region_summary.json")
)

# Explore key drivers of sales
sales_drivers = explore_key_drivers_of_sales(df)

# Explore XGBoost sales drivers
xgboost_sales_drivers = xgboost_key_drivers(df)

llm_agent = LLMReportAgent()

# Step 1 — Sales trend analysis
spinner = Spinner("Analyzing overall and regional sales trends")
spinner.start()
sales_report_md = llm_agent.analyze_sales_trend(sales_summary, figures_dir)
spinner.stop()

# Step 2 — Model performance by years
spinner = Spinner("Analyzing model performance trends across years")
spinner.start()
model_by_year_report_md = llm_agent.analyze_models_over_years_trend(
    model_by_year_summary, figures_dir
)
spinner.stop()

# Step 3 — Regional model performance
spinner = Spinner("Analyzing regional model sales performance")
spinner.start()
model_by_region_report_md = llm_agent.analyze_models_over_region_trend(
    model_by_region_summary, figures_dir
)
spinner.stop()

# Step 4 — Sales drivers
spinner = Spinner("Analyzing key drivers of sales (correlations)")
spinner.start()
drivers_report_md = llm_agent.analyze_correlation_matrix(sales_drivers, figures_dir)
spinner.stop()

# Step 5 — Combine all reports
spinner = Spinner("Generating final report")
spinner.start()
combined_md = llm_agent.combine_and_summarize_reports(
    [
        sales_report_md,
        model_by_year_report_md,
        model_by_region_report_md,
        drivers_report_md,
    ]
)
spinner.stop()

# Step 6 — Build final file
combined_report_path = build_markdown_report(
    [combined_md],
    out_dir=experiment_dir,
    report_title="BMW Sales Analysis Report",
)

print(f"Final report saved to: {combined_report_path}")
