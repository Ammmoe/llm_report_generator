import json
import pandas as pd


def load_dataset(path: str) -> pd.DataFrame:
    """Load BMW sales dataset from Excel."""
    df = pd.read_excel(path)
    return df


def summarize_sales_by_region_year(df: pd.DataFrame, output_path: str):
    """
    Summarize total sales by Region, and by Region + Year.
    Save the summary dict as a JSON file at output_path.

    Output format:
    {
        "sales_by_year": {
            "2020": 123456,
            "2021": 234567,
            ...
        },
        "sales_by_region_year": {
            "Europe": {
                "2020": 45678,
                "2021": 56789,
                ...
            },
            "Asia": {
                ...
            }
        }
    }
    """
    # Ensure correct types
    df = df.copy()
    df["Year"] = df["Year"].astype(int)
    df["Sales_Volume"] = pd.to_numeric(df["Sales_Volume"], errors="coerce")
    df["Sales_Volume"] = df["Sales_Volume"].fillna(0)

    # Summarize sales by year (overall)
    sales_by_year = df.groupby("Year")["Sales_Volume"].sum().astype(int).to_dict()

    # Summarize sales by region and year
    sales_by_region_year_df = (
        df.groupby(["Region", "Year"])["Sales_Volume"].sum().astype(int).reset_index()
    )

    # Convert to nested dict Region -> Year -> Sales
    sales_by_region_year = {}
    for _, row in sales_by_region_year_df.iterrows():
        region = row["Region"]
        year = str(row["Year"])
        sales = row["Sales_Volume"]
        sales_by_region_year.setdefault(region, {})[year] = sales

    # Combine results
    summary = {
        "sales_by_year": sales_by_year,
        "sales_by_region_year": sales_by_region_year,
    }

    # Save to JSON file
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)

    return summary
