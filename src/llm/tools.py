from src.plotting.plot_functions import (
    plot_sales_by_year,
    plot_regions,  # or rename to plot_regions_by_year if you prefer
    # plot_top_models,  # add later if summary includes top_models
)


class PlotTool:
    """
    Python-side plotting tool exposing functions that LLM can invoke by name.
    """

    def __init__(self):
        # Map plot_type keys to plot functions
        self.plot_functions = {
            "sales_by_year": plot_sales_by_year,
            "sales_by_region_year": plot_regions,
            # "top_models": plot_top_models,  # enable once summary includes this
        }

    def generate_plot(self, plot_type: str, data: dict, out_dir: str) -> str:
        """
        Generate a specific plot given plot_type and data.

        Args:
            plot_type: Identifier string of plot type requested by LLM.
            data: Dict or relevant data needed to generate the plot.
            out_dir: Directory to save plot file.

        Returns:
            Path (str) to the saved plot image (e.g., PNG).

        Raises:
            ValueError: if plot_type is unknown or data is invalid.
        """
        if plot_type not in self.plot_functions:
            raise ValueError(
                f"Unknown plot_type '{plot_type}'. Available types: {list(self.plot_functions.keys())}"
            )

        plot_func = self.plot_functions[plot_type]

        # Call the plot function, passing data and output directory
        try:
            plot_path = plot_func(data, out_dir)
        except Exception as e:
            raise RuntimeError(f"Plot generation failed for '{plot_type}': {e}")

        return plot_path

    def generate_all(self, summary: dict, out_dir: str) -> dict:
        """
        Generate all predefined plots using the summary data.

        Returns:
            Dict of plot_type -> saved plot path.
        """
        paths = {}
        for plot_type, plot_func in self.plot_functions.items():
            try:
                # Use the summary keys exactly as mapped in plot_functions
                plot_data = summary.get(plot_type)
                if plot_data is None:
                    print(f"Warning: no data for plot type '{plot_type}', skipping.")
                    continue  # skip if no data for this plot

                paths[plot_type] = plot_func(plot_data, out_dir)
            except Exception as e:
                print(f"Warning: failed to generate plot {plot_type}: {e}")
        return paths
