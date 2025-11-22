def evaluate_report(text: str) -> dict:
    """Simple evaluation framework."""
    return {
        "length": len(text.split()),
        "contains_exec_summary": "executive summary" in text.lower(),
    }
