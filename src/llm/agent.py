"""
LLM Agent (Gemini/OpenAI/Ollama)

This module handles:
1. Generating analysis text
2. Calling tools (optional)
"""

import json
from src.llm.tools import PlotTool


class LLMReportAgent:
    def __init__(self, client):
        self.client = client
        self.plot_tool = PlotTool()

    def analyze(self, summary_dict: dict) -> str:
        """
        Sends structured metrics to LLM and receives narrative analysis.
        """
        prompt = f"""
You are a data analyst. Analyze the following BMW sales summary:

{json.dumps(summary_dict, indent=2)}

Write:
- Executive summary
- Sales trends
- Top & underperforming models/regions
- Key drivers
- 1–2 additional insights
"""

        response = self.client.generate(prompt)  # adapt based on API
        return response

    def request_plots(self, summary_dict: dict, figures_dir: str) -> dict:
        """
        Let the LLM decide what plots to generate.
        For simplicity, call Python plotting directly in this starter.
        """
        return self.plot_tool.generate_all(summary_dict, figures_dir)
