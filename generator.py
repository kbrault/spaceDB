import json
import os
from jinja2 import Environment, FileSystemLoader

# Paths
data_file = "data/pages.json"
output_dir = "site"
template_dir = "templates"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load JSON data
with open(data_file, "r", encoding="utf-8") as f:
    pages = json.load(f)

# Setup Jinja2 environment
env = Environment(loader=FileSystemLoader(template_dir))

# Generate index.html
index_template = env.get_template("index.html")
index_path = os.path.join(output_dir, "index.html")
with open(index_path, "w", encoding="utf-8") as f:
    f.write(index_template.render(title="Home", pages=pages))

# Generate individual pages
page_template = env.get_template("page.html")
for page in pages:
    page_path = os.path.join(output_dir, page["url"])
    with open(page_path, "w", encoding="utf-8") as f:
        f.write(page_template.render(title=page["title"], summary=page["summary"]))

print(f"Site generated in '{output_dir}' folder.")
