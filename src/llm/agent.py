import json
import re
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

    def analyze(
        self, summary_dict: dict, figures_dir: str
    ) -> tuple[str, dict[str, str]]:
        """Generate a sales trend report and handle multiple plot requests."""

        prompt = (
            "You are a data analyst. Focus ONLY on identifying and describing "
            "sales performance trends over time (by year and by region).\n\n"
            f"Here is the sales summary JSON data:\n```json\n{json.dumps(summary_dict, indent=2)}\n```"
            "You can request plots to support your analysis by outputting lines exactly like:\n"
            "`CALL_TOOL:generate_plot <plot_type>`\n"
            "where <plot_type> must be one of the following:\n"
            "- sales_by_year\n"
            "- sales_by_region_year\n\n"
            "Request any number of plots needed and produce your analysis text in markdown.\n\n"
        )

        token_count = self.count_prompt_tokens(prompt)
        print("Token count:", token_count)

        if token_count > self.max_input_tokens:
            raise ValueError(
                f"Prompt too large: {token_count} tokens (limit: {self.max_input_tokens})"
            )

        config = types.GenerateContentConfig()

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config,
        )

        text = self._extract_text(response)

        # Find ALL plot requests in the LLM output
        plot_requests = re.findall(r"CALL_TOOL:generate_plot (\w+)", text)
        plot_paths = {}

        if plot_requests:
            print(f"LLM requested plots: {plot_requests}")

            for plot_type in plot_requests:
                plot_data = summary_dict.get(plot_type)
                if not plot_data:
                    # Instead of returning error string, raise an exception or handle it
                    raise ValueError(f"No data found for plot type '{plot_type}'.")

                plot_path = self.plot_tool.generate_plot(
                    plot_type, plot_data, figures_dir
                )
                plot_paths[plot_type] = plot_path

            # Remove all tool call lines from the text
            for plot_type in plot_requests:
                text = text.replace(f"CALL_TOOL:generate_plot {plot_type}", "")

        # Always return a tuple (text, plot_paths), where plot_paths may be empty dict if no plots
        return text.strip(), plot_paths

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
