import os
from datetime import datetime
from typing import Optional, List


def build_markdown_report(
    analysis_markdowns: List[str],
    out_dir: str,
    report_title: str = "BMW Sales Analysis Report",
    intro_text: Optional[str] = None,
) -> str:
    """
    Combine multiple LLM-generated markdown reports into a single markdown file
    with a title, timestamp, and optional intro.

    Args:
        analysis_markdowns: List of complete markdown strings to combine.
        out_dir: Directory where report.md will be saved.
        report_title: Title for the markdown document.
        intro_text: Optional introductory text for the combined report.

    Returns:
        Path to the saved markdown file.
    """
    os.makedirs(out_dir, exist_ok=True)

    lines = []

    # Report title and timestamp
    lines.append(f"# {report_title}\n")
    lines.append(f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

    # Optional intro text
    if intro_text:
        lines.append(intro_text.strip() + "\n")

    # Add each markdown report with a horizontal rule separator
    for idx, md in enumerate(analysis_markdowns):
        if idx > 0:
            # Add a horizontal rule to visually separate sections
            lines.append("\n---\n")
        lines.append(md.strip())

    # Join all lines with double newlines
    markdown_content = "\n\n".join(lines)

    # Save combined markdown file
    out_path = os.path.join(out_dir, "report.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    return out_path
