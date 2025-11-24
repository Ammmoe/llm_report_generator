"""
PlotTool module: Provides plotting functions for BMW sales data analysis.

Includes line plots for sales by year, by region, model sales over years,
region-specific model performance, and correlation heatmaps.

Designed for easy invocation by name and integration with LLM-based workflows.
"""

import os
from src.plotting.plot_functions import (
    plot_sales_by_year,
    plot_regions,
    plot_models_over_years,
    plot_models_by_region_over_years,
    plot_correlation_vector,
)


class PlotTool:
    """
    Plotting tool that exposes Python-side plotting functions
    for LLM to invoke by name.
    """

    def __init__(self):
        # plot_type -> function
        self.plot_functions = {
            "sales_by_year": plot_sales_by_year,
            "sales_by_region_year": plot_regions,
            # region-specific multi-plot handled separately
        }

    def generate_plot(self, plot_type: str, data: dict, out_dir: str) -> str:
        """
        Generate a plot using a simple plot function (accepts only data + out_dir).
        """
        if plot_type not in self.plot_functions:
            raise ValueError(
                f"Unknown plot_type '{plot_type}'. "
                f"Available: {list(self.plot_functions.keys())}"
            )

        plot_func = self.plot_functions[plot_type]

        try:
            return plot_func(data, out_dir)
        except Exception as e:
            raise RuntimeError(f"Plot generation failed for '{plot_type}': {e}") from e

    def generate_models_over_years_plot(
        self, year_models_summary: dict, out_dir: str, title_prefix: str = "All Regions"
    ) -> str:
        """
        Generate the line plot for models aggregated by year (no regions).

        Args:
            year_models_summary: dict like:
                {
                    "2020": [
                        {"Model": "X5", "Total_Sales": 23000},
                        {"Model": "3 Series", "Total_Sales": 18000},
                        ...
                    ],
                    "2021": [...],
                    ...
                }
            out_dir: Directory to save the plot
            title_prefix: Optional title prefix for the plot and filename

        Returns:
            Path to saved PNG file
        """
        os.makedirs(out_dir, exist_ok=True)
        try:
            return plot_models_over_years(year_models_summary, out_dir, title_prefix)
        except Exception as e:
            raise RuntimeError(f"Models-over-years plot generation failed: {e}") from e

    def generate_region_model_plots(
        self, region_models_summary: dict, out_dir: str
    ) -> dict:
        """
        Generate region-level line plots for all models per year.

        Args:
            region_models_summary: dict like:
                {
                    "Europe": {
                        "2020": [ {"Model": "X5", "Total_Sales": 50000}, ... ],
                        "2021": [ ... ],
                        ...
                    },
                    "Asia": {...}
                }

        Returns:
            Dict mapping region -> file path
        """
        os.makedirs(out_dir, exist_ok=True)
        output_paths = {}

        for region, year_dict in region_models_summary.items():
            if not year_dict:
                print(f"Skipping region '{region}' due to empty data.")
                continue
            try:
                path = plot_models_by_region_over_years(
                    year_dict,  # per-year model data
                    out_dir,  # output directory
                    region,  # region name
                )
                output_paths[region] = path

            except Exception as e:
                raise RuntimeError(
                    f"Warning: Failed to generate model-performance plot for {region}: {e}"
                ) from e

        return output_paths

    def generate_correlation_matrix(self, data, out_dir: str) -> str:
        """
        Generate the correlation matrix plot separately.
        """
        os.makedirs(out_dir, exist_ok=True)
        try:
            return plot_correlation_vector(data, out_dir)
        except Exception as e:
            raise RuntimeError(f"Correlation matrix plot generation failed: {e}") from e

    def generate_all(self, summary: dict, out_dir: str) -> dict:
        """
        Run all default single-output plots.
        Region model plots must be called separately.
        """
        paths = {}
        for plot_type, plot_func in self.plot_functions.items():
            try:
                data = summary.get(plot_type)
                if data is None:
                    print(f"Skipping '{plot_type}' – missing data in summary.")
                    continue

                paths[plot_type] = plot_func(data, out_dir)
            except Exception as e:
                raise RuntimeError(
                    f"Warning: Failed to generate '{plot_type}': {e}"
                ) from e

        return paths
