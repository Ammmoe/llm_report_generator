# Automated LLM Report Generation Pipeline

This repository contains a pipeline for automated report generation using a Large Language Model (LLM), specifically Google Gemini 2.5 Flash. The pipeline processes BMW sales data (2020-2024) and generates insightful markdown reports with supporting figures.

---

## 🏁 Getting Started

### Installation

Before running the pipeline, please install the required dependencies:

```bash
pip install -r requirements.txt
```

### Configuration

Before running the report generation script, you must configure your Gemini API key:

1. Open the `.env.example` file.
2. Set the following variables:

   ```bash
   GOOGLE_GENAI_USE_VERTEXAI=0
   GOOGLE_API_KEY=<YOUR GEMINI API KEY>
   ```

3. Save the file as `.env` in the root directory.

> **Note:** Make sure your Gemini API key is correctly set in the `.env` file before proceeding.

### Generating a Report

After installing dependencies and setting up your `.env` file, generate a report by running the main script:

```bash
python main.py
```

This will create a new report folder inside the `reports/` directory with a timestamped name like:

```bash
reports/run_YYYY_MM_DD_HH_MM_SS/
```

Inside that folder, you will find:

- The generated `report.md` markdown file.
- A `figures/` folder containing the visualizations.

Open the `report.md` file to view the automated LLM-generated report.

---

## 📂 Directory Structure

```bash
bmw-llm-reporting/
│
├── datasets/
│   └── BMW sales data (2020-2024).xlsx       # Dataset in Excel format
│
├── notebooks/
│   └── exploratory_analysis.ipynb             # Jupyter notebook for exploratory analysis
│
├── reports/
│   └── run_YYYY_MM_DD_HH_MM_SS/
│       ├── report.md                          # Generated markdown report
│       └── figures/                           # Generated figures/images
│
├── src/
│   ├── data_processing/
│   │   └── loader.py                          # Data loading and preprocessing
│   ├── llm/
│   │   ├── agent.py                           # LLM interaction logic
│   │   ├── tools.py                           # Helper tools for LLM
│   │   └── utils.py                           # Utility functions
│   ├── plotting/
│   │   └── plot_functions.py                  # Plotting functions for data visualization
│   ├── reporting/
│   │   └── markdown_builder.py                # Markdown report builder
│   └── config.py                              # Configuration settings
│
├── tests/
│   ├── test_loader.py                         # Tests for data loading
│   └── test_plotting.py                       # Tests for plotting functions
│
├── main.py                                    # Main entry point to run the report generation pipeline
├── requirements.txt                           # Python dependencies
└── .env.example                               # Example environment variables file
```

---

## 🧪 Running Tests

To run tests, use `pytest`.

- To run tests on the data loader:

  ```bash
  pytest tests/test_loader.py
  ```

- To test plotting functions:

  ```bash
  pytest tests/test_plotting.py
  ```

---

If you have any questions or issues, feel free to open an issue or reach out.
