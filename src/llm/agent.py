import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.llm.tools import PlotTool

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

    def analyze_model_trend(self, model_summary: dict, figures_dir: str) -> str:
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
