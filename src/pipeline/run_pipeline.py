from src.data_processing.loader import load_dataset, preprocess_dataset
from src.data_processing.utils import extract_summary_statistics
from src.llm.agent import LLMReportAgent
from src.config import get_run_report_dir
from src.reporting.markdown_builder import build_markdown
from src.reporting.html_exporter import convert_md_to_html


class DummyLLMClient:
    def generate(self, prompt):
        return "This is a placeholder LLM response. Replace with actual API call."


def run_pipeline():
    run_dir = get_run_report_dir()
    figures_dir = f"{run_dir}/figures"

    print(f"Running pipeline. Report folder: {run_dir}")

    df = load_dataset()
    df = preprocess_dataset(df)
    summary = extract_summary_statistics(df)

    agent = LLMReportAgent(DummyLLMClient())

    analysis = agent.analyze(summary)
    plots = agent.request_plots(summary, figures_dir)

    md_path = build_markdown(analysis, plots, run_dir)
    convert_md_to_html(md_path, run_dir)

    print("Pipeline completed.")
