import os
from jinja2 import Environment, FileSystemLoader
from utils import load_json, remove_and_recreate_dir, validate_json

# Paths of files and dir
pages_file = "data/pages.json"
rockets_file = "data/rockets.json"
rockets_schema_file = "models/rockets.schema.json"
output_dir = "site"
template_dir = "templates"

# Load rockets and validate data
rockets = load_json(rockets_file)
rockets_schema = load_json(rockets_schema_file)
validate_json(rockets, rockets_schema)

# Load pages
pages = load_json(pages_file)

# Prepare output directory
remove_and_recreate_dir(output_dir)

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
