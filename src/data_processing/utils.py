def extract_summary_statistics(df):
    """Extract metrics to send to the LLM."""
    summary = {
        "yearly_sales": df.groupby("year")["sales"].sum().to_dict(),
        "top_models": df.groupby("model")["sales"].sum().nlargest(5).to_dict(),
        "region_performance": df.groupby("region")["sales"].sum().to_dict(),
    }
    return summary
