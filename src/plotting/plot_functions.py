import os
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.cm as cm
from matplotlib.colors import Normalize


def plot_sales_by_year(yearly_dict: dict, out_dir: str) -> str:
    """
    Plot total sales volume by year as a line chart.

    Args:
        yearly_dict (dict): Mapping of year (str or int) to total sales volume (int).
            Example: {"2020": 1234, "2021": 2345, ...}
        out_dir (str): Directory path where the plot image will be saved.

    Returns:
        str: File path to the saved PNG plot image.
    """
    years = sorted(yearly_dict.keys())
    values = [yearly_dict[year] for year in years]

    plt.figure(figsize=(8, 4))
    plt.plot(years, values, marker="o")
    plt.title("Sales by Year")
    plt.xlabel("Year")
    plt.ylabel("Sales Volume")
    plt.grid(True)

    path = os.path.join(out_dir, "sales_by_year.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    return path


def plot_regions(region_year_dict: dict, out_dir: str) -> str:
    """
    Plot sales volume by region over multiple years as a multi-line chart.

    Args:
        region_year_dict (dict): Nested dict with regions as keys and values as dicts mapping year to sales volume.
            Example:
            {
                "Europe": {"2020": 1234, "2021": 2345},
                "Asia": {"2020": 3456, "2021": 4567},
            }
        out_dir (str): Directory path where the plot image will be saved.

    Returns:
        str: File path to the saved PNG plot image.
    """
    plt.figure(figsize=(10, 6))

    # Collect all years across regions (union of all years)
    all_years = set()
    for region_data in region_year_dict.values():
        all_years.update(region_data.keys())
    all_years = sorted(all_years)

    # Plot sales trend per region
    for region, year_dict in region_year_dict.items():
        values = [year_dict.get(year, 0) for year in all_years]
        plt.plot(all_years, values, marker="o", label=region)

    plt.title("Sales by Region Over Years")
    plt.xlabel("Year")
    plt.ylabel("Sales Volume")
    plt.legend()
    plt.grid(True)

    path = os.path.join(out_dir, "sales_by_region_year.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    return path


import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import os
from typing import Dict, Any


def plot_models_by_region_over_years(
    region_models_dict: Dict[str, Any],
    out_dir: str,
    region_name: str,
) -> str:
    """
    Plot sales of all models over years as lines for a given region.

    Args:
        region_models_dict: {
            "2020": [
                {"Model": "X5", "Total_Sales": 23000},
                {"Model": "3 Series", "Total_Sales": 18000},
                ...
            ],
            "2021": [...],
            ...
        }
        out_dir: Directory to save the plot
        region_name: Region name, used for filename and title

    Returns:
        Path to saved PNG file
    """

    years = sorted(region_models_dict.keys())
    n_years = len(years)

    if n_years == 0:
        raise ValueError(f"No data available for region {region_name}")

    # Collect all unique models appearing in this region across years
    all_models_set = set()
    for year in years:
        for entry in region_models_dict[year]:
            all_models_set.add(entry["Model"])
    all_models = sorted(all_models_set)
    n_models = len(all_models)

    plt.figure(figsize=(max(12, n_models * 0.5), 7))  # widen plot if many models

    # Generate color map for all models
    colors = cm.get_cmap("tab20")(np.linspace(0, 1, n_models))

    model_color_map = {model: colors[i] for i, model in enumerate(all_models)}

    # Prepare sales data matrix: rows = models, cols = years
    sales_matrix = np.zeros((n_models, n_years), dtype=float)
    for year_idx, year in enumerate(years):
        year_data = region_models_dict[year]
        sales_dict = {entry["Model"]: entry["Total_Sales"] for entry in year_data}
        for model_idx, model in enumerate(all_models):
            sales_matrix[model_idx, year_idx] = sales_dict.get(model, 0)

    # Plot each model's sales over years as a line
    for model_idx, model in enumerate(all_models):
        plt.plot(
            years,
            sales_matrix[model_idx],
            label=model,
            color=model_color_map[model],
            marker="o",
            linewidth=2,
            markersize=5,
        )

    plt.title(f"Model Sales Over Years – {region_name}")
    plt.xlabel("Year")
    plt.ylabel("Sales Volume")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.xticks(rotation=45)

    plt.legend(loc="upper left", bbox_to_anchor=(1, 1), fontsize="small")
    plt.tight_layout()

    os.makedirs(out_dir, exist_ok=True)
    safe_region_name = region_name.replace(" ", "_")
    path = os.path.join(out_dir, f"{safe_region_name}_all_models_performance_line.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()

    return path

def plot_correlation_vector(
    corr_vector, out_dir: str, filename: str = "correlation_vector.png"
) -> str:
    """
    Plot a correlation vector (single-column DataFrame or Series) as a horizontal bar plot
    with color reflecting correlation strength and sign.

    Args:
        corr_vector (pd.Series or pd.DataFrame): Correlation values with features as index.
        out_dir (str): Directory to save the plot.
        filename (str): Output filename.

    Returns:
        str: File path to the saved plot image.
    """
    # Convert single-column DataFrame to Series if needed
    if isinstance(corr_vector, pd.DataFrame):
        if corr_vector.shape[1] != 1:
            raise ValueError(
                "Input DataFrame must have exactly one column for correlation vector plot."
            )
        corr_vector = corr_vector.iloc[:, 0]

    # Sort correlations by absolute value descending for better visual
    corr_vector = corr_vector.reindex(
        corr_vector.abs().sort_values(ascending=False).index
    )

    features = corr_vector.index.tolist()
    values = np.array(corr_vector.values, dtype=float)  # ensure numpy float array

    fig_height = max(6, 0.3 * len(features))
    fig, ax = plt.subplots(figsize=(10, fig_height))

    # Normalize correlation values for color mapping [-1,1]
    norm = Normalize(-1, 1)
    colors = cm.coolwarm(norm(values))

    bars = ax.barh(features, values, color=colors)

    # Add value labels
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + 0.01 * np.sign(width),
            bar.get_y() + bar.get_height() / 2,
            f"{width:.3f}",
            va="center",
            ha="left" if width >= 0 else "right",
            fontsize=8,
        )

    ax.set_xlabel("Correlation with Sales Volume")
    ax.set_title("Correlation Vector Heatmap")
    ax.axvline(0, color="black", linewidth=0.8)
    plt.tight_layout()

    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    plt.savefig(path, bbox_inches="tight")
    plt.close()

    return path
