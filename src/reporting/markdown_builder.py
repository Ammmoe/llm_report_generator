import os
from datetime import datetime
from typing import Optional


def build_markdown_report(
    analysis_text: str,
    plot_paths: dict[str, str],
    out_dir: str,
    report_title: str = "BMW Sales Analysis Report",
    intro_text: Optional[str] = None,
) -> str:
    """
    Build a markdown report combining analysis text and plots.

    Args:
        analysis_text: The main analysis content in markdown format.
        plot_paths: Dictionary mapping plot_type (str) to plot image file path (str).
        out_dir: Directory where the report markdown file will be saved.
        report_title: Title for the report (default: "BMW Sales Analysis Report").
        intro_text: Optional introductory text/summary to include under the title.

    Returns:
        The full file path of the saved markdown report.
    """
    os.makedirs(out_dir, exist_ok=True)

    lines = []

    # Report title and generation time
    lines.append(f"# {report_title}\n")
    lines.append(
        f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    )

    if intro_text:
        lines.append(intro_text.strip() + "\n")

    # Main analysis content
    lines.append("## Analysis\n")
    lines.append(analysis_text.strip() + "\n")

    # Plots section
    if plot_paths:
        lines.append("## Visualizations\n")

        for plot_type, img_path in plot_paths.items():
            # Make a readable title from plot_type, e.g. sales_by_year -> Sales By Year
            section_title = plot_type.replace("_", " ").title()

            # Use relative path if possible, assuming images and md are saved in same out_dir or subdirs
            rel_path = os.path.relpath(img_path, out_dir)

            lines.append(f"### {section_title}\n")
            lines.append(f"![{section_title}]({rel_path})\n")

    # Join lines with double newlines for markdown formatting
    markdown_content = "\n\n".join(lines)

    # Save markdown file
    out_path = os.path.join(out_dir, "report.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    return out_path
