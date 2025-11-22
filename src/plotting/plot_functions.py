import os
import matplotlib.pyplot as plt


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


def plot_top_models(models_dict: dict, out_dir: str) -> str:
    """
    Plot top-selling models as a bar chart.

    Args:
        models_dict (dict): Mapping of model names (str) to sales volume (int).
                            Example: {"Model A": 1234, "Model B": 2345, ...}
        out_dir (str): Directory path where the plot image will be saved.

    Returns:
        str: File path to the saved PNG plot image.
    """
    labels = list(models_dict.keys())
    values = list(models_dict.values())

    plt.figure(figsize=(8, 4))
    plt.bar(labels, values)
    plt.title("Top Models Sales")
    plt.xticks(rotation=45, ha="right")

    path = os.path.join(out_dir, "top_models.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    return path
