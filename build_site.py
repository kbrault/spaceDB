import os
from jinja2 import Environment, FileSystemLoader
from utils import load_json, remove_and_recreate_dir, validate_json

# Paths of files and dir
pages_file = "data/pages.json"
rockets_file = "data/rockets.json"
rockets_schema_file = "models/rockets.schema.json"
output_dir = "output_site"
template_dir = "templates"
assets_dir = "assets"

# Load rockets and validate data
rockets = load_json(rockets_file)
rockets_schema = load_json(rockets_schema_file)
validate_json(rockets, rockets_schema)

# Load pages
pages = load_json(pages_file)

# Prepare output directory
remove_and_recreate_dir(output_dir)

# Copy flat assets
output_assets_dir = os.path.join(output_dir, "assets")
os.makedirs(output_assets_dir, exist_ok=True)

for filename in os.listdir(assets_dir):
    src_path = os.path.join(assets_dir, filename)
    dest_path = os.path.join(output_assets_dir, filename)
    if os.path.isfile(src_path):
        with open(src_path, "rb") as src_file:
            content = src_file.read()
        with open(dest_path, "wb") as dest_file:
            dest_file.write(content)

# Setup Jinja2
env = Environment(loader=FileSystemLoader(template_dir))

# Generate pages
## Index
index_template = env.get_template("index.html")
index_path = os.path.join(output_dir, "index.html")
with open(index_path, "w", encoding="utf-8") as f:
    f.write(index_template.render(title="Home", pages=pages))

index_template = env.get_template("rockets.html")
index_path = os.path.join(output_dir, "rockets.html")
with open(index_path, "w", encoding="utf-8") as f:
    f.write(index_template.render(title="Rockets", rockets=rockets))

print(f"Site generated in '{output_dir}' folder.")
