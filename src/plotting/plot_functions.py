import os
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from matplotlib.ticker import FuncFormatter
import numpy as np
from typing import Dict, Any
import matplotlib.patches as mpatches


def plot_sales_by_year(yearly_dict: dict, out_dir: str) -> str:
    """
    Plot total sales volume by year as a line chart.

    Args:
        yearly_dict (dict): {"2020": 1234, "2021": 2345, ...}
        out_dir (str): Directory where plot will be saved.

    Returns:
        str: File path to saved PNG.
    """
    years = sorted([int(y) for y in yearly_dict.keys()])
    values = [
        yearly_dict[str(year)] if str(year) in yearly_dict else yearly_dict[year]
        for year in years
    ]

    # Scale values to millions
    values_m = [v / 1e6 for v in values]

    plt.figure(figsize=(10, 5.5))
    plt.plot(years, values_m, marker="o")

    plt.title("Sales by Year")
    plt.xlabel("Year")
    plt.ylabel("Sales Volume (Millions)")
    plt.grid(True)

    # Force integer ticks for years (fixes 2020.5 issue)
    plt.xticks(years)

    path = os.path.join(out_dir, "sales_by_year_millions.png")
    plt.savefig(path, dpi=120, bbox_inches="tight")
    plt.close()
    return path


def plot_regions(region_year_dict: dict, out_dir: str) -> str:
    """
    Plot sales volume by region over multiple years as a multi-line chart.

    Args:
        region_year_dict (dict): {
            "Europe": {"2020": 1234, "2021": 2345},
            "Asia": {"2020": 3456, "2021": 4567},
        }
        out_dir (str): Directory where plot will be saved.

    Returns:
        str: File path to saved PNG.
    """
    plt.figure(figsize=(10, 5.5))

    # Collect all years across regions
    all_years = sorted(
        {year for region_data in region_year_dict.values() for year in region_data}
    )

    # Plot each region
    for region, year_dict in region_year_dict.items():
        values = [
            year_dict.get(year, 0) / 1e6 for year in all_years
        ]  # convert to millions
        plt.plot(all_years, values, marker="o", label=region)

    plt.title("Sales by Region Over Years")
    plt.xlabel("Year")
    plt.ylabel("Sales Volume (Millions)")
    plt.legend()
    plt.grid(True)

    path = os.path.join(out_dir, "sales_by_region_year_millions.png")
    plt.savefig(path, dpi=120, bbox_inches="tight")
    plt.close()
    return path


def plot_models_over_years(
    year_models_dict: Dict[str, Any],
    out_dir: str,
    title_prefix: str = "All Regions",
) -> str:
    """
    Plot sales of all models over years as lines.

    Args:
        year_models_dict: {
            "2020": [
                {"Model": "X5", "Total_Sales": 23000},
                {"Model": "3 Series", "Total_Sales": 18000},
                ...
            ],
            "2021": [...],
            ...
        }
        out_dir: Directory to save the plot
        title_prefix: Title prefix, default "All Regions"

    Returns:
        Path to saved PNG file
    """

    years = sorted(year_models_dict.keys())
    n_years = len(years)

    if n_years == 0:
        raise ValueError("No data available to plot")

    # Collect all unique models across all years
    all_models_set = set()
    for year in years:
        for entry in year_models_dict[year]:
            all_models_set.add(entry["Model"])
    all_models = sorted(all_models_set)
    n_models = len(all_models)

    plt.figure(figsize=(10, 5.5))

    # Generate color map
    colors = cm.get_cmap("tab20")(np.linspace(0, 1, n_models))
    model_color_map = {model: colors[i] for i, model in enumerate(all_models)}

    # Build matrix: rows = models, cols = years (in millions)
    sales_matrix = np.zeros((n_models, n_years), dtype=float)
    for year_idx, year in enumerate(years):
        year_data = year_models_dict[year]
        sales_dict = {
            entry["Model"]: entry["Total_Sales"] / 1_000_000  # convert to millions
            for entry in year_data
        }
        for model_idx, model in enumerate(all_models):
            sales_matrix[model_idx, year_idx] = sales_dict.get(model, 0)

    # Plot lines
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

    plt.title(f"Model Sales Over Years – {title_prefix}")
    plt.xlabel("Year")
    plt.ylabel("Sales Volume (Millions)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.xticks(rotation=45)

    plt.legend(loc="upper left", bbox_to_anchor=(1, 1), fontsize="small")
    plt.tight_layout()

    os.makedirs(out_dir, exist_ok=True)
    safe_title = title_prefix.replace(" ", "_")
    path = os.path.join(out_dir, f"{safe_title}_models_performance_line.png")
    plt.savefig(path, dpi=120, bbox_inches="tight")
    plt.close()

    return path


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

    # plt.figure(figsize=(max(12, n_models * 0.5), 7))  # widen plot if many models
    plt.figure(figsize=(10, 5.5))

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

    # Format y-axis with commas for thousands
    ax = plt.gca()
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}"))

    plt.legend(loc="upper left", bbox_to_anchor=(1, 1), fontsize="small")
    plt.tight_layout()

    os.makedirs(out_dir, exist_ok=True)
    safe_region_name = region_name.replace(" ", "_")
    path = os.path.join(out_dir, f"{safe_region_name}_all_models_performance_line.png")
    plt.savefig(path, dpi=120, bbox_inches="tight")
    plt.close()

    return path


def plot_correlation_vector(
    corr_vector, out_dir: str, filename: str = "correlation_vector.png"
) -> str:
    """
    Plot a correlation vector (single-column DataFrame or Series) as a horizontal bar plot
    with color reflecting correlation strength and sign, value labels, and legend.

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

    fig_height = max(5, 0.35 * len(features))
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

    # Fix x-axis limits to symmetric range
    ax.set_xlim(-1, 1)

    # Legend for correlation strength ranges
    legend_labels = [
        "Strong +ive correlation (≥ 0.6)",
        "Medium +ive correlation (0.3 to 0.6)",
        "Weak +ive correlation (0.1 to 0.3)",
        "No correlation (-0.1 to 0.1)",
        "Weak -ive correlation (-0.3 to -0.1)",
        "Medium -ive correlation (-0.6 to -0.3)",
        "Strong -ive correlation (≤ -0.6)",
    ]

    legend_colors = [
        "#d73027",  # strong positive red
        "#fc8d59",  # medium positive light red
        "#fddbc7",  # weak positive very light red
        "#f7f7f7",  # no correlation gray/white        "#d1e5f0",  # weak negative very light blue
        "#d1e5f0",  # weak negative very light blue
        "#91bfdb",  # medium negative light blue
        "#4575b4",  # strong negative blue
    ]

    patches = [
        mpatches.Patch(color=color, label=label)
        for color, label in zip(legend_colors, legend_labels)
    ]
    ax.legend(
        handles=patches,
        loc="upper right",
        fontsize=8,
        frameon=False,
        title="Correlation Strength",
    )

    plt.tight_layout()

    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    plt.savefig(path, dpi=120, bbox_inches="tight")
    plt.close()

    return path
