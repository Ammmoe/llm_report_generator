"""
Tests for src.data_processing.loader module functions.

These tests validate the data loading, summarization, and analysis
functions used in BMW sales analysis.

Uses pytest fixtures and temporary file paths for file-based outputs.
"""

import os
import pandas as pd
import pytest

# Add src path to sys.path if needed (adjust this if you run tests from a different CWD) # pylint: disable=all
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from src.data_processing import loader


@pytest.fixture
def sample_df():
    """
    Sample DataFrame fixture with simple BMW sales data
    covering multiple years, regions, models, and sales volumes.
    """
    data = {
        "Year": [2020, 2020, 2021, 2021],
        "Region": ["Europe", "Asia", "Europe", "Asia"],
        "Model": ["X5", "X3", "X5", "X3"],
        "Sales_Volume": [100, 150, 200, 250],
    }
    return pd.DataFrame(data)


def test_load_dataset(tmp_path):
    """
    Test loading a dataset from an Excel file.
    """
    df = pd.DataFrame(
        {"Year": [2020], "Region": ["Europe"], "Model": ["X5"], "Sales_Volume": [100]}
    )
    file_path = tmp_path / "test_data.xlsx"
    df.to_excel(file_path, index=False)

    loaded_df = loader.load_dataset(str(file_path))
    assert isinstance(loaded_df, pd.DataFrame)
    assert loaded_df.shape == (1, 4)
    assert list(loaded_df.columns) == ["Year", "Region", "Model", "Sales_Volume"]


def test_summarize_sales_by_region_year(sample_df, tmp_path):
    """
    Test summarizing sales by year and by region-year.
    Checks structure, JSON output, and some sample values.
    """
    output_path = tmp_path / "sales_summary.json"
    summary = loader.summarize_sales_by_region_year(sample_df, str(output_path))

    # Keys in summary dict
    assert "sales_by_year" in summary
    assert "sales_by_region_year" in summary

    # JSON file creation check
    assert os.path.exists(output_path)

    # Year keys are strings in sales_by_region_year, ints in sales_by_year
    # Check overall sales by year
    assert summary["sales_by_year"][2020] == 250  # 100 + 150
    assert summary["sales_by_year"][2021] == 450  # 200 + 250

    # Check sales for Europe in 2020 (key as string)
    assert summary["sales_by_region_year"]["Europe"]["2020"] == 100


def test_summarize_models_by_year(sample_df, tmp_path):
    """
    Test summarizing model sales by year.
    Validates output structure and sample data correctness.
    """
    output_path = tmp_path / "models_by_year.json"
    summary = loader.summarize_models_by_year(sample_df, str(output_path))

    assert isinstance(summary, dict)
    assert "2020" in summary and "2021" in summary

    # Check that model sales for 2020 includes X5 and X3
    models_2020 = summary["2020"]
    models_names_2020 = [item["Model"] for item in models_2020]
    assert "X5" in models_names_2020
    assert "X3" in models_names_2020

    # JSON file created
    assert os.path.exists(output_path)


def test_summarize_models_by_region_year(sample_df, tmp_path):
    """
    Test summarizing model sales by region and year.
    Checks nested dict structure and sample values.
    """
    output_path = tmp_path / "models_by_region.json"
    summary = loader.summarize_models_by_region_year(sample_df, str(output_path))

    assert isinstance(summary, dict)
    assert "Europe" in summary and "Asia" in summary
    assert "2020" in summary["Europe"] and "2021" in summary["Europe"]

    models_2020_europe = summary["Europe"]["2020"]
    models_2021_asia = summary["Asia"]["2021"]

    # Check that "X5" is in Europe 2020 models
    assert any(m["Model"] == "X5" for m in models_2020_europe)
    # Check that "X3" is in Asia 2021 models
    assert any(m["Model"] == "X3" for m in models_2021_asia)

    # JSON file created
    assert os.path.exists(output_path)


def test_explore_key_drivers_of_sales(sample_df):
    """
    Test Pearson correlation calculation for key drivers.
    Checks output type and presence of expected columns.
    """
    corr_df = loader.explore_key_drivers_of_sales(sample_df)
    assert isinstance(corr_df, pd.DataFrame)
    assert "Correlation_with_Sales_Volume" in corr_df.columns

    # Sales_Volume correlation with itself should be 1
    value = corr_df.loc["Sales_Volume", "Correlation_with_Sales_Volume"]
    assert isinstance(value, (int, float))
    assert abs(value - 1) < 1e-6


def test_xgboost_key_drivers(sample_df):
    """
    Test XGBoost feature importance calculation.
    Checks that the output DataFrame is non-empty and has importance scores.
    """
    importance_df = loader.xgboost_key_drivers(sample_df)
    assert isinstance(importance_df, pd.DataFrame)
    assert not importance_df.empty
    assert "importance" in importance_df.columns

    # All importance scores should be non-negative
    assert (importance_df["importance"] >= 0).all()
