"""
Test suite for src.plotting.plot_functions module.

These tests verify that the plotting functions:
- execute without errors
- produce output PNG files at expected locations
- handle edge cases such as empty inputs or invalid data correctly

Visual correctness of the plots is not tested here.
"""

import os
import pytest
import pandas as pd

# Add src path to sys.path if needed (adjust this if you run tests from a different CWD) # pylint: disable=all
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.plotting import plot_functions as pf


@pytest.fixture
def yearly_dict():
    """Fixture providing sample yearly sales data."""
    return {"2020": 1000000, "2021": 1200000, "2022": 900000}


@pytest.fixture
def region_year_dict():
    """Fixture providing sample regional sales data by year."""
    return {
        "Europe": {"2020": 500000, "2021": 600000, "2022": 400000},
        "Asia": {"2020": 500000, "2021": 600000, "2022": 500000},
    }


@pytest.fixture
def year_models_dict():
    """Fixture providing sample model sales data aggregated by year."""
    return {
        "2020": [
            {"Model": "X5", "Total_Sales": 23000},
            {"Model": "X3", "Total_Sales": 18000},
        ],
        "2021": [
            {"Model": "X5", "Total_Sales": 25000},
            {"Model": "X3", "Total_Sales": 19000},
        ],
    }


@pytest.fixture
def region_models_dict():
    """Fixture providing sample model sales data aggregated by year within a region."""
    return {
        "2020": [
            {"Model": "X5", "Total_Sales": 15000},
            {"Model": "X3", "Total_Sales": 12000},
        ],
        "2021": [
            {"Model": "X5", "Total_Sales": 16000},
            {"Model": "X3", "Total_Sales": 13000},
        ],
    }


@pytest.fixture
def corr_vector():
    """Fixture providing a sample correlation vector as a pandas Series."""
    return pd.Series(
        {
            "Year_2020": 0.9,
            "Year_2021": 0.8,
            "Model_X5": 0.5,
            "Model_X3": -0.3,
            "Region_Europe": 0.1,
            "Region_Asia": -0.05,
        },
        name="Correlation_with_Sales_Volume",
    )


def test_plot_sales_by_year(tmp_path, yearly_dict):
    """
    Test plot_sales_by_year generates a PNG file successfully
    and the file exists with non-zero size.
    """
    path = pf.plot_sales_by_year(yearly_dict, str(tmp_path))
    assert os.path.isfile(path)
    assert path.endswith(".png")
    assert os.path.getsize(path) > 0


def test_plot_regions(tmp_path, region_year_dict):
    """
    Test plot_regions generates a multi-line region sales plot PNG
    file successfully and the file exists.
    """
    path = pf.plot_regions(region_year_dict, str(tmp_path))
    assert os.path.isfile(path)
    assert path.endswith(".png")
    assert os.path.getsize(path) > 0


def test_plot_models_over_years(tmp_path, year_models_dict):
    """
    Test plot_models_over_years generates a line plot for model sales over years,
    saving to PNG and verifying file creation.
    """
    path = pf.plot_models_over_years(
        year_models_dict, str(tmp_path), title_prefix="Test Region"
    )
    assert os.path.isfile(path)
    assert path.endswith(".png")
    assert os.path.getsize(path) > 0


def test_plot_models_over_years_no_data(tmp_path):
    """
    Test plot_models_over_years raises ValueError when given empty data.
    """
    with pytest.raises(ValueError, match="No data available to plot"):
        pf.plot_models_over_years({}, str(tmp_path))


def test_plot_models_by_region_over_years(tmp_path, region_models_dict):
    """
    Test plot_models_by_region_over_years generates line plot for a region's model sales
    and saves a PNG file successfully.
    """
    path = pf.plot_models_by_region_over_years(
        region_models_dict, str(tmp_path), region_name="Europe"
    )
    assert os.path.isfile(path)
    assert path.endswith(".png")
    assert os.path.getsize(path) > 0


def test_plot_models_by_region_over_years_no_data(tmp_path):
    """
    Test plot_models_by_region_over_years raises ValueError when data for the region is empty.
    """
    with pytest.raises(ValueError, match="No data available for region TestRegion"):
        pf.plot_models_by_region_over_years({}, str(tmp_path), region_name="TestRegion")


def test_plot_correlation_vector(tmp_path, corr_vector):
    """
    Test plot_correlation_vector creates a horizontal bar plot PNG from a correlation vector
    and verifies the output file exists.
    """
    path = pf.plot_correlation_vector(corr_vector, str(tmp_path))
    assert os.path.isfile(path)
    assert path.endswith(".png")
    assert os.path.getsize(path) > 0


def test_plot_correlation_vector_invalid_df(tmp_path):
    """
    Test plot_correlation_vector raises ValueError when input DataFrame
    has more than one column.
    """
    import pandas as pd

    df_invalid = pd.DataFrame({"a": [1, 2], "b": [3, 4]})

    with pytest.raises(
        ValueError, match="Input DataFrame must have exactly one column"
    ):
        pf.plot_correlation_vector(df_invalid, str(tmp_path))
