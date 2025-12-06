import datetime
import math
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from utils import load_json, remove_and_recreate_dir, validate_json, get_pagination_range

# -----------------------------
# Configuration
# -----------------------------
PAGES_FILE = Path("data/pages.json")
ROCKETS_FILE = Path("data/rockets.json")
ROCKETS_SCHEMA_FILE = Path("models/rockets.schema.json")
OUTPUT_DIR = Path("output_site")
TEMPLATE_DIR = Path("templates")
ASSETS_DIR = Path("assets")
ITEMS_PER_PAGE = 10

# -----------------------------
# Helper Functions
# -----------------------------
def copy_assets(src_dir: Path, dest_dir: Path):
    dest_dir.mkdir(parents=True, exist_ok=True)
    for file_path in src_dir.iterdir():
        if file_path.is_file():
            dest_file = dest_dir / file_path.name
            dest_file.write_bytes(file_path.read_bytes())

def render_template(template_env, template_name, output_path, **context):
    template = template_env.get_template(template_name)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(template.render(**context), encoding="utf-8")

def generate_index(env, pages, output_dir):
    render_template(
        env, "index.html", output_dir / "index.html",
        title="Home",
        pages=pages,
        date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

def generate_rockets_pages(env, rockets, output_dir, items_per_page=10):
    total_rockets = len(rockets)
    total_pages = math.ceil(total_rockets / items_per_page)
    template_name = "rockets.html"

    for page_num in range(1, total_pages + 1):
        start = (page_num - 1) * items_per_page
        end = start + items_per_page
        rockets_page = rockets[start:end]
        pagination = get_pagination_range(page_num, total_pages, delta=3)

        if page_num == 1:
            rockets_path = output_dir / "rockets.html"
        else:
            rockets_path = output_dir / f"rockets_page_{page_num}.html"

        render_template(
            env, template_name, rockets_path,
            title="Rockets",
            rockets=rockets_page,
            date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            current_page=page_num,
            total_pages=total_pages,
            pagination=pagination
        )

# -----------------------------
# Main Script
# -----------------------------
def main():
    # Load data
    rockets = load_json(ROCKETS_FILE)
    rockets_schema = load_json(ROCKETS_SCHEMA_FILE)
    validate_json(rockets, rockets_schema)
    pages = load_json(PAGES_FILE)

    # Prepare output directory
    remove_and_recreate_dir(OUTPUT_DIR)

    # Copy assets
    copy_assets(ASSETS_DIR, OUTPUT_DIR / "assets")

    # Setup Jinja2
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

    # Generate pages
    generate_index(env, pages, OUTPUT_DIR)
    generate_rockets_pages(env, rockets, OUTPUT_DIR, ITEMS_PER_PAGE)

    print(f"Site generated in '{OUTPUT_DIR}' folder.")

if __name__ == "__main__":
    main()
