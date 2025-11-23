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

def summarize_models_by_year(df: pd.DataFrame, output_path: str):
    """
    For each Year, list all models sorted by total sales descending,
    combining sales from all regions.

    Output Structure:
    {
        "2020": [
            {"Model": "X5", "Total_Sales": 12000},
            {"Model": "3 Series", "Total_Sales": 11000},
            ...
        ],
        "2021": [...]
    }
    """

    df = df.copy()

    # Ensure correct types
    df["Year"] = df["Year"].astype(int)
    df["Sales_Volume"] = pd.to_numeric(df["Sales_Volume"], errors="coerce").fillna(0)

    summary = {}

    # Group by Year
    for year, df_year in df.groupby("Year"):
        year_str = str(year)

        # Aggregate and sort models by total sales descending
        model_sales = (
            df_year.groupby("Model")["Sales_Volume"]
            .sum()
            .sort_values(ascending=False)
            .astype(int)
        )

        # Convert to list of dicts
        all_models = (
            model_sales.reset_index()
            .rename(columns={"Sales_Volume": "Total_Sales"})
            .to_dict(orient="records")
        )

        summary[year_str] = all_models

    # Save JSON
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)

    return summary

def summarize_models_by_region_year(df: pd.DataFrame, output_path: str):
    """
    For each Region and Year, list all models sorted by sales descending.

    Output Structure:
    {
        "Europe": {
            "2020": [
                {"Model": "X5", "Total_Sales": 5000},
                {"Model": "3 Series", "Total_Sales": 4500},
                ...
            ],
            "2021": [...]
        },
        "Asia": {...}
    }
    """

    df = df.copy()

    # Ensure correct types
    df["Year"] = df["Year"].astype(int)
    df["Sales_Volume"] = pd.to_numeric(df["Sales_Volume"], errors="coerce").fillna(0)

    summary = {}

    # Group by Region first
    for region, df_region in df.groupby("Region"):
        summary[region] = {}

        # Then by Year within Region
        for year, df_region_year in df_region.groupby("Year"):
            year_str = str(year)

            # Aggregate and sort models by sales descending
            model_sales = (
                df_region_year.groupby("Model")["Sales_Volume"]
                .sum()
                .sort_values(ascending=False)
                .astype(int)
            )

            # Convert to list of dicts
            all_models = (
                model_sales.reset_index()
                .rename(columns={"Sales_Volume": "Total_Sales"})
                .to_dict(orient="records")
            )

            summary[region][year_str] = all_models

    # Save JSON
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)

    return summary


def explore_key_drivers_of_sales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the Pearson correlation values between all features
    (after encoding categorical variables, including Year)
    and Sales_Volume. Year is treated as a categorical variable.

    Returns:
        pd.DataFrame: A sorted dataframe of correlations vs Sales_Volume.
    """

    df = df.copy()

    # Ensure Sales_Volume is numeric
    df["Sales_Volume"] = pd.to_numeric(df["Sales_Volume"], errors="ignore").fillna(0)

    # --- Treat Year as categorical ---
    df["Year"] = df["Year"].astype(
        str
    )  # convert to string so it becomes a categorical column

    # Identify categorical columns
    categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()

    # One-hot encode categorical variables (including Year)
    df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

    # Compute Pearson correlation matrix
    corr_matrix = df_encoded.corr(method="pearson")

    # Extract correlations with Sales_Volume
    sales_corr = corr_matrix["Sales_Volume"].sort_values(ascending=False)

    return sales_corr.to_frame(name="Correlation_with_Sales_Volume")
