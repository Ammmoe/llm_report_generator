import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()  # loads .env where GOOGLE_API_KEY is set


class LLMReportAgent:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.client = genai.Client()
        self.model_name = model_name

    def analyze(self, summary_dict: dict) -> str:
        # Prepare prompt with instructions + JSON summary
        prompt = f"""
You are a data analyst who writes clear business reports about BMW sales data.
You analyze the structured sales summary JSON input and produce:

- Executive summary
- Sales trends
- Top & underperforming models and regions
- Key drivers
- Additional insights

Use markdown format for the output.

Here is the data:
{json.dumps(summary_dict, indent=2)}
"""

        # Config with no special tools or function calls needed
        config = types.GenerateContentConfig()

        # Call the Gemini model to generate content
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config,
        )

        # Extract text from response
        generated_text = ""
        for candidate in response.candidates:
            for part in candidate.content.parts:
                generated_text += part.text

        return generated_text

    # Optional placeholder for plot request, if you have PlotTool implemented
    def request_plots(self, summary_dict: dict, figures_dir: str) -> dict:
        # Implement if you have plotting logic
        raise NotImplementedError("PlotTool not implemented yet.")
