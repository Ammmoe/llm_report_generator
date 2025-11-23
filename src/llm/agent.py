import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.llm.tools import PlotTool
import pandas as pd

load_dotenv()  # loads GOOGLE_API_KEY


class LLMReportAgent:
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
            "- Embed images using markdown: ![alt](filename.png)\n"
            "- Use clear, logical sections.\n"
            "- Do not invent new plots.\n\n"
            "### Plot Filenames\n"
            f"{json.dumps(plot_filenames, indent=2)}\n\n"
            "### Sales Summary Data\n"
            f"```json\n{json.dumps(summary_dict, indent=2)}\n```\n\n"
            "Now produce ONLY the final markdown report.\n"
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )

        markdown = self._extract_text(response)

        return markdown.strip()
    
    def analyze_models_over_years_trend(self, year_model_summary: dict, figures_dir: str, title_prefix: str = "All Regions") -> str:
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
            year_model_summary,
            figures_dir,
            title_prefix=title_prefix
        )

        if not plot_path:
            raise RuntimeError("Models-over-years plot was not generated.")

        plot_filename = os.path.basename(plot_path)

        # 2) Prepare LLM prompt
        prompt = f"""
            You are a senior automotive market analyst. Write a structured and insightful Markdown report analyzing
            the top-performing and underperforming BMW models across all regions over the years.

            ### Rules
            - Embed the plot BEFORE the analysis using markdown syntax: `![alt]({plot_filename})`.
            - Focus on identifying high-growth models, weak performers,
            and notable year-over-year trends.
            - Do NOT invent additional plots or data.

            ### Plot Filename
            {plot_filename}

            ### Model Performance Summary (Top 3 & Bottom 3 per Year)
            ```json
            {json.dumps(year_model_summary, indent=2)}
            ```

            Now produce ONLY the final markdown report.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}")

        markdown = self._extract_text(response)
        return markdown.strip()

    def analyze_models_over_region_trend(self, model_summary: dict, figures_dir: str) -> str:
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
        prompt = f"""
            You are a senior automotive market analyst. Write a structured and insightful Markdown report analyzing
            top-performing and underperforming BMW models for each region across years.

            ### Rules
            - For each region: embed the corresponding plot BEFORE the analysis.
            - Embed plots using markdown syntax: `![alt](filename.png)`.
            - Focus on identifying high-growth models, weak performers,
            notable regional differences, and year-over-year patterns.
            - Do NOT invent additional plots or data.

            ### Region Plot Filenames\n
            {json.dumps(region_plot_filenames, indent=2)}\n\n

            ### Model Performance Summary (Top 3 & Bottom 3 per Year)\n
            ```json\n{json.dumps(model_summary, indent=2)}\n```\n\n

            Now produce ONLY the final markdown report.\n
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}")

        markdown = self._extract_text(response)
        return markdown.strip()
    
    def analyze_correlation_matrix(self, corr_df: pd.DataFrame, figures_dir: str) -> str:
        """
        Generate correlation matrix plot and produce a markdown report with the plot
        embedded BEFORE the analysis text.

        Args:
            corr_df: pandas DataFrame of the correlation matrix.
            figures_dir: directory where plot images will be saved.

        Returns:
            str: Markdown report generated by the LLM.
        """
        import os

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
            "Create a detailed and insightful Markdown report analyzing key sales drivers by oberving the correlation vector.\n\n"
            "### Important Instructions\n"
            "- ALWAYS place the correlation vector plot BEFORE the analysis text.\n"
            "- Embed the image using markdown syntax: ![Correlation Vector](filename.png)\n"
            "- Provide clear interpretations of the strongest positive and negative correlations.\n"
            "- Do not invent additional plots or data.\n\n"
            "### Plot Filename\n"
            f"{json.dumps(plot_filename)}\n\n"
            "### Correlation Vector Data\n"
            f"```json\n{json.dumps(corr_dict, indent=2)}\n```\n\n"
            "Now produce ONLY the final markdown report.\n"
        )

        # 5) Call the model
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}")

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
            "Combine these reports into one concise markdown report containing only the key insights from each, "
            "while keeping all existing plot images embedded exactly as they are.\n\n"
            "### Important Instructions\n"
            "- DO NOT remove or alter any existing plot embeds like ![alt](filename.png).\n"
            "- Summarize the text content to keep only the most important insights.\n"
            "- Organize the report logically with clear section headings.\n"
            "- Preserve all original markdown formatting where relevant.\n\n"
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
            raise RuntimeError(f"LLM generation failed: {e}")

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
