import markdown
import os


def convert_md_to_html(md_path, out_dir):
    with open(md_path, "r") as f:
        text = f.read()

    html = markdown.markdown(text)

    out_path = os.path.join(out_dir, "report.html")
    with open(out_path, "w") as f:
        f.write(html)

    return out_path
