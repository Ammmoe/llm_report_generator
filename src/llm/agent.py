"""
Module for generating BMW sales analysis reports by combining
plot creation and large language model (LLM) based markdown report generation.
"""

import json
import os
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.llm.tools import PlotTool

load_dotenv()  # loads GOOGLE_API_KEY


class LLMReportAgent:
    """
    Agent that generates detailed markdown reports analyzing BMW sales data.

    Combines automated plotting utilities with LLM-powered narrative generation
    for sales trends, model performance, regional analysis, and correlation insights.
    """

    def __init__(self, model_name="gemini-2.5-flash", max_input_tokens=25000):
        self.client = genai.Client()
        self.model_name = model_name
        self.max_input_tokens = max_input_tokens
        self.plot_tool = PlotTool()

    def analyze_sales_trend(self, summary_dict: dict, figures_dir: str) -> str:
        """
        Generate plots first, then ask the LLM to assemble
        a complete markdown report with correct local plot filenames.
        """

        # ALWAYS generate the two known plots
        plot_paths = {}
        fixed_plot_types = ["sales_by_year", "sales_by_region_year"]

        for plot_type in fixed_plot_types:
            plot_data = summary_dict.get(plot_type)
            if not plot_data:
                raise ValueError(f"No data found for required plot type '{plot_type}'.")

            # Save plot
            full_path = self.plot_tool.generate_plot(plot_type, plot_data, figures_dir)
            plot_paths[plot_type] = full_path

        # Convert absolute paths → just filenames
        plot_filenames = {
            key: os.path.basename(path) for key, path in plot_paths.items()
        }

        # Ask LLM to produce structured markdown report
        prompt = (
            "You are a senior data analyst. "
            "Create a clean and structured Markdown report based on BMW sales trends.\n\n"
            "### Important Instructions\n"
            "- ALWAYS place each plot BEFORE its related analysis.\n"
            "- Embed images using markdown: ![alt](figures/filename.png)\n"
            "- Use clear, logical sections.\n"
            "- Do not invent new plots.\n\n"
            "### Sections to Produce\n"
            "1. Overall Sales Trend Analysis\n"
            "   - Identify and describe key trends in total sales volume over the years.\n"
            "   - Mention any notable peaks, dips, or steady growth patterns.\n\n"
            "2. Regional Sales Trend Analysis\n"
            "   - Identify and describe sales performance for each region individually.\n"
            "   - Compare regional trends where relevant.\n\n"
            "### Plot Filenames\n"
            f"{json.dumps(plot_filenames, indent=2)}\n\n"
            "### Sales Summary Data\n"
            f"```json\n{json.dumps(summary_dict, indent=2)}\n```\n\n"
            "Now produce ONLY the final markdown report with these sections.\n"
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )

        markdown = self._extract_text(response)

        return markdown.strip()

    def analyze_models_over_years_trend(
        self,
        year_model_summary: dict,
        figures_dir: str,
        title_prefix: str = "All Regions",
    ) -> str:
        """
        Generate the models-over-years plot and ask the LLM
        to produce a markdown report highlighting performance
        of top and bottom performing models across years.

        Args:
            year_model_summary: dict like:
                {
                    "2020": [
                        {"Model": "X5", "Total_Sales": 23000},
                        {"Model": "3 Series", "Total_Sales": 18000},
                        ...
                    ],
                    "2021": [...],
                    ...
                }
            figures_dir: directory to save generated plot
            title_prefix: title prefix for the plot and filename

        Returns:
            Markdown report string
        """

        if not year_model_summary:
            raise ValueError("Year-model summary data is empty or None.")

        # 1) Generate the combined plot for all models over years
        plot_path = self.plot_tool.generate_models_over_years_plot(
            year_model_summary, figures_dir, title_prefix=title_prefix
        )

        if not plot_path:
            raise RuntimeError("Models-over-years plot was not generated.")

        plot_filename = os.path.basename(plot_path)

        # 2) Prepare LLM prompt
        prompt = (
            "You are a senior automotive market analyst. "
            "Create a clear and structured Markdown report analyzing BMW model sales performance over the years.\n\n"
            "### Important Instructions\n"
            "- ALWAYS place the plot BEFORE its related analysis.\n"
            "- Embed images using markdown: ![alt](figures/filename.png)\n"
            "- Use clear, logical sections.\n"
            "- Do not invent new plots or data.\n\n"
            "### Sections to Produce\n"
            "1. Top-Performing Models Over the Years\n"
            "   - Identify models with consistently high sales across multiple years.\n"
            "   - Highlight any models showing strong growth trends.\n\n"
            "2. Underperforming Models Over the Years\n"
            "   - Identify models with consistently low or declining sales.\n"
            "   - Mention any models that dropped significantly or disappeared.\n\n"
            "3. Notable Year-over-Year Trends\n"
            "   - Discuss interesting shifts or patterns in model sales.\n"
            "   - Mention emerging popular models or any anomalies.\n\n"
            "### Plot Filename\n"
            f"{plot_filename}\n\n"
            "### Model Performance Summary Data\n"
            f"```json\n{json.dumps(year_model_summary, indent=2)}\n```\n\n"
            "Now produce ONLY the final markdown report with these sections.\n"
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}") from e

        markdown = self._extract_text(response)
        return markdown.strip()

    def analyze_models_over_region_trend(
        self, model_summary: dict, figures_dir: str
    ) -> str:
        """
        Generate region-level model plots and ask the LLM
        to produce a markdown report highlighting performance
        of BMW models per region across years.
        """

        if not model_summary:
            raise ValueError("Model summary data is empty or None.")

        # 1) Generate plots → one per region
        region_plot_paths = self.plot_tool.generate_region_model_plots(
            model_summary, figures_dir
        )

        if not region_plot_paths:
            raise RuntimeError("No region plots were generated.")

        # 2) Convert paths to filenames for markdown embedding
        region_plot_filenames = {
            region.replace(" ", "_"): os.path.basename(path)
            for region, path in region_plot_paths.items()
        }

        # 3) Prepare LLM prompt
        prompt = (
            "You are a senior automotive market analyst. "
            "Write a clear and concise Markdown report analyzing BMW model sales performance per region across years.\n\n"
            "### Important Instructions\n"
            "- For each region, embed the corresponding plot BEFORE its analysis.\n"
            "- Use markdown syntax to embed images: ![alt](figures/filename.png)\n"
            "- Focus on:\n"
            "  1. Interesting and unique regional sales trends.\n"
            "  2. High-performing models specific to each region.\n"
            "  3. Underperforming models and notable declines.\n"
            "- Keep the analysis succinct and avoid repeating information from the overall model performance section.\n"
            "- Do NOT invent additional plots or data.\n\n"
            "### Region Plot Filenames\n"
            f"{json.dumps(region_plot_filenames, indent=2)}\n\n"
            "### Model Performance Summary for All Regions\n"
            f"```json\n{json.dumps(model_summary, indent=2)}\n```\n\n"
            "Now produce ONLY the final markdown report with regional model performance analysis sections.\n"
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}") from e

        markdown = self._extract_text(response)
        return markdown.strip()

    def analyze_correlation_matrix(
        self, corr_df: pd.DataFrame, figures_dir: str
    ) -> str:
        """
        Generate correlation matrix plot and produce a markdown report with the plot
        embedded BEFORE the analysis text.

        Args:
            corr_df: pandas DataFrame of the correlation matrix.
            figures_dir: directory where plot images will be saved.

        Returns:
            str: Markdown report generated by the LLM.
        """
        if corr_df.empty:
            raise ValueError("Correlation DataFrame is empty.")

        # 1) Generate correlation matrix plot and save the path
        plot_path = self.plot_tool.generate_correlation_matrix(corr_df, figures_dir)

        # 2) Extract filename from full path for markdown embedding
        plot_filename = os.path.basename(plot_path)

        # 3) Convert correlation DataFrame to JSON-serializable dict
        corr_dict = corr_df.to_dict()

        # 4) Prepare prompt with plot BEFORE analysis text
        prompt = (
            "You are a senior data analyst.\n"
            "Create a detailed and insightful Markdown report analyzing key drivers of BMW sales by examining the correlation vector.\n\n"
            "### Important Instructions\n"
            "- ALWAYS place the correlation vector plot BEFORE the analysis text.\n"
            "- Embed the image using markdown syntax: ![Correlation Vector](figures/plot_filename)\n"
            "- Provide honest and balanced interpretations of the strongest positive and negative correlations.\n"
            "- Clearly explain which features appear to be key drivers of sales and why.\n"
            "- Mention any features with weak or no correlation briefly.\n"
            "- Do not invent additional plots or data.\n\n"
            "### Plot Filename\n"
            f"{json.dumps(plot_filename)}\n\n"
            "### Correlation Vector Data\n"
            f"```json\n{json.dumps(corr_dict, indent=2)}\n```\n\n"
            "Now produce ONLY the final markdown report with focused analysis of key sales drivers based on the correlations.\n"
        )

        # 5) Call the model
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}") from e

        # 6) Extract text from response
        markdown = self._extract_text(response)

        return markdown.strip()

    def combine_and_summarize_reports(self, markdown_reports: list[str]) -> str:
        """
        Combine multiple markdown reports into one compact report containing
        only key insights but keeping all plot markdown image embeds intact.

        Args:
            markdown_reports (list[str]): List of markdown report strings to combine.

        Returns:
            str: Combined concise markdown report.
        """

        # Join input reports with separators for clarity
        joined_reports = "\n\n---\n\n".join(markdown_reports)
        prompt = (
            "You are a senior data analyst.\n"
            "You have multiple markdown reports, each containing text analysis and embedded plots.\n"
            "Combine these reports into one concise markdown report structured into exactly three main sections:\n\n"
            "1. Executive Summary\n"
            "   - Provide a clear and brief summary of the key insights from all reports.\n"
            "   - Organize the summary to reflect the three main analysis areas:\n"
            "     sales trend analysis, model performance analysis, and key drivers of sales analysis.\n"
            "   - Use bullet points where necessary to ensure the summary is clear, concise, and easy to read for business stakeholders.\n\n"
            "2. Analysis\n"
            "   - This section should have the following subsections:\n"
            "     1) Overall Sales Trend Analysis\n"
            "     2) Regional Sales Trend Analysis\n"
            "     3) Overall Model Performance Analysis\n"
            "     4) Regional Model Performance Analysis\n"
            "        - 4.1 Africa\n"
            "        - 4.2 Asia\n"
            "        - 4.3 Europe\n"
            "        - 4.4 Middle East\n"
            "        - 4.5 North America\n"
            "        - 4.6 South America\n"
            "        - Use bullet points liberally in this section to break up text and improve clarity.\n"
            "     5) Key Drivers of Sales through Correlation Analysis\n"
            "   - Synthesize findings from the reports for each subsection without repetition.\n"
            "   - Ensure each subsection logically builds on the previous ones, creating a clear flow of insights.\n"
            "   - Use bullet points where they help highlight important points and improve clarity.\n\n"
            "3. Recommendations\n"
            "   - Provide actionable recommendations clearly linked to insights from the analysis.\n"
            "   - Structure recommendations to correspond with the three analysis areas:\n"
            "     sales trends, model performance, and key drivers of sales.\n"
            "   - Use bullet points where appropriate to keep recommendations clear and concise.\n\n"
            "### Important Instructions\n"
            "- DO NOT remove or modify any existing plot embeds like ![alt](figures/filename.png).\n"
            "- Immediately after each plot embed, add a figure caption in the format:\n"
            "  'Figure X: <meaningful descriptive figure title>' where X is the figure number in order of appearance starting from 1.\n"
            "- Ensure the explanatory paragraph related to each figure always comes immediately after the figure caption.\n"
            "- Maintain this figure numbering and formatting uniformly throughout the report.\n"
            "- Ensure smooth narrative flow: the report should read as a cohesive document, not a collection of separate parts.\n"
            "- Prioritize only the most meaningful, high-impact insights that contribute substantially to understanding sales trends, model performance, and key drivers of sales.\n"
            "- Do NOT include every minor observation from the original reports. Consolidate and summarize the information to focus on the strongest patterns and conclusions.\n"
            "- This report is intended for business readers, not technical experts.\n"
            "- Do NOT include technical or advanced analytics method recommendations such as machine learning models or statistical techniques.\n"
            "- Focus recommendations on clear, actionable business insights only.\n\n"
            "### Reports to Combine\n"
            f"{joined_reports}\n\n"
            "Now produce ONLY the final combined markdown report."
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}") from e

        combined_markdown = self._extract_text(response)
        return combined_markdown.strip()

    def _extract_text(self, response) -> str:
        """Robustly extract text from Gemini response."""

        if not response or not response.candidates:
            return ""

        candidate = response.candidates[0]  # safest + recommended

        if not candidate.content or not candidate.content.parts:
            return ""

        parts_text = [
            getattr(part, "text", "")
            for part in candidate.content.parts
            if hasattr(part, "text") and part.text
        ]

        return "".join(parts_text)

    def count_prompt_tokens(self, prompt: str) -> int:
        """Return number of tokens for a given text prompt."""

        content = types.Content(parts=[types.Part(text=prompt)])

        response = self.client.models.count_tokens(
            model=self.model_name, contents=content
        )

        if response.total_tokens is None:
            raise RuntimeError("count_tokens() returned None")

        return response.total_tokens
