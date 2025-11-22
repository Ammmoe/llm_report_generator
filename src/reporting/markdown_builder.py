import os


def build_markdown(analysis_text: str, plot_paths: dict, out_dir: str):
    md = "# BMW Sales Analysis Report\n\n"
    md += analysis_text + "\n\n"

    for title, path in plot_paths.items():
        md += f"## {title.replace('_', ' ').title()}\n"
        md += f"![{title}]({path})\n\n"

    out_path = os.path.join(out_dir, "report.md")
    with open(out_path, "w") as f:
        f.write(md)

    return out_path
