import datetime
import math
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from utils import load_json, remove_and_recreate_dir, validate_json, get_pagination_range

# -----------------------------
# Configuration
# -----------------------------
# Paths and directories
PAGES_FILE = Path("data/pages.json")
ROCKETS_FILE = Path("data/rockets.json")
ROCKETS_SCHEMA_FILE = Path("models/rockets.schema.json")
OUTPUT_DIR = Path("output_site")
TEMPLATE_DIR = Path("templates")
ASSETS_DIR = Path("assets")

# Pagination
ITEMS_PER_PAGE = 10

# Base URL for canonical links and assets
BASE_URL = "http://127.0.0.1:5500/output_site"  

# Meta defaults
INDEX_TITLE = "Home – RocketDB"
INDEX_DESCRIPTION = "RocketDB home page listing rocket pages"
INDEX_CANONICAL = f"{BASE_URL}/index.html"

ROCKETS_TITLE_PATTERN = "Rockets – Page {page_num}"
ROCKETS_DESCRIPTION_PATTERN = "RocketDB listing rockets – page {page_num}"
ROCKETS_CANONICAL_PATTERN = "rockets{page_suffix}.html"

ROCKET_TITLE_PATTERN = "{rocket_name} ({manufacturer})"
ROCKET_DESCRIPTION_PATTERN = "{rocket_name} – Manufacturer: {manufacturer}, First Flight: {first_flight}"
ROCKET_CANONICAL_PATTERN = "rocket/{slug}.html"

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

# -----------------------------
# Page Generators
# -----------------------------
def generate_index(env, pages):
    render_template(
        env, "index.html", OUTPUT_DIR / "index.html",
        title=INDEX_TITLE,
        description=INDEX_DESCRIPTION,
        canonical=INDEX_CANONICAL,
        pages=pages,
        date=datetime.datetime.now().strftime("%Y-%m-%d"),
        base_url=BASE_URL
    )

def generate_rockets_pages(env, rockets):
    total_rockets = len(rockets)
    total_pages = math.ceil(total_rockets / ITEMS_PER_PAGE)
    template_name = "rockets.html"

    for page_num in range(1, total_pages + 1):
        start = (page_num - 1) * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        rockets_page = rockets[start:end]
        pagination = get_pagination_range(page_num, total_pages, delta=3)

        page_suffix = "" if page_num == 1 else f"_page_{page_num}"
        rockets_path = OUTPUT_DIR / (f"rockets.html" if page_num == 1 else f"rockets_page_{page_num}.html")
        canonical_url = f"{BASE_URL}/" + ROCKETS_CANONICAL_PATTERN.format(page_suffix=page_suffix)

        render_template(
            env, template_name, rockets_path,
            title=ROCKETS_TITLE_PATTERN.format(page_num=page_num),
            description=ROCKETS_DESCRIPTION_PATTERN.format(page_num=page_num),
            canonical=canonical_url,
            rockets=rockets_page,
            current_page=page_num,
            total_pages=total_pages,
            pagination=pagination,
            date=datetime.datetime.now().strftime("%Y-%m-%d"),
            base_url=BASE_URL
        )

def generate_rocket_pages(env, rockets):
    template_name = "rocket.html"
    rocket_dir = OUTPUT_DIR / "rocket"
    rocket_dir.mkdir(parents=True, exist_ok=True)

    for rocket in rockets:
        rocket_path = rocket_dir / f"{rocket['slug']}.html"
        canonical_url = f"{BASE_URL}/" + ROCKET_CANONICAL_PATTERN.format(slug=rocket["slug"])

        render_template(
            env, template_name, rocket_path,
            title=ROCKET_TITLE_PATTERN.format(
                rocket_name=rocket["name"],
                manufacturer=rocket["manufacturer"]
            ),
            description=ROCKET_DESCRIPTION_PATTERN.format(
                rocket_name=rocket["name"],
                manufacturer=rocket["manufacturer"],
                first_flight=rocket["first_flight"]
            ),
            canonical=canonical_url,
            rocket=rocket,
            date=datetime.datetime.now().strftime("%Y-%m-%d"),
            base_url=BASE_URL
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
    
    # Sort rockets
    rockets = sorted(rockets, key=lambda r: r["first_flight"])

    # Prepare output directory
    remove_and_recreate_dir(OUTPUT_DIR)

    # Copy assets
    copy_assets(ASSETS_DIR, OUTPUT_DIR / "assets")

    # Setup Jinja2
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    env.globals["base_url"] = BASE_URL 

    # Generate pages
    generate_index(env, pages)
    generate_rockets_pages(env, rockets)
    generate_rocket_pages(env, rockets)

    print(f"Site generated in '{OUTPUT_DIR}' folder.")

if __name__ == "__main__":
    main()
