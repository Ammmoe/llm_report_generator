import os
import matplotlib.pyplot as plt


def plot_sales_by_year(yearly_dict, out_dir):
    years = list(yearly_dict.keys())
    values = list(yearly_dict.values())

    plt.figure(figsize=(8, 4))
    plt.plot(years, values)
    plt.title("Sales by Year")
    plt.xlabel("Year")
    plt.ylabel("Sales")

    path = os.path.join(out_dir, "sales_by_year.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    return path


def plot_top_models(models_dict, out_dir):
    labels = list(models_dict.keys())
    values = list(models_dict.values())

    plt.figure(figsize=(8, 4))
    plt.bar(labels, values)
    plt.title("Top Models")
    plt.xticks(rotation=45)

    path = os.path.join(out_dir, "top_models.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    return path


def plot_regions(region_dict, out_dir):
    labels = list(region_dict.keys())
    values = list(region_dict.values())

    plt.figure(figsize=(8, 4))
    plt.bar(labels, values)
    plt.title("Region Sales Performance")

    path = os.path.join(out_dir, "region_performance.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    return path
