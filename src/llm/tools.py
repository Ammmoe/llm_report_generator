from src.plotting.plot_functions import (
    plot_sales_by_year,
    plot_top_models,
    plot_regions,
)


class PlotTool:
    """
    Python-side tools that the LLM can trigger via tool-calling.
    """

    def generate_all(self, summary, out_dir):
        paths = {}

        paths["yearly"] = plot_sales_by_year(summary["yearly_sales"], out_dir)
        paths["models"] = plot_top_models(summary["top_models"], out_dir)
        paths["regions"] = plot_regions(summary["region_performance"], out_dir)

        return paths
